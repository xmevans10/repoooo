"""Frozen 30-day forward paper experiment. All prices/fills are hypothetical."""
import copy
import hashlib
import json
import math
import random
import statistics
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote
from .engine import stamp, utcnow
from .kalshi import fee, BASE, scan
from .feeds import espn, fetch
from .benchmark import compare

POLICY = dict(version='mlb-dk-kalshi-paper-v1', days=30, starting_cents=100000,
              probability_buffer=.05, min_net_ev=.02, max_position=.01,
              max_exposure=.05, quarter_kelly=.25, min_minutes_before_start=15,
              min_validation_events=100, bootstrap_samples=5000,
              entry_window_hours=24, max_spread=.05)
POLICY_HASH = hashlib.sha256(json.dumps(POLICY, sort_keys=True).encode()).hexdigest()


def initialize(now):
    return dict(schema=1, started_at=now.isoformat(),
                entries_end_at=(now+timedelta(days=30)).isoformat(),
                policy=copy.deepcopy(POLICY), policy_hash=POLICY_HASH,
                positions=[], scans=0, last_scan=None, errors=[], last_opportunities=[])


def accounting(state):
    profit = sum(p.get('profit_cents', 0) for p in state['positions'])
    exposure = sum(p['cost_cents'] for p in state['positions'] if p['status']=='open')
    equity = state['policy']['starting_cents'] + profit
    return dict(equity_cents=equity, available_cents=equity-exposure,
                exposure_cents=exposure, profit_cents=profit)


def assess(state, now):
    closed=[p for p in state['positions'] if p['status']=='settled']
    # Group positions by event before resampling: complementary contracts are correlated.
    groups={}
    for p in closed:
        g=groups.setdefault(p['event'], [0,0])
        g[0]+=p['profit_cents'];g[1]+=p['cost_cents']
    cost=sum(v[1] for v in groups.values())
    roi=sum(v[0] for v in groups.values())/cost if cost else None
    low=high=None
    if len(groups)>=2:
        rng=random.Random(30)
        values=list(groups.values());samples=[]
        for _ in range(POLICY['bootstrap_samples']):
            sample=rng.choices(values,k=len(values))
            samples.append(sum(x[0] for x in sample)/sum(x[1] for x in sample))
        samples.sort();low=samples[int(.025*len(samples))];high=samples[int(.975*len(samples))]
    open_count=sum(p['status']=='open' for p in state['positions'])
    if now < stamp(state['entries_end_at']):
        verdict='Collecting forward evidence'
    elif open_count:
        verdict='Entry window finished; waiting for settlement'
    elif len(groups)<POLICY['min_validation_events']:
        verdict='Inconclusive: insufficient independent settled events'
    elif low is not None and low>0:
        verdict='Positive paper evidence under simulated-fill assumptions; not proof of future profit'
    else:
        verdict='Profitability not established'
    balance=peak=state['policy']['starting_cents'];drawdown=0
    for p in sorted(closed,key=lambda p:p['settled_at']):
        balance+=p['profit_cents'];peak=max(peak,balance)
        drawdown=max(drawdown,(peak-balance)/peak)
    binary=[p for p in closed if p.get('settlement_value') in (0,1)]
    brier=statistics.mean((p['probability']-p['settlement_value'])**2 for p in binary) if binary else None
    return dict(verdict=verdict, settled_events=len(groups), open_positions=open_count,
                roi=roi, roi_95pct_event_bootstrap=[low,high], brier=brier,
                max_realized_drawdown=drawdown)


def settle(state, now, getter=fetch):
    for p in state['positions']:
        if p['status']!='open':
            continue
        try:
            m=getter(BASE+'/markets/'+quote(p['ticker'],safe=''))['market']
            if m['status'] not in ('settled','finalized'):
                continue
            value=m.get('settlement_value_dollars')
            if value is None:
                value={'yes':1,'no':0}.get(m.get('result'))
            if value is None or not 0 <= float(value) <= 1:
                raise ValueError('Settlement value missing or invalid')
            value=float(value)
            payout=round(p['contracts']*value*100)
            p.update(status='settled',settled_at=now.isoformat(),settlement_value=value,
                     payout_cents=payout,profit_cents=payout-p['cost_cents'])
        except (RuntimeError,ValueError,KeyError,TypeError) as e:
            state['errors'].append(f"Settlement {p['ticker']}: {e}")


def enter(state, benchmarks, markets, now, getter=fetch):
    if now>=stamp(state['entries_end_at']):
        return
    seen={p['event'] for p in state['positions']}
    by_ticker={m['ticker']:m for m in markets}
    for b in benchmarks:
        m=by_ticker[b['ticker']]
        if m['event'] in seen or b['raw_gap'] <= POLICY['probability_buffer']:
            continue
        try:
            minutes=(stamp(b['commence_time'])-now).total_seconds()/60
            if not POLICY['min_minutes_before_start'] <= minutes <= POLICY['entry_window_hours']*60:
                continue
            if not 0 <= (now-stamp(b['retrieved_at'])).total_seconds() <= 120:
                continue
            if m['fee_type'] not in ('quadratic','quadratic_with_maker_fees'):
                continue
            multiplier=float(m['fee_multiplier'])
            # Re-fetch the exact contract immediately before simulating a fill.
            fresh=getter(BASE+'/markets/'+quote(m['ticker'],safe=''))['market']
            if fresh['status']!='active' or fresh.get('rules_primary')!=m['rules'] or fresh.get('rules_secondary')!=m['rules_secondary']:
                continue
            ask=float(fresh['yes_ask_dollars']);bid=float(fresh['yes_bid_dollars'])
            depth=math.floor(float(fresh.get('yes_ask_size_fp',0)))
            if not 0 < bid <= ask < 1 or ask-bid>POLICY['max_spread'] or depth<1:
                continue
            conservative=max(0,b['probability']-POLICY['probability_buffer'])
            unit=ask+fee(1,ask,multiplier)
            if unit>=1:
                continue
            kelly=max(0,(conservative-unit)/(1-unit))*POLICY['quarter_kelly']
            a=accounting(state)
            budget=min(a['equity_cents']*POLICY['max_position'],a['equity_cents']*kelly,
                       a['available_cents'], max(0,a['equity_cents']*POLICY['max_exposure']-a['exposure_cents']))/100
            count=min(depth,math.floor(budget/unit))
            if count<1:
                continue
            fees=fee(count,ask,multiplier)
            cost=math.ceil((count*ask+fees)*100-1e-8)
            if cost<100 or (count*conservative-cost/100)/(cost/100)<POLICY['min_net_ev']:
                continue
            state['positions'].append(dict(ticker=m['ticker'],event=m['event'],
                title=b['event'],selection=b['selection'],status='open',side='yes',
                contracts=count,price=ask,fee_cents=round(fees*100),cost_cents=cost,
                probability=b['probability'],buffered_probability=conservative,
                entered_at=now.isoformat(),commence_time=b['commence_time'],
                source=b['source'],source_retrieved_at=b['retrieved_at'],
                source_quote_time=None,quote_observed_at=utcnow().isoformat(),
                displayed_ask_size=depth,rules_primary=m['rules'],rules_secondary=m['rules_secondary'],
                fill_assumption='Full displayed ask fill; no actual order or fill confirmation'))
            seen.add(m['event'])
        except (RuntimeError,ValueError,TypeError,KeyError) as e:
            state['errors'].append(f"Entry {m['ticker']}: {e}")


def render(state):
    a=accounting(state);v=state['assessment']
    cash=lambda c:f'${c/100:,.2f}'
    pct=lambda p:'—' if p is None else f'{p:+.2%}'
    lines=['# Predicter · 30-day paper experiment','',
        '**Paper only. No real orders. Positive returns are not guaranteed.**','',
        f"**{v['verdict']}**",'',
        f"Entry window: {state['started_at']} → {state['entries_end_at']}",
        f"Last run: {state['last_scan']} · Scans: {state['scans']}",'',
        '| Starting bankroll | Equity | Available cash | Open exposure | Realized P&L |',
        '|---:|---:|---:|---:|---:|',
        f"| $1,000.00 | {cash(a['equity_cents'])} | {cash(a['available_cents'])} | {cash(a['exposure_cents'])} | {cash(a['profit_cents'])} |",'',
        f"Settled independent events: **{v['settled_events']}** · Open positions: **{v['open_positions']}** · Net ROI: **{pct(v['roi'])}**",
        f"95% event-bootstrap ROI interval: {pct(v['roi_95pct_event_bootstrap'][0])} to {pct(v['roi_95pct_event_bootstrap'][1])}",
        f"Realized drawdown: {v['max_realized_drawdown']:.2%} · Brier score: {v['brier'] if v['brier'] is not None else '—'}",'',
        '## Positions','',
        '| Entered (UTC) | Contract | YES count | Price | Cost incl. fee | Status | P&L |',
        '|---|---|---:|---:|---:|---|---:|']
    for p in reversed(state['positions']):
        lines.append(f"| {p['entered_at']} | {p['ticker']} | {p['contracts']} | ${p['price']:.4f} | {cash(p['cost_cents'])} | {p['status']} | {cash(p['profit_cents']) if 'profit_cents' in p else '—'} |")
    if not state['positions']:lines+=['| — | No qualifying paper entries | — | — | — | — | — |']
    lines+=['','## Latest matched prices','',
        'Indicative differences below are **before fees and uncertainty buffer**, not entry signals.','',
        '| Contract | DK implied probability | Kalshi ask | Raw difference |','|---|---:|---:|---:|']
    for b in state['last_opportunities'][:30]:
        lines.append(f"| {b['ticker']} | {b['probability']:.1%} | ${b['yes_ask']:.2f} | {b['raw_gap']:+.1%} |")
    lines+=['','## Feed health','']+(state['errors'] or ['All requested feeds responded.'])
    lines+=['','## Frozen protocol','',
        'MLB YES contracts only. Exact participant/time/rule matching. DraftKings margin-free implied probability minus 5 percentage points; require 2% expected return after taker fees. Enter 15 minutes–24 hours before start. Quarter Kelly, maximum 1% equity per event and 5% total exposure. One entry per event. Recheck Kalshi ask/depth immediately before hypothetical fill; skip spreads over 5 cents. Hold to official settlement. Stop new entries after 30 days; settle remaining positions.', '',
        'This exploratory paper strategy uses one sportsbook benchmark with unknown original quote age. It assumes fills at displayed prices without latency or execution failures. Fees use live series multiplier with the standard quadratic formula. No execution-quality claim is made. Changes to code/strategy during the trial invalidate a clean fixed-policy interpretation.', '',
        'At least 100 settled events and a positive lower 95% event-bootstrap ROI bound are required for the positive-evidence label. The interval is conditional on this sample; shared-day and book errors, selection bias, fill assumptions and future regime changes remain. No trades or too few trades means inconclusive. Equity values open positions at cost, not current market value.', '',
        f"Policy hash: `{state['policy_hash']}`"]
    return '\n'.join(lines)+'\n'


def run(state_dir='cloud-state'):
    path=Path(state_dir);path.mkdir(parents=True,exist_ok=True)
    file=path/'state.json';now=utcnow()
    if file.exists():
        state=json.loads(file.read_text())
        if state['policy_hash']!=POLICY_HASH or state['policy']!=POLICY:
            raise RuntimeError('Frozen policy changed; do not silently restart the experiment')
    else:
        state=initialize(now)
    state['errors']=[]
    settle(state,now)
    if now<stamp(state['entries_end_at']):
        try:
            k=scan();events,errors=espn()
            state['errors'].extend(k['errors']+errors)
            benchmarks=compare(k['markets'],events)
            state['last_opportunities']=benchmarks
            # Any partial-feed error blocks new entries this cycle.
            if not state['errors']:
                enter(state,benchmarks,k['markets'],utcnow())
        except (RuntimeError,ValueError,KeyError,TypeError) as e:
            state['errors'].append(str(e))
    state['scans']+=1;state['last_scan']=utcnow().isoformat()
    state['assessment']=assess(state,utcnow())
    tmp=file.with_suffix('.tmp');tmp.write_text(json.dumps(state,indent=2));tmp.replace(file)
    (path/'README.md').write_text(render(state))
    history=path/'history';history.mkdir(exist_ok=True)
    with (history/f'{now:%Y-%m-%d}.jsonl').open('a') as f:
        f.write(json.dumps(dict(time=state['last_scan'],account=accounting(state),
                               assessment=state['assessment'],errors=state['errors'],
                               benchmarks=state['last_opportunities']))+'\n')
    print(json.dumps(dict(account=accounting(state),assessment=state['assessment'],errors=state['errors']),indent=2))
    return 1 if state['errors'] else 0


if __name__=='__main__':
    raise SystemExit(run())
