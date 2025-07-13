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
        font-family: 'Arial', sans-serif;
    }
    .main {
        background-color: #fffdf7;
    }
    h1 {
        color: #d2691e;
        text-align: center;
        font-size: 36px;
        margin-bottom: 20px;
    }
    .stButton > button {
        background-color: #ffb347;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .stDownloadButton > button {
        background-color: #20c997;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

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
    profit_C = st.number_input("Keuntungan Kue Cokelat (Rp)", value=6000)
    flour_C = st.number_input("Tepung untuk Cokelat (gr)", value=200)
    labor_C = st.number_input("Jam kerja Kue Cokelat", value=2)

with col2:
    profit_K = st.number_input("Keuntungan Kue Keju (Rp)", value=8000)
    flour_K = st.number_input("Tepung untuk Keju (gr)", value=300)
    labor_K = st.number_input("Jam kerja Kue Keju", value=1)

# batasan
st.subheader("⛔ Batasan Sumber Daya")
total_flour = st.slider("Total Tepung (gr)", min_value=1000, max_value=10000, value=6000, step=100)
total_labor = st.slider("Total Jam Kerja (jam)", min_value=10, max_value=100, value=40, step=1)

# Fungsi untuk download data sebagai JSON
def download_json(data, filename="hasil.json"):
    json_str = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}" style="display:inline-block;margin-top:10px;font-weight:bold;">📥 Download Hasil sebagai JSON</a>'
    return href

# Solve using linprog
c = [-profit_C, -profit_K]  # Max profit -> Minimize negative
A = [
    [flour_C, flour_K],
    [labor_C, labor_K]
]
b = [total_flour, total_labor]

res = linprog(c, A_ub=A, b_ub=b, method='highs')

if res.success:
    x_cokelat, x_keju = res.x
    total_profit = -res.fun

    st.success("✅ Solusi Optimal Ditemukan!")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Jumlah Kue Cokelat", f"{x_cokelat:.2f} unit")
        st.metric("Jumlah Kue Keju", f"{x_keju:.2f} unit")
    with col4:
        st.metric("💰 Total Keuntungan Maksimal", f"Rp {total_profit:,.0f}")

    # Tabel ringkasan
    hasil = pd.DataFrame({
        "Produk": ["Kue Cokelat", "Kue Keju"],
        "Jumlah Optimal": [x_cokelat, x_keju],
        "Keuntungan per Unit": [profit_C, profit_K],
        "Total Keuntungan": [x_cokelat*profit_C, x_keju*profit_K]
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
    y1 = (total_flour - flour_C * x) / flour_K
    y2 = (total_labor - labor_C * x) / labor_K

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
        1. Fungsi tujuan: `Max Z = {profit_C}C + {profit_K}K`
        2. Batasan:
            - `{flour_C}C + {flour_K}K <= {total_flour}` (Tepung)
            - `{labor_C}C + {labor_K}K <= {total_labor}` (Jam kerja)
        3. Diubah ke bentuk matriks dan diselesaikan dengan metode *Simplex*
        4. Hasil berupa kombinasi optimal dan nilai maksimum fungsi tujuan
        """)

else:
    st.error("❌ Tidak ditemukan solusi feasible. Coba ubah batasan atau input.")
