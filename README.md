# Predicter · 30-day paper experiment

**Paper only. No real orders. Positive returns are not guaranteed.**

**Collecting forward evidence**

Entry window: 2026-09-06T07:04:06.724949+00:00 → 2026-10-06T07:04:06.724949+00:00
Last run: 2026-09-24T19:15:24.295527+00:00 · Scans: 107

| Starting bankroll | Equity | Available cash | Open exposure | Realized P&L |
|---:|---:|---:|---:|---:|
| $1,000.00 | $1,000.00 | $1,000.00 | $0.00 | $0.00 |

Settled independent events: **0** · Open positions: **0** · Net ROI: **—**
95% event-bootstrap ROI interval: — to —
Realized drawdown: 0.00% · Brier score: —

## Positions

| Entered (UTC) | Contract | YES count | Price | Cost incl. fee | Status | P&L |
|---|---|---:|---:|---:|---|---:|
| — | No qualifying paper entries | — | — | — | — | — |

## Latest matched prices

Indicative differences below are **before fees and uncertainty buffer**, not entry signals.

| Contract | DK implied probability | Kalshi ask | Raw difference |
|---|---:|---:|---:|
| KXMLBGAME-26SEP241915CINATL-CIN | 33.2% | $0.32 | +1.2% |
| KXMLBGAME-26SEP241845CLEBOS-BOS | 54.2% | $0.54 | +0.2% |
| KXMLBGAME-26SEP242210SDLAD-SD | 39.2% | $0.39 | +0.2% |
| KXMLBGAME-26SEP241805MILPHI-MIL | 44.9% | $0.45 | -0.1% |
| KXMLBGAME-26SEP241905TBNYY-TB | 41.7% | $0.42 | -0.3% |
| KXMLBGAME-26SEP242140LAASEA-SEA | 66.7% | $0.67 | -0.3% |
| KXMLBGAME-26SEP242140LAASEA-LAA | 33.3% | $0.34 | -0.7% |
| KXMLBGAME-26SEP241905TBNYY-NYY | 58.3% | $0.59 | -0.7% |
| KXMLBGAME-26SEP241805MILPHI-PHI | 55.1% | $0.56 | -0.9% |
| KXMLBGAME-26SEP242210SDLAD-LAD | 60.8% | $0.62 | -1.2% |
| KXMLBGAME-26SEP241845CLEBOS-CLE | 45.8% | $0.47 | -1.2% |
| KXMLBGAME-26SEP241915CINATL-ATL | 66.8% | $0.69 | -2.2% |

## Feed health

All requested feeds responded.

## Frozen protocol

MLB YES contracts only. Exact participant/time/rule matching. DraftKings margin-free implied probability minus 5 percentage points; require 2% expected return after taker fees. Enter 15 minutes–24 hours before start. Quarter Kelly, maximum 1% equity per event and 5% total exposure. One entry per event. Recheck Kalshi ask/depth immediately before hypothetical fill; skip spreads over 5 cents. Hold to official settlement. Stop new entries after 30 days; settle remaining positions.

This exploratory paper strategy uses one sportsbook benchmark with unknown original quote age. It assumes fills at displayed prices without latency or execution failures. Fees use live series multiplier with the standard quadratic formula. No execution-quality claim is made. Changes to code/strategy during the trial invalidate a clean fixed-policy interpretation.

At least 100 settled events and a positive lower 95% event-bootstrap ROI bound are required for the positive-evidence label. The interval is conditional on this sample; shared-day and book errors, selection bias, fill assumptions and future regime changes remain. No trades or too few trades means inconclusive. Equity values open positions at cost, not current market value.

Policy hash: `abeb85cef7fc196028c927d8813fa77d4e77d5a7f71b33b38ec876ea07b69e10`
