# Bithumb REST API 2.0 Facts

Verified against apidocs.bithumb.com (2026-08). Everything the bundled scripts
already implement; read this only when debugging an API error or extending the
scripts.

## Versions

- API 2.0 (JWT, Upbit-compatible style) is the current standard — all new code
  uses it. API 1.0 (Api-Sign HMAC) still runs but gets no new features; do not
  use it.
- Market code format is `KRW-BTC` (not the 1.0-style `BTC_KRW`).

## Auth (implemented in scripts/bithumb_api.py)

- Header: `Authorization: Bearer <jwt>`, signed HS256 with the Secret Key.
- JWT claims: `access_key`, `nonce` (uuid4), `timestamp` (epoch ms); when the
  request has parameters also `query_hash` = SHA-512 hex of the urlencoded
  params and `query_hash_alg: "SHA512"`. POST bodies are hashed the same way.
- 401 error codes: `invalid_query_payload`, `jwt_verification`, `expired_jwt`,
  `NotAllowIP` (API key IP allowlist mismatch), `out_of_scope` (key lacks the
  permission — e.g. trade permission not enabled on the key).

## Endpoints used

| Purpose | Endpoint |
|---|---|
| Candles (day) | `GET /v1/candles/days?market=&count=&to=` (count ≤ 200) |
| Candles (minute) | `GET /v1/candles/minutes/{unit}?market=&count=&to=` (unit ∈ 1,3,5,10,15,30,60,240) |
| Ticker | `GET /v1/ticker?markets=KRW-BTC,KRW-ETH` |
| Balances | `GET /v1/accounts` (private) |
| Order constraints | `GET /v1/orders/chance?market=` (private) — `bid_fee`/`ask_fee`, `market.bid.min_total` (min order KRW), `market.max_total` |
| Place order | `POST /v2/orders` (private) — `market`, `side` (`bid`/`ask`), `ord_type` (`limit`: price+volume / `price`: market BUY with total KRW / `market`: market SELL with volume) |
| Cancel | `DELETE /v2/order?order_id=` (private) |
| Order status | `GET /v1/order?uuid=` (private) — `state`: wait/watch/done/cancel |

## Rate limits

- Public: 150 req/s per IP (per category). Private: 140 req/s per IP.
- The scripts sleep 0.12s between candle pages; the live loop makes only a
  handful of calls per cycle, so limits are never a concern in normal use.

## Unverified items — check live, never assume

- Actual account fee rate: docs show 0.25% examples but Bithumb has run 0.04%
  base fees; ALWAYS read the real `bid_fee`/`ask_fee` from `/v1/orders/chance`
  before the first order and update the spec's `fee_pct` if it differs.
- Minimum order amount varies per market — read `market.bid.min_total` from
  the same call (commonly around 5,000 KRW).
- Orders may require an `stp_type` (self-trade prevention) field per a 2026
  changelog note. The script does not send it; if `POST /v2/orders` returns an
  error naming `stp_type`, add it to the params in `cmd_order` per the error
  message and the current official docs.
