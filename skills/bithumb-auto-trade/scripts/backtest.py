#!/usr/bin/env python3
"""Deterministic long-only backtest for bithumb-auto-trade strategy specs.

Usage:
  python3 backtest.py --csv candles.csv --spec spec.json [--fng fng.csv]                 # full backtest -> JSON
  python3 backtest.py --csv candles.csv --spec spec.json [--fng fng.csv] --mode signal   # latest target position -> JSON

--fng (CSV from fetch_fng.py) is REQUIRED when the spec has a "fng" block:
new entries are allowed only while the Fear & Greed index <= fng.entry_max
(buy fear), and an open position is force-exited while index >= fng.exit_min
(sell greed; optional). Days without an index value are unconstrained.

The same template code computes both backtest positions and the live signal,
so there is no live/backtest divergence. Spec format: references/strategy-spec.md.

Semantics: signals are computed on bar close; trades execute at the NEXT bar's
open (no look-ahead). Stop-loss / take-profit are checked intrabar against
low/high. Costs (fee + slippage) apply to both sides of every trade.

Verdict (deterministic): PASS if strategy beats buy-and-hold on return, OR
return is within 5 %p of buy-and-hold while MDD is at least 10 %p smaller.

Exit codes: 0 ok / 1 usage or spec error / 2 data error.
"""
import argparse
import json
import sys

import pandas as pd


def die(code, msg):
    print(f"backtest.py error: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------- templates: df -> Series of target position (0 or 1) ----------

def t_sma_cross(df, p):
    fast = df["close"].rolling(int(p["fast"])).mean()
    slow = df["close"].rolling(int(p["slow"])).mean()
    return (fast > slow).fillna(False).astype(int)


def _rsi(close, period):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, 1e-12)
    return 100 - 100 / (1 + rs)


def t_rsi_meanrev(df, p):
    r = _rsi(df["close"], int(p["period"]))
    buy_th, sell_th = float(p["buy_th"]), float(p["sell_th"])
    holding, out = 0, []
    for v in r:
        if pd.isna(v):
            out.append(0)
            continue
        if holding == 0 and v < buy_th:
            holding = 1
        elif holding == 1 and v > sell_th:
            holding = 0
        out.append(holding)
    return pd.Series(out, index=df.index)


def t_donchian_breakout(df, p):
    upper = df["high"].rolling(int(p["entry_n"])).max().shift(1)
    lower = df["low"].rolling(int(p["exit_n"])).min().shift(1)
    holding, out = 0, []
    for c, u, l in zip(df["close"], upper, lower):
        if pd.isna(u) or pd.isna(l):
            out.append(0)
            continue
        if holding == 0 and c > u:
            holding = 1
        elif holding == 1 and c < l:
            holding = 0
        out.append(holding)
    return pd.Series(out, index=df.index)


def t_macd_trend(df, p):
    ema_f = df["close"].ewm(span=int(p["fast"]), adjust=False).mean()
    ema_s = df["close"].ewm(span=int(p["slow"]), adjust=False).mean()
    macd = ema_f - ema_s
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    return (macd > sig).astype(int)


TEMPLATES = {
    "sma_cross": (t_sma_cross, ["fast", "slow"]),
    "rsi_meanrev": (t_rsi_meanrev, ["period", "buy_th", "sell_th"]),
    "donchian_breakout": (t_donchian_breakout, ["entry_n", "exit_n"]),
    "macd_trend": (t_macd_trend, ["fast", "slow", "signal"]),
}


def load_spec(path):
    try:
        with open(path) as f:
            spec = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        die(1, f"cannot read spec: {e}")
    tpl = spec.get("template")
    if tpl not in TEMPLATES:
        die(1, f"unknown template '{tpl}' (allowed: {sorted(TEMPLATES)})")
    _, required = TEMPLATES[tpl]
    params = spec.get("params", {})
    for k in required:
        if k not in params:
            die(1, f"template '{tpl}' requires param '{k}'")
        try:
            float(params[k])
        except (TypeError, ValueError):
            die(1, f"param '{k}' must be numeric, got {params[k]!r}")
    for k in ("position_fraction", "fee_pct", "slippage_pct"):
        if k in spec:
            try:
                float(spec[k])
            except (TypeError, ValueError):
                die(1, f"'{k}' must be numeric")
    for k in ("stop_loss_pct", "take_profit_pct"):
        if spec.get(k) is not None:
            try:
                v = float(spec[k])
            except (TypeError, ValueError):
                die(1, f"'{k}' must be numeric or null")
            if v <= 0:
                die(1, f"'{k}' must be > 0 when set")
    fng = spec.get("fng")
    if fng is not None:
        if not isinstance(fng, dict) or "entry_max" not in fng:
            die(1, "'fng' block must be an object with at least 'entry_max'")
        for k in ("entry_max", "exit_min"):
            if fng.get(k) is not None:
                try:
                    v = float(fng[k])
                except (TypeError, ValueError):
                    die(1, f"fng.{k} must be numeric")
                if not 0 <= v <= 100:
                    die(1, f"fng.{k} must be in 0..100")
        if fng.get("exit_min") is not None and float(fng["exit_min"]) <= float(fng["entry_max"]):
            die(1, "fng.exit_min must be greater than fng.entry_max")
    return spec


def load_fng(path, df):
    """Return a Series of F&G values aligned to df rows (NaN = unconstrained)."""
    try:
        fng = pd.read_csv(path)
    except Exception as e:
        die(2, f"cannot read fng csv: {e}")
    if not {"date", "value"} <= set(fng.columns):
        die(2, "fng csv must have columns: date,value")
    lookup = dict(zip(fng["date"].astype(str), fng["value"].astype(float)))
    dates = df["timestamp"].astype(str).str[:10]
    return dates.map(lookup)


def apply_fng(target, fng_series, fng_conf):
    """Gate entries by fear, force exits by greed. Deterministic walk."""
    entry_max = float(fng_conf["entry_max"])
    exit_min = fng_conf.get("exit_min")
    exit_min = float(exit_min) if exit_min is not None else None
    holding, out = 0, []
    for t, f in zip(target, fng_series):
        t = int(t)
        constrained = not pd.isna(f)
        if holding == 0:
            ok_entry = (not constrained) or f <= entry_max
            holding = 1 if (t == 1 and ok_entry) else 0
        else:
            greed_exit = constrained and exit_min is not None and f >= exit_min
            holding = 0 if (t == 0 or greed_exit) else 1
        out.append(holding)
    return pd.Series(out, index=target.index)


def load_csv(path):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        die(2, f"cannot read csv: {e}")
    need = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = need - set(df.columns)
    if missing:
        die(2, f"csv missing columns: {sorted(missing)}")
    df = df.sort_values("timestamp").reset_index(drop=True)
    if df[["open", "high", "low", "close"]].isna().any().any():
        die(2, "csv contains NaN prices")
    return df


def warmup_bars(spec):
    p = spec["params"]
    tpl = spec["template"]
    if tpl == "sma_cross":
        return int(p["slow"])
    if tpl == "rsi_meanrev":
        return int(p["period"]) * 3
    if tpl == "donchian_breakout":
        return max(int(p["entry_n"]), int(p["exit_n"])) + 1
    if tpl == "macd_trend":
        return int(p["slow"]) + int(p["signal"])
    return 50


def max_drawdown_pct(equity):
    peak = equity.cummax()
    dd = (equity - peak) / peak
    return round(float(-dd.min()) * 100, 2)


def target_series(df, spec, fng_series):
    fn, _ = TEMPLATES[spec["template"]]
    target = fn(df, spec["params"])
    if spec.get("fng") is not None:
        target = apply_fng(target, fng_series, spec["fng"])
    return target


def run_backtest(df, spec, fng_series):
    target = target_series(df, spec, fng_series)
    fee = float(spec.get("fee_pct", 0.04)) / 100
    slip = float(spec.get("slippage_pct", 0.05)) / 100
    cost = fee + slip
    frac = float(spec.get("position_fraction", 1.0))
    sl = spec.get("stop_loss_pct")
    tp = spec.get("take_profit_pct")
    sl = float(sl) / 100 if sl is not None else None
    tp = float(tp) / 100 if tp is not None else None

    cash, units, entry_price = 1.0, 0.0, None
    stopped_this_trade = False
    trades, equity_curve = [], []

    def equity_at(price):
        return cash + units * price

    for i in range(len(df)):
        o, h, l, c = (float(df[k].iloc[i]) for k in ("open", "high", "low", "close"))
        desired = int(target.iloc[i - 1]) if i > 0 else 0

        # execute at this bar's open based on the previous bar's signal
        if units == 0 and desired == 1 and not stopped_this_trade:
            invest = cash * frac
            units = invest * (1 - cost) / o
            cash -= invest
            entry_price = o
        elif units > 0 and desired == 0:
            cash += units * o * (1 - cost)
            trades.append(o / entry_price - 1)
            units, entry_price = 0.0, None
        stopped_this_trade = False

        # intrabar stop-loss / take-profit
        if units > 0 and sl is not None and l <= entry_price * (1 - sl):
            px = entry_price * (1 - sl)
            cash += units * px * (1 - cost)
            trades.append(px / entry_price - 1)
            units, entry_price = 0.0, None
            stopped_this_trade = True  # avoid instant re-entry from a stale signal
        elif units > 0 and tp is not None and h >= entry_price * (1 + tp):
            px = entry_price * (1 + tp)
            cash += units * px * (1 - cost)
            trades.append(px / entry_price - 1)
            units, entry_price = 0.0, None
            stopped_this_trade = True

        equity_curve.append(equity_at(c))

    equity = pd.Series(equity_curve)
    final = float(equity.iloc[-1])
    if units > 0:  # mark open position to market, count its P&L as an open trade
        trades.append(float(df["close"].iloc[-1]) / entry_price - 1)

    # buy & hold benchmark: all-in at first open, valued at closes, exit cost at end
    first_open = float(df["open"].iloc[0])
    bh_units = (1 - cost) / first_open
    bh_equity = bh_units * df["close"].astype(float)
    bh_final = float(bh_equity.iloc[-1]) * (1 - cost)

    ret = round((final - 1) * 100, 2)
    bh_ret = round((bh_final - 1) * 100, 2)
    mdd = max_drawdown_pct(equity)
    bh_mdd = max_drawdown_pct(bh_equity)
    wins = sum(1 for t in trades if t > 0)
    n_round_trips = len(trades)

    edge_pass = ret > bh_ret
    defense_pass = (ret >= bh_ret - 5.0) and (mdd <= bh_mdd - 10.0)

    return {
        "period": {"start": str(df["timestamp"].iloc[0]), "end": str(df["timestamp"].iloc[-1]),
                   "bars": len(df)},
        "strategy": {"return_pct": ret, "mdd_pct": mdd, "trades": n_round_trips,
                     "win_rate_pct": round(wins / n_round_trips * 100, 1) if n_round_trips else None,
                     "cost_per_side_pct": round(cost * 100, 3)},
        "buy_and_hold": {"return_pct": bh_ret, "mdd_pct": bh_mdd},
        "verdict": "PASS" if (edge_pass or defense_pass) else "FAIL",
        "verdict_rule": {"edge_pass": edge_pass, "defense_pass": defense_pass,
                         "rule": "PASS if return > buy&hold, or return within 5%p of buy&hold "
                                 "with MDD at least 10%p smaller"},
        "spec_echo": spec,
    }


def run_signal(df, spec, fng_series):
    target = target_series(df, spec, fng_series)
    last = df.iloc[-1]
    out = {
        "timestamp": str(last["timestamp"]),
        "close": float(last["close"]),
        "target_position": int(target.iloc[-1]),
    }
    if spec.get("fng") is not None:
        f = fng_series.iloc[-1]
        out["fng_value"] = None if pd.isna(f) else float(f)
        out["fng_rule"] = spec["fng"]
    if spec.get("stop_loss_pct") is not None:
        out["stop_loss_pct"] = float(spec["stop_loss_pct"])
    if spec.get("take_profit_pct") is not None:
        out["take_profit_pct"] = float(spec["take_profit_pct"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--fng", help="fear & greed CSV from fetch_fng.py")
    ap.add_argument("--mode", choices=["backtest", "signal"], default="backtest")
    args = ap.parse_args()

    spec = load_spec(args.spec)
    df = load_csv(args.csv)
    need = warmup_bars(spec) + 30
    if len(df) < need:
        die(2, f"not enough candles: have {len(df)}, need >= {need} for this spec")
    fng_series = None
    if spec.get("fng") is not None:
        if not args.fng:
            die(1, "spec has a 'fng' block: pass --fng <csv from fetch_fng.py>")
        fng_series = load_fng(args.fng, df)
        if fng_series.notna().sum() == 0:
            die(2, "fng csv covers none of the candle dates")

    result = (run_backtest(df, spec, fng_series) if args.mode == "backtest"
              else run_signal(df, spec, fng_series))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
