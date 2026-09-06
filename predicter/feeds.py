import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .engine import decimal, utcnow

LEAGUES = {'mlb': 'baseball/mlb', 'nfl': 'football/nfl', 'nba': 'basketball/nba',
           'wnba': 'basketball/wnba', 'nhl': 'hockey/nhl', 'ncaaf': 'football/college-football',
           'epl': 'soccer/eng.1', 'mls': 'soccer/usa.1', 'laliga': 'soccer/esp.1'}


def fetch(url):
    # curl honors the host's network configuration. The URL is passed on stdin
    # so API credentials never appear in process arguments or exception messages.
    import subprocess
    result = subprocess.run(['curl', '--silent', '--show-error', '--fail',
                             '--max-time', '25', '--config', '-'],
                            input='url = ' + json.dumps(url) + '\n',
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'Feed request failed (transport code {result.returncode})')
    try:
        return json.loads(result.stdout)
    except ValueError:
        raise RuntimeError('Feed returned invalid JSON') from None


def espn_parse(data, sport, retrieved):
    events = []
    for e in data.get('events', []):
        c = e['competitions'][0]
        teams = {t['homeAway']: t['team']['displayName'] for t in c['competitors']}
        books = []
        for o in c.get('odds') or []:
            # Suspended/unavailable ESPN prices can be represented by null.
            if not isinstance(o, dict):
                continue
            provider = o.get('provider')
            if not isinstance(provider, dict):
                continue
            name = provider.get('name')
            if not isinstance(name, str) or not name.strip():
                continue
            prices = {}
            try:
                ml = o.get('moneyline', {})
                for side in ('home', 'away'):
                    prices[teams[side]] = decimal(ml[side]['close']['odds'])
                if 'draw' in ml:
                    prices['Draw'] = decimal(ml['draw']['close']['odds'])
                # Soccer requires the draw; do not normalize a partial market.
                if sport in ('epl', 'mls', 'laliga') and 'Draw' not in prices:
                    continue
            except (KeyError, ValueError, TypeError):
                continue
            books.append(dict(key=name.lower().replace(' ', ''), title=name,
                              prices=prices, last_update=None))
        events.append(dict(id='espn:' + e['id'], sport_key=sport, name=e['name'],
                           commence_time=e['date'], status=c['status']['type']['state'],
                           retrieved_at=retrieved, bookmakers=books))
    return events


def espn():
    today = utcnow().date()
    tasks = [(sport, path, today + timedelta(days=day)) for sport, path in LEAGUES.items() for day in (0, 1)]
    def read(task):
        sport, path, date = task
        url = f'https://site.api.espn.com/apis/site/v2/sports/{path}/scoreboard?dates={date:%Y%m%d}'
        try:
            return espn_parse(fetch(url), sport, utcnow().isoformat()), None
        except (RuntimeError, KeyError, ValueError, TypeError) as e:
            return [], f'{sport} {date}: {e}'
    events, errors = {}, []
    with ThreadPoolExecutor(max_workers=6) as pool:
        for batch, error in pool.map(read, tasks):
            events.update({e['id']: e for e in batch})
            if error:
                errors.append(error)
    return list(events.values()), errors


def odds_api(sports='upcoming', regions='us,uk,eu'):
    key = os.environ.get('ODDS_API_KEY')
    if not key:
        raise RuntimeError('Set ODDS_API_KEY in your local environment to enable cross-book odds.')
    base = 'https://api.the-odds-api.com/v4/sports'
    if sports == 'all':
        catalog = fetch(base + '?' + urlencode({'apiKey': key}))
        sports = ','.join(s['key'] for s in catalog if s['active'] and not s['has_outrights'])
    events, errors = [], []
    for sport in sports.split(','):
        if not sport.replace('_', '').isalnum():
            raise ValueError('Invalid sport key')
        query = urlencode(dict(apiKey=key, regions=regions, markets='h2h', oddsFormat='decimal'))
        try:
            data = fetch(f'{base}/{sport}/odds?{query}')
            retrieved = utcnow().isoformat()
            for e in data:
                books = []
                for b in e['bookmakers']:
                    for m in b['markets']:
                        if m['key'] == 'h2h':
                            books.append(dict(key=b['key'], title=b['title'],
                                last_update=m.get('last_update') or b.get('last_update'),
                                prices={o['name']: float(o['price']) for o in m['outcomes']}))
                events.append(dict(id='odds:' + e['id'], sport_key=e['sport_key'],
                    name=f"{e['away_team']} at {e['home_team']}", commence_time=e['commence_time'],
                    retrieved_at=retrieved, bookmakers=books))
        except RuntimeError as e:
            errors.append(f'{sport}: {e}')
            break  # Stop on quota/auth/network errors rather than spend more requests.
    return events, errors
