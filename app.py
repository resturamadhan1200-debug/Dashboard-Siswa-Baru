import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="EduAnalytics Pro | M Restu",
    page_icon="💎",
    layout="wide"
)

# 2. CSS CUSTOM UNTUK TAMPILAN MEWAH & RAPI
st.markdown("""
    <style>
    /* Gradient Background untuk Judul Utama */
    .main-title {
        font-size: 40px;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #00DBDE, #FC00FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* Panel Sidebar agar lebih rapi */
    [data-testid="stSidebar"] {
        background-color: rgba(20, 20, 30, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Card Glassmorphism untuk Metric */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 20px;
        backdrop-filter: blur(15px);
    }

    /* Penataan Nama & NIM di Sidebar */
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

# 3. SIDEBAR: PROFIL CREATOR & KONTROL
with st.sidebar:
    # Branding Creator
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

# 4. LOAD DATA EXCEL
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        return df
    except Exception as e:
        return None

df = load_data()

# 5. LOGIKA DASHBOARD
if df is not None:
    # Pre-processing Kolom Soal
    soal_cols = [col for col in df.columns if "soal" in col.lower()]
    df['Skor_Total'] = df[soal_cols].sum(axis=1)
    df['Siswa_ID'] = [f"Siswa {i+1}" for i in range(len(df))]

    st.markdown('<p class="main-title">🚀 EDU-PERFORMANCE ANALYTICS</p>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:grey;'>Sistem Analisis Cerdas untuk Memantau Kompetensi Akademik</p>", unsafe_allow_html=True)

    if mode_view == "Global Insight":
        # --- VIEW 1: GLOBAL INSIGHT ---
        # KPI ROW
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("👥 Total Partisipan", f"{len(df)} Siswa")
        c2.metric("📊 Rata-rata Kelas", f"{df['Skor_Total'].mean():.1f}")
        c3.metric("🏆 Skor Tertinggi", int(df['Skor_Total'].max()))
        c4.metric("⚠️ Skor Terendah", int(df['Skor_Total'].min()))

        st.write("")

        t1, t2, t3 = st.tabs(["📊 Analisis Soal", "🤖 AI Clustering", "📋 Spreadsheet"])

        with t1:
            st.subheader("📈 Tingkat Keberhasilan per Item Soal")
            avg_soal = df[soal_cols].mean().reset_index()
            avg_soal.columns = ['Soal', 'Nilai']
            fig_bar = px.bar(avg_soal, x='Soal', y='Nilai', color='Nilai', 
                             color_continuous_scale=theme_color, text_auto='.2f')
            fig_bar.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

        with t2:
            st.subheader("🤖 Segmentasi Kemampuan (K-Means)")
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            df['Cluster'] = kmeans.fit_predict(df[soal_cols])
            
            cl1, cl2 = st.columns([1, 2])
            with cl1:
                fig_pie = px.pie(df, names='Cluster', hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_pie, use_container_width=True)
            with cl2:
                fig_scatter = px.scatter(df, x='Siswa_ID', y='Skor_Total', color='Cluster', 
                                         size='Skor_Total', color_continuous_scale=theme_color)
                st.plotly_chart(fig_scatter, use_container_width=True)
        
        with t3:
            st.subheader("📑 Database Lengkap")
            st.dataframe(df, use_container_width=True)

    else:
        # --- VIEW 2: DETAIL PER SISWA (PENGGANTI CARI CEPAT) ---
        st.subheader("🎯 Profiling Siswa Secara Mendalam")
        selected_student = st.selectbox("Pilih Nama/ID Siswa untuk Dianalisis:", df['Siswa_ID'].unique())
        
        student_data = df[df['Siswa_ID'] == selected_student]
        
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            # Gauge Chart untuk Skor
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = student_data['Skor_Total'].values[0],
                title = {'text': f"Total Skor {selected_student}"},
                gauge = {'axis': {'range': [0, len(soal_cols)*5]},
                         'bar': {'color': "#00DBDE"},
                         'steps': [
                             {'range': [0, 40], 'color': "rgba(255,0,0,0.1)"},
                             {'range': [40, 70], 'color': "rgba(255,255,0,0.1)"},
                             {'range': [70, 100], 'color': "rgba(0,255,0,0.1)"}]}
            ))
            fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_s2:
            # Radar Chart / Performa per soal
            st.markdown(f"**Detail Jawaban {selected_student}**")
            vals = student_data[soal_cols].values.flatten()
            fig_line = px.line(x=soal_cols, y=vals, markers=True, title="Pola Jawaban")
            fig_line.update_traces(line_color='#FC00FF', fill='toself')
            st.plotly_chart(fig_line, use_container_width=True)

else:
    st.error("❌ File 'data.xlsx' tidak terdeteksi di GitHub!")
