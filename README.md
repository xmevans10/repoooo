# Predicter · 30-day paper experiment

**Paper only. No real orders. Positive returns are not guaranteed.**

**Collecting forward evidence**

Entry window: 2026-09-06T07:04:06.724949+00:00 → 2026-10-06T07:04:06.724949+00:00
Last run: 2026-09-23T17:10:25.397662+00:00 · Scans: 101

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
| KXMLBGAME-26SEP231835TORBAL-TOR | 47.5% | $0.47 | +0.5% |
| KXMLBGAME-26SEP231545MINSF-MIN | 59.1% | $0.59 | +0.1% |
| KXMLBGAME-26SEP232005NYMTEX-TEX | 50.1% | $0.50 | +0.1% |
| KXMLBGAME-26SEP231905TBNYY-NYY | 55.1% | $0.55 | +0.1% |
| KXMLBGAME-26SEP231915CINATL-CIN | 30.1% | $0.30 | +0.1% |
| KXMLBGAME-26SEP232040AZCOL-COL | 40.9% | $0.41 | -0.1% |
| KXMLBGAME-26SEP232210SDLAD-SD | 33.8% | $0.34 | -0.2% |
| KXMLBGAME-26SEP231840STLPIT-STL | 43.8% | $0.44 | -0.2% |
| KXMLBGAME-26SEP231310WSHDET-DET | 60.8% | $0.61 | -0.2% |
| KXMLBGAME-26SEP231940MIACHC-CHC | 61.6% | $0.62 | -0.4% |
| KXMLBGAME-26SEP231940MIACHC-MIA | 38.4% | $0.39 | -0.6% |
| KXMLBGAME-26SEP231310WSHDET-WSH | 39.2% | $0.40 | -0.8% |
| KXMLBGAME-26SEP231840STLPIT-PIT | 56.2% | $0.57 | -0.8% |
| KXMLBGAME-26SEP232210SDLAD-LAD | 66.2% | $0.67 | -0.8% |
| KXMLBGAME-26SEP231840MILPHI-PHI | 46.2% | $0.47 | -0.8% |
| KXMLBGAME-26SEP232040AZCOL-AZ | 59.1% | $0.60 | -0.9% |
| KXMLBGAME-26SEP231915CINATL-ATL | 69.9% | $0.71 | -1.1% |
| KXMLBGAME-26SEP231905TBNYY-TB | 44.9% | $0.46 | -1.1% |
| KXMLBGAME-26SEP232005NYMTEX-NYM | 49.9% | $0.51 | -1.1% |
| KXMLBGAME-26SEP231545MINSF-SF | 40.9% | $0.42 | -1.1% |
| KXMLBGAME-26SEP231840MILPHI-MIL | 53.8% | $0.55 | -1.2% |
| KXMLBGAME-26SEP231835TORBAL-BAL | 52.5% | $0.54 | -1.5% |

## Feed health

All requested feeds responded.

## Frozen protocol

MLB YES contracts only. Exact participant/time/rule matching. DraftKings margin-free implied probability minus 5 percentage points; require 2% expected return after taker fees. Enter 15 minutes–24 hours before start. Quarter Kelly, maximum 1% equity per event and 5% total exposure. One entry per event. Recheck Kalshi ask/depth immediately before hypothetical fill; skip spreads over 5 cents. Hold to official settlement. Stop new entries after 30 days; settle remaining positions.

This exploratory paper strategy uses one sportsbook benchmark with unknown original quote age. It assumes fills at displayed prices without latency or execution failures. Fees use live series multiplier with the standard quadratic formula. No execution-quality claim is made. Changes to code/strategy during the trial invalidate a clean fixed-policy interpretation.

At least 100 settled events and a positive lower 95% event-bootstrap ROI bound are required for the positive-evidence label. The interval is conditional on this sample; shared-day and book errors, selection bias, fill assumptions and future regime changes remain. No trades or too few trades means inconclusive. Equity values open positions at cost, not current market value.

Policy hash: `abeb85cef7fc196028c927d8813fa77d4e77d5a7f71b33b38ec876ea07b69e10`
