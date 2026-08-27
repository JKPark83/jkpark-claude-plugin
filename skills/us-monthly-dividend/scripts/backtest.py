#!/usr/bin/env python3
"""Deterministic monthly-rebalance portfolio backtest vs benchmarks.

Usage:
    python3 backtest.py --weights MAIN:0.392 O:0.389 JEPQ:0.138 SCHD:0.081 \
        --years 5 --benchmarks SPY SCHD [--tax 0.15]

Method (fixed, no options beyond the tax rate):
- Data: yfinance history with auto_adjust=False — split-adjusted Close plus
  the as-paid (split-adjusted) Dividends series, so dividends can be taxed
  and withdrawn separately from price moves.
- Two realistic scenarios per series (a pre-tax reinvest track is not
  achievable for a Korean resident, so it is not reported):
      net_reinvest: (P_t + (1-tax) * D_t) / P_{t-1} - 1
          after-tax dividends reinvested monthly (compounding track)
      withdraw:      P_t / P_{t-1} - 1
          after-tax dividends withdrawn as cash every month; the position
          compounds on price only. Reported alongside the withdrawn cash:
          monthly cash yield c_t = (1-tax) * D_t / P_{t-1}, its annualized
          average, and the total cash collected as % of the initial value
          (each month's cash scaled by the price-only curve).
  Default tax = 0.15 (US treaty withholding for a Korean resident).
  Benchmarks get the same treatment so the comparison stays fair.
- Common history: months where every portfolio ticker has data; the actual
  start date is reported so a young ticker shortening the window is visible.
- Portfolio: rebalanced back to target weights every month
  (monthly return = sum(w_i * r_i)).
- Metrics per return series: total_return, cagr, annual_vol (monthly std *
  sqrt(12)), sharpe (rf=0, stated in output), mdd (on the monthly compounded
  curve), best/worst calendar year, monthly win rate.

Output: single JSON object on stdout. Report numbers must come from here.
Exit 1 with a stderr message if data cannot be fetched.
"""

import argparse
import json
import math
import sys

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
    # partial first/last years are included as-is
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


def cash_stats(price_ret: pd.Series, cash_yield: pd.Series) -> dict:
    """Stats for the withdrawn after-tax dividend cash of the withdraw track."""
    df = pd.concat({"r": price_ret, "c": cash_yield}, axis=1).dropna()
    if df.empty:
        return {"error": "no overlapping months"}
    # value factor at the START of each month on the price-only curve (V_0 = 1)
    prev_curve = (1 + df["r"]).cumprod().shift(1).fillna(1.0)
    total_cash = float((df["c"] * prev_curve).sum())
    return {
        "avg_annual_cash_yield": round(float(df["c"].mean() * 12), 4),
        "total_cash_pct_of_initial": round(total_cash, 4),
        "months": int(len(df)),
    }


def monthly_series(ticker: str, years: int, tax: float):
    """dict of monthly Series {reinvest, price, cash} + first data date, or None."""
    try:
        h = yf.Ticker(ticker).history(period=f"{years}y", auto_adjust=False)
    except Exception:
        return None
    if h is None or h.empty or h["Close"].dropna().empty:
        return None
    px = h["Close"].resample("ME").last()
    div = h["Dividends"].fillna(0).resample("ME").sum()
    prev = px.shift(1)
    out = {
        "reinvest": ((px + (1 - tax) * div) / prev - 1).dropna(),
        "price": (px / prev - 1).dropna(),
        "cash": ((1 - tax) * div / prev).dropna(),
    }
    for k in out:
        out[k].index = out[k].index.tz_localize(None)
    first = h["Close"].dropna().index[0]
    return out, pd.Timestamp(first).tz_localize(None)


def track_report(reinvest: pd.Series, price: pd.Series, cash: pd.Series) -> dict:
    return {
        "net_reinvest": metrics(reinvest),
        "withdraw": {
            "price_only": metrics(price),
            "dividend_cash": cash_stats(price, cash),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", nargs="+", required=True,
                    metavar="TICKER:WEIGHT",
                    help="e.g. MAIN:0.392 O:0.389 JEPQ:0.138 SCHD:0.081")
    ap.add_argument("--years", type=int, default=5)
    ap.add_argument("--benchmarks", nargs="*", default=["SPY", "SCHD"])
    ap.add_argument("--tax", type=float, default=0.15,
                    help="withholding applied to all dividends")
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

    series, missing = {}, []
    for t in sorted(set(weights) | set(benchmarks)):
        r = monthly_series(t, args.years, args.tax)
        if r is None:
            missing.append(t)
        else:
            series[t] = r
    bad = [t for t in missing if t in weights]
    if bad:
        sys.exit(f"no price data for portfolio ticker(s): {bad}")

    # common history across portfolio tickers
    start = max(series[t][1] for t in weights)
    w = pd.Series(weights)

    def port(kind: str) -> pd.Series:
        df = pd.DataFrame({t: series[t][0][kind] for t in weights}).loc[start:].dropna()
        return (df * w).sum(axis=1)

    p_reinvest, p_price, p_cash = port("reinvest"), port("price"), port("cash")

    out = {
        "method": {
            "prices": ("split-adjusted Close + as-paid dividends "
                       "(explicit price/dividend decomposition)"),
            "dividend_tax": args.tax,
            "tracks": {
                "net_reinvest": f"dividends reinvested monthly after {args.tax:.0%} withholding",
                "withdraw": (f"dividends withdrawn as cash monthly after {args.tax:.0%} "
                             "withholding; position compounds on price only"),
            },
            "rebalance": "monthly, back to target weights",
            "risk_free_rate": 0.0,
            "requested_years": args.years,
        },
        "weights": {t: round(v, 4) for t, v in weights.items()},
        "period": {
            "start": str(start.date()),
            "end": str(p_reinvest.index[-1].date()),
            "note": ("start is the first date ALL portfolio tickers have data; "
                     "a young ticker shortens the window"),
        },
        "portfolio": track_report(p_reinvest, p_price, p_cash),
        "benchmarks": {},
        "skipped_benchmarks": [b for b in benchmarks if b in missing],
    }
    for b in benchmarks:
        if b in missing:
            continue
        # align to the portfolio's monthly index so windows match exactly
        s = series[b][0]
        out["benchmarks"][b] = track_report(
            s["reinvest"].reindex(p_reinvest.index),
            s["price"].reindex(p_reinvest.index),
            s["cash"].reindex(p_reinvest.index),
        )

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
