import streamlit as st
from scipy.optimize import linprog
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import base64

st.set_page_config(page_title="Optimasi Produksi Kue - SweetBite", layout="centered")

# Custom CSS styling
st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }
    .main {
        background-color: #fffdf7;
    }
    h1 {
        color: #d2691e;
        text-align: center;
        font-size: 40px;
        margin-bottom: 20px;
    }
    .stButton > button {
        background-color: #ffb347;
        color: white;
        font-weight: bold;
    }
    .stDownloadButton > button {
        background-color: #20c997;
        color: white;
        font-weight: bold;
    }
    .logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 300px;
        margin-bottom: 1rem;
</style>
""", unsafe_allow_html=True)
# Tambahkan logo
st.markdown("<img src='https://marketplace.canva.com/EAE_dLvTFF8/1/0/800w/canva-cokelat-sederhana-logo-toko-kue-OLQJvUWFkw0.jpg' class='logo'>", unsafe_allow_html=True)

st.markdown("<h1>🎂 Optimasi Produksi Kue - Toko Roti SweetBite</h1>", unsafe_allow_html=True)

st.markdown("""
<p style='font-size: 18px;'>
Aplikasi ini membantu menentukan kombinasi produksi <strong>Kue Cokelat</strong> dan <strong>Kue Keju</strong> yang memberikan keuntungan maksimal berdasarkan keterbatasan sumber daya.
</p>
""", unsafe_allow_html=True)

# INPUT
st.header("📥 Input Data Produksi")

col1, col2 = st.columns(2)
with col1:
    profit_X = st.number_input("Keuntungan Kue Cokelat (Rp)", value=6000)
    flour_X = st.number_input("Tepung untuk Cokelat (gr)", value=200)
    labor_X = st.number_input("Jam kerja Kue Cokelat", value=2)

with col2:
    profit_Y = st.number_input("Keuntungan Kue Keju (Rp)", value=8000)
    flour_Y = st.number_input("Tepung untuk Keju (gr)", value=300)
    labor_Y = st.number_input("Jam kerja Kue Keju", value=1)

# batasan
st.subheader("⛔ Batasan Sumber Daya")
total_flour = st.slider("Total Tepung (gr)", min_value=1000, max_value=10000, value=6000, step=100)
total_labor = st.slider("Total Jam Kerja (jam)", min_value=10, max_value=100, value=40, step=1)

# Fungsi untuk download data sebagai JSON
def download_json(data, filename="hasil.json"):
    json_str = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}">📥 Download Hasil sebagai JSON</a>'
    return href

# Solve using linprog
c = [-profit_X, -profit_Y]  # Max profit -> Minimize negative
A = [
    [flour_X, flour_Y],
    [labor_X, labor_Y]
]
b = [total_flour, total_labor]

res = linprog(c, A_ub=A, b_ub=b, method='highs')

if res.success:
    x_cokelat, x_keju = res.x
    total_profit = -res.fun

    st.success("✅ Solusi Optimal Ditemukan!")
    st.write(f"Jumlah **Kue Cokelat**: `{x_cokelat:.2f}` unit")
    st.write(f"Jumlah **Kue Keju**: `{x_keju:.2f}` unit")
    st.write(f"💰 **Total Keuntungan Maksimal**: `Rp {total_profit:,.0f}`")

    # Tabel ringkasan
    hasil = pd.DataFrame({
        "Produk": ["Kue Cokelat", "Kue Keju"],
        "Jumlah Optimal": [x_cokelat, x_keju],
        "Keuntungan per Unit": [profit_X, profit_Y],
        "Total Keuntungan": [x_cokelat*profit_X, x_keju*profit_Y]
    })
    st.subheader("📋 Ringkasan Perhitungan")
    st.dataframe(hasil, use_container_width=True)

    # Download hasil
    st.markdown(download_json({
        "Kue Cokelat": round(x_cokelat, 2),
        "Kue Keju": round(x_keju, 2),
        "Total Keuntungan": round(total_profit, 2)
    }), unsafe_allow_html=True)

    # Visualisasi
    st.subheader("📊 Visualisasi Area Feasible dan Solusi Optimal")
    x = np.linspace(0, 50, 400)
    y1 = (total_flour - flour_X * x) / flour_Y
    y2 = (total_labor - labor_X * x) / labor_Y

    fig, ax = plt.subplots()
    ax.plot(x, y1, label='Batas Tepung', color='brown')
    ax.plot(x, y2, label='Batas Jam Kerja', color='orange')
    ax.fill_between(x, np.minimum(y1, y2), 0, where=(y1>0)&(y2>0), color='peachpuff', alpha=0.3)

    ax.plot(x_cokelat, x_keju, 'ro', label='Solusi Optimal')
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Kue Cokelat")
    ax.set_ylabel("Kue Keju")
    ax.legend()
    st.pyplot(fig)

    # Penjelasan
    with st.expander("🔍 Lihat Penjelasan Langkah Linear Programming"):
        st.markdown(f"""
        1. Fungsi tujuan: `Z = {profit_C}X + {profit_K}Y`
        2. Batasan:
            - `{flour_X}X + {flour_Y}Y <= {total_flour}` (Tepung)
            - `{labor_X}X + {labor_Y}Y <= {total_labor}` (Jam kerja)
        3. Diubah ke bentuk matriks dan diselesaikan dengan metode *Simplex*
        4. Hasil berupa kombinasi optimal dan nilai maksimum fungsi tujuan
        """)

else:
    st.error("❌ Tidak ditemukan solusi feasible. Coba ubah batasan atau input.")
