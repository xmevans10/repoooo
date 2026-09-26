# Predicter · 30-day paper experiment

**Paper only. No real orders. Positive returns are not guaranteed.**

**Collecting forward evidence**

Entry window: 2026-09-06T07:04:06.724949+00:00 → 2026-10-06T07:04:06.724949+00:00
Last run: 2026-09-26T13:10:48.533164+00:00 · Scans: 116

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
| KXMLBGAME-26SEP261610TEXMIN-MIN | 46.8% | $0.46 | +0.8% |
| KXMLBGAME-26SEP262040AZSD-SD | 52.6% | $0.52 | +0.6% |
| KXMLBGAME-26SEP261910CLEKC-CLE | 54.2% | $0.54 | +0.2% |
| KXMLBGAME-26SEP261915TBPHI-TB | 50.1% | $0.50 | +0.1% |
| KXMLBGAME-26SEP261507CINTOR-CIN | 40.0% | $0.40 | +0.0% |
| KXMLBGAME-26SEP262140LAASEA-LAA | 37.0% | $0.37 | -0.0% |
| KXMLBGAME-26SEP261605LADSF-SF | 25.9% | $0.26 | -0.1% |
| KXMLBGAME-26SEP261910STLMIL-MIL | 62.8% | $0.63 | -0.2% |
| KXMLBGAME-26SEP261610ATLMIA-MIA | 45.8% | $0.46 | -0.2% |
| KXMLBGAME-26SEP261310PITDET-PIT | 49.6% | $0.50 | -0.4% |
| KXMLBGAME-26SEP261310PITDET-DET | 50.4% | $0.51 | -0.6% |
| KXMLBGAME-26SEP262040AZSD-AZ | 47.4% | $0.48 | -0.6% |
| KXMLBGAME-26SEP261610ATLMIA-ATL | 54.2% | $0.55 | -0.8% |
| KXMLBGAME-26SEP261910STLMIL-STL | 37.2% | $0.38 | -0.8% |
| KXMLBGAME-26SEP261605LADSF-LAD | 74.1% | $0.75 | -0.9% |
| KXMLBGAME-26SEP262140LAASEA-SEA | 63.0% | $0.64 | -1.0% |
| KXMLBGAME-26SEP261507CINTOR-TOR | 60.0% | $0.61 | -1.0% |
| KXMLBGAME-26SEP261915TBPHI-PHI | 49.9% | $0.51 | -1.1% |
| KXMLBGAME-26SEP261910CLEKC-KC | 45.8% | $0.47 | -1.2% |
| KXMLBGAME-26SEP261610TEXMIN-TEX | 53.2% | $0.55 | -1.8% |

## Feed health

All requested feeds responded.

## Frozen protocol

MLB YES contracts only. Exact participant/time/rule matching. DraftKings margin-free implied probability minus 5 percentage points; require 2% expected return after taker fees. Enter 15 minutes–24 hours before start. Quarter Kelly, maximum 1% equity per event and 5% total exposure. One entry per event. Recheck Kalshi ask/depth immediately before hypothetical fill; skip spreads over 5 cents. Hold to official settlement. Stop new entries after 30 days; settle remaining positions.

This exploratory paper strategy uses one sportsbook benchmark with unknown original quote age. It assumes fills at displayed prices without latency or execution failures. Fees use live series multiplier with the standard quadratic formula. No execution-quality claim is made. Changes to code/strategy during the trial invalidate a clean fixed-policy interpretation.

At least 100 settled events and a positive lower 95% event-bootstrap ROI bound are required for the positive-evidence label. The interval is conditional on this sample; shared-day and book errors, selection bias, fill assumptions and future regime changes remain. No trades or too few trades means inconclusive. Equity values open positions at cost, not current market value.

Policy hash: `abeb85cef7fc196028c927d8813fa77d4e77d5a7f71b33b38ec876ea07b69e10`
