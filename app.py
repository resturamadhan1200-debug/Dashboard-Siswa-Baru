import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans

# 1. SETTING HALAMAN
st.set_page_config(
    page_title="EduAnalytics Pro",
    page_icon="💎",
    layout="wide"
)

# 2. CSS FIX: Memastikan Teks Terlihat Jelas (Warna Gelap di Kartu Putih)
st.markdown("""
    <style>
    /* Background utama aplikasi agar tetap bersih */
    .stApp {
        background-color: #f1f5f9;
    }
    
    /* Memaksa Kartu Metric agar Teksnya Hitam/Gelap */
    div[data-testid="metric-container"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        padding: 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1) !important;
    }

    /* Memaksa Warna Label (Judul Kecil di Metric) */
    [data-testid="stMetricLabel"] {
        color: #475569 !important;
        font-weight: 600 !important;
    }

    /* Memaksa Warna Value (Angka Besar di Metric) */
    [data-testid="stMetricValue"] {
        color: #1e293b !important;
        font-weight: 800 !important;
    }

    /* Mengatur style Tab agar lebih modern */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOAD DATA EXCEL
@st.cache_data
def load_data():
    try:
        # Membaca data.xlsx
        df = pd.read_excel("data.xlsx")
        return df
    except Exception as e:
        return None

df = load_data()

# --- DASHBOARD LOGIC ---
if df is not None:
    # Cari kolom soal secara otomatis
    soal_cols = [col for col in df.columns if "soal" in col.lower()]
    df['Skor_Total'] = df[soal_cols].sum(axis=1)
    
    st.title("💎 Student Performance Insight")
    st.markdown("Dashboard analisis kompetensi siswa berbasis **Excel**")
    
    # --- SECTION 1: KARTU STATISTIK (KPI) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Siswa", f"{len(df)}")
    with c2:
        st.metric("Rata-rata Skor", f"{df['Skor_Total'].mean():.1f}")
    with c3:
        st.metric("Skor Tertinggi", f"{df['Skor_Total'].max()}")
    with c4:
        st.metric("Variansi", f"{df['Skor_Total'].std():.1f}")

    st.write("") # Spasi

    # --- SECTION 2: VISUALISASI ---
    tab1, tab2 = st.tabs(["📊 Analisis Performa", "🎯 AI Clustering"])

    with tab1:
        # Grafik batang dengan tema terang agar teks terbaca
        rata_soal = df[soal_cols].mean().reset_index()
        rata_soal.columns = ['Soal', 'Rata_Rata']
        
        fig_bar = px.bar(rata_soal, x='Soal', y='Rata_Rata', 
                         color='Rata_Rata',
                         template="plotly_white", # Memaksa background grafik putih
                         color_continuous_scale='Viridis')
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        # K-Means Clustering
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit_predict(df[soal_cols])
        
        col_left, col_right = st.columns(2)
        with col_left:
            fig_pie = px.pie(df, names='Cluster', hole=0.5, 
                             template="plotly_white",
                             color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_right:
            st.info("💡 **Tips Membaca:** Cluster menunjukkan kelompok siswa dengan pola jawaban serupa. Gunakan ini untuk menentukan strategi remedial.")
            st.dataframe(df[['Skor_Total', 'Cluster']].head(10), use_container_width=True)

else:
    st.error("Gagal memuat file 'data.xlsx'. Pastikan file sudah di-upload ke GitHub.")
