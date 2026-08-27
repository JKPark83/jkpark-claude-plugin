---
name: bithumb-auto-trade
description: >-
  Designs, reviews, backtests, and - after explicit per-order user approval -
  live-trades BTC/ETH on Bithumb via REST API 2.0. A strategy-designer
  subagent proposes a template-based rule strategy (backtestable Fear & Greed
  filter that buys fear and exits greed, BTC halving-cycle context, live-only
  news entry filter), two reviewers critique it from different angles (risk
  gatekeeper; overfitting validator), a backtester runs the bundled
  deterministic pandas script on Bithumb candles and must beat buy-and-hold
  or match it with far lower drawdown (fees included), then the user approves
  and a session trading loop starts where every order is confirmed before
  execution under a hard total-KRW cap. BITHUMB_API_KEY/BITHUMB_SECRET_KEY
  env vars are needed only for live trading. Use for Bithumb auto-trading or
  crypto strategy design/backtesting - "빗썸 자동매매", "코인 자동거래 해줘",
  "빗썸 매매 전략 세워서 돌려줘", "BTC 전략 백테스트", "공포탐욕지수로
  매매해줘", "start Bithumb auto trading".
---

# Bithumb Auto-Trade

Pipeline: **설계 → 이중 리뷰 → 결정적 백테스트 → 전략 승인 → 세션 루프
(주문마다 승인)**. The LLM designs and interprets; a fixed deterministic
script (`scripts/backtest.py`) computes every backtest number AND every live
signal — the same code path, so live behavior cannot diverge from what was
tested. All conversation with the user is in Korean.

## Hard rules

1. **Every order needs its own user approval.** Show the exact order (market,
   side, type, price/volume, KRW value, reason) via AskUserQuestion and place
   it only on approval. This includes stop-loss and take-profit sells.
   Violation example: the price crashed through the stop, so you execute the
   sell first and inform the user after "because timing matters" — never; you
   propose the sell and wait.
2. **Never exceed the approved total KRW cap.** Before proposing any buy,
   check `invested_krw + order_krw <= cap` in the state file. Violation
   example: the signal is strong so you propose "이번만 한도 10% 초과" — never
   offer cap-exceeding orders at all.
3. **Orders go only through `scripts/bithumb_api.py order --confirm yes`.**
   Never hand-roll a `POST /v2/orders` call with curl/requests, and never add
   `--confirm yes` before the user approved that exact order.
4. **Backtest and signal numbers come only from `scripts/backtest.py`
   output.** Never estimate performance, and never tweak the script's
   PASS/FAIL verdict or thresholds mid-run. Violation example: FAIL by 1 %p
   so you "round it" to PASS — the redesign loop exists for that.
5. **API keys stay in env vars.** Read `BITHUMB_API_KEY`/`BITHUMB_SECRET_KEY`
   only inside the script; never echo them, never write them to any file.

## Phase 0 — Preflight

```bash
python3 -c "import pandas, requests, jwt" 2>&1
```

Missing modules → `pip3 install pandas requests PyJWT` (ask via the normal
permission flow). Check env keys with `python3 -c "import os; print(bool(os.environ.get('BITHUMB_API_KEY') and os.environ.get('BITHUMB_SECRET_KEY')))"`.
Keys absent → tell the user design/review/backtest still work, live trading
will need keys (빗썸 마이페이지 → API 관리에서 발급, IP 등록 필수, 거래
권한 체크), and continue.

Create the session directory and state file:

```bash
mkdir -p ~/.bithumb-auto-trade/sessions/$(date +%Y%m%d-%H%M%S)
```

`state.json` schema (maintain it after every event):

```json
{"cap_krw": 0, "invested_krw": 0, "markets": {},
 "positions": {"KRW-BTC": {"volume": 0, "entry_price": null, "invested": 0}},
 "orders": [], "cycle": 0}
```

## Phase 1 — Trading parameters

One AskUserQuestion round: ① 총 투입 한도 KRW (hard cap — options 500,000 /
1,000,000 / 3,000,000 / 직접 입력), ② 대상 마켓 (KRW-BTC / KRW-ETH / 둘 다),
③ 캔들 주기 = 루프 주기 (일봉 (추천 — 하루 1회 판단) / minutes:240 /
minutes:60). Record answers in `state.json`.

## Phase 2 — Strategy design

Spawn the `bithumb-strategy-designer` agent with: markets, cap, interval,
absolute `scripts/` and `references/` paths, and — on redesign — the full
reviewer/backtester feedback. Save each returned spec JSON to the session
directory as `spec_{market}.json` exactly as returned.

## Phase 3 — Dual review (parallel)

Spawn `bithumb-risk-reviewer` and `bithumb-validity-reviewer` **in one
message** (they are independent), each with the spec paths, cap, designer
rationale, and `references/` path.

- Both PASS → Phase 4.
- Any REVISE → back to Phase 2 with both verdict JSONs as feedback.
- After **3 design rounds** without both PASS → stop and report the unresolved
  issues to the user; ask whether to relax direction or abort. Never
  soft-pass a REVISE yourself.

## Phase 4 — Backtest

Spawn `bithumb-backtester` with the spec paths, candle count (730 for days,
2000 for minute intervals — or what the validity reviewer recommended), and
the `scripts/` path.

- All specs PASS → Phase 5.
- Any FAIL → back to Phase 2 with the backtester's report as feedback (counts
  toward the same 3-round limit). On round exhaustion: report honestly that
  no reviewed strategy beat buy-and-hold, suggest 단순 보유 as the rational
  alternative, and stop. Do not ship a FAIL strategy to Phase 5.

## Phase 5 — Strategy approval

Present one Korean report: 전략 요약 (템플릿·파라미터·손절·뉴스 오버레이),
두 리뷰 요약 (남은 medium/low 이슈 포함), 백테스트 비교 표 + 판정, 운영
계획 (루프 주기, 주문마다 승인 필요, 한도), 면책 1줄. Then AskUserQuestion:
**승인하고 루프 시작 / 재설계 요청 / 여기서 중단** (+ 승인 시 실거래 vs
관찰 모드(주문 제안 없이 신호만 보고) 선택지 포함). 재설계 → Phase 2.

## Phase 6 — Session trading loop

Runs until the user stops it, the session ends, or a halt condition fires.
Before the first cycle, if keys exist: run `bithumb_api.py chance` per
market; if the real `bid_fee`/`ask_fee` differ from the spec's `fee_pct`,
report it and rerun Phase 4 with the corrected fee before trading.

Each cycle, per market:

1. **Data + signal**

   ```bash
   python3 scripts/fetch_candles.py --market {m} --interval {itv} --count 200 --out {sess}/live_{m}.csv
   python3 scripts/fetch_fng.py --out {sess}/fng.csv        # when the spec has a "fng" block
   python3 scripts/backtest.py --csv {sess}/live_{m}.csv --spec {sess}/spec_{m}.json --fng {sess}/fng.csv --mode signal
   ```

   Note: with a `fng` block, --count 200 minute candles may predate the FNG
   window edge — harmless; uncovered days are simply unconstrained. The
   signal output includes `fng_value` so the cycle report can show it.

2. **Decide** (deterministic, from signal + state):
   - No position & `target_position` 1 → entry candidate. First check the
     spec's `news_overlay`: run its `queries` via WebSearch; any
     `block_entry_if` condition met → skip entry, log why. Order size =
     `min(cap × cap_allocation_pct × position_fraction, cap − invested_krw)`;
     below the market's min order (~5,000 KRW) → skip.
   - Position & `target_position` 0 → exit candidate (전량 매도).
   - Position & price ≤ entry × (1 − stop_loss_pct/100) → stop-loss sell
     candidate (still user-approved, per hard rule 1).
3. **Propose & execute** — for each candidate order: AskUserQuestion showing
   market/side/type/amount/reason/한도 잔여 (options: 승인 / 이번은 건너뛰기
   / 루프 중단). Approved →

   ```bash
   python3 scripts/bithumb_api.py order --market {m} --side {bid|ask} --ord-type {price|market} --price {krw} --volume {vol} --confirm yes
   python3 scripts/bithumb_api.py status --order-id {id}
   ```

   Use `price` (market buy, KRW total) and `market` (market sell, volume)
   order types by default. Update `state.json` (positions, invested_krw,
   orders, entry_price from the fill).
4. **Cycle report** — 2–4 lines: 신호, 포지션, 평가손익 (현재가 × 보유량 −
   투입), 누적 투입/한도. In 관찰 모드 stop after reporting what WOULD have
   been ordered.
5. **Wait** for the next candle close: `sleep` in ≤10-minute chunks (the user
   can interrupt anytime; on interruption, treat it as input, not an error).

**Halt conditions** — stop the loop and report immediately: 3 consecutive
script failures (network/API); an order rejected for `out_of_scope`/
`NotAllowIP` (key permission problem — explain the fix); the user picks 루프
중단. On any stop, print a final session summary (모든 주문, 실현/미실현
손익, 남은 포지션과 그 처리 방법).

## References

- `references/strategy-spec.md` — spec JSON format, the 4 templates, allowed
  param ranges, news-overlay fail-safe rule. The designer and reviewers read
  this; read it yourself when validating specs.
- `references/bithumb-api.md` — API 2.0 endpoints/auth/rate limits and the
  UNVERIFIED items (real fee rate, min order, stp_type) to check live.

## Example (input → key outputs)

User: "빗썸으로 BTC 자동매매 해줘, 한도 100만원" → Phase 1 confirms KRW-BTC
/ 1,000,000 / 일봉 → designer returns `sma_cross {fast:20, slow:60}`,
stop 8%, fng {entry_max:60, exit_min:85} (반감기 사이클상 후반부라 보수적
진입), overlay: 거래소 해킹·급락 뉴스 시 진입 보류 → risk PASS (medium:
비용 드래그 연 ~1.4%), validity PASS → backtest: 전략 +22.1% / MDD 31.8% vs
보유 +31.9% / MDD 50.2% → **FAIL** (edge X, defense X) → redesign round 2
with that feedback → … → PASS → user approves → loop proposes "KRW-BTC 시장가
매수 950,000원 (한도 내 95%)" → user 승인 → order placed, state updated.
