#!/usr/bin/env python3
"""Fetch the crypto Fear & Greed index history (alternative.me) into a CSV.

Usage:
  python3 fetch_fng.py --out fng.csv            # full history (2018-02 ~ today)
  python3 fetch_fng.py --out fng.csv --limit 60 # last 60 days

Output CSV columns: date,value  (date = YYYY-MM-DD UTC, value = 0-100 int,
ascending). 0 = extreme fear, 100 = extreme greed.
Exit codes: 0 ok / 2 network or API error / 3 unexpected response shape.
"""
import argparse
import csv
import sys
from datetime import datetime, timezone

import requests

URL = "https://api.alternative.me/fng/"


def die(code, msg):
    print(f"fetch_fng.py error: {msg}", file=sys.stderr)
    sys.exit(code)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0, help="0 = full history")
    args = ap.parse_args()

    try:
        r = requests.get(URL, params={"limit": args.limit, "format": "json"}, timeout=15)
    except requests.RequestException as e:
        die(2, f"network error: {e}")
    if r.status_code != 200:
        die(2, f"HTTP {r.status_code}: {r.text[:300]}")
    try:
        data = r.json()["data"]
        rows = sorted(
            {datetime.fromtimestamp(int(d["timestamp"]), tz=timezone.utc).strftime("%Y-%m-%d"):
             int(d["value"]) for d in data}.items()
        )
    except (KeyError, TypeError, ValueError) as e:
        die(3, f"unexpected response shape ({e}): {r.text[:300]}")
    if not rows:
        die(3, "empty data")

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "value"])
        w.writerows(rows)
    print(f"wrote {len(rows)} days to {args.out} ({rows[0][0]} ~ {rows[-1][0]})")


if __name__ == "__main__":
    main()
