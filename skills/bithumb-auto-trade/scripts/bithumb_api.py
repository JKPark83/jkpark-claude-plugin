#!/usr/bin/env python3
"""Bithumb REST API 2.0 helper (JWT auth). All output is JSON on stdout.

Private calls read BITHUMB_API_KEY / BITHUMB_SECRET_KEY from the environment.

Subcommands:
  ticker   --markets KRW-BTC,KRW-ETH
  accounts
  chance   --market KRW-BTC                      # fees + min order amount
  order    --market KRW-BTC --side bid|ask --ord-type limit|price|market
           [--price N] [--volume N] --confirm yes
  cancel   --order-id UUID
  status   --order-id UUID

The `order` subcommand REFUSES to run without `--confirm yes`. This is a
deliberate guard: the calling agent must have shown the order to the user and
received approval before adding that flag.

Exit codes: 0 ok / 1 usage error / 2 API or network error / 3 missing credentials.
"""
import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from urllib.parse import urlencode

import requests

try:
    import jwt
except ImportError:
    print("bithumb_api.py error: PyJWT not installed. Run: pip3 install PyJWT", file=sys.stderr)
    sys.exit(1)

BASE = "https://api.bithumb.com"


def die(code, msg):
    print(f"bithumb_api.py error: {msg}", file=sys.stderr)
    sys.exit(code)


def auth_headers(params=None):
    access = os.environ.get("BITHUMB_API_KEY")
    secret = os.environ.get("BITHUMB_SECRET_KEY")
    if not access or not secret:
        die(3, "BITHUMB_API_KEY / BITHUMB_SECRET_KEY environment variables are not set")
    payload = {
        "access_key": access,
        "nonce": str(uuid.uuid4()),
        "timestamp": round(time.time() * 1000),
    }
    if params:
        query = urlencode(params, doseq=True)
        payload["query_hash"] = hashlib.sha512(query.encode()).hexdigest()
        payload["query_hash_alg"] = "SHA512"
    token = jwt.encode(payload, secret, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode()
    return {"Authorization": f"Bearer {token}"}


def request(method, path, params=None, private=False, as_body=False):
    url = BASE + path
    headers = auth_headers(params) if private else {}
    try:
        if as_body:
            headers["Content-Type"] = "application/json"
            r = requests.request(method, url, headers=headers, json=params, timeout=15)
        else:
            r = requests.request(method, url, headers=headers, params=params, timeout=15)
    except requests.RequestException as e:
        die(2, f"network error: {e}")
    body = r.text
    try:
        parsed = r.json()
    except ValueError:
        parsed = {"raw": body[:500]}
    if r.status_code not in (200, 201):
        die(2, f"HTTP {r.status_code} on {path}: {json.dumps(parsed, ensure_ascii=False)[:500]}")
    return parsed


def cmd_ticker(args):
    return request("GET", "/v1/ticker", {"markets": args.markets})


def cmd_accounts(args):
    return request("GET", "/v1/accounts", private=True)


def cmd_chance(args):
    return request("GET", "/v1/orders/chance", {"market": args.market}, private=True)


def cmd_order(args):
    if args.confirm != "yes":
        die(1, "order refused: user approval gate. Re-run with --confirm yes ONLY after "
               "the user explicitly approved this exact order.")
    if args.side not in ("bid", "ask"):
        die(1, "--side must be bid (buy) or ask (sell)")
    params = {"market": args.market, "side": args.side, "ord_type": args.ord_type}
    if args.ord_type == "limit":
        if not args.price or not args.volume:
            die(1, "limit order needs --price and --volume")
        params["price"] = args.price
        params["volume"] = args.volume
    elif args.ord_type == "price":  # market buy: spend a KRW total
        if args.side != "bid" or not args.price:
            die(1, "ord_type=price is a market BUY and needs --price (total KRW)")
        params["price"] = args.price
    elif args.ord_type == "market":  # market sell: sell a volume
        if args.side != "ask" or not args.volume:
            die(1, "ord_type=market is a market SELL and needs --volume")
        params["volume"] = args.volume
    else:
        die(1, "--ord-type must be limit, price, or market")
    return request("POST", "/v2/orders", params, private=True, as_body=True)


def cmd_cancel(args):
    return request("DELETE", "/v2/order", {"order_id": args.order_id}, private=True)


def cmd_status(args):
    return request("GET", "/v1/order", {"uuid": args.order_id}, private=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ticker")
    p.add_argument("--markets", required=True)
    sub.add_parser("accounts")
    p = sub.add_parser("chance")
    p.add_argument("--market", required=True)
    p = sub.add_parser("order")
    p.add_argument("--market", required=True)
    p.add_argument("--side", required=True)
    p.add_argument("--ord-type", required=True)
    p.add_argument("--price")
    p.add_argument("--volume")
    p.add_argument("--confirm", default="no")
    p = sub.add_parser("cancel")
    p.add_argument("--order-id", required=True)
    p = sub.add_parser("status")
    p.add_argument("--order-id", required=True)

    args = ap.parse_args()
    fn = {"ticker": cmd_ticker, "accounts": cmd_accounts, "chance": cmd_chance,
          "order": cmd_order, "cancel": cmd_cancel, "status": cmd_status}[args.cmd]
    print(json.dumps(fn(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
