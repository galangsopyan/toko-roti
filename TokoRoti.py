import streamlit as st
from scipy.optimize import linprog
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Optimasi Produksi Kue - SweetBite", layout="centered")
st.title("🎂 Optimasi Produksi Kue - Toko Roti SweetBite")

st.markdown("Aplikasi ini membantu menentukan kombinasi produksi **Kue Cokelat** dan **Kue Keju** yang memberikan keuntungan maksimal berdasarkan keterbatasan sumber daya.")

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
total_flour = st.number_input("Total Tepung (gr)", value=6000)
total_labor = st.number_input("Total Jam Kerja (jam)", value=40)

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
    st.write(f"Jumlah **Kue Cokelat**: `{x_cokelat:.2f}` unit")
    st.write(f"Jumlah **Kue Keju**: `{x_keju:.2f}` unit")
    st.write(f"💰 **Total Keuntungan Maksimal**: `Rp {total_profit:,.0f}`")

    # Visualisasi feasible region
    st.subheader("📊 Visualisasi Area Feasible dan Solusi Optimal")
    x = np.linspace(0, 50, 400)
    y1 = (total_flour - flour_C * x) / flour_K
    y2 = (total_labor - labor_C * x) / labor_K

    fig, ax = plt.subplots()
    ax.plot(x, y1, label='Batas Tepung')
    ax.plot(x, y2, label='Batas Jam Kerja')
    ax.fill_between(x, np.minimum(y1, y2), 0, where=(y1>0)&(y2>0), alpha=0.3)

    ax.plot(x_cokelat, x_keju, 'ro', label='Solusi Optimal')
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Kue Cokelat")
    ax.set_ylabel("Kue Keju")
    ax.legend()
    st.pyplot(fig)

else:
    st.error("❌ Tidak ditemukan solusi feasible. Coba ubah batasan atau input.")
