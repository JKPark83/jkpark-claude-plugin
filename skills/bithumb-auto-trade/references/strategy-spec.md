# Strategy Spec Format

The single interface between the designer, reviewers, backtester, and the live
loop. One JSON file per market. `scripts/backtest.py` consumes it directly
(unknown keys are ignored by the script but read by agents).

## Full example

```json
{
  "market": "KRW-BTC",
  "interval": "days",
  "template": "sma_cross",
  "params": {"fast": 20, "slow": 60},
  "position_fraction": 1.0,
  "stop_loss_pct": 8,
  "take_profit_pct": null,
  "fee_pct": 0.04,
  "slippage_pct": 0.05,
  "cap_allocation_pct": 60,
  "fng": {"entry_max": 60, "exit_min": 85},
  "news_overlay": {
    "queries": ["bitcoin exchange hack news", "비트코인 규제 뉴스"],
    "block_entry_if": [
      "주요 거래소 해킹·출금 중단이 최근 24시간 내 보도됨",
      "미국/한국의 즉시 시행 규제 발표로 급락 진행 중"
    ]
  },
  "rationale": "최근 6개월 일봉이 뚜렷한 추세장이라 중기 SMA 크로스가 ..."
}
```

## Fields

| Field | Type | Notes |
|---|---|---|
| `market` | string | `KRW-BTC` or `KRW-ETH` |
| `interval` | string | `days` or `minutes:<1\|3\|5\|10\|15\|30\|60\|240>` — also the live loop cycle |
| `template` | string | one of the 4 templates below |
| `params` | object | template-specific, all numeric |
| `position_fraction` | number | fraction of this market's allocated capital used per entry (0-1] |
| `stop_loss_pct` | number\|null | intrabar stop below entry price; null = none |
| `take_profit_pct` | number\|null | intrabar take-profit above entry; null = none |
| `fee_pct` | number | per-side taker fee %; default 0.04 — verify per account via `bithumb_api.py chance` |
| `slippage_pct` | number | per-side slippage assumption %; default 0.05 |
| `cap_allocation_pct` | number | share of the user's total KRW cap for this market; all specs must sum ≤ 100 |
| `fng` | object\|absent | Fear & Greed filter, **backtested** (see below): `entry_max` (0–100, required) — new entries only while index ≤ this (buy fear); `exit_min` (optional, > entry_max) — force-exit while index ≥ this (sell greed) |
| `news_overlay` | object | live-loop-only filter, see rule below |
| `rationale` | string | Korean; why this template/params fit the current market |

## Templates and parameter ranges

Long-only, position 0 or 1. Signals are computed on bar close and executed at
the next bar's open (backtest and live behave identically via
`backtest.py --mode signal`).

| Template | Logic | Params (allowed range) |
|---|---|---|
| `sma_cross` | long while SMA(fast) > SMA(slow) | fast 5–30, slow 20–120, fast < slow |
| `rsi_meanrev` | enter when RSI < buy_th, exit when RSI > sell_th | period 7–21, buy_th 20–35, sell_th 55–75 |
| `donchian_breakout` | enter on close > prior entry_n-bar high; exit on close < prior exit_n-bar low | entry_n 10–55, exit_n 5–30 |
| `macd_trend` | long while MACD line > signal line | fast 8–15, slow 20–35, signal 5–12 |

Parameters outside these ranges are a validity-review failure. Ranges exist to
keep the search space small (overfitting guard), not because other values
can't work.

## Fear & Greed filter (`fng`) — backtested component

The crypto Fear & Greed index (alternative.me, daily since 2018-02) is fetched
by `scripts/fetch_fng.py` and consumed by `backtest.py --fng`. Because history
exists, this filter is a REAL strategy component verified by the backtest —
unlike the news overlay. Semantics (deterministic, same in backtest and live):
entries only while index ≤ `entry_max`; open positions force-exit while index
≥ `exit_min`. Days without index data are unconstrained. Typical values:
entry_max 50–70, exit_min 80–90; entry_max below ~40 keeps the strategy in
cash most of a bull market — check the backtest's trade count.

## Halving-cycle context (design-time input, not a spec field)

The designer researches BTC halving-epoch statistics (2012/2016/2020/2024:
post-halving bull ~12–18 months, then deep multi-month drawdowns) and must
state in `rationale` where the current date sits in the cycle and how that
influenced the template choice. It is context, not a mechanical rule — there
are only 4 historical samples, so the validity reviewer treats any hard
halving-based timing claim ("반감기 후 18개월째라 반드시 하락") as
overfitting on n=4.

## News overlay rule (fail-safe principle)

The overlay is NOT backtestable, so it must only ever **block or reduce risk**,
never create it:

- Allowed: skip a new entry, tighten a stop, propose an early exit for user
  approval.
- Forbidden: generate an entry the template didn't signal, increase position
  size, or widen a stop. Violation example: "긍정 뉴스가 강하니 시그널 없이
  선매수" — this is untested alpha and must be rejected in review.

`block_entry_if` conditions must be checkable from a WebSearch of `queries`
within the loop cycle, and must describe observable events (보도/발표/중단),
not vibes ("분위기가 나쁘면").
