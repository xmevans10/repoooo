from __future__ import annotations

import math
import statistics
from datetime import datetime, timezone

MAJOR_BOOKS = {'draftkings', 'fanduel', 'betmgm', 'williamhill_us', 'caesars',
               'pinnacle', 'bet365', 'betfair_ex_uk', 'betfair_ex_eu', 'unibet',
               'unibet_uk', 'unibet_eu', 'williamhill', 'bovada', 'betrivers',
               'fanatics', 'pointsbetau', 'sportsbet', 'ladbrokes_uk', 'coral'}
# Exchanges need commission and fill modelling; excluded from executable targets.
TARGETS = MAJOR_BOOKS - {'betfair_ex_uk', 'betfair_ex_eu'}
MODEL = 'leave-one-book-out-v1'


def utcnow():
    return datetime.now(timezone.utc)


def stamp(value):
    d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if d.tzinfo is None:
        raise ValueError('Timezone required')
    return d


def decimal(american):
    a = float(american)
    if not math.isfinite(a) or abs(a) < 100:
        raise ValueError('Invalid American odds')
    return 1 + (a / 100 if a > 0 else 100 / -a)


def devig(prices):
    if len(prices) not in (2, 3) or any(not math.isfinite(p) or p <= 1 for p in prices.values()):
        raise ValueError('Incomplete or invalid moneyline market')
    total = sum(1 / p for p in prices.values())
    if not .95 <= total <= 1.25:
        raise ValueError('Suspicious market margin')
    return {k: (1 / v) / total for k, v in prices.items()}


def analyze(events, equity=1000, now=None, allowed=None):
    """Consensus is a hypothesis, not a calibrated independent prediction.

    Each target is excluded from its reference set. Three other books required.
    The uncertainty haircut is a sensitivity buffer, NOT a confidence interval.
    """
    now = now or utcnow()
    rows = []
    for e in events:
        try:
            if stamp(e['commence_time']) <= now or e.get('status', 'pre') != 'pre':
                continue
        except (ValueError, KeyError, TypeError):
            continue
        valid = {}
        for b in e.get('bookmakers', []):
            if b['key'] not in MAJOR_BOOKS:
                continue
            try:
                fair = devig(b['prices'])
                age = (now - stamp(b['last_update'])).total_seconds() if b.get('last_update') else None
                valid[b['key']] = (b, fair, age)
            except (ValueError, TypeError, KeyError):
                continue
        for key, (b, fair, age) in valid.items():
            if key not in TARGETS or (allowed and key not in allowed):
                continue
            refs = [(other, f) for k, (other, f, a) in valid.items()
                    if k != key and a is not None and 0 <= a <= 300 and set(f) == set(fair)]
            for outcome, price in b['prices'].items():
                ps = [f[outcome] for _, f in refs]
                estimate = statistics.mean(ps) if len(ps) >= 3 else fair[outcome]
                dispersion = statistics.pstdev(ps) if len(ps) >= 3 else 0
                buffer = max(.02, dispersion * 1.5)
                cautious = max(0, estimate - buffer)
                ev = estimate * price - 1
                conservative_ev = cautious * price - 1
                reason = 'Paper candidate'
                if len(ps) < 3:
                    reason = 'Pass: fewer than 3 other fresh books'
                elif age is None:
                    reason = 'Pass: source quote timestamp unavailable'
                elif not 0 <= age <= 300:
                    reason = 'Pass: quote stale or clock mismatch'
                elif dispersion > .04:
                    reason = 'Pass: reference books disagree'
                elif conservative_ev < .02:
                    reason = 'Pass: buffered edge below 2%'
                kelly = max(0, conservative_ev / (price - 1)) * .25
                stake = math.floor(min(equity * .01, equity * kelly) * 100) / 100 if reason == 'Paper candidate' else 0
                if reason == 'Paper candidate' and stake < 1:
                    reason, stake = 'Pass: stake below $1', 0
                rows.append(dict(event_id=e['id'], sport=e['sport_key'], event=e['name'],
                                 commence_time=e['commence_time'], book=key, outcome=outcome,
                                 decimal_odds=price, probability=estimate, buffered_probability=cautious,
                                 ev=ev, buffered_ev=conservative_ev, stake=stake, reason=reason,
                                 references=[r['key'] for r, _ in refs], quote_time=b.get('last_update'),
                                 retrieved_at=e['retrieved_at'], model=MODEL))
    return sorted(rows, key=lambda r: (r['stake'] > 0, r['buffered_ev']), reverse=True)
