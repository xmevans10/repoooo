# Predicter · 30-day paper experiment

**Paper only. No real orders. Positive returns are not guaranteed.**

**Collecting forward evidence**

Entry window: 2026-09-06T07:04:06.724949+00:00 → 2026-10-06T07:04:06.724949+00:00
Last run: 2026-09-07T10:26:14.122480+00:00 · Scans: 8

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
| KXMLBGAME-26SEP071335CLEBAL-BAL | 54.2% | $0.54 | +0.2% |
| KXMLBGAME-26SEP071410AZKC-KC | 51.1% | $0.51 | +0.1% |
| KXMLBGAME-26SEP071335LAABOS-BOS | 62.1% | $0.62 | +0.1% |
| KXMLBGAME-26SEP071710WSHSD-WSH | 35.9% | $0.36 | -0.1% |
| KXMLBGAME-26SEP071510MINDET-MIN | 46.8% | $0.47 | -0.2% |
| KXMLBGAME-26SEP071410CHCMIL-CHC | 46.8% | $0.47 | -0.2% |
| KXMLBGAME-26SEP072010STLSF-STL | 45.8% | $0.46 | -0.2% |
| KXMLBGAME-26SEP072110CINLAD-CIN | 41.7% | $0.42 | -0.3% |
| KXMLBGAME-26SEP071310NYMMIA-NYM | 47.7% | $0.48 | -0.3% |
| KXMLBGAME-26SEP071310NYMMIA-MIA | 52.3% | $0.53 | -0.7% |
| KXMLBGAME-26SEP072110CINLAD-LAD | 58.3% | $0.59 | -0.7% |
| KXMLBGAME-26SEP072010STLSF-SF | 54.2% | $0.55 | -0.8% |
| KXMLBGAME-26SEP071510MINDET-DET | 53.2% | $0.54 | -0.8% |
| KXMLBGAME-26SEP071410CHCMIL-MIL | 53.2% | $0.54 | -0.8% |
| KXMLBGAME-26SEP071710WSHSD-SD | 64.1% | $0.65 | -0.9% |
| KXMLBGAME-26SEP071305ATLPHI-ATL | 40.0% | $0.41 | -1.0% |
| KXMLBGAME-26SEP071305ATLPHI-PHI | 60.0% | $0.61 | -1.0% |
| KXMLBGAME-26SEP071335LAABOS-LAA | 37.9% | $0.39 | -1.1% |
| KXMLBGAME-26SEP071410AZKC-AZ | 48.9% | $0.50 | -1.1% |
| KXMLBGAME-26SEP071335CLEBAL-CLE | 45.8% | $0.47 | -1.2% |

## Feed health

All requested feeds responded.

## Frozen protocol

MLB YES contracts only. Exact participant/time/rule matching. DraftKings margin-free implied probability minus 5 percentage points; require 2% expected return after taker fees. Enter 15 minutes–24 hours before start. Quarter Kelly, maximum 1% equity per event and 5% total exposure. One entry per event. Recheck Kalshi ask/depth immediately before hypothetical fill; skip spreads over 5 cents. Hold to official settlement. Stop new entries after 30 days; settle remaining positions.

This exploratory paper strategy uses one sportsbook benchmark with unknown original quote age. It assumes fills at displayed prices without latency or execution failures. Fees use live series multiplier with the standard quadratic formula. No execution-quality claim is made. Changes to code/strategy during the trial invalidate a clean fixed-policy interpretation.

At least 100 settled events and a positive lower 95% event-bootstrap ROI bound are required for the positive-evidence label. The interval is conditional on this sample; shared-day and book errors, selection bias, fill assumptions and future regime changes remain. No trades or too few trades means inconclusive. Equity values open positions at cost, not current market value.

Policy hash: `abeb85cef7fc196028c927d8813fa77d4e77d5a7f71b33b38ec876ea07b69e10`
