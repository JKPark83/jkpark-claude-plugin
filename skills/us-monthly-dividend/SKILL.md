---
name: us-monthly-dividend
description: Designs and analyzes US monthly-dividend income portfolios (SCHD, JEPI, JEPQ, O, DGRO, covered-call ETFs, REITs). Covers four operations - designing a portfolio from a budget and target monthly income with a Jan-Dec dividend calendar that fills every month; analyzing existing holdings for month-by-month cash flow and coverage gaps; computing after-tax cash flow for a Korean resident (15% US withholding); and checking holdings for dividend cuts or payout anomalies. Fetches dividend history and yields deterministically via a bundled yfinance script and saves the report to the Obsidian vault via the obs skill. Use when the user mentions 월배당, 배당 달력, 배당 포트폴리오, 세후 배당, 배당컷 - e.g. "월배당 포트폴리오 짜줘", "내 배당 포트폴리오 분석해줘", "세후 월 현금흐름 계산해줘", "배당컷 있는지 점검해줘", "design a monthly dividend portfolio". Not for growth-stock screening, options strategies, or Korean domestic (KOSPI) dividend stocks.
---

# US Monthly-Dividend Portfolio

Builds and reviews US dividend portfolios aimed at receiving cash **every
month**. All conversation and reports are in Korean (한국어). Every report ends
with the fixed disclaimer in Step 6 — this skill informs, it does not advise.

## Step 0 — Pick the mode

| User gives | Mode |
|------------|------|
| Budget and/or target monthly income, no holdings | **design** |
| A holdings list (ticker + shares) | **analyze** (includes calendar, after-tax, and monitor verdicts) |
| Holdings + asks only about cuts/anomalies ("배당컷 점검") | **monitor** |

If neither a budget nor holdings are present, ask one Korean question to get
them — do not guess a portfolio.

## Step 1 — Collect input

- **design**: budget (KRW or USD — convert KRW→USD with the script's
  `usdkrw`), optional target monthly after-tax income, and covered-call
  tolerance. If tolerance is not stated, default: covered-call ETFs capped at
  **20%** of the portfolio, single ticker capped at **40%**.
- **analyze / monitor**: holdings as `TICKER shares` pairs (e.g. `SCHD 40,
  JEPI 30, O 20`). Shares missing → ask; do not assume equal weights.

## Step 2 — Fetch data (deterministic)

```bash
python3 scripts/fetch_dividends.py TICKER1 TICKER2 ...
```

- **analyze/monitor**: pass exactly the user's tickers.
- **design**: pass the candidate universe below plus any tickers the user
  named. Trim or extend the universe only on user request.

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

## Step 3 — Build the dividend calendar

Per ticker: monthly amount = `by_month_ttm[m] × shares`. Produce a 1–12월
table (rows = tickers, columns = months, plus a 합계 row) in pre-tax USD.

**design** additionally: choose a combination whose 합계 row has no zero
month, within the Step 1 caps, spending ≤ the budget at current prices.
Prefer the smallest number of tickers that fills all 12 months; break ties
toward higher TTM yield. State share counts and cost per ticker. The caps are
hard ceilings after share rounding — if rounding pushes a ticker over a cap,
drop one share and leave the cash uninvested. **Violation example:** 342
shares makes MAIN 40.04% of the portfolio — over the 40% cap; buy 341.
Mention only tickers actually in the chosen portfolio in the report.

## Step 4 — After-tax cash flow

- Default: `세후 = 세전 × 0.85` (US 15% treaty withholding; no additional
  Korean withholding since 15% ≥ 14%). Details: references/tax-rules.md.
- Convert to KRW with the script's `usdkrw`; show both currencies.
- If projected **annual gross** dividends exceed 20,000,000 KRW, add one
  warning line about 금융소득종합과세 (do not compute it — point to a tax
  professional, per references/tax-rules.md).

## Step 5 — Monitor verdicts (deterministic)

Apply to every ticker in analyze/monitor mode; skip in pure design mode.

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

## Step 7 — Save to Obsidian

Invoke the `obs` skill to save the full report, titled
`미국 월배당 {mode} {as_of}` (routing: Research). Then relay the obsidian://
link from obs to the user. If obs fails, keep the chat report and say the
vault save failed — do not silently drop it.

## Worked example (abbreviated)

Input: "SCHD 40, JEPI 30, O 20 분석해줘"
→ Step 2 fetches the 3 tickers → calendar shows 1월 합계 $4.9 (O only),
3월 $25.0 (SCHD+JEPI+O) … → 세후 = 각 월 × 0.85, KRW 병기 → JEPI TTM 4.58 <
4.81×0.97 → WARN → report per Step 6 → obs save.
