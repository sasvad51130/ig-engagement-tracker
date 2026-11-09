import streamlit as st
import instaloader
import re

st.set_page_config(
    page_title="IG Public Engagement Tracker",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Instagram Public Engagement Dashboard")
st.caption("Deteksi metrik postingan dan followers secara otomatis tanpa perlu login.")

# Sidebar Informasi (Input Manual Dihapus)
with st.sidebar:
    st.header("📌 Informasi Dashboard")
    st.info("Sistem kini melacak **jumlah followers secara real-time** langsung dari profil kreator setiap kali tautan dianalisis.")
    st.warning("Catatan: Metrik privat (Reach, Saves, Shares) tetap dikunci oleh sistem keamanan Meta.")

# Input URL
url_input = st.text_input(
    "Masukkan Link Postingan / Reel Instagram:",
    placeholder="https://www.instagram.com/p/C_xxxxxx/ atau /reel/..."
)

def extract_shortcode(url):
    """Mengekstrak ID unik (shortcode) dari link URL Instagram"""
    match = re.search(r'/(?:p|reel|tv)/([^/?#&]+)', url)
    if match:
        return match.group(1)
    return None

if st.button("🔍 Analisis Konten & Akun", type="primary"):
    if not url_input:
        st.warning("Silakan tempel tautan postingan Instagram terlebih dahulu.")
    else:
        shortcode = extract_shortcode(url_input)
        
        if not shortcode:
            st.error("Format link tidak valid! Pastikan link mengandung /p/ atau /reel/.")
        else:
            with st.spinner("Mengambil data postingan dan profil real-time dari Instagram..."):
                try:
                    # Inisialisasi Instaloader
                    L = instaloader.Instaloader(quiet=True)
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    
                    # --- FITUR BARU: Deteksi Followers Real-time ---
                    profile = post.owner_profile
                    realtime_followers = profile.followers
                    
                    # Ekstraksi Data Publik
                    likes = post.likes
                    comments = post.comments
                    views = post.video_view_count if post.is_video else 0
                    uploader = post.owner_username
                    caption = post.caption if post.caption else "Tidak ada caption"
                    thumbnail = post.url 
                    
                    # Hitung Total dan Engagement Rate
                    total_interaksi = likes + comments
                    er_by_followers = (total_interaksi / realtime_followers) * 100 if realtime_followers > 0 else 0

                    st.success("Data profil dan postingan berhasil ditarik!")

                    # Tampilan Visual Dashboard
                    col_left, col_right = st.columns([1, 1.8], gap="large")

                    with col_left:
                        st.subheader("🖼️ Preview Konten")
                        st.image(thumbnail, use_container_width=True)
                        
                        # Info Profil Otomatis
                        st.markdown(f"**Kreator:** `@{uploader}`")
                        st.markdown(f"**Followers:** `{realtime_followers:,}`".replace(",", "."))
                        
                        with st.expander("Teks Caption"):
                            st.write(caption)

                    with col_right:
                        st.subheader("📈 Ringkasan Metrik Publik")
                        
                        # Baris Metrik Dasar
                        m1, m2, m3 = st.columns(3)
                        m1.metric("👍 Likes", f"{likes:,}".replace(",", "."))
                        m2.metric("💬 Komentar", f"{comments:,}".replace(",", "."))
                        
                        if post.is_video:
                            m3.metric("👁️ Penonton / Views", f"{views:,}".replace(",", "."))
                        else:
                            m3.metric("📸 Tipe Konten", "Foto / Carousel")

                        st.markdown("---")
                        
                        # Baris Analisis Engagement
                        e1, e2 = st.columns(2)
                        e1.metric(
                            "🔥 ER vs Realtime Followers", 
                            f"{er_by_followers:.4f}%",
                            help=f"Formula: ((Likes + Komentar) / {realtime_followers:,}) * 100"
                        )
                        
                        if post.is_video and views > 0:
                            er_by_views = (total_interaksi / views) * 100
                            e2.metric("🎯 ER vs Views (Tayangan)", f"{er_by_views:.2f}%")
                        else:
                            e2.metric("🎯 ER vs Views", "N/A (Hanya untuk Video)")

                        st.markdown("---")
                        st.write(f"Total interaksi langsung: **{total_interaksi:,}** interaksi.".replace(",", "."))

                except Exception as err:
                    st.error("Gagal membaca link. Pastikan postingan bersifat publik dan bukan akun private.")
                    with st.expander("Detail Log Error"):
                        st.code(str(err))
