#!/usr/bin/env python3
"""Fetch dividend history, yield, and payout months for US tickers via yfinance.

Usage:
    python3 fetch_dividends.py SCHD JEPI O [--recent N]

Prints a single JSON object to stdout:
{
  "as_of": "YYYY-MM-DD",
  "usdkrw": 1390.5 | null,
  "tickers": {
    "SCHD": {
      "price": 27.13,
      "ttm_dividend": 1.05,          # sum of dividends, trailing 12 months
      "prev_ttm_dividend": 1.01,     # sum, months 13-24 back (trend check)
      "ttm_yield_pct": 3.87,
      "pay_months": [3, 6, 9, 12],   # months with a payment in trailing 12m
      "by_month_ttm": {"1": 0.0, ... "12": 0.27},
      "recent": [{"date": "2026-06-25", "amount": 0.27}, ...],  # newest last
      "error": null                  # or a message; other fields null then
    }, ...
  }
}

Exit codes: 0 on success (per-ticker failures are reported inline in "error"),
1 only when yfinance is missing or no ticker could be fetched at all.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone

try:
    import yfinance as yf
except ImportError:
    print(
        json.dumps({"fatal": "yfinance is not installed. Run: pip3 install yfinance"}),
        file=sys.stderr,
    )
    sys.exit(1)


def last_close(ticker_obj):
    hist = ticker_obj.history(period="5d")
    if hist is None or hist.empty:
        return None
    return float(hist["Close"].iloc[-1])


def fetch_ticker(symbol, recent_n):
    t = yf.Ticker(symbol)
    price = last_close(t)
    if price is None:
        return {"error": f"no price data for '{symbol}' (bad ticker or network issue)"}

    divs = t.dividends
    if divs is None or divs.empty:
        return {"error": f"'{symbol}' has no dividend history on Yahoo Finance"}

    now = datetime.now(timezone.utc)
    tz = divs.index.tz
    if tz is not None:
        now = now.astimezone(tz)
    ttm_start = now - timedelta(days=365)
    prev_start = now - timedelta(days=730)

    ttm = divs[divs.index >= ttm_start]
    prev = divs[(divs.index >= prev_start) & (divs.index < ttm_start)]

    by_month = {str(m): 0.0 for m in range(1, 13)}
    for ts, amount in ttm.items():
        by_month[str(ts.month)] = round(by_month[str(ts.month)] + float(amount), 6)

    ttm_total = round(float(ttm.sum()), 6)
    recent = [
        {"date": ts.strftime("%Y-%m-%d"), "amount": round(float(a), 6)}
        for ts, a in divs.tail(recent_n).items()
    ]

    return {
        "price": round(price, 4),
        "ttm_dividend": ttm_total,
        "prev_ttm_dividend": round(float(prev.sum()), 6),
        "ttm_yield_pct": round(ttm_total / price * 100, 2) if price else None,
        "pay_months": sorted({ts.month for ts in ttm.index}),
        "by_month_ttm": by_month,
        "recent": recent,
        "error": None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tickers", nargs="+", help="US ticker symbols, e.g. SCHD JEPI O")
    parser.add_argument("--recent", type=int, default=8, help="recent payments to include")
    args = parser.parse_args()

    result = {"as_of": datetime.now().strftime("%Y-%m-%d"), "usdkrw": None, "tickers": {}}

    try:
        fx = last_close(yf.Ticker("USDKRW=X"))
        result["usdkrw"] = round(fx, 2) if fx else None
    except Exception:
        pass  # FX is optional; report proceeds in USD only

    ok = 0
    for symbol in args.tickers:
        symbol = symbol.upper().strip()
        try:
            data = fetch_ticker(symbol, args.recent)
        except Exception as exc:
            data = {"error": f"fetch failed for '{symbol}': {exc}"}
        result["tickers"][symbol] = data
        if not data.get("error"):
            ok += 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    if ok == 0:
        print("all tickers failed — check network or ticker symbols", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
