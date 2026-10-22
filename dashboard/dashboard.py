import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")
sns.set_theme(style="whitegrid")

BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']
URUTAN_KATEGORI = ['Sangat baik (0-35)', 'Baik (35-75)', 'Polusi ringan (75-115)',
                   'Polusi sedang (115-150)', 'Polusi berat (150-250)', 'Polusi sangat berat (>250)']
WARNA_KATEGORI = ['#2E86AB', '#7FB7BE', '#F2C14E', '#F28F3B', '#C0392B', '#6B1D1D']


@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_data.csv")
    return pd.read_csv(path, parse_dates=["date"])


df = load_data()

# ---------- Sidebar: filter ----------
st.sidebar.header("Filter Data")
semua_stasiun = sorted(df["station"].unique())
stasiun = st.sidebar.multiselect("Stasiun", semua_stasiun, default=semua_stasiun)
tgl_min, tgl_maks = df["date"].min().date(), df["date"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", value=(tgl_min, tgl_maks), min_value=tgl_min, max_value=tgl_maks)

if len(rentang) != 2 or not stasiun:
    st.warning("Pilih minimal satu stasiun dan rentang tanggal (tanggal awal dan akhir).")
    st.stop()

mask = df["station"].isin(stasiun) & df["date"].between(pd.Timestamp(rentang[0]), pd.Timestamp(rentang[1]))
data = df[mask]
if data.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# ---------- Header & metrik ----------
st.title("Dashboard Kualitas Udara Beijing (PM2.5)")
st.caption("Sumber: Air Quality Dataset (PRSA), 12 stasiun, Maret 2013 - Februari 2017. Data harian rata-rata per stasiun.")

per_stasiun = data.groupby("station")["PM2.5"].mean().sort_values(ascending=False)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rata-rata PM2.5", f"{data['PM2.5'].mean():.1f} µg/m³")
c2.metric("Hari berpolusi (>75 µg/m³)", f"{(data['PM2.5'] > 75).mean() * 100:.1f}%")
c3.metric("Stasiun tertinggi", per_stasiun.index[0], f"{per_stasiun.iloc[0]:.1f} µg/m³", delta_color="off")
c4.metric("Stasiun terendah", per_stasiun.index[-1], f"{per_stasiun.iloc[-1]:.1f} µg/m³", delta_color="off")

# ---------- Pertanyaan 1 ----------
st.subheader("1. Rata-rata PM2.5 per Stasiun")
warna = ['#C0392B' if i == 0 else '#2E86AB' if i == len(per_stasiun) - 1 else '#B8BEC6' for i in range(len(per_stasiun))]
fig, ax = plt.subplots(figsize=(9, max(2.5, 0.5 * len(per_stasiun) + 1)))
ax.barh(per_stasiun.index, per_stasiun.values, color=warna)
ax.invert_yaxis()
for i, v in enumerate(per_stasiun.values):
    ax.text(v + 0.8, i, f"{v:.1f}", va="center", fontsize=9)
ax.axvline(35, color="#555555", linestyle="--", linewidth=1)
ax.text(35.8, -0.45, "Batas tahunan China Kelas II (35 µg/m³)", fontsize=8, color="#555555")
ax.set_xlim(0, max(100, per_stasiun.max() * 1.15))
ax.set_xlabel("Rata-rata PM2.5 (µg/m³)")
ax.set_ylabel("")
sns.despine(left=True)
st.pyplot(fig)
if len(per_stasiun) > 1:
    selisih = (per_stasiun.iloc[0] - per_stasiun.iloc[-1]) / per_stasiun.iloc[-1] * 100
    st.info(f"{per_stasiun.index[0]} lebih tinggi sekitar {selisih:.1f}% dibanding {per_stasiun.index[-1]} pada filter ini.")

# ---------- Pertanyaan 2 ----------
st.subheader("2. Pola Bulanan PM2.5")
bulanan = data.groupby(["year", "month"])["PM2.5"].mean().reset_index()
rata_bulan = data.groupby("month")["PM2.5"].mean().reindex(range(1, 13))
fig, ax = plt.subplots(figsize=(10, 4.5))
for y, g in bulanan.groupby("year"):
    ax.plot(g["month"], g["PM2.5"], color="#B8BEC6", linewidth=1, alpha=0.9)
ax.plot(rata_bulan.index, rata_bulan.values, color="#1F3A5F", linewidth=3, marker="o", label="Rata-rata semua tahun terpilih")
ax.plot([], [], color="#B8BEC6", label="Tiap tahun")
ax.set_xticks(range(1, 13)); ax.set_xticklabels(BULAN)
ax.set_ylim(0, None)
ax.set_xlabel("Bulan"); ax.set_ylabel("Rata-rata PM2.5 (µg/m³)")
ax.legend(frameon=False)
sns.despine()
st.pyplot(fig)
st.caption("Catatan: 2013 hanya mulai Maret dan 2017 hanya Januari-Februari. Untuk pola musiman yang adil, pilih rentang 1 Jan 2014 - 31 Des 2016.")

# ---------- Analisis lanjutan ----------
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("3. Proporsi Hari menurut Kategori")
    kat = data["kategori"].value_counts(normalize=True).reindex(URUTAN_KATEGORI).fillna(0) * 100
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(kat.index, kat.values, color=WARNA_KATEGORI)
    ax.invert_yaxis()
    for i, v in enumerate(kat.values):
        ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)
    ax.set_xlim(0, max(40, kat.max() * 1.2))
    ax.set_xlabel("Persentase hari (%)"); ax.set_ylabel("")
    sns.despine(left=True)
    st.pyplot(fig)
with col_b:
    st.subheader("4. PM2.5 menurut Kecepatan Angin")
    kelas = pd.cut(data["WSPM"], bins=[-0.1, 1, 2, 4, 20], labels=["<=1", "1-2", "2-4", ">4"])
    angin = data.groupby(kelas, observed=True)["PM2.5"].mean()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(angin.index.astype(str), angin.values, color="#2E86AB")
    for i, v in enumerate(angin.values):
        ax.text(i, v + 1, f"{v:.1f}", ha="center", fontsize=9)
    ax.set_xlabel("Kecepatan angin harian (m/s)"); ax.set_ylabel("Rata-rata PM2.5 (µg/m³)")
    sns.despine()
    st.pyplot(fig)

with st.expander("Lihat data"):
    st.dataframe(data.sort_values(["date", "station"]).reset_index(drop=True))
