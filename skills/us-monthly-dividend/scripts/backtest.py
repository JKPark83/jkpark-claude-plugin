#!/usr/bin/env python3
"""Deterministic monthly-rebalance portfolio backtest vs benchmarks.

Usage:
    python3 backtest.py --weights MAIN:0.392 O:0.389 JEPQ:0.138 SCHD:0.081 \
        --years 5 --benchmarks SPY SCHD

Method (fixed, no options):
- Prices: yfinance download, auto_adjust=True Close (splits + dividends
  reinvested -> total-return series).
- Common history: rows where every portfolio ticker has data (dropna); the
  actual start date is reported so a young ticker shortening the window is
  visible.
- Portfolio: month-end resample, monthly return = sum(w_i * r_i) — i.e. the
  portfolio is rebalanced back to target weights every month.
- Benchmarks: same month-end series, buy-and-hold single ticker.
- Metrics per series: total_return, cagr, annual_vol (monthly std * sqrt(12)),
  sharpe (rf=0, stated in output), mdd (on the monthly compounded curve),
  best/worst calendar year, monthly win rate.

Output: single JSON object on stdout. Report numbers must come from here.
Exit 1 with a stderr message if data cannot be fetched.
"""

import argparse
import json
import math
import sys

import numpy as np
import pandas as pd
import yfinance as yf


def metrics(monthly: pd.Series) -> dict:
    monthly = monthly.dropna()
    n = len(monthly)
    if n < 12:
        return {"error": f"only {n} monthly returns; need >= 12"}
    curve = (1 + monthly).cumprod()
    years = n / 12.0
    total = float(curve.iloc[-1] - 1)
    cagr = float(curve.iloc[-1] ** (1 / years) - 1)
    vol = float(monthly.std(ddof=1) * math.sqrt(12))
    mean_ann = float(monthly.mean() * 12)
    sharpe = mean_ann / vol if vol > 0 else None
    mdd = float((curve / curve.cummax() - 1).min())
    by_year = (1 + monthly).groupby(monthly.index.year).prod() - 1
    # partial first/last years are included as-is; label them
    best_y = by_year.idxmax()
    worst_y = by_year.idxmin()
    return {
        "total_return": round(total, 4),
        "cagr": round(cagr, 4),
        "annual_vol": round(vol, 4),
        "sharpe_rf0": round(sharpe, 2) if sharpe is not None else None,
        "mdd": round(mdd, 4),
        "best_year": {"year": int(best_y), "return": round(float(by_year.loc[best_y]), 4)},
        "worst_year": {"year": int(worst_y), "return": round(float(by_year.loc[worst_y]), 4)},
        "monthly_win_rate": round(float((monthly > 0).mean()), 4),
        "months": n,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", nargs="+", required=True,
                    metavar="TICKER:WEIGHT",
                    help="e.g. MAIN:0.392 O:0.389 JEPQ:0.138 SCHD:0.081")
    ap.add_argument("--years", type=int, default=5)
    ap.add_argument("--benchmarks", nargs="*", default=["SPY", "SCHD"])
    args = ap.parse_args()

    weights = {}
    for pair in args.weights:
        try:
            t, w = pair.split(":")
            weights[t.upper()] = float(w)
        except ValueError:
            sys.exit(f"bad --weights entry {pair!r}; expected TICKER:WEIGHT")
    wsum = sum(weights.values())
    if not 0.5 < wsum < 1.5:
        sys.exit(f"weights sum to {wsum:.3f}; expected ~1.0")
    weights = {t: w / wsum for t, w in weights.items()}  # normalize

    benchmarks = [b.upper() for b in args.benchmarks]
    tickers = sorted(set(weights) | set(benchmarks))

    try:
        raw = yf.download(tickers, period=f"{args.years}y", auto_adjust=True,
                          progress=False)["Close"]
    except Exception as e:  # network / API failure
        sys.exit(f"price download failed: {e}")
    if isinstance(raw, pd.Series):
        raw = raw.to_frame(tickers[0])
    raw = raw.dropna(how="all")
    missing = [t for t in tickers if t not in raw.columns or raw[t].dropna().empty]
    if any(t in missing for t in weights):
        sys.exit(f"no price data for portfolio ticker(s): "
                 f"{[t for t in missing if t in weights]}")

    port_px = raw[list(weights)].dropna()  # common history of portfolio tickers
    monthly_px = port_px.resample("ME").last()
    rets = monthly_px.pct_change().dropna()
    w = pd.Series(weights)
    port_monthly = (rets * w).sum(axis=1)

    out = {
        "method": {
            "prices": "yfinance auto_adjust Close (total return: splits+dividends)",
            "rebalance": "monthly, back to target weights",
            "risk_free_rate": 0.0,
            "requested_years": args.years,
        },
        "weights": {t: round(v, 4) for t, v in weights.items()},
        "period": {
            "start": str(port_px.index[0].date()),
            "end": str(port_px.index[-1].date()),
            "note": ("start is the first date ALL portfolio tickers have data; "
                     "a young ticker shortens the window"),
        },
        "portfolio": metrics(port_monthly),
        "benchmarks": {},
        "skipped_benchmarks": [b for b in benchmarks if b in missing],
    }
    # benchmarks over the SAME window as the portfolio for comparability
    for b in benchmarks:
        if b in missing:
            continue
        b_monthly = (raw[b].loc[port_px.index[0]:].resample("ME").last()
                     .pct_change().dropna())
        out["benchmarks"][b] = metrics(b_monthly)

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
