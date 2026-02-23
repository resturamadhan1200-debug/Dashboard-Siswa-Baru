import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="EduAnalytics Pro | M Restu",
    page_icon="🔥",
    layout="wide"
)

# 2. CSS DYNAMIC & MEWAH (Support Dark/Light Mode)
st.markdown("""
    <style>
    /* Gradient Background untuk Judul */
    .main-title {
        font-size: 45px;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF512F, #DD2476, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Styling Card yang Transparan (Glassmorphism) */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
    }

    /* Footer Style */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: grey;
        text-align: center;
        padding: 10px;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR INTERAKTIF & BRANDING
with st.sidebar:
    st.markdown(f"<h2 style='text-align: center;'>🚀 Creator</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; color: #DD2476;'>M Restu Ramadhan Arrahma</h3>", unsafe_allow_html=True)
    st.divider()
    
    st.write("### 🛠️ Pengaturan Dashboard")
    color_theme = st.selectbox("Pilih Skema Warna Grafik", 
                               ["Plasma", "Viridis", "Rainbow", "Electric", "Sunset"])
    
    st.write("### 🔍 Filter Cepat")
    top_n = st.slider("Lihat Top Siswa", 5, 20, 10)
    
    st.divider()
    st.info("Dashboard ini dirancang untuk memberikan insight mendalam tentang performa akademis.")

# 4. LOAD DATA EXCEL
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("data.xlsx")
        return df
    except Exception as e:
        return None

df = load_data()

# 5. LOGIKA UTAMA
if df is not None:
    # Preprocessing
    soal_cols = [col for col in df.columns if "soal" in col.lower()]
    df['Skor_Total'] = df[soal_cols].sum(axis=1)
    df['Rata_Rata'] = df[soal_cols].mean(axis=1)

    # Header Utama
    st.markdown('<p class="main-title">🔥 EDU-PERFORMANCE ANALYTICS</p>', unsafe_allow_html=True)
    
    # --- SECTION 1: METRIK INTERAKTIF ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Siswa", len(df), "Active")
    c2.metric("📊 Rata-rata Skor", f"{df['Skor_Total'].mean():.1f}")
    c3.metric("🏆 Skor Tertinggi", f"{df['Skor_Total'].max()}")
    c4.metric("📉 Skor Terendah", f"{df['Skor_Total'].min()}")

    st.write("")

    # --- SECTION 2: TABS INTERAKTIF ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Statistik Soal", "📈 Distribusi Nilai", "🤖 AI Clustering", "📑 Data View"])

    with tab1:
        st.subheader("📍 Analisis Kualitas Tiap Soal")
        rata_soal = df[soal_cols].mean().reset_index()
        rata_soal.columns = ['Nomor Soal', 'Rata-rata Nilai']
        
        fig_bar = px.bar(rata_soal, x='Nomor Soal', y='Rata-rata Nilai', 
                         color='Rata-rata Nilai',
                         color_continuous_scale=color_theme,
                         text_auto='.2f',
                         title="Rata-rata Nilai Per Soal (Tingkat Kesulitan)")
        fig_bar.update_layout(template="none", hovermode="x unified")
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.subheader("📉 Kurva Distribusi Skor")
            fig_dist = px.histogram(df, x="Skor_Total", color_discrete_sequence=['#DD2476'],
                                   marginal="box", nbins=15, title="Frekuensi Skor Siswa")
            st.plotly_chart(fig_dist, use_container_width=True)
        with col_right:
            st.subheader(f"🏆 Top {top_n} Siswa")
            st.dataframe(df[['Skor_Total']].sort_values('Skor_Total', ascending=False).head(top_n), use_container_width=True)

    with tab3:
        st.subheader("🤖 Segmentasi Siswa (Machine Learning)")
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Group'] = kmeans.fit_predict(df[soal_cols])
        
        c_pie, c_scatter = st.columns([1, 2])
        with c_pie:
            fig_pie = px.pie(df, names='Group', hole=0.4, title="Komposisi Kelompok",
                             color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)
        with c_scatter:
            # Scatter Plot interaktif
            fig_scat = px.scatter(df, x='Skor_Total', y='Rata_Rata', color='Group',
                                 title="Peta Sebaran Kelompok Siswa",
                                 color_continuous_scale=color_theme)
            st.plotly_chart(fig_scat, use_container_width=True)

    with tab4:
        st.subheader("📋 Seluruh Data Siswa")
        st.dataframe(df, use_container_width=True)

    # FOOTER
    st.markdown(f"""
        <div class="footer">
            Dashboard Created with ❤️ by M Restu Ramadhan Arrahma | © 2024
        </div>
    """, unsafe_allow_html=True)

else:
    st.error("Gagal memuat file 'data.xlsx'. Pastikan file ada di GitHub.")
