# Predicter

A live sports-price research engine with a $1,000 paper bankroll. The cloud experiment is a frozen 30-day forward paper trial, running hourly in GitHub Actions. Python 3.11+ and curl; no pip dependencies. Built and live-tested on September 6, 2026.

**This is a working research prototype, not a proven profitable or real-money trading bot.** It uses market-derived probabilities, not a trained sports model. No endpoint can place real bets. No account credentials are needed for public scans.

## Run

From this project directory:

```sh
python3 -m predicter scan
python3 -m predicter kalshi --benchmark
python3 -m predicter status
python3 -m unittest discover -s tests -v
```

Read `data/latest.md` for sportsbook predictions and `data/kalshi.md` for matched Kalshi comparisons. JSON contains full observations; SQLite stores scan history and paper positions. Fetch errors are explicit, never replaced with invented odds. All dates are UTC unless a source contract specifies another timezone.

ESPN fetches today and tomorrow for MLB, NFL, NBA, WNBA, NHL, college football, EPL, MLS and La Liga. Inactive leagues can return zero events. Public feed fields are undocumented and can change. Source bookmaker name is preserved; current observed prices were DraftKings. ESPN quote timestamps are unknown, so these quotes cannot trigger paper positions.

## Cross-book estimates

Obtain your own key from https://the-odds-api.com/ and set `ODDS_API_KEY` in your local environment. Do not paste secrets in chat or commit them. This app does not read `.env` automatically.

```sh
python3 -m predicter scan --source odds-api --sports upcoming
python3 -m predicter scan --source odds-api --sports baseball_mlb,basketball_wnba --paper
```

`--sports all` discovers every active non-futures sport. It can consume substantial provider quota; it is not the default. `upcoming` is the provider's bounded upcoming slate, not all markets. Only full-game two/three-outcome moneylines are supported. Player props, spreads, totals, parlays and futures are not implemented. US targets are DraftKings, FanDuel, BetMGM, Caesars, BetRivers and Fanatics; this list is for price research, not a claim of state availability or execution API access.

The model excludes the target book from its reference set, removes margin within each other complete market, and averages at least three fresh references with identical outcome sets. It reduces the probability by max(2 percentage points, 1.5 times reference standard deviation). It requires at least 2% buffered EV and rejects started events, unknown or >5-minute timestamps and reference dispersion above 4 percentage points. The buffer is a heuristic, not a confidence interval. Correlated book pricing and systematic model errors remain possible.

## Paper bankroll

Quarter Kelly on buffered probability; max 1% equity per event and 5% open exposure. Initially $10/event and $50 total. One position per event across books. SQLite transactions prevent duplicate positions and serialize competing writers. Available cash excludes outstanding stakes. Stakes use cents; wins, losses, pushes and voids are supported.

```sh
python3 -m predicter bets
python3 -m predicter settle 1 win
```

Settlement is manual and should be recorded only after checking the official result and venue rules. Cannot settle before scheduled start or settle twice. `status` reports equity, realized profit, ROI, drawdown and Brier score of settled win/loss predictions. No historical performance is fabricated. Actual fills, slippage, sportsbook taxes and limits are not simulated.

## Kalshi

```sh
python3 -m predicter kalshi --benchmark
python3 -m predicter kalshi --series KXMLBGAME
```

The public adapter paginates up to 5,000 markets per series and reports truncation. Any valid series ticker can be scanned. MLB benchmark matching verifies both participants, selection, and the exact scheduled date/time parsed from contract rules; ambiguous matches fail closed. MLB aliases are intentionally limited. These are **single-book, before-fee indicative comparisons**, never trading signals. Kalshi market `updated_time` is not treated as a quote timestamp. Prices are public snapshots; a real execution system would need a fresh order book.

The optional `--forecasts file.json` interface evaluates independently supplied YES probabilities for exact contracts. Format:

```json
{
  "EXACT-CONTRACT-TICKER": {
    "probability_yes": 0.6,
    "buffer": 0.03,
    "generated_at": "2026-09-06T06:00:00+00:00",
    "valid_until": "2026-09-06T06:05:00+00:00",
    "rules_verified": true,
    "rules_primary": "Exact current contract rules string"
  }
}
```

This example is illustrative and expired, not a real forecast. The evaluator requires matching rules, a fresh unexpired forecast, a supported series fee type, and displayed YES ask size. It models standard quadratic taker fees using the live series multiplier and rounds up to cents. Special fee schedules, waivers, fee changes, fractional fills and nonstandard settlement are not modelled. Candidates remain research output and are not booked or sent as orders. The input forecast's calibration is the supplier's responsibility; passing validation does not establish statistical quality. Kalshi is not used to predict its own probability.

## What remains before passive real-money execution

1. A validated independent forecasting source, or timestamped multi-book odds key, plus reliable contract-rule mapping.
2. Forward performance after fees, out-of-sample calibration, closing-line comparisons and realistic fill simulation. Current evidence does not establish profitability.
3. Account-specific API access, state eligibility and exchange rules; no assumption that a major retail sportsbook permits bot execution.
4. Demo execution, authenticated order reconciliation, idempotent order IDs, partial-fill handling, cancel-on-disconnect and a kill switch before any real account integration.

Kalshi has an official trading API, but it is not connected to an account here. An odds data API is not a sportsbook bet-placement API. The system currently collects and analyzes data; it does not generate passive income.

## Sources

- The Odds API: https://the-odds-api.com/liveapi/guides/v4/
- Kalshi market API: https://docs.kalshi.com/api-reference/market/get-markets
- Kalshi series fees: https://docs.kalshi.com/api-reference/market/get-series
- Kalshi current fee schedule: https://kalshi.com/regulatory/fee-schedule
- Public ESPN endpoint: https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard

## Cloud paper-trading experiment

**Watch the live report:** https://github.com/xmevans10/repoooo/tree/predicter-data

**Run status / manual trigger:** https://github.com/xmevans10/repoooo/actions/workflows/paper-trading.yml

GitHub Actions runs on GitHub-hosted Linux, hourly at minute 17 UTC. Your computer can be off. Schedules can be delayed; this is not a low-latency execution service. The first successful initialization starts the 30-day entry window. After it ends, no new paper positions are opened; remaining positions are monitored until settlement. Runs continue to publish the final assessment. You can disable the workflow in GitHub Actions.

State, a readable report, position details and daily observation logs persist on the `predicter-data` branch. Each update is a Git commit, so earlier results remain auditable. This repository is public: only public market data and hypothetical positions belong here. No account balances or secrets are used. Actions has write access only to repository contents for report persistence; runs are serialized. Failure reports are saved before the run is marked failed.

Run the same experiment locally with `python3 -m predicter.experiment`; it uses a separate `cloud-state` directory. The local CLI ledger and cloud experiment are distinct; the cloud report is authoritative for the 30-day trial. Do not copy a local experiment over cloud state.

### Frozen entry and settlement policy

The trial starts with $1,000 and trades MLB Kalshi YES game-winner contracts using an exactly matched DraftKings margin-free probability benchmark. It subtracts a 5-percentage-point probability buffer, requires at least 2% expected return after modelled taker fees, and applies quarter Kelly with 1% equity/event and 5% total exposure caps. It re-fetches the exact Kalshi contract, checks rules and visible ask depth, rejects bid/ask spreads above 5 cents, enters only 15 minutes–24 hours before game start, and holds to official settlement. One position per event; no doubling down. Unsupported fees, feed errors, ambiguous mappings and unknown settlement values block the affected action.

Paper fills assume the displayed ask was fully available for the requested size. They are not confirmed real fills. ESPN's original quote age is unknown; the fresh retrieval and large buffer do not remove stale-price risk. These assumptions are explicit in every report and position. No actual trade is sent. The earlier CLI consensus model remains separate; its three-reference requirement does not apply to this deliberately exploratory, single-book paper trial.

The experiment reports realized net P&L, ROI after entry fees, event-group bootstrap intervals, Brier score and realized drawdown. Open positions are valued at cost, not marked to market. A positive-evidence result requires at least 100 independent settled events, the 30-day window to finish, all positions settled, and a positive lower 95% event-bootstrap ROI bound. Otherwise the result is inconclusive or profitability not established. This is not proof of future earnings; simulation, market dependence and selection bias limit the inference. Parameters are hashed and checked at every run; changing them cannot silently restart the trial.

Validation: 18 tests pass. The Odds API adapter remains untested against an account key. No paid data feed is called by the cloud workflow.
