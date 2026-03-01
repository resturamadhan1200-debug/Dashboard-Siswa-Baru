import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="EduAnalytics Pro | M Restu",
    page_icon="💎",
    layout="wide"
)

# 2. CSS CUSTOM
st.markdown("""
    <style>
    .main-title {
        font-size: 40px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00DBDE, #FC00FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(20, 20, 30, 0.95);
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 20px;
    }
    .profile-card {
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0));
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR
with st.sidebar:
    st.markdown(f"""
    <div class="profile-card">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="70">
        <p style='margin-top:10px; font-weight:bold; font-size:18px; color:white;'>M Restu Ramadhan Arrahma</p>
        <p style='color:#00DBDE; font-size:14px;'>NIM: 06111282429064</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    theme_color = st.selectbox("Pilih Palet Warna", ["Turbo", "Viridis", "Magma", "Hot", "Electric"])
    mode_view = st.radio("Pilih Mode Tampilan:", ["Global Insight", "Detail Per Siswa"])

# 4. LOAD DATA (Mendukung file Anda)
@st.cache_data
def load_data():
    try:
        # Mencoba membaca file CSV yang Anda unggah
        df = pd.read_csv("data.xlsx - Sheet1.csv")
        return df
    except:
        try:
            df = pd.read_excel("data.xlsx")
            return df
        except:
            return None

df = load_data()

# 5. LOGIKA UTAMA
if df is not None:
    # Identifikasi kolom soal (Soal_1, Soal_2, dst)
    soal_cols = [col for col in df.columns if "soal" in col.lower()]
    df['Skor_Total'] = df[soal_cols].sum(axis=1)
    df['Siswa_ID'] = [f"Siswa {i+1}" for i in range(len(df))]

    # --- SEGMENTASI AI (K-Means) ---
    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['Cluster_ID'] = kmeans.fit_predict(df[soal_cols])
    
    # Labeling Otomatis
    avg_scores = df.groupby('Cluster_ID')['Skor_Total'].mean().sort_values().index
    cat_names = ["Perlu Perhatian", "Potensial", "Sangat Baik"]
    mapping = {cluster_idx: cat_names[i] for i, cluster_idx in enumerate(avg_scores)}
    df['Kategori'] = df['Cluster_ID'].map(mapping)

    st.markdown('<p class="main-title">🚀 EDU-PERFORMANCE ANALYTICS</p>', unsafe_allow_html=True)

    if mode_view == "Global Insight":
        # KPI
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 Total Siswa", len(df))
        c2.metric("📊 Rata-rata Skor", f"{df['Skor_Total'].mean():.1f}")
        c3.metric("🏆 Skor Tertinggi", int(df['Skor_Total'].max()))
        c4.metric("⚠️ Skor Terendah", int(df['Skor_Total'].min()))

        t1, t2, t3, t4 = st.tabs(["📊 Analisis Soal", "🤖 Segmentasi AI", "🔍 Statistik Lanjut", "📋 Database"])

        with t1:
            st.subheader("📈 Rata-rata per Butir Soal")
            avg_soal = df[soal_cols].mean().reset_index()
            avg_soal.columns = ['Soal', 'Nilai']
            st.plotly_chart(px.bar(avg_soal, x='Soal', y='Nilai', color='Nilai', color_continuous_scale=theme_color), use_container_width=True)

        with t2:
            st.subheader("🤖 Segmentasi Kemampuan Siswa")
            col_a, col_b = st.columns(b)
            with col_a:
                fig_pie = px.pie(df, names='Kategori', hole=0.5, color_discrete_map={"Sangat Baik":"#00DBDE", "Potensial":"#FC00FF", "Perlu Perhatian":"#FF4B4B"})
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_b:
                fig_scatter = px.scatter(df, x='Siswa_ID', y='Skor_Total', color='Kategori', size='Skor_Total', color_discrete_map={"Sangat Baik":"#00DBDE", "Potensial":"#FC00FF", "Perlu Perhatian":"#FF4B4B"})
                st.plotly_chart(fig_scatter, use_container_width=True)

        with t3:
            col_l, col_r = st.columns(2)
            with col_l:
                st.subheader("🔗 Korelasi Antar Soal")
                corr = df[soal_cols].corr()
                st.plotly_chart(px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r'), use_container_width=True)
            with col_r:
                st.subheader("🎯 Faktor Penentu (Regresi)")
                model = LinearRegression().fit(df[soal_cols], df['Skor_Total'])
                importance = pd.DataFrame({'Soal': soal_cols, 'Pengaruh': model.coef_}).sort_values('Pengaruh')
                st.plotly_chart(px.bar(importance, x='Pengaruh', y='Soal', orientation='h', color='Pengaruh', color_continuous_scale='Viridis'), use_container_width=True)

        with t4:
            st.subheader("📑 Data Lengkap")
            st.dataframe(df, use_container_width=True)

    else:
        # DETAIL PER SISWA
        st.subheader("🎯 Profiling Individu")
        sel_siswa = st.selectbox("Pilih Siswa:", df['Siswa_ID'].unique())
        s_data = df[df['Siswa_ID'] == sel_siswa]
        
        cs1, cs2 = st.columns()
        with cs1:
            st.markdown(f"### Kategori: **{s_data['Kategori'].values}**")
            fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=s_data['Skor_Total'].values, gauge={'axis': {'range': [None, len(soal_cols)*5]}}))
            st.plotly_chart(fig_gauge, use_container_width=True)
        with cs2:
            st.markdown("### Pola Jawaban")
            y_vals = s_data[soal_cols].values.flatten()
            st.plotly_chart(px.line(x=soal_cols, y=y_vals, markers=True), use_container_width=True)
else:
    st.error("❌ Data tidak ditemukan! Pastikan file CSV/Excel ada di folder yang sama.")

