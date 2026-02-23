import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans

# 1. SETTING HALAMAN (Layout Wide agar Lega)
st.set_page_config(
    page_title="EduAnalytics Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. CSS CUSTOM UNTUK TAMPILAN MEWAH (Glassmorphism & Border Gradient)
st.markdown("""
    <style>
    /* Mengubah background utama */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Style Kartu Metric */
    div[data-testid="metric-container"] {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #efefef;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-left: 5px solid #6366f1;
    }

    /* Mempercantik judul */
    h1 {
        color: #1e293b;
        font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNGSI LOAD DATA (KHUSUS EXCEL)
@st.cache_data
def load_data():
    try:
        # Membaca data.xlsx
        df = pd.read_excel("data.xlsx")
        return df
    except Exception as e:
        return None

df = load_data()

# --- HEADER & SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=80)
    st.title("EduDash Pro")
    st.markdown("---")
    st.markdown("### 🛠️ Control Panel")
    show_raw = st.checkbox("Tampilkan Data Mentah")
    st.info("Gunakan menu ini untuk memfilter tampilan dashboard utama.")

# --- PROSES DATA ---
if df is not None:
    # Cari kolom soal
    soal_cols = [col for col in df.columns if "soal" in col.lower()]
    df['Skor_Total'] = df[soal_cols].sum(axis=1)
    
    # Header Utama
    st.title("💎 Student Performance Insight")
    st.markdown("Dashboard analisis kompetensi siswa berbasis kecerdasan buatan (K-Means Clustering).")
    
    # --- SECTION 1: KPI CARDS ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Partisipan", f"{len(df)} Siswa", delta="Active")
    with c2:
        st.metric("Rata-rata Skor", f"{df['Skor_Total'].mean():.2f}")
    with c3:
        st.metric("Pencapaian Tertinggi", f"{df['Skor_Total'].max()}")
    with c4:
        st.metric("Standar Deviasi", f"{df['Skor_Total'].std():.2f}")

    st.divider()

    # --- SECTION 2: TABS VISUALISASI MEWAH ---
    tab1, tab2, tab3 = st.tabs(["🚀 Performance Analytics", "📊 Detail Soal", "🤖 AI Segmentation"])

    with tab1:
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.subheader("Distribusi Performa Keseluruhan")
            fig_dist = px.histogram(df, x="Skor_Total", nbins=10, 
                                   color_discrete_sequence=['#6366f1'],
                                   marginal="violin") # Menambah efek violin agar mewah
            fig_dist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with col_b:
            st.subheader("🏆 Leaderboard")
            top_siswa = df[['Skor_Total']].sort_values(by='Skor_Total', ascending=False).head(5)
            st.table(top_siswa)

    with tab2:
        st.subheader("Analisis Kesulitan per Item Soal")
        rata_soal = df[soal_cols].mean().reset_index()
        rata_soal.columns = ['Item Soal', 'Rata-rata']
        
        fig_bar = px.bar(rata_soal, x='Item Soal', y='Rata-rata', 
                         color='Rata-rata', 
                         color_continuous_scale='Sunsetdark')
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("AI-Driven Student Profiling")
        # Clustering K-Means
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit_predict(df[soal_cols])
        
        # Penamaan Cluster
        map_nama = {0: "Potential", 1: "Advanced", 2: "Standard"} 
        df['Status'] = df['Cluster'].map(map_nama)

        c_pie, c_desc = st.columns([1, 1])
        with c_pie:
            fig_pie = px.pie(df, names='Status', hole=0.5, 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with c_desc:
            st.write("#### Insight Strategis")
            st.success("🟢 **Advanced**: Siswa yang menguasai hampir seluruh materi.")
            st.warning("🟡 **Standard**: Perlu penguatan pada beberapa topik tertentu.")
            st.error("🔴 **Potential**: Butuh pendampingan intensif (Remedial).")

    if show_raw:
        st.subheader("🔍 Spreadsheet View")
        st.dataframe(df, use_container_width=True)

else:
    st.error("❌ File 'data.xlsx' tidak ditemukan!")
    st.info("Pastikan kamu sudah mengupload file bernama 'data.xlsx' (huruf kecil semua) ke GitHub.")