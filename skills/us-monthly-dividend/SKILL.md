---
name: us-monthly-dividend
description: Designs and analyzes US monthly-dividend income portfolios (SCHD, JEPI, JEPQ, O, DGRO, covered-call ETFs, REITs). Covers five operations - designing a portfolio from a budget and target monthly income with a Jan-Dec dividend calendar that fills every month; rebalancing an existing account when new money is added (buy-only allocation of the new cash to underweight tickers, Swedroe 5/25 band check, sells only on explicit opt-in); analyzing existing holdings for month-by-month cash flow and coverage gaps; computing after-tax cash flow for a Korean resident (15% US withholding); and checking holdings for dividend cuts or payout anomalies. In design/rebalance mode, proposes the covered-call cap and ticker count from current market conditions (VIX, US 10Y yield + three parallel analyst subagents) with user confirmation instead of fixed defaults. Fetches dividend history, yields, and market indicators deterministically via a bundled yfinance script, saves the report to the Obsidian vault via the obs skill, and offers an optional Google Sheets export. Use when the user mentions 월배당, 배당 달력, 배당 포트폴리오, 세후 배당, 배당컷, 추가납입, 리밸런싱 - e.g. "월배당 포트폴리오 짜줘", "1000만원 추가납입하려는데 재조정해줘", "내 배당 포트폴리오 분석해줘", "세후 월 현금흐름 계산해줘", "배당컷 있는지 점검해줘", "design a monthly dividend portfolio". Not for growth-stock screening, options strategies, or Korean domestic (KOSPI) dividend stocks.
---

# US Monthly-Dividend Portfolio

Builds and reviews US dividend portfolios aimed at receiving cash **every
month**. All conversation and reports are in Korean (한국어). Every report ends
with the fixed disclaimer in Step 6 — this skill informs, it does not advise.

## Step 0 — Pick the mode

| User gives | Mode |
|------------|------|
| Budget and/or target monthly income, no holdings | **design** |
| New money (추가납입) + an existing account | **rebalance** |
| A holdings list (ticker + shares) | **analyze** (includes calendar, after-tax, and monitor verdicts) |
| Holdings + asks only about cuts/anomalies ("배당컷 점검") | **monitor** |

If neither a budget nor holdings are present, ask one Korean question to get
them — do not guess a portfolio.

When the user gives only a budget, ask one Korean question before designing:
does an existing account already hold dividend assets (기존 계좌 보유 여부)?
Yes → switch to **rebalance** and collect the holdings; no → stay **design**.
Words like 추가납입/추납/재조정 always mean rebalance — never design a fresh
portfolio that ignores what the account already holds.

## Step 1 — Collect input

- **design**: budget (KRW or USD — convert KRW→USD with the script's
  `usdkrw`), optional target monthly after-tax income, and optionally an
  explicit covered-call cap and/or ticker count. If the user states them,
  those values are final and Step 2.5 is skipped. Otherwise both are proposed
  in Step 2.5 from market conditions. Hard guardrails that no assessment or
  proposal may cross: covered-call ETFs ≤ **40%** of the portfolio, single
  ticker ≤ **40%**, ticker count 3–6.
- **rebalance**: the new cash (KRW or USD) plus current holdings, from
  either source:
  - `TICKER shares` pairs typed by the user, or
  - **the Google Sheet this skill previously exported** — when the user
    points at it (a link/ID or "지난번 시트"), load it with the Google
    Drive MCP tools (ToolSearch-load them if deferred): find it via
    `search_files` on the report title (`미국 월배당`, newest first) or use
    the given ID, read it with `read_file_content`, and parse the
    `[보유종목]` section: Ticker + 주수 become the current holdings, and —
    when present — 평단(USD)/매입금액(USD) plus the `[요약]` section's
    투자시작일·시작환율 carry the cost basis and 환차익 through to the new
    report. Prices, yields, and FX are always re-fetched fresh in Step 2,
    never trusted from the sheet. Unreadable or unparsable sheet → say so
    and ask for `TICKER shares`.

  Holdings missing → ask; do not guess. The design caps above apply to the
  **combined** portfolio (existing value + new cash).
- **analyze / monitor**: holdings as `TICKER shares` pairs (e.g. `SCHD 40,
  JEPI 30, O 20`). Shares missing → ask; do not assume equal weights.

## Step 2 — Fetch data (deterministic)

```bash
python3 scripts/fetch_dividends.py TICKER1 TICKER2 ...
```

- **analyze/monitor**: pass exactly the user's tickers.
- **design/rebalance**: pass the candidate universe below plus any tickers
  the user named or already holds, and add `--market` (VIX and US 10Y for
  Step 2.5). Trim or extend the universe only on user request.

| Group | Tickers | Note |
|-------|---------|------|
| Monthly payers | JEPI JEPQ O SPHD MAIN | JEPI/JEPQ/SPHD are covered-call/enhanced-income |
| Quarterly core | SCHD DGRO VYM | payout months come from the data, not assumption |

Rules for using the output:
- Every number in the report (price, yield, per-month amounts, FX) comes from
  the script output or the user's input — nothing else. **Violation example:**
  the script errors on JEPI, and the report states "JEPI 배당률 약 7%" from
  memory — forbidden. Instead report: "JEPI 조회 실패(사유)로 분석에서 제외".
- Payout months come from `pay_months`/`by_month_ttm` only. **Violation
  example:** listing SCHD under January because "quarterly ETFs pay in
  Jan/Apr/Jul/Oct" — SCHD's data says 3/6/9/12.
- If the script exits non-zero (all tickers failed), stop and report the
  stderr message; do not fall back to web estimates.

## Step 2.5 — Market assessment (design & rebalance)

Decides the covered-call cap and target ticker count instead of hardcoding
them. Skip when the user stated both explicitly in Step 1, or in
analyze/monitor mode. Pipeline (modeled on analyst → risk manager →
portfolio manager separation):

1. **Analysts** — launch three subagents in parallel (one message, three
   Agent calls), each given the script's `market` numbers and returning ≤5
   lines: a verdict (favorable / neutral / unfavorable) plus 2–3 cited facts
   from web research:
   - **금리/매크로**: rate direction and what it means for REITs (O) and
     BDCs (MAIN).
   - **변동성/커버드콜**: VIX level vs 3 months ago → option-premium
     richness; covered-call payout outlook.
   - **인컴자산 건전성**: covered-call ETF NAV-erosion news, BDC credit
     conditions, dividend-cut chatter in the candidate universe.
2. **Risk-manager synthesis** (you, in-chat): start from baseline
   covered-call cap 20%, ticker count = smallest that fills 12 months.
   Adjust within guardrails — high/rising VIX with healthy income assets
   supports a higher covered-call cap (premiums rich); falling rates favor
   REIT/BDC weight; NAV-erosion or credit warnings push the cap down, and
   worse conditions favor more tickers for diversification. State the
   numbers behind every adjustment.
3. **User confirmation** — present the proposal via AskUserQuestion with
   options: apply the proposal / keep baseline (20%, minimum tickers) /
   custom values. The confirmed values become Step 3's caps.

If the `market` block is null or the analysts fail, fall back to the
baseline, and say so in the report. Analyst opinions never override the
guardrails, never add tickers outside the universe, and never touch the
deterministic math in Steps 3–5.

## Step 3 — Build the dividend calendar

Per ticker: monthly amount = `by_month_ttm[m] × shares`. Produce a 1–12월
table (rows = tickers, columns = months, plus a 합계 row) in pre-tax USD.

**design** additionally: choose a combination whose 합계 row has no zero
month, within the confirmed caps (Step 2.5 or user-stated), spending ≤ the
budget at current prices. Use exactly the confirmed ticker count N: among
N-ticker combinations that fill all 12 months, pick the highest TTM yield.
If no N-ticker combination is feasible, try N+1 then N−1 and state the
deviation. When Step 2.5 was skipped without user-stated values (fallback),
prefer the smallest N that fills all 12 months; break ties toward higher
TTM yield. State share counts and cost per ticker. The caps are
hard ceilings after share rounding — if rounding pushes a ticker over a cap,
drop one share and leave the cash uninvested. **Violation example:** 342
shares makes MAIN 40.04% of the portfolio — over the 40% cap; buy 341.
Mention only tickers actually in the chosen portfolio in the report.

**rebalance** instead of choosing from scratch (buy-only pattern, after
RePort / lazy-allocation / M1 dynamic rebalancing):
1. Value the existing holdings at script prices; combined total = existing
   value + new cash. Compute Step 5 verdicts for the held tickers now.
2. Set target weights: the design-optimal portfolio for the combined total
   under the confirmed caps, keeping the held tickers unless one is
   REVIEW-flagged or outside the universe (then its target grows no further
   — say why).
3. Allocate the **new cash only** — no sells by default (taxes, fees):
   repeatedly buy 1 share of the most-underweight ticker (target − current,
   in dollars) until the remaining cash cannot buy the cheapest underweight
   share. Never send new cash to a REVIEW-flagged ticker.
4. Judge the result with the Swedroe **5/25 band**: out-of-band when a
   ticker is off target by ≥5%p absolute (targets ≥20%) or ≥25% relative
   (targets <20%). Still out-of-band after allocation → present the sell
   orders that would fix it as an *option*; execute sells only when the
   user explicitly opts in. Existing positions may already break a hard
   cap — buying never fixes that, so flag it instead of selling silently.

## Step 4 — After-tax cash flow

- Default: `세후 = 세전 × 0.85` (US 15% treaty withholding; no additional
  Korean withholding since 15% ≥ 14%). Details: references/tax-rules.md.
- Convert to KRW with the script's `usdkrw`; show both currencies.
- If projected **annual gross** dividends exceed 20,000,000 KRW, add one
  warning line about 금융소득종합과세 (do not compute it — point to a tax
  professional, per references/tax-rules.md).

## Step 5 — Monitor verdicts (deterministic)

Apply to every held ticker in analyze/monitor/rebalance mode (rebalance
computes them during Step 3, before allocating new cash); skip in pure
design mode.

| Verdict | Condition (first match wins) |
|---------|------------------------------|
| REVIEW | non-covered-call: latest `recent` payment < 95% of the one before it. Covered-call (JEPI JEPQ SPHD): `ttm_dividend` < `prev_ttm_dividend × 0.90` |
| WARN | `ttm_dividend` < `prev_ttm_dividend × 0.97` |
| OK | otherwise |

Covered-call payouts vary month to month by design — never flag them REVIEW
on a single-payment comparison. **Violation example:** JEPI pays $0.34 after
$0.45 the prior month → not a REVIEW; its TTM total is what counts.

## Step 6 — Report (Korean)

Output the full report in chat using exactly these sections:

```markdown
# 미국 월배당 리포트 — {mode} ({as_of})

## 요약
- 투자원금/평가액, 세전·세후 연 배당, 평균 월 세후 현금흐름 (USD·KRW), 적용 환율

## 시장 상황 평가 (Step 2.5를 수행한 경우만)
- 지표: VIX {now} (3개월 전 {then}), 미 10년물 {now}% ({then}%)
- 애널리스트 3인 판정 각 1줄 + 근거
- 적용 파라미터: 커버드콜 한도 {x}%, 종목 수 {n} (사용자 확인: 제안 적용/수정)

## 리밸런싱 내역 (rebalance만)
- 기존 평가액, 신규 납입액, 합산 총액 (USD·KRW)
- | 종목 | 기존 주수 | 추가 매수 | 최종 주수 | 목표 비중 | 실제 비중 | 드리프트 | 5/25 밴드 |
- (해당 시) buy-only로 해소되지 않은 밴드 초과 종목 + 매도 옵션 1줄
  (매도는 사용자가 명시적으로 요청할 때만 반영)

## 월별 배당 달력 (세전 USD)
| 종목 | 1월 | … | 12월 | 연간 |
| 합계 |

## 세후 월 현금흐름
- 월별 세후 (USD·KRW) 표 + 빈 달(커버리지 갭) 명시
- (해당 시) 금융소득종합과세 경고 1줄

## 종목별 상세·판정
| 종목 | 주수 | 단가 | 비중 | TTM 배당률 | 판정(OK/WARN/REVIEW) | 근거 |

## 참고
- 조회 실패 종목과 사유 (없으면 생략)
- 본 리포트는 {as_of} 기준 과거 배당 실적(TTM) 기반 추정이며 미래 배당을
  보장하지 않습니다. 투자 판단과 책임은 본인에게 있으며, 이 문서는 투자
  자문이 아닙니다.
```

The 근거 column cites the numbers that produced the verdict (e.g. "TTM 4.58
vs 직전 4.81, -4.8% → WARN").

## Step 7 — Save & export

Invoke the `obs` skill to save the full report, titled
`미국 월배당 {mode} {as_of}` (routing: Research). Then relay the obsidian://
link from obs to the user. If obs fails, keep the chat report and say the
vault save failed — do not silently drop it.

Then ask via AskUserQuestion whether to also export to Google Sheets
(구글시트에도 저장할까요? 예/아니오 — 세션당 한 번; the user may also state
the preference up front). On yes:

1. Build a CSV from Steps 2–5 numbers only. One sheet, sections stacked
   vertically under fixed markers (`[요약]`, `[보유종목]`,
   `[월별 배당 달력(세전 USD)]`, `[세후 월 현금흐름]`) so a later rebalance
   run can parse it back. Layout follows the user's JK 포트폴리오 sheet
   plus common dividend trackers (Tawcan, DividendEarner):
   - `[요약]`: 리포트 제목·기준일, 투자시작일·시작환율, 현재환율,
     환차익률·환차익금 (시작환율을 알 때만), 세전/세후 연 배당, 세후
     월평균 (USD·KRW). Fresh design: 투자시작일 = as_of, 시작환율 =
     현재환율.
   - `[보유종목]` — exact header, one row per ticker, then 합계(USD)/합계(KRW):
     `종목,Ticker,목표비중(%),밴드하한(%),밴드상한(%),평단(USD),주수,매입금액(USD),현재단가(USD),평가금액(USD),수익금(USD),수익률(%),현재비중(%),TTM배당률(%),리밸런싱주수`
     주수 is always the **final** share count; 리밸런싱주수 holds this
     run's buy (or explicitly opted-in sell) orders; 밴드하한/상한 are the
     5/25 bounds around 목표비중; 평단·매입금액·수익 columns stay blank
     when no cost basis is known — never invent one.
   - `[월별 배당 달력(세전 USD)]`: rows = tickers, columns = 1월…12월,연간,
     plus a 합계 row (the standard ticker × month matrix).
   - `[세후 월 현금흐름]`: USD and KRW rows across 1월…12월,월평균.
2. Upload with the Google Drive MCP tool
   `mcp__claude_ai_Google_Drive__create_file` (load it via ToolSearch first
   if deferred): `title` = the report title, `textContent` = the CSV,
   `contentMimeType` = `text/csv`. The default conversion turns it into a
   Google Sheets document — relay the returned link.
3. If the tool is unavailable or the upload fails, save the CSV as an
   attachment inside the same obs folder-note folder and say the Sheets
   upload failed — do not silently drop it.

## Worked example (abbreviated)

Input: "SCHD 40, JEPI 30, O 20 분석해줘"
→ Step 2 fetches the 3 tickers → calendar shows 1월 합계 $4.9 (O only),
3월 $25.0 (SCHD+JEPI+O) … → 세후 = 각 월 × 0.85, KRW 병기 → JEPI TTM 4.58 <
4.81×0.97 → WARN → report per Step 6 → obs save.

Input: "계좌에 JEPQ 20주, O 15주 있는데 1,000만원 추가납입해서 재조정해줘"
→ rebalance: fetch universe + holdings with `--market` → Step 2.5 proposal
→ target weights for (기존 평가액 + 1,000만원) → new cash buys the most
underweight ticker one share at a time, no sells → 드리프트/5/25 밴드 표 →
report + obs save → "구글시트에도 저장할까요?".
