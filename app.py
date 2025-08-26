import streamlit as st
import os
import sys
from pathlib import Path
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import dengan error handling
try:
    from detect import detect_image, detect_video
    from utils import get_weather, get_city_coordinates, INDONESIAN_CITIES
    DETECTION_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    DETECTION_AVAILABLE = False

# Auto-create folder assets
assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

# Page config dengan tema milky way
st.set_page_config(
    page_title="Deteksi Hilal - Observatorium Digital", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS untuk tema milky way
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
    background-image: 
        radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 40px),
        radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 30px),
        radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 40px),
        radial-gradient(rgba(255,255,255,.4), rgba(255,255,255,.1) 2px, transparent 30px);
    background-size: 550px 550px, 350px 350px, 250px 250px, 150px 150px;
    background-position: 0 0, 40px 60px, 130px 270px, 70px 100px;
    color: white;
}

.main-header {
    text-align: center;
    color: #ffffff;
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 2rem;
    text-shadow: 0 0 20px rgba(255,255,255,0.5);
}

.section-header {
    color: #87ceeb;
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 2rem;
    margin-bottom: 1rem;
    text-shadow: 0 0 10px rgba(135,206,235,0.3);
}

.stButton > button {
    background: linear-gradient(45deg, #1e3c72, #2a5298);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 2rem;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(46, 82, 152, 0.3);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(45deg, #2a5298, #1e3c72);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(46, 82, 152, 0.4);
}

.metric-container {
    background: rgba(255, 255, 255, 0.1);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(10px);
    margin: 0.5rem 0;
}

.weather-info {
    background: rgba(135, 206, 235, 0.1);
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid rgba(135, 206, 235, 0.3);
    margin: 1rem 0;
}

.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.1);
    color: white;
}

.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.stNumberInput > div > div > input {
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
}
</style>
""", unsafe_allow_html=True)

# Header utama
st.markdown('<div class="main-header">🌙 Observatorium Deteksi Hilal Digital</div>', unsafe_allow_html=True)

# Cek status sistem
if not DETECTION_AVAILABLE:
    st.error("⚠️ Sistem deteksi tidak tersedia. Beberapa fungsi mungkin tidak berjalan optimal.")
    st.info("Aplikasi tetap dapat digunakan untuk input data SQM dan informasi cuaca.")

# --- Upload Gambar/Video ---
st.markdown('<div class="section-header">📸 Unggah Media Observasi</div>', unsafe_allow_html=True)

media_file = st.file_uploader(
    "Pilih gambar atau video untuk dianalisis", 
    type=["jpg", "png", "jpeg", "mp4", "mov", "avi"],
    help="Format yang didukung: JPG, PNG, JPEG untuk gambar | MP4, MOV, AVI untuk video"
)

if media_file:
    st.success(f"✅ File berhasil diunggah: {media_file.name}")
    
    # Preview media
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if media_file.type.startswith("image"):
            st.image(media_file, caption="Pratinjau Gambar", use_column_width=True)
        else:
            st.video(media_file)

# --- Input SQM ---
st.markdown('<div class="section-header">📊 Pengaturan Sky Quality Meter (SQM)</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    sqm = st.number_input(
        "Masukkan Nilai SQM:", 
        min_value=0.0, 
        max_value=30.0, 
        step=0.1,
        value=20.0,
        help="Nilai SQM menunjukkan kualitas langit (semakin tinggi = semakin gelap/baik untuk observasi)"
    )

with col2:
    if sqm > 0:
        if sqm < 18:
            quality = "❌ Sangat Terang (Area Perkotaan)"
            quality_desc = "Tidak ideal untuk observasi hilal"
        elif sqm < 20:
            quality = "⚠️ Terang (Area Suburban)"  
            quality_desc = "Kurang ideal untuk observasi"
        elif sqm < 21.5:
            quality = "✅ Sedang (Area Pedesaan)"
            quality_desc = "Cukup baik untuk observasi"
        else:
            quality = "⭐ Sangat Gelap (Excellent)"
            quality_desc = "Sangat ideal untuk observasi hilal"
        
        st.markdown(f"""
        <div class="metric-container">
            <strong>Kualitas Langit:</strong> {quality}<br>
            <small>{quality_desc}</small>
        </div>
        """, unsafe_allow_html=True)

# --- Input Lokasi ---
st.markdown('<div class="section-header">📍 Informasi Lokasi Observasi</div>', unsafe_allow_html=True)

# Pilihan metode input lokasi
location_method = st.radio(
    "Pilih metode input lokasi:",
    ["Pilih Kota", "Input Koordinat Manual"],
    horizontal=True
)

selected_lat = None
selected_lon = None
location_name = None

if location_method == "Pilih Kota":
    col1, col2 = st.columns(2)
    
    with col1:
        selected_city = st.selectbox(
            "Pilih Kota:",
            [""] + list(INDONESIAN_CITIES.keys()),
            help="Pilih kota untuk mendapatkan koordinat otomatis"
        )
    
    with col2:
        if selected_city:
            coords = INDONESIAN_CITIES[selected_city]
            selected_lat = coords["lat"]
            selected_lon = coords["lon"]
            location_name = selected_city
            st.success(f"📍 {selected_city}: {selected_lat}, {selected_lon}")

else:  # Input koordinat manual
    col1, col2 = st.columns(2)
    
    with col1:
        lat_input = st.text_input(
            "Latitude", 
            placeholder="-6.175",
            help="Koordinat lintang (contoh: -6.175 untuk Jakarta)"
        )
    
    with col2:
        lon_input = st.text_input(
            "Longitude", 
            placeholder="106.827",
            help="Koordinat bujur (contoh: 106.827 untuk Jakarta)"
        )
    
    if lat_input and lon_input:
        try:
            selected_lat = float(lat_input)
            selected_lon = float(lon_input)
            location_name = f"Koordinat Manual ({selected_lat}, {selected_lon})"
            st.success(f"📍 Koordinat: {selected_lat}, {selected_lon}")
        except ValueError:
            st.error("❌ Format koordinat tidak valid. Gunakan angka desimal.")

# Tampilkan informasi cuaca jika lokasi tersedia
if selected_lat and selected_lon:
    try:
        weather = get_weather(selected_lat, selected_lon)
        
        st.markdown(f"""
        <div class="weather-info">
            <h4>🌤️ Informasi Cuaca - {location_name}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌡️ Suhu", f"{weather.get('suhu', 'N/A')}°C")
        with col2:
            st.metric("💧 Kelembapan", f"{weather.get('kelembapan', 'N/A')}%")
        with col3:
            st.metric("🌤️ Kondisi", weather.get('cuaca', 'N/A'))
        with col4:
            visibility = "Baik" if weather.get('kelembapan', 100) < 70 else "Sedang" if weather.get('kelembapan', 100) < 85 else "Buruk"
            st.metric("👁️ Visibilitas", visibility)
            
    except Exception as e:
        st.warning(f"⚠️ Tidak dapat mengambil data cuaca: {str(e)}")

# --- Tombol Proses ---
st.markdown('<div class="section-header">🔍 Proses Analisis Hilal</div>', unsafe_allow_html=True)

if st.button("🚀 Mulai Deteksi Hilal", type="primary"):
    if not media_file:
        st.warning("⚠️ Silakan unggah file gambar atau video terlebih dahulu!")
    else:
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Save uploaded file
            status_text.text("💾 Menyimpan file media...")
            progress_bar.progress(20)
            
            save_path = assets_dir / media_file.name
            with open(save_path, "wb") as f:
                f.write(media_file.getbuffer())
            
            # Process detection
            if DETECTION_AVAILABLE:
                status_text.text("🔍 Menganalisis dan mendeteksi hilal...")
                progress_bar.progress(50)
                
                if media_file.type.startswith("image"):
                    output_path, csv_path = detect_image(str(save_path), "best.pt")
                else:
                    output_path, csv_path = detect_video(str(save_path), "best.pt")
                
                progress_bar.progress(80)
                
                # Display results
                if output_path and os.path.exists(output_path):
                    st.success("✅ Deteksi hilal berhasil!")
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if media_file.type.startswith("image"):
                            st.image(output_path, caption="Hasil Deteksi Hilal dengan Bounding Box", use_column_width=True)
                        else:
                            st.video(output_path)
                    
                    # Tampilkan informasi deteksi dari CSV
                    if csv_path and os.path.exists(csv_path):
                        import pandas as pd
                        try:
                            df = pd.read_csv(csv_path)
                            if not df.empty:
                                st.success(f"🌙 Terdeteksi {len(df)} objek hilal dengan tingkat kepercayaan rata-rata: {df['confidence'].mean():.2%}")
                                
                                # Tampilkan detail deteksi
                                st.subheader("📋 Detail Hasil Deteksi")
                                for i, row in df.iterrows():
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric(f"Hilal {i+1} - X", f"{row['x1']:.0f}-{row['x2']:.0f}")
                                    with col2:
                                        st.metric(f"Hilal {i+1} - Y", f"{row['y1']:.0f}-{row['y2']:.0f}")
                                    with col3:
                                        st.metric("Kepercayaan", f"{row['confidence']:.1%}")
                                    with col4:
                                        confidence_level = "Tinggi" if row['confidence'] > 0.7 else "Sedang" if row['confidence'] > 0.4 else "Rendah"
                                        st.metric("Kualitas", confidence_level)
                            else:
                                st.info("🔍 Tidak ada hilal yang terdeteksi dalam media ini")
                        except Exception as e:
                            st.warning(f"Tidak dapat membaca hasil deteksi: {e}")
                else:
                    st.error("❌ Gagal memproses deteksi")
            else:
                st.warning("⚠️ Sistem deteksi tidak tersedia, menampilkan file asli")
                output_path = str(save_path)
                csv_path = None
            
            progress_bar.progress(100)
            status_text.text("✅ Analisis selesai!")
            
            # Display SQM analysis
            st.subheader("📊 Analisis Kondisi Observasi")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📏 Nilai SQM", f"{sqm}")
            with col2:
                if sqm > 21:
                    obs_quality = "Sangat Baik"
                elif sqm > 19:
                    obs_quality = "Baik"
                elif sqm > 17:
                    obs_quality = "Cukup"
                else:
                    obs_quality = "Kurang Ideal"
                st.metric("🔭 Kualitas Observasi", obs_quality)
            with col3:
                st.metric("📍 Lokasi", location_name if location_name else "Tidak Diset")
            with col4:
                overall_score = "Optimal" if sqm > 20 and selected_lat and selected_lon else "Baik" if sqm > 18 else "Perlu Perbaikan"
                st.metric("⭐ Skor Keseluruhan", overall_score)

            # Download buttons
            st.subheader("📥 Unduh Hasil Analisis")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if output_path and os.path.exists(output_path):
                    with open(output_path, "rb") as f:
                        file_ext = Path(output_path).suffix
                        mime_type = "image/jpeg" if file_ext.lower() in ['.jpg', '.jpeg'] else "video/mp4"
                        st.download_button(
                            "🖼️ Unduh Hasil Deteksi",
                            f,
                            file_name=f"hilal_terdeteksi_{Path(output_path).name}",
                            mime=mime_type
                        )
            
            with col2:
                if csv_path and os.path.exists(csv_path):
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            "📊 Unduh Data CSV",
                            f,
                            file_name=f"data_hilal_{Path(csv_path).name}",
                            mime="text/csv"
                        )
            
            with col3:
                # Create report
                report_data = {
                    "lokasi": location_name,
                    "koordinat": f"{selected_lat}, {selected_lon}" if selected_lat and selected_lon else "Tidak diset",
                    "sqm": sqm,
                    "kualitas_observasi": obs_quality,
                    "file_media": media_file.name,
                    "cuaca": weather if 'weather' in locals() else None
                }
                
                report_json = json.dumps(report_data, indent=2, ensure_ascii=False)
                st.download_button(
                    "📄 Unduh Laporan JSON",
                    report_json,
                    file_name=f"laporan_observasi_{media_file.name.split('.')[0]}.json",
                    mime="application/json"
                )
            
            # Clear progress
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Terjadi kesalahan: {str(e)}")
            progress_bar.empty()
            status_text.empty()

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #87ceeb; margin-top: 2rem;">
    <h3>🌟 Tentang Observatorium Digital</h3>
    <p><strong>Deteksi Hilal Otomatis</strong> menggunakan teknologi Computer Vision terdepan dengan model YOLOv5/v8</p>
    <p><strong>Integrasi SQM</strong> untuk analisis mendalam kondisi kualitas langit</p>  
    <p><strong>Data Cuaca Real-time</strong> dari koordinat lokasi observasi</p>
    <p><strong>Export Multi-format</strong> hasil analisis dalam berbagai format</p>
    <br>
    <p><em>🌙 Membantu komunitas astronomi dalam pengamatan hilal yang akurat dan ilmiah</em></p>
</div>
""", unsafe_allow_html=True)