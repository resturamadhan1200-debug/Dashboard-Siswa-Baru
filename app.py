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

# 2. CSS CUSTOM (Tetap sama seperti kode Anda)
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

# 3. SIDEBAR
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
    theme_color = st.selectbox("Pilih Palet Warna", ["Turbo", "Viridis", "Magma", "Hot", "Electric"])
    mode_view = st.radio("Pilih Mode Tampilan:", ["Global Insight", "Detail Per Siswa"])

# 4. LOAD DATA (Menggunakan CSV sesuai file yang Anda berikan sebelumnya)
@st.cache_data
def load_data():
    try:
        # Ganti ke .csv jika file Anda CSV, atau tetap .xlsx
        df = pd.read_csv("data.xlsx - Sheet1.csv") 
        return df
    except:
        try:
            df = pd.read_excel("data.xlsx")
            return df
        except:
            return None

df = load_data()

# 5. LOGIKA DASHBOARD
if df is not None:
    soal_cols = [col for col in df.columns if "soal" in col.lower()]
    df['Skor_Total'] = df[soal_cols].sum(axis=1)
    df['Siswa_ID'] = [f"Siswa {i+1}" for i in range(len(df))]

    st.markdown('<p class="main-title">🚀 EDU-PERFORMANCE ANALYTICS</p>', unsafe_allow_html=True)

    if mode_view == "Global Insight":
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 Partisipan", f"{len(df)}")
        c2.metric("📊 Rata-rata", f"{df['Skor_Total'].mean():.1f}")
        c3.metric("🏆 Tertinggi", int(df['Skor_Total'].max()))
        c4.metric("⚠️ Terendah", int(df['Skor_Total'].min()))

        # Penambahan Tab Statistik Lanjut
        t1, t2, t4, t3 = st.tabs(["📊 Analisis Soal", "🤖 Segmentasi", "🔍 Statistik Lanjut", "📋 Database"])

        with t1:
            st.subheader("📈 Skor Rata-rata per Indikator")
            avg_soal = df[soal_cols].mean().reset_index()
            avg_soal.columns = ['Soal', 'Nilai']
            fig_bar = px.bar(avg_soal, x='Soal', y='Nilai', color='Nilai', color_continuous_scale=theme_color)
            st.plotly_chart(fig_bar, use_container_width=True)

        with t2:
            st.subheader("🤖 Segmentasi Siswa (AI Clustering)")
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(df[soal_cols])
            
            # Memberikan label nama pada cluster berdasarkan rata-rata skor
            df['Cluster_ID'] = clusters
            cluster_means = df.groupby('Cluster_ID')['Skor_Total'].mean().sort_values()
            cluster_map = {
                cluster_means.index: "Low Performance",
                cluster_means.index: "Average",
                cluster_means.index: "High Performance"
            }
            df['Segmentasi'] = df['Cluster_ID'].map(cluster_map)

            col_a, col_b = st.columns()
            with col_a:
                fig_pie = px.pie(df, names='Segmentasi', hole=0.5, 
                                 color_discrete_map={"High Performance":"cyan", "Average":"purple", "Low Performance":"red"})
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_b:
                fig_scatter = px.scatter(df, x='Siswa_ID', y='Skor_Total', color='Segmentasi', 
                                         size='Skor_Total', hover_name='Siswa_ID')
                st.plotly_chart(fig_scatter, use_container_width=True)

        with t4:
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader("🔗 Korelasi Antar Indikator")
                corr_matrix = df[soal_cols].corr()
                fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                                     color_continuous_scale='RdBu_r', title="Heatmap Hubungan Soal")
                st.plotly_chart(fig_corr, use_container_width=True)
                st.info("💡 Semakin mendekati 1, kedua soal memiliki hubungan searah yang sangat kuat.")

            with col_right:
                st.subheader("🎯 Regresi: Faktor Pendorong Skor")
                # X = Soal-soal, y = Skor Total
                X = df[soal_cols]
                y = df['Skor_Total']
                model = LinearRegression()
                model.fit(X, y)
                
                # Mendapatkan koefisien (pengaruh tiap soal)
                importance = pd.DataFrame({
                    'Indikator': soal_cols,
                    'Pengaruh': model.coef_
                }).sort_values(by='Pengaruh', ascending=True)
                
                fig_reg = px.bar(importance, x='Pengaruh', y='Indikator', orientation='h',
                                 title="Indikator Paling Berpengaruh terhadap Skor Total",
                                 color='Pengaruh', color_continuous_scale='Viridis')
                st.plotly_chart(fig_reg, use_container_width=True)
                st.success("💡 Indikator dengan 'Pengaruh' tertinggi adalah faktor kunci keberhasilan siswa.")

        with t3:
            st.dataframe(df, use_container_width=True)

    else:
        # VIEW DETAIL PER SISWA (Tetap sama)
        selected_student = st.selectbox("Pilih Siswa:", df['Siswa_ID'].unique())
        student_data = df[df['Siswa_ID'] == selected_student]
        
        c_s1, c_s2 = st.columns()
        with c_s1:
            st.metric("Status Segmentasi", student_data['Segmentasi'].values)
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = student_data['Skor_Total'].values,
                gauge = {'axis': {'range': [0, len(soal_cols)*4]}, 'bar': {'color': "#FC00FF"}}
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)
        with c_s2:
            vals = student_data[soal_cols].values.flatten()
            fig_line = px.line(x=soal_cols, y=vals, markers=True, title=f"Pola Kompetensi {selected_student}")
            st.plotly_chart(fig_line, use_container_width=True)
else:
    st.error("❌ Data tidak ditemukan!")
