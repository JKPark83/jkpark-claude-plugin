#!/usr/bin/env python3
"""Fetch Bithumb OHLCV candles (public API 2.0) into a CSV.

Usage:
  python3 fetch_candles.py --market KRW-BTC --interval days --count 730 --out candles.csv
  python3 fetch_candles.py --market KRW-ETH --interval minutes:60 --count 2000 --out eth_60m.csv

Output CSV columns: timestamp,open,high,low,close,volume — ascending by time (KST).
Exit codes: 0 ok / 1 usage error / 2 network or API error / 3 unexpected response shape.
"""
import argparse
import csv
import sys
import time

import requests

BASE = "https://api.bithumb.com"
MINUTE_UNITS = {1, 3, 5, 10, 15, 30, 60, 240}
PAGE = 200  # documented max count per request


def die(code, msg):
    print(f"fetch_candles.py error: {msg}", file=sys.stderr)
    sys.exit(code)


def endpoint_for(interval):
    if interval == "days":
        return f"{BASE}/v1/candles/days"
    if interval.startswith("minutes:"):
        unit = interval.split(":", 1)[1]
        if not unit.isdigit() or int(unit) not in MINUTE_UNITS:
            die(1, f"invalid minute unit '{unit}' (allowed: {sorted(MINUTE_UNITS)})")
        return f"{BASE}/v1/candles/minutes/{unit}"
    die(1, f"invalid --interval '{interval}' (use 'days' or 'minutes:<unit>')")


def fetch_page(url, market, count, to):
    params = {"market": market, "count": count}
    if to:
        params["to"] = to
    try:
        r = requests.get(url, params=params, timeout=15)
    except requests.RequestException as e:
        die(2, f"network error: {e}")
    if r.status_code != 200:
        die(2, f"HTTP {r.status_code}: {r.text[:300]}")
    data = r.json()
    if not isinstance(data, list):
        die(3, f"expected a list, got: {str(data)[:300]}")
    return data


def row_of(c):
    try:
        return {
            "timestamp": c["candle_date_time_kst"],
            "open": c["opening_price"],
            "high": c["high_price"],
            "low": c["low_price"],
            "close": c["trade_price"],
            "volume": c["candle_acc_trade_volume"],
        }
    except KeyError as e:
        die(3, f"missing field {e} in candle; got keys: {sorted(c.keys())}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", required=True, help="e.g. KRW-BTC")
    ap.add_argument("--interval", required=True, help="'days' or 'minutes:<1|3|5|10|15|30|60|240>'")
    ap.add_argument("--count", type=int, required=True, help="total candles to fetch")
    ap.add_argument("--out", required=True, help="output CSV path")
    args = ap.parse_args()

    if args.count < 1:
        die(1, "--count must be >= 1")
    url = endpoint_for(args.interval)

    rows = {}
    to = None
    remaining = args.count
    while remaining > 0:
        batch = fetch_page(url, args.market, min(PAGE, remaining), to)
        if not batch:
            break  # no older data available
        for c in batch:
            r = row_of(c)
            rows[r["timestamp"]] = r
        oldest = min(c["candle_date_time_kst"] for c in batch)
        if to is not None and oldest >= to:
            break  # no progress; stop instead of looping forever
        to = oldest
        remaining = args.count - len(rows)
        time.sleep(0.12)  # stay far under the public rate limit

    if not rows:
        die(2, f"no candles returned for {args.market} {args.interval}")

    ordered = [rows[k] for k in sorted(rows.keys())]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        w.writeheader()
        w.writerows(ordered)
    print(f"wrote {len(ordered)} candles to {args.out} "
          f"({ordered[0]['timestamp']} ~ {ordered[-1]['timestamp']})")


if __name__ == "__main__":
    main()
