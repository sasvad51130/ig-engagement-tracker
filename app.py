import streamlit as st
import instaloader
import re

st.set_page_config(
    page_title="IG Public Engagement Tracker",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Instagram Public Engagement Dashboard")
st.caption("Deteksi metrik postingan & followers cepat (Optimized Mode).")

def extract_shortcode(url):
    match = re.search(r'/(?:p|reel|tv)/([^/?#&]+)', url)
    return match.group(1) if match else None

# Fungsi fetch cepat dengan Caching Streamlit
@st.cache_data(show_spinner=False, ttl=600)
def fetch_post_data(shortcode):
    # Inisialisasi cepat tanpa download media mentah
    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    
    post_info = {
        "likes": post.likes,
        "comments": post.comments,
        "is_video": post.is_video,
        "views": post.video_view_count if post.is_video else 0,
        "uploader": post.owner_username,
        "caption": post.caption or "Tidak ada caption",
        "thumbnail": post.url
    }
    
    # Coba ambil followers dengan pengaman agar tidak membuat loading macet
    followers = None
    try:
        followers = post.owner_profile.followers
    except Exception:
        followers = None
        
    post_info["followers"] = followers
    return post_info

# Input Form
url_input = st.text_input(
    "Masukkan Link Postingan / Reel Instagram:",
    placeholder="https://www.instagram.com/p/DFxyz.../ atau /reel/..."
)

if st.button("🔍 Analisis Cepat", type="primary"):
    if not url_input:
        st.warning("Silakan tempel tautan postingan Instagram.")
    else:
        shortcode = extract_shortcode(url_input)
        if not shortcode:
            st.error("Link tidak valid! Pastikan tautan mengandung /p/ atau /reel/.")
        else:
            with st.spinner("Mengambil metrik postingan..."):
                try:
                    data = fetch_post_data(shortcode)
                    st.session_state["post_data"] = data
                    st.success("Data postingan berhasil diambil!")
                except Exception as err:
                    st.error("Gagal menarik data. Server Instagram mungkin sedang membatasi permintaan sementara.")
                    with st.expander("Detail Error"):
                        st.code(str(err))

# Tampilkan hasil jika data sudah ada di session
if "post_data" in st.session_state:
    data = st.session_state["post_data"]
    
    col_left, col_right = st.columns([1, 1.8], gap="large")

    with col_left:
        st.subheader("Preview Konten")
        if data.get("thumbnail"):
            st.image(data["thumbnail"], use_container_width=True)
        st.markdown(f"**Kreator:** `@{data['uploader']}`")
        with st.expander("Teks Caption"):
            st.write(data["caption"])

    with col_right:
        st.subheader("Ringkasan Metrik")
        
        # Penanganan Followers (Otomatis vs Cadangan Manual jika IG Lambat)
        auto_followers = data.get("followers")
        if auto_followers:
            followers_val = auto_followers
            st.caption(f"Followers terdeteksi otomatis: **{auto_followers:,}**".replace(",", "."))
        else:
            followers_val = st.number_input(
                "Followers (Auto-fetch profil dibatasi IG, ketik estimasi):",
                min_value=1,
                value=8400000,
                step=50000
            )

        # Kartu Metrik
        m1, m2, m3 = st.columns(3)
        m1.metric("👍 Likes", f"{data['likes']:,}".replace(",", "."))
        m2.metric("💬 Komentar", f"{data['comments']:,}".replace(",", "."))
        
        if data["is_video"]:
            m3.metric("👁️ Views", f"{data['views']:,}".replace(",", "."))
        else:
            m3.metric("📸 Format", "Foto / Carousel")

        st.markdown("---")

        # Perhitungan ER
        total_interaksi = data["likes"] + data["comments"]
        er_followers = (total_interaksi / followers_val) * 100 if followers_val > 0 else 0

        e1, e2 = st.columns(2)
        e1.metric(
            "🔥 ER vs Followers", 
            f"{er_followers:.4f}%",
            help=f"((Likes + Komentar) / {followers_val:,}) * 100"
        )
        
        if data["is_video"] and data["views"] > 0:
            er_views = (total_interaksi / data["views"]) * 100
            e2.metric("🎯 ER vs Views", f"{er_views:.2f}%")
        else:
            e2.metric("🎯 ER vs Views", "N/A")

        st.markdown("---")
        st.write(f"Total interaksi: **{total_interaksi:,}** interaksi.".replace(",", "."))
