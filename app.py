import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression # Tambahan untuk Regresi

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="EduAnalytics Pro | M Restu",
    page_icon="💎",
    layout="wide"
)

# 2. CSS CUSTOM (Tetap sama)
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
    st.subheader("🎨 Kustomisasi Grafik")
    theme_color = st.selectbox("Pilih Palet Warna", ["Turbo", "Viridis", "Magma", "Hot", "Electric"])
    
    st.markdown("---")
    st.subheader("🎯 Fokus Analisis")
    mode_view = st.radio("Pilih Mode Tampilan:", ["Global Insight", "Detail Per Siswa"])
    
    st.divider()
    st.caption("© 2024 EduAnalytics Pro System")

# 4. LOAD DATA (Support CSV dan Excel)
@st.cache_data
def load_data():
    try:
        # Mencoba membaca file csv atau excel
        df = pd.read_csv("data.xlsx - Sheet1.csv") # Menyesuaikan dengan file yang Anda unggah
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
    st.markdown("<p style='text-align:center; color:grey;'>Analisis Korelasi, Segmentasi, dan Regresi Akademik</p>", unsafe_allow_html=True)

    if mode_view == "Global Insight":
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 Total Partisipan", f"{len(df)} Siswa")
        c2.metric("📊 Rata-rata Kelas", f"{df['Skor_Total'].mean():.1f}")
        c3.metric("🏆 Skor Tertinggi", int(df['Skor_Total'].max()))
        c4.metric("⚠️ Skor Terendah", int(df['Skor_Total'].min()))

        st.write("")

        # Menambahkan Tab baru untuk Statistik Lanjut
        t1, t2, t3, t4 = st.tabs(["📊 Analisis Soal", "🤖 Segmentasi AI", "🔍 Statistik Lanjut", "📋 Spreadsheet"])

        with t1:
            st.subheader("📈 Skor Rata-rata per Item Soal")
            avg_soal = df[soal_cols].mean().reset_index()
            avg_soal.columns = ['Soal', 'Nilai']
            fig_bar = px.bar(avg_soal, x='Soal', y='Nilai', color='Nilai', 
                             color_continuous_scale=theme_color, text_auto='.2f')
            fig_bar.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

        with t2:
            st.subheader("🤖 Segmentasi Siswa (Clustering)")
            # Mengelompokkan siswa jadi 3 level
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            df['Cluster_ID'] = kmeans.fit_predict(df[soal_cols])
            
            # Memberi label berdasarkan rata-rata skor agar Cluster 0,1,2 jadi bermakna
            mapping = df.groupby('Cluster_ID')['Skor_Total'].mean().sort_values().index
            cluster_labels = {mapping: "Perlu Perhatian", mapping: "Potensial", mapping: "Sangat Baik"}
            df['Kategori'] = df['Cluster_ID'].map(cluster_labels)

            cl1, cl2 = st.columns()
            with cl1:
                fig_pie = px.pie(df, names='Kategori', hole=0.5, 
                                 color_discrete_map={"Sangat Baik":"#00DBDE", "Potensial":"#FC00FF", "Perlu Perhatian":"#FF4B4B"})
                st.plotly_chart(fig_pie, use_container_width=True)
            with cl2:
                fig_scatter = px.scatter(df, x='Siswa_ID', y='Skor_Total', color='Kategori', 
                                         size='Skor_Total', color_discrete_map={"Sangat Baik":"#00DBDE", "Potensial":"#FC00FF", "Perlu Perhatian":"#FF4B4B"})
                st.plotly_chart(fig_scatter, use_container_width=True)

        with t3:
            # --- BAGIAN KORELASI & REGRESI ---
            col_stat1, col_stat2 = st.columns(2)
            
            with col_stat1:
                st.subheader("🔗 Matriks Korelasi")
                st.caption("Melihat hubungan antar butir soal (0 = Tidak berhubungan, 1 = Searah kuat)")
                corr = df[soal_cols].corr()
                fig_corr = px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r', aspect="auto")
                st.plotly_chart(fig_corr, use_container_width=True)

            with col_stat2:
                st.subheader("🎯 Analisis Regresi (Faktor Kunci)")
                st.caption("Indikator mana yang paling menentukan Skor Total?")
                
                # Menghitung Regresi
                X = df[soal_cols]
                y = df['Skor_Total']
                model = LinearRegression()
                model.fit(X, y)
                
                importance = pd.DataFrame({
                    'Indikator': soal_cols,
                    'Tingkat Pengaruh': model.coef_
                }).sort_values(by='Tingkat Pengaruh', ascending=True)
                
                fig_reg = px.bar(importance, x='Tingkat Pengaruh', y='Indikator', orientation='h',
                                 color='Tingkat Pengaruh', color_continuous_scale='Viridis')
                st.plotly_chart(fig_reg, use_container_width=True)

        with t4:
            st.subheader("📑 Database Lengkap")
            st.dataframe(df, use_container_width=True)

    else:
        # --- VIEW 2: DETAIL PER SISWA ---
        st.subheader("🎯 Profiling Siswa Secara Mendalam")
        selected_student = st.selectbox("Pilih Nama/ID Siswa untuk Dianalisis:", df['Siswa_ID'].unique())
        student_data = df[df['Siswa_ID'] == selected_student]
        
        col_s1, col_s2 = st.columns()
        with col_s1:
            # Tampilkan kategori hasil segmentasi
            st.markdown(f"**Kategori Siswa:** `{student_data['Kategori'].values}`")
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = student_data['Skor_Total'].values,
                title = {'text': f"Total Skor"},
                gauge = {'axis': {'range': [0, len(soal_cols)*4]},
                         'bar': {'color': "#00DBDE"}}
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"}, height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_s2:
            vals = student_data[soal_cols].values.flatten()
            fig_line = px.line(x=soal_cols, y=vals, markers=True, title="Pola Kompetensi")
            fig_line.update_traces(line_color='#FC00FF', fill='toself')
            st.plotly_chart(fig_line, use_container_width=True)

else:
    st.error("❌ Data tidak terdeteksi! Pastikan file 'data.xlsx' atau 'data.xlsx - Sheet1.csv' tersedia.")
