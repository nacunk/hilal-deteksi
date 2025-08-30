import streamlit as st
import os
from pathlib import Path
import sys
from utils import (
    extract_exif_metadata,
    compute_hilal_position,
    predict_hilal_visibility,
    get_weather,
    calculate_moon_phase,
    get_moon_phase_name,
)


# Panggil ini PALING ATAS, sebelum Streamlit lain
st.set_page_config(
    page_title="🌙 Deteksi Hilal - Observatorium Astronomi", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/hilal-deteksi',
        'Report a bug': 'https://github.com/yourusername/hilal-deteksi/issues',
        'About': "Aplikasi Deteksi Hilal dengan YOLOv5 dan Data Astronomis"
    }
)

st.title("Sistem Deteksi Hilal")

uploaded_file = st.file_uploader("Unggah Gambar Hilal", type=["jpg", "jpeg", "png"])

if uploaded_file:
    with open("temp.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # --- Ekstraksi metadata EXIF ---
    camera, dt, gps_lat, gps_lon = extract_exif_metadata("temp.jpg")

    st.subheader("📷 Metadata Foto")
    st.write(f"Perangkat/Kamera: {camera}")
    st.write(f"Waktu Pengambilan: {dt if dt else 'Tidak tersedia'}")
    st.write(f"Latitude: {gps_lat if gps_lat is not None else 'Tidak tersedia'}")
    st.write(f"Longitude: {gps_lon if gps_lon is not None else 'Tidak tersedia'}")

    # --- Auto-Deteksi Lokasi & Posisi Hilal ---
    if dt and gps_lat is not None and gps_lon is not None:
        alt, az = compute_hilal_position(dt, gps_lat, gps_lon)
        st.subheader("🌙 Posisi Hilal (Otomatis)")
        st.write(f"Altitud: {alt:.2f}°")
        st.write(f"Azimut: {az:.2f}°")

        visibility = predict_hilal_visibility(dt, gps_lat, gps_lon)
        st.subheader("🔮 Prediksi Visibilitas Hilal")
        st.write(visibility)

        # --- Kecerlangan Langit (Estimasi) ---
        weather = get_weather(gps_lat, gps_lon)
        st.subheader("🌤️ Data Cuaca & Kecerlangan Langit")
        st.write(weather)

        # --- Fase Bulan ---
        moon_phase = calculate_moon_phase(dt)
        st.subheader("🌗 Fase Bulan")
        st.write(f"Fase: {moon_phase['phase_name']}")
        st.write(f"Derajat Fase: {moon_phase['phase_degrees']}°")
        st.write(f"Iluminasi: {moon_phase['illumination']}%")
    else:
        st.warning(
            "Metadata EXIF tidak tersedia atau tidak lengkap pada gambar yang diunggah. "
            "Silakan masukkan data waktu, lokasi (koordinat), dan informasi lainnya secara manual pada form di bawah ini untuk melanjutkan analisis hilal."
        )

    # --- Preview gambar ---
    st.image("temp.jpg", caption="Gambar Hilal yang Diupload", use_column_width=True)

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import dengan error handling
try:
    from detect import detect_image, detect_video
    DETECTION_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    DETECTION_AVAILABLE = False

# Auto-create folder assets
assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

# Predefined cities in Indonesia
CITIES = {
    "Jakarta": {"lat": -6.2088, "lon": 106.8456, "timezone": "WIB"},
    "Surabaya": {"lat": -7.2575, "lon": 112.7521, "timezone": "WIB"},
    "Bandung": {"lat": -6.9175, "lon": 107.6191, "timezone": "WIB"},
    "Medan": {"lat": 3.5952, "lon": 98.6722, "timezone": "WIB"},
    "Semarang": {"lat": -6.9667, "lon": 110.4167, "timezone": "WIB"},
    "Makassar": {"lat": -5.1477, "lon": 119.4327, "timezone": "WITA"},
    "Palembang": {"lat": -2.9761, "lon": 104.7754, "timezone": "WIB"},
    "Bandar Lampung": {"lat": -5.4292, "lon": 105.2610, "timezone": "WIB"},
    "Denpasar": {"lat": -8.6705, "lon": 115.2126, "timezone": "WITA"},
    "Balikpapan": {"lat": -1.2379, "lon": 116.8529, "timezone": "WITA"},
    "Pontianak": {"lat": -0.0263, "lon": 109.3425, "timezone": "WIB"},
    "Manado": {"lat": 1.4748, "lon": 124.8421, "timezone": "WIT"},
    "Yogyakarta": {"lat": -7.7956, "lon": 110.3695, "timezone": "WIB"},
    "Malang": {"lat": -7.9797, "lon": 112.6304, "timezone": "WIB"},
    "Padang": {"lat": -0.9471, "lon": 100.4172, "timezone": "WIB"}
}

# Custom CSS for astronomical theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0c0c2e 0%, #1a1a3a 50%, #2d1b69 100%);
        color: white;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0c0c2e 0%, #1a1a3a 50%, #2d1b69 100%);
    }
    
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
    }
    
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        color: white;
    }
    
    .uploadedFile {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        border: 2px dashed rgba(255, 255, 255, 0.3);
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #F7931E, #FF6B35);
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
        transform: translateY(-2px);
    }
    
    .sidebar .sidebar-content {
        background: rgba(12, 12, 46, 0.8);
    }
    
    h1, h2, h3 {
        color: #FFD700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    
    .stSuccess {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid rgba(0, 255, 0, 0.3);
        border-radius: 10px;
    }
    
    .stWarning {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid rgba(255, 193, 7, 0.3);
        border-radius: 10px;
    }
    
    .stError {
        background: rgba(255, 0, 0, 0.1);
        border: 1px solid rgba(255, 0, 0, 0.3);
        border-radius: 10px;
    }
    
    /* Animated stars background */
    .stars {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    }
    
    .star {
        position: absolute;
        width: 2px;
        height: 2px;
        background: white;
        border-radius: 50%;
        animation: twinkle 3s infinite;
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 0; }
        50% { opacity: 1; }
    }
</style>

<div class="stars">
    <div class="star" style="top: 20%; left: 10%; animation-delay: 0s;"></div>
    <div class="star" style="top: 30%; left: 80%; animation-delay: 1s;"></div>
    <div class="star" style="top: 60%; left: 20%; animation-delay: 2s;"></div>
    <div class="star" style="top: 80%; left: 90%; animation-delay: 0.5s;"></div>
    <div class="star" style="top: 15%; left: 50%; animation-delay: 1.5s;"></div>
    <div class="star" style="top: 70%; left: 60%; animation-delay: 2.5s;"></div>
    <div class="star" style="top: 40%; left: 30%; animation-delay: 3s;"></div>
    <div class="star" style="top: 25%; left: 70%; animation-delay: 0.8s;"></div>
</div>
""", unsafe_allow_html=True)

# Header dengan tema astronomis
st.markdown("""
<div style="text-align: center; padding: 20px; margin-bottom: 30px;">
    <h1 style="font-size: 3em; margin-bottom: 10px;">🌙 HILAL DETECTION OBSERVATORY</h1>
    <p style="font-size: 1.2em; color: #B8860B; margin-bottom: 0;">
        ✨ Advanced Crescent Moon Detection with YOLOv5 & Astronomical Data Integration ✨
    </p>
    <div style="margin-top: 15px;">
        <span style="background: rgba(255, 215, 0, 0.2); padding: 5px 15px; border-radius: 20px; margin: 0 10px;">🔭 Computer Vision</span>
        <span style="background: rgba(255, 215, 0, 0.2); padding: 5px 15px; border-radius: 20px; margin: 0 10px;">🌌 Sky Quality</span>
        <span style="background: rgba(255, 215, 0, 0.2); padding: 5px 15px; border-radius: 20px; margin: 0 10px;">🌤️ Weather Data</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Cek status sistem
if not DETECTION_AVAILABLE:
    st.error("⚠️ Sistem deteksi tidak tersedia. Beberapa fungsi mungkin tidak berjalan optimal.")
    st.info("Aplikasi tetap dapat digunakan untuk input data SQM dan cuaca.")

# Sidebar untuk informasi tambahan
with st.sidebar:
    st.markdown("### 🌟 Observatory Status")
    st.markdown(f"**🔧 Detection System:** {'🟢 Online' if DETECTION_AVAILABLE else '🔴 Offline'}")
    st.markdown(f"**📡 Weather API:** 🟢 Active")
    st.markdown(f"**💾 Storage:** 🟢 Ready")
    
    st.markdown("---")
    st.markdown("### 📊 SQM Reference")
    st.markdown("""
    - **< 18**: 🏙️ City Sky (Poor)
    - **18-20**: 🏘️ Suburban (Fair)  
    - **20-21.5**: 🌾 Rural (Good)
    - **> 21.5**: 🌌 Dark Sky (Excellent)
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 Detection Classes")
    st.markdown("""
    - **Hilal**: 🌙 Crescent Moon
    - **Confidence**: Minimum 25%
    - **Resolution**: 640px optimal
    """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # --- Upload Gambar/Video ---
    st.markdown("### 🎬 Stasiun Unggah Media")
    media_file = st.file_uploader(
        "Unggah Gambar/Video Hilal untuk Analisis", 
        type=["jpg", "png", "jpeg", "mp4", "mov", "avi"],
        help="📸 Format Gambar: JPG, PNG, JPEG | 🎥 Format Video: MP4, MOV, AVI"
    )

    if media_file:
        st.success(f"✅ **Media Dimuat:** {media_file.name}")
        
        # Preview media dalam container yang lebih menarik
        with st.container():
            if media_file.type.startswith("image"):
                st.image(media_file, caption="🖼️ Preview - Ready for Analysis", use_column_width=True)
            else:
                st.video(media_file)

with col2:
    # Info panel
    st.markdown("### 📋 Analysis Info")
    st.info("""
    🔍 **Analysis Pipeline:**
    1. Media preprocessing
    2. YOLOv5 object detection  
    3. Hilal identification
    4. Bounding box generation
    5. Confidence scoring
    """)

# --- Input SQM ---
st.markdown("### 🌌 Pengukuran Kualitas Langit")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    sqm = st.number_input(
        "Nilai Sky Quality Meter (SQM):", 
        min_value=0.0, 
        max_value=30.0, 
        step=0.1,
        value=20.0,
        help="🌟 SQM mengukur kegelapan langit - nilai lebih tinggi berarti langit lebih gelap dan baik untuk observasi"
    )

with col2:
    if sqm > 0:
        if sqm < 18:
            quality = "🏙️ City Sky"
            color = "🔴"
        elif sqm < 20:
            quality = "🏘️ Suburban"
            color = "🟡"
        elif sqm < 21.5:
            quality = "🌾 Rural"
            color = "🟢"
        else:
            quality = "🌌 Dark Sky"
            color = "⭐"
        
        st.markdown(f"""
        <div class="metric-container">
            <h4>{color} Sky Quality</h4>
            <p>{quality}</p>
        </div>
        """, unsafe_allow_html=True)

with col3:
    # Visibility prediction
    if sqm > 21:
        visibility = "Excellent"
        vis_color = "🌟"
    elif sqm > 19:
        visibility = "Good"
        vis_color = "✅"
    elif sqm > 17:
        visibility = "Fair"
        vis_color = "⚠️"
    else:
        visibility = "Poor"
        vis_color = "❌"
    
    st.markdown(f"""
    <div class="metric-container">
        <h4>{vis_color} Visibility</h4>
        <p>{visibility}</p>
    </div>
    """, unsafe_allow_html=True)

# --- Input Lokasi dengan opsi Kota atau Koordinat ---
st.markdown("### 🌍 Lokasi & Koordinat")

# Toggle untuk memilih mode input
location_mode = st.radio(
    "Pilih metode input lokasi:",
    ["🏙️ Pilih Kota", "🎯 Koordinat Manual"],
    horizontal=True
)

if location_mode == "🏙️ Pilih Kota":
    selected_city = st.selectbox(
        "Pilih Kota di Indonesia:",
        [""] + list(CITIES.keys()),
        help="🗺️ Koordinat telah dikonfigurasi untuk kota-kota besar di Indonesia"
    )
    
    # Set coordinates from selected city
    if selected_city:
        lat = str(CITIES[selected_city]['lat'])
        lon = str(CITIES[selected_city]['lon'])
    else:
        lat = ""
        lon = ""

else:  # Manual coordinates
    col1, col2 = st.columns(2)
    
    with col1:
        lat = st.text_input(
            "🌐 Latitude", 
            placeholder="-6.175",
            help="📍 Latitude coordinate (example: -6.175 for Jakarta)"
        )
    
    with col2:
        lon = st.text_input(
            "🌐 Longitude", 
            placeholder="106.827",
            help="📍 Longitude coordinate (example: 106.827 for Jakarta)"
        )

# Validasi dan tampilkan koordinat
if lat and lon:
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        st.success(f"✅ **Coordinates Set:** {lat_float}°, {lon_float}°")
        
        # Tampilkan peta mini (placeholder)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: rgba(255, 255, 255, 0.1); border-radius: 10px;">
                <h4>🗺️ Observation Location</h4>
                <p><strong>Coordinates:</strong> {lat_float}°N, {lon_float}°E</p>
                <p><em>Ready for weather data retrieval</em></p>
            </div>
            """, unsafe_allow_html=True)
            
    except ValueError:
        st.error("❌ Invalid coordinate format. Please use decimal numbers.")

# --- Proses Deteksi ---
st.markdown("### 🔍 Deteksi & Analisis Hilal")

detection_col1, detection_col2 = st.columns([1, 1])

with detection_col1:
    process_button = st.button("🚀 Mulai Analisis Deteksi", type="primary")

with detection_col2:
    if media_file:
        st.metric("Media Status", "✅ Ready")
    else:
        st.metric("Media Status", "⏳ Waiting")

if process_button:
    if not media_file:
        st.warning("⚠️ Please upload an image or video file first!")
    else:
        # Enhanced progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Progress phases
            phases = [
                "🔄 Initializing detection system...",
                "💾 Processing uploaded media...",
                "🤖 Running YOLOv5 neural network...",
                "🎯 Identifying hilal objects...",
                "📊 Generating analysis results...",
                "✅ Analysis complete!"
            ]
            
        try:
            # Phase 1: Initialize
            status_text.text(phases[0])
            progress_bar.progress(10)
            
            # Save uploaded file
            status_text.text(phases[1])
            progress_bar.progress(25)
            
            save_path = assets_dir / media_file.name
            with open(save_path, "wb") as f:
                f.write(media_file.getbuffer())
            
            # Phase 2: Detection
            status_text.text(phases[2])
            progress_bar.progress(50)
            
            if DETECTION_AVAILABLE:
                status_text.text(phases[3])
                progress_bar.progress(70)
                
                if media_file.type.startswith("image"):
                    output_path, csv_path = detect_image(str(save_path), "best.pt")
                else:
                    output_path, csv_path = detect_video(str(save_path), "best.pt")
                
                status_text.text(phases[4])
                progress_bar.progress(90)
                
                # Display results
                if output_path and os.path.exists(output_path):
                    status_text.text(phases[5])
                    progress_bar.progress(100)
                    
                    st.success("🎉 **Detection Analysis Complete!**")
                    
                    # Enhanced result display
                    result_col1, result_col2 = st.columns([2, 1])
                    
                    with result_col1:
                        st.markdown("#### 🎯 Detection Results")
                        if media_file.type.startswith("image"):
                            st.image(output_path, caption="🌙 Hilal Detection with Bounding Boxes", use_column_width=True)
                        else:
                            st.video(output_path)
                    
                    with result_col2:
                        st.markdown("#### 📈 Detection Statistics")
                        
                        # Parse CSV to show detection stats
                        if csv_path and os.path.exists(csv_path):
                            import pandas as pd
                            try:
                                df = pd.read_csv(csv_path)
                                detection_count = len(df)
                                if detection_count > 0:
                                    avg_confidence = df['confidence'].mean() * 100
                                    max_confidence = df['confidence'].max() * 100
                                    
                                    st.metric("🎯 Detections Found", detection_count)
                                    st.metric("📊 Avg Confidence", f"{avg_confidence:.1f}%")
                                    st.metric("🏆 Best Confidence", f"{max_confidence:.1f}%")
                                else:
                                    st.metric("🎯 Detections Found", "0")
                                    st.info("No hilal detected in this image/video")
                            except:
                                st.warning("Unable to parse detection data")
                        
                        # Analysis summary
                        st.markdown("#### 🌟 Analysis Summary")
                        st.info(f"""
                        **Media Type:** {media_file.type.split('/')[0].title()}  
                        **File Size:** {len(media_file.getvalue()) / 1024:.1f} KB  
                        **Processing:** YOLOv5 Neural Network  
                        **Confidence Threshold:** 25%
                        """)
                
                else:
                    st.error("❌ Detection processing failed")
            else:
                st.warning("⚠️ Detection system unavailable - showing original file")
                output_path = str(save_path)
                csv_path = None
                progress_bar.progress(100)
                status_text.text("✅ File processed (detection unavailable)")
                
                # Show original file
                if media_file.type.startswith("image"):
                    st.image(output_path, caption="📷 Original Image (Detection Unavailable)", use_column_width=True)
                else:
                    st.video(output_path)
            
            # Enhanced Information Panels
            st.markdown("---")
            
            # Three-column layout for comprehensive info
            info_col1, info_col2, info_col3 = st.columns(3)
            
            with info_col1:
                st.markdown("#### 🌌 Sky Quality Analysis")
                
                # Enhanced SQM display
                sqm_quality_map = {
                    (0, 18): ("🏙️ City Sky", "Light pollution significant", "#FF6B6B"),
                    (18, 20): ("🏘️ Suburban", "Moderate visibility", "#FFE66D"),
                    (20, 21.5): ("🌾 Rural Sky", "Good conditions", "#4ECDC4"),
                    (21.5, 30): ("🌌 Dark Sky", "Excellent visibility", "#45B7D1")
                }
                
                for (min_val, max_val), (label, desc, color) in sqm_quality_map.items():
                    if min_val <= sqm < max_val:
                        st.markdown(f"""
                        <div style="padding: 15px; background: {color}20; border-left: 4px solid {color}; border-radius: 5px; margin: 10px 0;">
                            <h5 style="color: {color}; margin: 0;">{label}</h5>
                            <p style="margin: 5px 0 0 0; color: white;">SQM: {sqm} | {desc}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        break
            
            with info_col2:
                # Weather information
                if lat and lon:
                    st.markdown("#### 🌤️ Kondisi Cuaca")
                    try:
                        status_text.text("🌡️ Retrieving weather data...")
                        weather = get_weather(lat, lon)
                        
                        weather_metrics = [
                            ("🌡️", "Temperature", f"{weather.get('suhu', 'N/A')}°C"),
                            ("💧", "Humidity", f"{weather.get('kelembapan', 'N/A')}%"),
                            ("☁️", "Condition", weather.get('cuaca', 'N/A'))
                        ]
                        
                        for icon, label, value in weather_metrics:
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; padding: 8px; background: rgba(255, 255, 255, 0.1); border-radius: 8px; margin: 5px 0;">
                                <span style="font-size: 1.5em; margin-right: 10px;">{icon}</span>
                                <div>
                                    <strong>{label}:</strong> {value}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.warning(f"⚠️ Weather data unavailable: {str(e)}")
                else:
                    st.info("📍 Set coordinates to view weather data")
            
            with info_col3:
                st.markdown("#### 📥 Unduh Hasil")
                
                # Enhanced download section
                download_options = []
                
                if output_path and os.path.exists(output_path):
                    with open(output_path, "rb") as f:
                        file_ext = Path(output_path).suffix.lower()
                        if file_ext in ['.jpg', '.jpeg', '.png']:
                            mime_type = "image/jpeg"
                            icon = "🖼️"
                            label = "Detection Image"
                        else:
                            mime_type = "video/mp4"
                            icon = "🎥"
                            label = "Detection Video"
                        
                        st.download_button(
                            f"{icon} Download {label}",
                            f,
                            file_name=f"hilal_detection_{Path(output_path).name}",
                            mime=mime_type
                        )
                
                if csv_path and os.path.exists(csv_path):
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            "📊 Download Detection Data",
                            f,
                            file_name=f"hilal_data_{Path(csv_path).name}",
                            mime="text/csv"
                        )
                
                # Analysis report
                if st.button("📋 Generate Report"):
                    report_content = f"""
# Hilal Detection Report
**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis Parameters
- **File:** {media_file.name if media_file else 'N/A'}
- **SQM Value:** {sqm}
- **Location:** {lat}, {lon} 
- **Sky Quality:** {quality if sqm > 0 else 'N/A'}

## Detection Results  
- **Model:** YOLOv5
- **Confidence Threshold:** 25%
- **Status:** {'Complete' if DETECTION_AVAILABLE else 'Limited (Model Unavailable)'}

## Observation Conditions
- **Weather:** {weather.get('cuaca', 'N/A') if lat and lon else 'Not Available'}
- **Temperature:** {weather.get('suhu', 'N/A')}°C
- **Humidity:** {weather.get('kelembapan', 'N/A')}%
                    """
                    
                    st.download_button(
                        "📄 Download Full Report",
                        report_content,
                        file_name=f"hilal_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.md",
                        mime="text/markdown"
                    )
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            progress_bar.empty()
            status_text.empty()

# --- Enhanced Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; background: rgba(255, 255, 255, 0.05); border-radius: 15px; margin-top: 50px;">
    <h3>🌟 Observatorium Deteksi Hilal - Spesifikasi Teknis</h3>
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin: 20px 0;">
        <div style="margin: 10px; padding: 15px; background: rgba(255, 215, 0, 0.1); border-radius: 10px; min-width: 200px;">
            <h4>📊 Ekspor Data</h4>
            <p>Ekspor CSV bounding box<br>Laporan deteksi<br>Ringkasan analisis</p>
        </div>
    </div>
    <p style="margin-top: 30px; color: #B8860B;">
        <strong>🔬 Riset & Pengembangan:</strong> Computer vision untuk observasi astronomi Islam<br>
        <strong>📧 Dukungan:</strong> Untuk astronom, peneliti, dan otoritas kalender Islam<br>
        <strong>🚀 Versi:</strong> Edisi Observatorium dengan Tema Astronomi
    </p>
    <div style="margin-top: 20px;">
        <span style="background: rgba(255, 107, 53, 0.2); color: #FF6B35; padding: 8px 16px; border-radius: 20px; margin: 5px;">🔭 Computer Vision</span>
        <span style="background: rgba(255, 215, 0, 0.2); color: #FFD700; padding: 8px 16px; border-radius: 20px; margin: 5px;">🌙 Deteksi Hilal</span>
        <span style="background: rgba(70, 183, 209, 0.2); color: #46B7D1; padding: 8px 16px; border-radius: 20px; margin: 5px;">📡 API Cuaca</span>
        <span style="background: rgba(78, 205, 196, 0.2); color: #4ECDC4; padding: 8px 16px; border-radius: 20px; margin: 5px;">🌌 Kualitas Langit</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Debug panel (development mode)
if st.checkbox("🔧 Developer Debug Panel"):
    with st.expander("System Diagnostics"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 System Status:**")
            st.write(f"- Detection Available: {DETECTION_AVAILABLE}")
            st.write(f"- Assets Directory: {assets_dir.absolute()}")
            st.write(f"- Working Directory: {Path.cwd()}")
            st.write(f"- Python Path: {sys.path[0]}")
        
        with col2:
            st.write("**📁 File System:**")
            if assets_dir.exists():
                files = list(assets_dir.glob("*"))
                if files:
                    for file in files[-5:]:  # Show last 5 files
                        st.write(f"- {file.name}")
                else:
                    st.write("- No files in assets/")
            else:
                st.write("- Assets directory not found")
        
        st.write("**🌐 Session State:**")
        for key, value in st.session_state.items():
            st.write(f"- {key}: {str(value)[:100]}...")

# Additional imports for enhanced features
try:
    import pandas as pd
except ImportError:
    pd = None

# Lalu untuk HTML, gunakan Streamlit markdown:
if st.sidebar.button("Show Features"):
    st.markdown("""
    <div style="display: flex; flex-wrap: wrap; justify-content: center;">
        <div style="margin: 10px; padding: 15px; background: rgba(255, 215, 0, 0.1); 
             border-radius: 10px; min-width: 200px;">
            <h4>🤖 AI Detection</h4>
            <p>YOLOv5 Neural Network<br>Real-time object detection<br>25% confidence threshold</p>
        </div>
        
        <div style="margin: 10px; padding: 15px; background: rgba(255, 215, 0, 0.1); 
             border-radius: 10px; min-width: 200px;">
            <h4>🌌 Sky Quality</h4>
            <p>SQM Integration<br>Light pollution analysis<br>Visibility prediction</p>
        </div>
        
        <div style="margin: 10px; padding: 15px; background: rgba(255, 215, 0, 0.1); 
             border-radius: 10px; min-width: 200px;">
            <h4>🌍 Location Services</h4>
            <p>City presets available<br>Manual coordinates<br>Weather integration</p>
        </div>
    </div>
    """, unsafe_allow_html=True)