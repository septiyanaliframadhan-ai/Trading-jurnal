import streamlit as st
import pandas as pd

st.set_page_config(page_title="Trading Journal Manual", layout="wide")

st.title("📊 Trading Journal (Manual)")
st.caption("Input manual • Auto analisa • Tanpa API")

# =====================
# 📥 INPUT TRADING
# =====================
st.subheader("📥 Input Trade")

col1, col2, col3 = st.columns(3)

with col1:
    pair = st.text_input("Pair (contoh: BTC/USDT)")
    entry = st.number_input("Entry Price", min_value=0.0)
    exit_price = st.number_input("Exit Price", min_value=0.0)

with col2:
    size = st.number_input("Lot / Size", min_value=0.0)
    trade_type = st.selectbox("Type", ["Buy", "Sell"])

with col3:
    date = st.date_input("Tanggal")
    notes = st.text_input("Catatan")

# =====================
# 🧮 HITUNG PROFIT
# =====================
def hitung_profit(entry, exit_price, size, trade_type):
    if trade_type == "Buy":
        return (exit_price - entry) * size
    else:
        return (entry - exit_price) * size

# =====================
# 💾 SIMPAN DATA
# =====================
if "data" not in st.session_state:
    st.session_state.data = []

if st.button("➕ Tambah Trade"):
    profit = hitung_profit(entry, exit_price, size, trade_type)

    st.session_state.data.append({
        "Pair": pair,
        "Entry": entry,
        "Exit": exit_price,
        "Size": size,
        "Type": trade_type,
        "Profit": profit,
        "Tanggal": date,
        "Catatan": notes
    })

    st.success("Trade ditambahkan!")

# =====================
# 📊 DATAFRAME
# =====================
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    st.subheader("📋 Riwayat Trading")
    st.dataframe(df, use_container_width=True)

    # =====================
    # 📊 STATISTIK
    # =====================
    wins = df[df["Profit"] > 0]
    losses = df[df["Profit"] < 0]

    winrate = len(wins) / len(df) * 100
    total_profit = df["Profit"].sum()

    avg_win = wins["Profit"].mean() if not wins.empty else 0
    avg_loss = losses["Profit"].mean() if not losses.empty else 0

    rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    profit_factor = abs(wins["Profit"].sum() / losses["Profit"].sum()) if not losses.empty else 0

    st.subheader("📊 Statistik")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Winrate", f"{winrate:.2f}%")
    c2.metric("RR", f"{rr:.2f}")
    c3.metric("PF", f"{profit_factor:.2f}")
    c4.metric("Total Trade", len(df))

    st.metric("💰 Total Profit", round(total_profit, 2))

    # =====================
    # 📈 EQUITY CURVE
    # =====================
    st.subheader("📈 Equity Curve")
    st.line_chart(df["Profit"].cumsum())

    # =====================
    # 📊 PROFIT PER PAIR
    # =====================
    st.subheader("📊 Profit per Pair")
    pair_profit = df.groupby("Pair")["Profit"].sum()
    st.bar_chart(pair_profit)

    # =====================
    # 🤖 AI ANALYSIS
    # =====================
    st.subheader("🤖 AI Analysis")

    score = 0
    score += 25 if winrate > 60 else 10
    score += 25 if rr > 1 else 10
    score += 25 if profit_factor > 1 else 10
    score += 25 if total_profit > 0 else 10

    st.metric("AI Score", score)

    if score >= 75:
        st.success("🟢 Trading kamu bagus, lanjutkan!")
    elif score >= 50:
        st.warning("🟡 Performa sedang, perlu evaluasi")
    else:
        st.error("🔴 Stop dulu, perbaiki strategi")

else:
    st.info("Belum ada data trading")
