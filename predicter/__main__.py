import argparse
import json
from pathlib import Path
from . import feeds
from .engine import analyze, utcnow
from .ledger import Ledger

US_BOOKS = {'draftkings', 'fanduel', 'betmgm', 'williamhill_us', 'caesars', 'betrivers', 'fanatics'}


def write_report(report):
    s = report['bankroll']
    lines = ['# Predicter — live price research', '',
             f"Retrieved: {report['created']} · Source: {report['source']}", '',
             f"Paper equity **${s['equity']:,.2f}** · Available ${s['available']:,.2f} · Exposure ${s['exposure']:,.2f}",
             f"Realized P&L ${s['profit']:,.2f} · Settled bets {s['settled']}", '',
             '**Research model; profitability unproven. No real bets are placed.**', '',
             f"Events fetched: {report['events']} · Upcoming priced outcomes: {len(report['predictions'])} · Paper candidates: {sum(r['stake']>0 for r in report['predictions'])}", '',
             'Probabilities are market-derived estimates. With insufficient references, they are only the target book’s margin-free implied probabilities.', '',
             '| Event / selection | Book | Decimal odds | Estimate | Buffered EV | Paper stake | Decision |',
             '|---|---|---:|---:|---:|---:|---|']
    for r in report['predictions']:
        clean = lambda v: str(v).replace('|', '/').replace('\n', ' ')
        lines.append(f"| {clean(r['event'])} / {clean(r['outcome'])} | {clean(r['book'])} | {r['decimal_odds']:.3f} | {r['probability']:.1%} | {r['buffered_ev']:+.1%} | ${r['stake']:.2f} | {r['reason']} |")
    lines += ['', '## Feed status', ''] + (report['errors'] or ['All requested feeds responded.'])
    lines += ['', '## Method', '', 'Target book excluded from the reference consensus; at least three other fresh books required. Each complete moneyline is normalized to remove its margin. Mean reference probability is reduced by max(2 percentage points, 1.5 × cross-book standard deviation). This buffer is a heuristic, not a statistical confidence interval. Require buffered EV ≥ 2%; quarter Kelly, maximum 1% equity per event and 5% total open paper exposure. Unknown timestamps, started games and inconsistent markets are rejected.', '', 'Individual listed stakes are proposals. The paper ledger enforces portfolio limits and one position per event when recording.', '', 'ESPN odds are public display data with unknown quote age. The Odds API requires ODDS_API_KEY for timestamped cross-book research. US book filtering does not establish state eligibility or API execution permission.']
    Path('data').mkdir(exist_ok=True)
    Path('data/latest.json').write_text(json.dumps(report, indent=2))
    Path('data/latest.md').write_text('\n'.join(lines)+'\n')


def main():
    parser = argparse.ArgumentParser(description='Predicter: live odds research and $1,000 paper bankroll')
    parser.add_argument('--db', default='data/paper.sqlite')
    commands = parser.add_subparsers(dest='command', required=True)
    scan = commands.add_parser('scan')
    scan.add_argument('--source', choices=['espn', 'odds-api'], default='espn')
    scan.add_argument('--sports', default='upcoming', help='Odds API keys, comma-separated; all scans every active non-futures sport and consumes more quota')
    scan.add_argument('--regions', default='us', help='Odds API regions; additional regions consume quota')
    scan.add_argument('--paper', action='store_true', help='Record eligible hypothetical bets; never sends real bets')
    kalshi = commands.add_parser('kalshi')
    kalshi.add_argument('--series', default='KXMLBGAME')
    kalshi.add_argument('--benchmark', action='store_true', help='Compare MLB contracts to public DraftKings implied probabilities; watch only')
    kalshi.add_argument('--forecasts', help='JSON file of independent, rule-verified forecasts')
    commands.add_parser('status')
    commands.add_parser('bets')
    settle = commands.add_parser('settle')
    settle.add_argument('id', type=int)
    settle.add_argument('result', choices=['win', 'loss', 'push', 'void'])
    args = parser.parse_args()
    ledger = Ledger(args.db)
    try:
        if args.command == 'kalshi':
            from .kalshi import scan as kalshi_scan
            forecasts = json.loads(Path(args.forecasts).read_text()) if args.forecasts else {}
            report = kalshi_scan(args.series, forecasts, ledger.summary()['equity'])
            if args.benchmark:
                from .benchmark import compare
                events, errors = feeds.espn()
                report['errors'].extend(errors)
                report['benchmarks'] = compare(report['markets'], events)
            Path('data').mkdir(exist_ok=True)
            lines = ['# Kalshi research watchlist', '', 'Live public market data. No real orders. Benchmark gaps exclude fees and are not validated edges.', '', '| Contract | DK implied probability | Kalshi YES ask | Raw gap |', '|---|---:|---:|---:|']
            for r in report.get('benchmarks', []):
                lines.append(f"| {r['ticker']} | {r['probability']:.1%} | ${r['yes_ask']:.2f} | {r['raw_gap']:+.1%} |")
            lines += ['', f"Markets: {len(report['markets'])}; exact matched benchmarks: {len(report.get('benchmarks', []))}.", '', 'Unknown source quote age and a single reference book prevent trade recommendations. Full contract rules and data are in kalshi.json.']
            Path('data/kalshi.md').write_text('\n'.join(lines)+'\n')
            Path('data/kalshi.json').write_text(json.dumps(report, indent=2))
            ledger.record_scan(report)
            print(json.dumps(dict(markets=len(report['markets']), candidates=sum(r['contracts']>0 for r in report['markets']), errors=report['errors']), indent=2))
        elif args.command == 'scan':
            events, errors = feeds.espn() if args.source == 'espn' else feeds.odds_api(args.sports, args.regions)
            rows = analyze(events, ledger.summary()['equity'], allowed=US_BOOKS)
            accepted = ledger.paper(rows) if args.paper else []
            report = dict(created=utcnow().isoformat(), source=args.source, events=len(events),
                          predictions=rows, errors=errors, bankroll=ledger.summary(), paper_recorded=len(accepted))
            ledger.record_scan(report)
            write_report(report)
            print(json.dumps({k:v for k,v in report.items() if k != 'predictions'}, indent=2))
            print(f"{sum(r['stake']>0 for r in rows)} candidates; {len(accepted)} paper positions recorded. Report: data/latest.md")
        elif args.command == 'settle':
            ledger.settle(args.id, args.result)
            print(json.dumps(ledger.summary(), indent=2))
        else:
            print(json.dumps(ledger.bets() if args.command == 'bets' else ledger.summary(), indent=2))
    except (RuntimeError, ValueError) as e:
        parser.exit(1, str(e)+'\n')


if __name__ == '__main__':
    main()
