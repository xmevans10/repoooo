"""Conservative MLB contract matching for a public-feed research watchlist.

ESPN offers a single-book benchmark with unknown quote age. These are indicative
comparisons only; never passed to the paper-position or real-order machinery.
"""
import re
from datetime import datetime
from zoneinfo import ZoneInfo
from .engine import devig, stamp

ALIASES = {'Los Angeles D':'Los Angeles Dodgers', 'Los Angeles A':'Los Angeles Angels',
           'Chicago C':'Chicago Cubs', 'Chicago W':'Chicago White Sox',
           'New York M':'New York Mets', 'New York Y':'New York Yankees',
           'Athletics':'Athletics', 'Oakland':'Athletics'}
PATTERN = re.compile(r'^If (.+) wins the (.+) vs (.+) professional baseball game originally scheduled for (.+), then the market resolves to Yes\.$')


def resolve(label, teams):
    name = ALIASES.get(label)
    matches = [t for t in teams if t == name] if name else [t for t in teams if t == label or t.startswith(label+' ')]
    return matches[0] if len(matches)==1 else None


def match(market, events):
    rule = PATTERN.fullmatch(market.get('rules', ''))
    if not rule:
        return None
    selection, first, second, raw_time = rule.groups()
    try:
        # Explicit timezone labels only. Reject unexpected text or DST mismatches.
        local = datetime.strptime(raw_time[:-4], '%b %d, %Y at %I:%M %p').replace(tzinfo=ZoneInfo('America/New_York'))
        if local.tzname() != raw_time[-3:]:
            return None
    except ValueError:
        return None
    found=[]
    for e in events:
        if e['sport_key'] != 'mlb' or e.get('status') != 'pre' or stamp(e['commence_time']) != local:
            continue
        for b in e['bookmakers']:
            if b['key'] != 'draftkings' or len(b['prices']) != 2:
                continue
            teams=list(b['prices'])
            a,z,s = resolve(first,teams),resolve(second,teams),resolve(selection,teams)
            if not a or not z or a==z or s not in (a,z):
                continue
            found.append((e,b,s))
    return found[0] if len(found)==1 else None


def compare(markets, events):
    rows=[]
    for market in markets:
        matched=match(market,events)
        if not matched:
            continue
        e,b,selection=matched
        p=devig(b['prices'])[selection]
        try:
            ask=float(market['yes_ask'])
        except (ValueError,TypeError):
            continue
        if not 0 < ask < 1:
            continue
        rows.append(dict(ticker=market['ticker'], event=e['name'], selection=selection,
                         probability=p, yes_ask=ask, raw_gap=p-ask,
                         reason='Watch only: single-book benchmark; unknown quote age; before fees',
                         source='DraftKings via ESPN', commence_time=e['commence_time'], retrieved_at=e['retrieved_at']))
    return sorted(rows,key=lambda r:r['raw_gap'],reverse=True)
