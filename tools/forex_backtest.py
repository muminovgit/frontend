"""Oddiy EMA kesishuv + RSI filtri backtest. Faqat ta'lim uchun.
Ishlatish: python tools/forex_backtest.py data.csv
CSV ustunlari: time,open,high,low,close
"""
import sys
import pandas as pd


def rsi(s, n=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def atr(df, n=14):
    pc = df.close.shift()
    tr = pd.concat([df.high - df.low, (df.high - pc).abs(), (df.low - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def backtest(df, fast=20, slow=50, sl_atr=1.5, rr=2.0):
    df = df.copy()
    df["ef"] = df.close.ewm(span=fast, adjust=False).mean()
    df["es"] = df.close.ewm(span=slow, adjust=False).mean()
    df["rsi"] = rsi(df.close)
    df["atr"] = atr(df)
    trades, pos = [], None
    for i in range(slow + 1, len(df)):
        r, p = df.iloc[i], df.iloc[i - 1]
        if pos:
            hit_sl = r.low <= pos["sl"] if pos["dir"] == 1 else r.high >= pos["sl"]
            hit_tp = r.high >= pos["tp"] if pos["dir"] == 1 else r.low <= pos["tp"]
            if hit_sl or hit_tp:  # konservativ: ikkalasi bo'lsa SL
                trades.append(-1.0 if hit_sl else rr)
                pos = None
            continue
        if p.ef <= p.es and r.ef > r.es and r.rsi > 50:
            d = 1
        elif p.ef >= p.es and r.ef < r.es and r.rsi < 50:
            d = -1
        else:
            continue
        risk = sl_atr * r.atr
        pos = {"dir": d, "sl": r.close - d * risk, "tp": r.close + d * risk * rr}
    return trades  # R birliklarida


if __name__ == "__main__":
    df = pd.read_csv(sys.argv[1])
    t = pd.Series(backtest(df))
    if t.empty:
        sys.exit("Savdo topilmadi")
    print(f"Savdolar: {len(t)} | Win rate: {(t > 0).mean():.1%} | Jami R: {t.sum():.1f} | O'rtacha R: {t.mean():.2f}")
