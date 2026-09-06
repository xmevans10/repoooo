"""Public Kalshi discovery and explicit forecast evaluation. No order endpoint."""
import math
from decimal import Decimal, ROUND_CEILING
from urllib.parse import urlencode, quote
from .feeds import fetch
from .engine import stamp, utcnow

BASE = 'https://api.elections.kalshi.com/trade-api/v2'


def fee(count, price, multiplier):
    p = Decimal(str(price))
    if count < 1 or not 0 < p < 1 or not math.isfinite(multiplier) or multiplier < 0:
        raise ValueError('Invalid fee inputs')
    return float((Decimal('.07') * Decimal(str(multiplier)) * count * p * (1-p)).quantize(Decimal('.01'), rounding=ROUND_CEILING))


def scan(series='KXMLBGAME', forecasts=None, equity=1000):
    """Forecasts must explicitly name a contract and its rule-matched outcome.

    External forecasts are hypotheses, never inferred from Kalshi's own price.
    Discovery is bounded at 5,000 contracts; truncation is surfaced.
    """
    forecasts = forecasts or {}
    rows, errors = [], []
    for ticker in series.split(','):
        metadata = fetch(BASE + '/series/' + quote(ticker, safe=''))['series']
        cursor = ''
        for page in range(5):
            data = fetch(BASE + '/markets?' + urlencode(dict(series_ticker=ticker, status='open', limit=1000, cursor=cursor)))
            retrieved = utcnow().isoformat()
            for m in data['markets']:
                f = forecasts.get(m['ticker'])
                row = dict(ticker=m['ticker'], event=m['event_ticker'], title=m.get('title'),
                           yes_ask=m.get('yes_ask_dollars'), no_ask=m.get('no_ask_dollars'),
                           retrieved_at=retrieved, rules=m.get('rules_primary'), rules_secondary=m.get('rules_secondary'),
                           status=m.get('status'), close_time=m.get('close_time'),
                           yes_ask_size=m.get('yes_ask_size_fp'),
                           fee_type=metadata.get('fee_type'), fee_multiplier=metadata.get('fee_multiplier'),
                           reason='Pass: no independent, rule-matched forecast', contracts=0)
                if f:
                    try:
                        if not f.get('rules_verified') or f.get('rules_primary') != m.get('rules_primary'):
                            raise ValueError('contract rules not verified or have changed')
                        age = (utcnow()-stamp(f['generated_at'])).total_seconds()
                        if not 0 <= age <= 300 or stamp(f['valid_until']) <= utcnow():
                            raise ValueError('forecast stale')
                        if m['status'] != 'active' or stamp(m['close_time']) <= utcnow():
                            raise ValueError('market inactive')
                        if metadata.get('fee_type') not in ('quadratic', 'quadratic_with_maker_fees'):
                            raise ValueError('unsupported fee model')
                        multiplier = float(metadata['fee_multiplier'])
                        probability = float(f['probability_yes'])
                        buffer = float(f.get('buffer', .03))
                        if not 0 < probability < 1 or not .02 <= buffer <= .5:
                            raise ValueError('invalid probability or buffer')
                        # Use YES only: API supplies explicit YES ask depth.
                        price = float(m['yes_ask_dollars'])
                        size = math.floor(float(m.get('yes_ask_size_fp', 0)))
                        if not 0 < price < 1 or size < 1:
                            raise ValueError('no ask depth')
                        p = max(0, probability-buffer)
                        unit_cost = price + fee(1, price, multiplier)
                        kelly = max(0, (p-unit_cost)/(1-unit_cost))*.25 if unit_cost < 1 else 0
                        budget = min(equity*.01, equity*kelly)
                        count = min(size, math.floor(budget/unit_cost))
                        if count < 1:
                            raise ValueError('no buffered edge after fees')
                        cost = count*price + fee(count, price, multiplier)
                        expected_profit = count*p-cost
                        if expected_profit/cost < .02:
                            raise ValueError('net buffered edge below 2%')
                        row.update(contracts=count, cost=round(cost, 2),
                                   fee=fee(count, price, multiplier), probability=probability,
                                   buffered_probability=p, buffered_profit=expected_profit,
                                   reason='Research candidate; fill and rule review required')
                    except (KeyError, ValueError, TypeError) as e:
                        row['reason'] = 'Pass: ' + str(e)
                rows.append(row)
            cursor = data.get('cursor', '')
            if not cursor:
                break
        if cursor:
            errors.append(f'{ticker}: truncated at 5,000 markets')
    return dict(created=utcnow().isoformat(), source='kalshi', markets=rows, errors=errors)
