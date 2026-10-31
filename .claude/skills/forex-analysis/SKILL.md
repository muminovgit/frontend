---
name: forex-analysis
description: Forex (EUR/USD, GBP/USD, XAU/USD va h.k.) uchun texnik tahlil, strategiya g'oyasi, backtest va risk hisobi. Foydalanuvchi forex, signal, trade, backtest haqida so'raganda ishlating.
---

# Forex tahlil skill'i

## Qoidalar
- Hech qachon kafolatli signal yoki "100% foyda" va'da qilmang.
- Har bir g'oyaga entry, stop-loss, take-profit va risk (hisobning 1-2%) kiriting.
- Har doim "bu moliyaviy maslahat emas, avval demo hisobda sinang" deb eslatib o'ting.
- Real vaqt narxi yo'q bo'lsa, buni ochiq ayting. Foydalanuvchi bergan CSV yoki ma'lumotdan foydalaning.

## Tahlil tartibi
1. Yo'nalish: yuqori timeframe'da (H4/D1) trend (EMA 50/200).
2. Momentum: RSI(14), MACD.
3. Daraja: support/resistance, ATR(14) asosida stop masofasi.
4. Signal formati:
   - Juftlik / Timeframe
   - Yo'nalish (Buy/Sell/Kutish)
   - Entry, SL, TP, Risk:Reward
   - Sabab (2-3 gap) va bekor bo'lish sharti

## Backtest
`tools/forex_backtest.py` dan foydalaning:
`python tools/forex_backtest.py data.csv`
CSV ustunlari: `time,open,high,low,close`.

## Pozitsiya hajmi
lot = (balans * risk%) / (SL pips * pip qiymati)
