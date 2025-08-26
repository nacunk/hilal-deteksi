import streamlit as st
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import dengan error handling
try:
    from detect import detect_image, detect_video
    from utils import get_weather
    DETECTION_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    DETECTION_AVAILABLE = False

# Auto-create folder assets
assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

# Page config
st.set_page_config(
    page_title="Deteksi Hilal YOLOv5 + SQM/Hisab", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🌙 Deteksi Hilal Otomatis (Upgrade)")

# Cek status sistem
if not DETECTION_AVAILABLE:
    st.error("⚠️ Sistem deteksi tidak tersedia. Beberapa fungsi mungkin tidak berjalan optimal.")
    st.info("Aplikasi tetap dapat digunakan untuk input data SQM dan cuaca.")

# --- Upload Gambar/Video ---
st.header("1. Upload Media")
media_file = st.file_uploader(
    "Upload Gambar/Video Hilal", 
    type=["jpg", "png", "jpeg", "mp4", "mov", "avi"],
    help="Format yang didukung: JPG, PNG, JPEG untuk gambar | MP4, MOV, AVI untuk video"
)

if media_file:
    st.success(f"✅ File berhasil diupload: {media_file.name}")
    
    # Preview media
    if media_file.type.startswith("image"):
        st.image(media_file, caption="Preview Gambar", use_column_width=True)
    else:
        st.video(media_file)

# --- Input SQM ---
st.header("2. Input SQM (Sky Quality Meter)")
col1, col2 = st.columns(2)

with col1:
    sqm = st.number_input(
        "Masukkan Nilai SQM:", 
        min_value=0.0, 
        max_value=30.0, 
        step=0.1,
        value=20.0,
        help="Nilai SQM menunjukkan kualitas langit (semakin tinggi = semakin gelap/baik)"
    )

with col2:
    if sqm > 0:
        if sqm < 18:
            quality = "❌ Sangat Terang (Kota)"
        elif sqm < 20:
            quality = "⚠️ Terang (Suburban)"
        elif sqm < 21.5:
            quality = "✅ Sedang (Rural)"
        else:
            quality = "⭐ Sangat Gelap (Excellent)"
        
        st.info(f"Kualitas Langit: {quality}")

# --- Input Lokasi ---
st.header("3. Input Lokasi / Koordinat")
col1, col2 = st.columns(2)

with col1:
    lat = st.text_input(
        "Latitude", 
        placeholder="-6.175",
        help="Koordinat lintang (contoh: -6.175 untuk Jakarta)"
    )

with col2:
    lon = st.text_input(
        "Longitude", 
        placeholder="106.827",
        help="Koordinat bujur (contoh: 106.827 untuk Jakarta)"
    )

# Info lokasi
if lat and lon:
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        st.success(f"📍 Koordinat: {lat_float}, {lon_float}")
    except ValueError:
        st.error("❌ Format koordinat tidak valid. Gunakan angka desimal.")

# --- Tombol Proses ---
st.header("4. Proses Deteksi")

if st.button("🔍 Proses Deteksi Hilal", type="primary"):
    if not media_file:
        st.warning("⚠️ Silakan upload file gambar atau video terlebih dahulu!")
    else:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Save uploaded file
            status_text.text("💾 Menyimpan file...")
            progress_bar.progress(20)
            
            save_path = assets_dir / media_file.name
            with open(save_path, "wb") as f:
                f.write(media_file.getbuffer())
            
            # Process detection
            if DETECTION_AVAILABLE:
                status_text.text("🔍 Menjalankan deteksi...")
                progress_bar.progress(50)
                
                if media_file.type.startswith("image"):
                    output_path, csv_path = detect_image(str(save_path), "best.pt")
                else:
                    output_path, csv_path = detect_video(str(save_path), "best.pt")
                
                progress_bar.progress(80)
                
                # Display results
                if output_path and os.path.exists(output_path):
                    st.success("✅ Deteksi berhasil!")
                    
                    if media_file.type.startswith("image"):
                        st.image(output_path, caption="Hasil Deteksi", use_column_width=True)
                    else:
                        st.video(output_path)
                else:
                    st.error("❌ Gagal memproses deteksi")
            else:
                st.warning("⚠️ Deteksi tidak tersedia, menampilkan file asli")
                output_path = str(save_path)
                csv_path = None
            
            progress_bar.progress(100)
            status_text.text("✅ Selesai!")
            
            # Display SQM info
            st.subheader("📊 Informasi SQM")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Nilai SQM", f"{sqm}")
            with col2:
                if sqm > 20:
                    visibility = "Baik"
                elif sqm > 18:
                    visibility = "Sedang"
                else:
                    visibility = "Buruk"
                st.metric("Visibilitas", visibility)
            with col3:
                st.metric("Status", "Terukur" if sqm > 0 else "Tidak Terukur")

            # Display weather info
            if lat and lon:
                try:
                    status_text.text("🌤️ Mengambil data cuaca...")
                    weather = get_weather(lat, lon)
                    
                    st.subheader("🌤️ Informasi Cuaca")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Cuaca", weather.get('cuaca', 'N/A'))
                    with col2:
                        st.metric("Suhu", f"{weather.get('suhu', 'N/A')}°C")
                    with col3:
                        st.metric("Kelembapan", f"{weather.get('kelembapan', 'N/A')}%")
                        
                except Exception as e:
                    st.warning(f"⚠️ Tidak dapat mengambil data cuaca: {str(e)}")
            
            # Download buttons
            st.subheader("📥 Download Hasil")
            col1, col2 = st.columns(2)
            
            with col1:
                if output_path and os.path.exists(output_path):
                    with open(output_path, "rb") as f:
                        file_ext = Path(output_path).suffix
                        mime_type = "image/jpeg" if file_ext.lower() in ['.jpg', '.jpeg'] else "video/mp4"
                        st.download_button(
                            "📷 Download Hasil Deteksi",
                            f,
                            file_name=f"hasil_deteksi_{Path(output_path).name}",
                            mime=mime_type
                        )
            
            with col2:
                if csv_path and os.path.exists(csv_path):
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            "📊 Download Data CSV",
                            f,
                            file_name=f"data_deteksi_{Path(csv_path).name}",
                            mime="text/csv"
                        )
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Terjadi error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

# --- Footer ---
st.markdown("---")
st.markdown("""
### ℹ️ Tentang Aplikasi
- **Deteksi Hilal**: Menggunakan teknologi YOLOv5/v8 untuk mendeteksi bulan sabit
- **SQM Integration**: Mengintegrasikan data Sky Quality Meter untuk analisis kondisi langit  
- **Weather Data**: Menampilkan informasi cuaca dari koordinat yang dimasukkan
- **Export**: Hasil dapat didownload dalam format gambar/video dan CSV

**Catatan**: Pastikan model `best.pt` tersedia di root directory untuk deteksi optimal.
""")

# Debug info (only in development)
if st.checkbox("🔧 Show Debug Info"):
    st.write("**System Info:**")
    st.write(f"- Detection Available: {DETECTION_AVAILABLE}")
    st.write(f"- Assets Directory: {assets_dir.absolute()}")
    st.write(f"- Current Working Directory: {Path.cwd()}")