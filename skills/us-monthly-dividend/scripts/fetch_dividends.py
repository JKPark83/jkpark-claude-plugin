#!/usr/bin/env python3
"""Fetch dividend history, yield, and payout months for US tickers via yfinance.

Usage:
    python3 fetch_dividends.py SCHD JEPI O [--recent N] [--market]

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
      "calendar_adjustment": null,   # or a note; see below
      "recent": [{"date": "2026-06-25", "amount": 0.27}, ...],  # newest last
      "error": null                  # or a message; other fields null then
    }, ...
  }
}

Yahoo dates are ex-dates, not pay dates. Many monthly ETFs (iShares, Global X,
SPDR) pull January's distribution to a late-December ex-date, which leaves
by_month_ttm January empty and December doubled — the fund does pay in January.
When exactly one month is empty and the month before it holds two payments, the
later one is moved forward and "calendar_adjustment" describes the move. Gaps
that do not fit that pattern are left alone and only noted.

With --market, adds a "market" block (values null when unavailable):
{
  "vix": 15.2, "vix_3m_ago": 18.4,          # CBOE VIX close, now and ~3 months back
  "us10y_pct": 4.25, "us10y_3m_ago_pct": 4.6 # US 10Y treasury yield (%, ^TNX)
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


def normalize_ex_date_calendar(by_month, ttm):
    """Shift a distribution whose ex-date landed in the prior month back onto the
    month it is actually paid in. Returns a note, or None when nothing was moved.

    Only the unambiguous case is corrected: an otherwise-monthly payer with
    exactly one empty month whose preceding month holds two payments. A December
    ex-date for January's distribution is the common instance."""
    empty = [m for m in range(1, 13) if by_month[str(m)] == 0.0]
    if len(empty) != 1:
        return None  # 0 gaps = nothing to fix; 2+ = a genuine non-monthly payer
    gap = empty[0]
    prior = 12 if gap == 1 else gap - 1
    in_prior = sorted((ts, float(a)) for ts, a in ttm.items() if ts.month == prior)
    if len(in_prior) < 2:
        return (
            f"{gap}월 미지급이나 {prior}월 중복 지급이 아님 — "
            "TTM 창 경계 효과일 수 있으니 실제 지급 이력을 확인할 것"
        )
    moved_ts, amount = in_prior[-1]
    amount = round(amount, 6)
    by_month[str(prior)] = round(by_month[str(prior)] - amount, 6)
    by_month[str(gap)] = round(by_month[str(gap)] + amount, 6)
    return (
        f"{moved_ts.strftime('%Y-%m-%d')} 지급 {amount}를 "
        f"{prior}월에서 {gap}월로 이동 (배당락일이 전월 말로 당겨진 케이스)"
    )


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

    adjustment = normalize_ex_date_calendar(by_month, ttm)

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
        "pay_months": sorted(m for m in range(1, 13) if by_month[str(m)] != 0.0),
        "by_month_ttm": by_month,
        "calendar_adjustment": adjustment,
        "recent": recent,
        "error": None,
    }


def fetch_market():
    # Yahoo quotes ^TNX directly in percent (e.g. 4.25), unlike CBOE's 10x convention
    out = {"vix": None, "vix_3m_ago": None, "us10y_pct": None, "us10y_3m_ago_pct": None}
    for symbol, key, scale in (("^VIX", "vix", 1.0), ("^TNX", "us10y_pct", 1.0)):
        try:
            hist = yf.Ticker(symbol).history(period="6mo")
            if hist is None or hist.empty:
                continue
            closes = hist["Close"]
            out[key] = round(float(closes.iloc[-1]) * scale, 2)
            past_idx = max(0, len(closes) - 63)  # ~3 months of trading days
            past_key = "vix_3m_ago" if key == "vix" else "us10y_3m_ago_pct"
            out[past_key] = round(float(closes.iloc[past_idx]) * scale, 2)
        except Exception:
            pass  # market block is optional context; nulls are allowed
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("tickers", nargs="+", help="US ticker symbols, e.g. SCHD JEPI O")
    parser.add_argument("--recent", type=int, default=8, help="recent payments to include")
    parser.add_argument("--market", action="store_true", help="include VIX / US 10Y market block")
    args = parser.parse_args()

    result = {"as_of": datetime.now().strftime("%Y-%m-%d"), "usdkrw": None, "tickers": {}}
    if args.market:
        result["market"] = fetch_market()

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
