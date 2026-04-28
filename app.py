import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AI Trading Journal",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("📊 AI Trading Journal – Binance")
st.caption("Auto data dari Binance • 30 hari terakhir")

# =====================
# 🔐 AUTO LOGIN
# =====================
try:
    api_key = st.secrets["BINANCE_API_KEY"]
    secret = st.secrets["BINANCE_SECRET"]
    st.success("✅ Auto Login Aktif")
except:
    api_key = st.text_input("API Key")
    secret = st.text_input("Secret Key", type="password")

if api_key and secret:

    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': secret,
        'enableRateLimit': True
    })

    futures = ccxt.binance({
        'apiKey': api_key,
        'secret': secret,
        'options': {'defaultType': 'future'}
    })

    # =====================
    # 💰 SALDO
    # =====================
    spot = exchange.fetch_balance()
    fut = futures.fetch_balance()

    spot_usdt = spot['total'].get('USDT', 0)
    fut_usdt = fut['total'].get('USDT', 0)
    total_balance = spot_usdt + fut_usdt

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total", round(total_balance, 2))
    col2.metric("Spot", round(spot_usdt, 2))
    col3.metric("Futures", round(fut_usdt, 2))

    # =====================
    # 📅 RANGE
    # =====================
    since = exchange.parse8601((datetime.utcnow() - timedelta(days=30)).isoformat())

    # =====================
    # 🧠 AUTO DETECT AMAN
    # =====================
    symbols = set()
    all_trades = []

    try:
        # coba ambil default pair dulu
        trades = exchange.fetch_my_trades("BTC/USDT", since=since)
        for t in trades:
            symbols.add(t['symbol'])
            all_trades.append(t)
    except:
        pass

    # fallback scan pair
    if not all_trades:
        markets = exchange.load_markets()
        for symbol in markets:
            if "/USDT" in symbol:
                try:
                    t = exchange.fetch_my_trades(symbol, since=since)
                    if t:
                        symbols.add(symbol)
                        all_trades += t
                except:
                    pass

    df = pd.DataFrame(all_trades)

    if not df.empty:

        df['profit'] = df.apply(
            lambda row: row['cost'] if row['side'] == 'sell' else -row['cost'],
            axis=1
        )

        df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values('time')

        wins = df[df['profit'] > 0]
        losses = df[df['profit'] < 0]

        winrate = len(wins) / len(df) * 100 if len(df) > 0 else 0
        avg_win = wins['profit'].mean() if not wins.empty else 0
        avg_loss = losses['profit'].mean() if not losses.empty else 0

        rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        profit_factor = abs(wins['profit'].sum() / losses['profit'].sum()) if not losses.empty else 0

        total_profit = df['profit'].sum()

        # =====================
        # 📊 DASHBOARD
        # =====================
        st.subheader("📊 Statistik")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Winrate", f"{winrate:.2f}%")
        c2.metric("RR", f"{rr:.2f}")
        c3.metric("PF", f"{profit_factor:.2f}")
        c4.metric("Trades", len(df))

        # =====================
        # ⚠️ LOSS STREAK
        # =====================
        streak = 0
        max_streak = 0

        for p in df['profit']:
            if p < 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0

        st.metric("📉 Profit 30 Hari", round(total_profit, 2))
        st.write(f"Loss Streak: {max_streak}")

        # =====================
        # 📈 CHART
        # =====================
        st.subheader("📈 Equity Curve")
        st.line_chart(df['profit'].cumsum())

        # =====================
        # 🤖 AI ANALYSIS
        # =====================
        st.subheader("🤖 AI Analysis")

        score = 0
        score += 25 if winrate > 60 else 10
        score += 25 if rr > 1 else 10
        score += 25 if profit_factor > 1 else 10
        score += 25 if max_streak < 5 else 10

        st.metric("AI Score", score)

        if score >= 75:
            st.success("🟢 Sehat")
        elif score >= 50:
            st.warning("🟡 Hati-hati")
        else:
            st.error("🔴 Stop Trading")

    else:
        st.warning("Tidak ada data trading 30 hari terakhir")

    # =====================
    # 📈 FUTURES
    # =====================
    try:
        income = futures.fetch_income_history(limit=100)
        df_fut = pd.DataFrame(income)

        df_fut['income'] = df_fut['income'].astype(float)

        realized = df_fut[df_fut['incomeType'] == 'REALIZED_PNL']['income'].sum()
        funding = df_fut[df_fut['incomeType'] == 'FUNDING_FEE']['income'].sum()

        st.subheader("📈 Futures")
        st.write(f"PnL: {round(realized,2)}")
        st.write(f"Funding: {round(funding,2)}")
        st.write(f"Net: {round(realized + funding,2)}")

    except:
        st.warning("Data futures tidak tersedia")
