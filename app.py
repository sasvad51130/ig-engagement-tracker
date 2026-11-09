import streamlit as st
import yt_dlp

st.set_page_config(
    page_title="IG Public Engagement Tracker",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Instagram Public Engagement Dashboard")
st.caption("Deteksi metrik publik per postingan/Reel tanpa perlu login ke akun target.")

# Sidebar Pengaturan
with st.sidebar:
    st.header("⚙️ Parameter Akun")
    followers = st.number_input(
        "Estimasi Followers Akun Target:",
        min_value=1,
        value=8400000,
        step=50000,
        help="Sesuaikan dengan jumlah followers akun yang sedang dianalisis (misal: @infobmkg)."
    )
    st.info(
        "Catatan: Metrik privat seperti Reach, Saves, dan Shares secara teknis dikunci oleh sistem keamanan Meta "
        "dan hanya bisa dilihat oleh pemilik akun resmi."
    )

# Input URL
url_input = st.text_input(
    "Masukkan Link Postingan / Reel Instagram:",
    placeholder="https://www.instagram.com/reel/C_xxxxxx/ atau https://www.instagram.com/p/C_xxxxxx/"
)

def extract_meta(url):
    ydl_opts = {
        'skip_download': True,
        'extract_flat': False,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

if st.button("🔍 Analisis Konten", type="primary"):
    if not url_input:
        st.warning("Silakan tempel tautan postingan Instagram terlebih dahulu.")
    else:
        with st.spinner("Mengambil data publik dari Instagram..."):
            try:
                data = extract_meta(url_input)
                
                # Ekstraksi Data Publik
                likes = data.get('like_count') or 0
                comments = data.get('comment_count') or 0
                views = data.get('view_count') or 0
                uploader = data.get('uploader') or "Akun Publik"
                caption = data.get('title') or data.get('description') or "-"
                thumbnail = data.get('thumbnail')

                total_interaksi = likes + comments
                er_by_followers = (total_interaksi / followers) * 100
                er_by_views = (total_interaksi / views * 100) if views > 0 else 0

                st.success("Data berhasil ditarik!")

                # Tampilan Visual Dashboard
                col_left, col_right = st.columns([1, 1.8], gap="large")

                with col_left:
                    st.subheader("Preview Konten")
                    if thumbnail:
                        st.image(thumbnail, use_container_width=True)
                    st.markdown(f"**Kreator:** `@{uploader}`")
                    with st.expander("Teks Caption"):
                        st.write(caption)

                with col_right:
                    st.subheader("Ringkasan Metrik Publik")
                    
                    # Baris Metrik Dasar
                    m1, m2, m3 = st.columns(3)
                    m1.metric("👍 Likes", f"{likes:,}".replace(",", "."))
                    m2.metric("💬 Komentar", f"{comments:,}".replace(",", "."))
                    m3.metric("👁️ Penonton / Views", f"{views:,}".replace(",", ".") if views > 0 else "N/A")

                    st.markdown("---")
                    
                    # Baris Analisis Engagement
                    e1, e2 = st.columns(2)
                    e1.metric(
                        "🔥 ER vs Followers", 
                        f"{er_by_followers:.4f}%",
                        help="Formula: ((Likes + Komentar) / Followers) * 100"
                    )
                    e2.metric(
                        "🎯 ER vs Views (Tayangan)", 
                        f"{er_by_views:.2f}%" if views > 0 else "Hanya format Video/Reel",
                        help="Formula: ((Likes + Komentar) / Views) * 100"
                    )

                    st.markdown("---")
                    st.write(f"Total interaksi langsung: **{total_interaksi:,}** interaksi.".replace(",", "."))

            except Exception as err:
                st.error("Gagal membaca link. Pastikan postingan berasal dari akun publik, bukan akun yang dikunci/private.")
                with st.expander("Detail Log"):
                    st.code(str(err))