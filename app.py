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

# 2. CSS CUSTOM UNTUK TAMPILAN MEWAH
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
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 20px;
        backdrop-filter: blur(15px);
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

# 3. SIDEBAR: PROFIL & KONTROL
with st.sidebar:
    st.markdown(f"""
    <div class="profile-card">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" width="70">
        <p style='margin-top:10px; font-weight:bold; font-size:18px; color:white;'>M Restu Ramadhan Arrahma</p>
        <p style='color:#00DBDE; font-size:14px;'>NIM: 06111282429064</p>
        <p style='background:#FC00FF; color:white; font-size:10px; border-radius:10px; padding:2px 10px; display:inline-block;'>DEVELOPER</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("🎨 Kustomisasi")
    theme_color = st.selectbox("Pilih Palet Warna", ["Turbo", "Viridis", "Magma", "Hot", "Electric"])
    
    st.markdown("---")
    st.subheader("🎯 Fokus Analisis")
    mode_view = st.radio("Pilih Mode Tampilan:", ["Global Insight", "Detail Per Siswa"])
    
    st.divider()
    st.caption("© 2024 EduAnalytics Pro System")

# 4. LOAD DATA
@st.cache_data
def load_data():
    # List file yang mungkin ada
    files = ["data.xlsx - Sheet1.csv", "data.xlsx", "data.csv"]
    for f in files:
        try:
            if f.endswith('.csv'):
                return pd.read_csv(f)
            else:
                return pd.read_excel(f)
        except:
            continue
    return None

df = load_data()

# 5. LOGIKA UTAMA
if df is not None:
    # Identifikasi kolom soal secara otomatis
    soal_cols = [col for col in df.columns if "soal" in col.lower()]
    df['Skor_Total'] = df[soal_cols].sum(axis=1)
    df['Siswa_ID'] = [f"Siswa {i+1}" for i in range(len(df))]

    # Perhitungan Segmentasi AI (K-Means)
    n_clusters = min(3, len(df))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['Cluster_ID'] = kmeans.fit_predict(df[soal_cols])
    
    # Mengurutkan label cluster berdasarkan rata-rata skor
    avg_per_cluster = df.groupby('Cluster_ID')['Skor_Total'].mean().sort_values().index
    labels_names = ["Perlu Perhatian", "Potensial", "Sangat Baik"]
    cluster_mapping = {cluster_idx: labels_names[i] for i, cluster_idx in enumerate(avg_per_cluster)}
    df['Kategori'] = df['Cluster_ID'].map(cluster_mapping)

    st.markdown('<p class="main-title">🚀 EDU-PERFORMANCE ANALYTICS</p>', unsafe_allow_html=True)

    if mode_view == "Global Insight":
        # --- ROW 1: KPI ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 Total Siswa", f"{len(df)}")
        c2.metric("📊 Rata-rata Skor", f"{df['Skor_Total'].mean():.1f}")
        c3.metric("🏆 Skor Tertinggi", int(df['Skor_Total'].max()))
        c4.metric("⚠️ Skor Terendah", int(df['Skor_Total'].min()))

        # --- ROW 2: TABS ---
        t1, t2, t3, t4 = st.tabs(["📊 Analisis Soal", "🤖 Segmentasi AI", "🔍 Statistik Lanjut", "📋 Database"])

        with t1:
            st.subheader("📈 Skor Rata-rata per Butir Soal")
            avg_soal = df[soal_cols].mean().reset_index()
            avg_soal.columns = ['Soal', 'Nilai']
            fig_bar = px.bar(avg_soal, x='Soal', y='Nilai', color='Nilai', 
                             color_continuous_scale=theme_color, text_auto='.2f')
            st.plotly_chart(fig_bar, use_container_width=True)

        with t2:
            st.subheader("🤖 Pengelompokkan Kemampuan Siswa")
            col_a, col_b = st.columns()
            with col_a:
                fig_pie = px.pie(df, names='Kategori', hole=0.5, 
                                 color_discrete_map={"Sangat Baik":"#00DBDE", "Potensial":"#FC00FF", "Perlu Perhatian":"#FF4B4B"})
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_b:
                fig_scatter = px.scatter(df, x='Siswa_ID', y='Skor_Total', color='Kategori', 
                                         size='Skor_Total', color_discrete_map={"Sangat Baik":"#00DBDE", "Potensial":"#FC00FF", "Perlu Perhatian":"#FF4B4B"})
                st.plotly_chart(fig_scatter, use_container_width=True)

        with t3:
            col_l, col_r = st.columns(2)
            with col_l:
                st.subheader("🔗 Korelasi Antar Soal")
                corr = df[soal_cols].corr()
                fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r')
                st.plotly_chart(fig_corr, use_container_width=True)
            
            with col_r:
                st.subheader("🎯 Regresi: Faktor Penentu Skor")
                # Analisis Regresi Linear
                model = LinearRegression().fit(df[soal_cols], df['Skor_Total'])
                importance = pd.DataFrame({'Soal': soal_cols, 'Pengaruh': model.coef_}).sort_values('Pengaruh')
                fig_reg = px.bar(importance, x='Pengaruh', y='Soal', orientation='h', color='Pengaruh', color_continuous_scale='Viridis')
                st.plotly_chart(fig_reg, use_container_width=True)

        with t4:
            st.subheader("📑 Data Mentah")
            st.dataframe(df, use_container_width=True)

    else:
        # --- VIEW: DETAIL PER SISWA ---
        st.subheader("🎯 Profiling Mandiri")
        selected_student = st.selectbox("Pilih Siswa:", df['Siswa_ID'].unique())
        student_data = df[df['Siswa_ID'] == selected_student]
        
        cs1, cs2 = st.columns()
        with cs1:
            st.markdown(f"### Segmen: **{student_data['Kategori'].values}**")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=student_data['Skor_Total'].values,
                gauge={'axis': {'range': [None, len(soal_cols)*4]}, 'bar': {'color': "#00DBDE"}}
            ))
            fig_gauge.update_layout(height=350)
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with cs2:
            st.markdown("### Pola Jawaban")
            y_vals = student_data[soal_cols].values.flatten()
            fig_line = px.line(x=soal_cols, y=y_vals, markers=True)
            fig_line.update_traces(line_color='#FC00FF', fill='toself')
            st.plotly_chart(fig_line, use_container_width=True)

else:
    st.error("❌ File data tidak ditemukan! Pastikan file 'data.xlsx' atau CSV Anda sudah diunggah.")
