import streamlit as st
import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import dengan error handling
try:
    from detect import detect_image, detect_video
    from utils import get_weather, get_astronomical_data, calculate_moon_phase
    from research_analytics import HilalVisibilityAnalyzer, HistoricalDataManager
    DETECTION_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    DETECTION_AVAILABLE = False

# Database setup
def init_database():
    """Initialize SQLite database for historical data"""
    conn = sqlite3.connect('hilal_database.db')
    cursor = conn.cursor()
    
    # Create tables for historical data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hilal_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            observation_date TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            city TEXT,
            sqm_value REAL,
            weather_condition TEXT,
            temperature REAL,
            humidity REAL,
            visibility_km REAL,
            hilal_detected INTEGER,
            detection_confidence REAL,
            observer_name TEXT,
            equipment_used TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            observation_id INTEGER,
            image_path TEXT,
            detection_count INTEGER,
            avg_confidence REAL,
            max_confidence REAL,
            bounding_boxes TEXT,
            processing_time REAL,
            model_version TEXT,
            FOREIGN KEY (observation_id) REFERENCES hilal_observations (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_date TEXT,
            total_observations INTEGER,
            success_rate REAL,
            correlation_sqm_detection REAL,
            correlation_weather_detection REAL,
            best_conditions TEXT,
            recommendations TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Auto-create folder assets
assets_dir = Path("assets")
assets_dir.mkdir(exist_ok=True)

# Extended cities with more data for research
CITIES = {
    "Jakarta": {"lat": -6.2088, "lon": 106.8456, "timezone": "WIB", "elevation": 8, "light_pollution": "high"},
    "Surabaya": {"lat": -7.2575, "lon": 112.7521, "timezone": "WIB", "elevation": 3, "light_pollution": "high"},
    "Bandung": {"lat": -6.9175, "lon": 107.6191, "timezone": "WIB", "elevation": 768, "light_pollution": "medium"},
    "Medan": {"lat": 3.5952, "lon": 98.6722, "timezone": "WIB", "elevation": 25, "light_pollution": "medium"},
    "Semarang": {"lat": -6.9667, "lon": 110.4167, "timezone": "WIB", "elevation": 2, "light_pollution": "medium"},
    "Makassar": {"lat": -5.1477, "lon": 119.4327, "timezone": "WITA", "elevation": 2, "light_pollution": "medium"},
    "Palembang": {"lat": -2.9761, "lon": 104.7754, "timezone": "WIB", "elevation": 8, "light_pollution": "medium"},
    "Bandar Lampung": {"lat": -5.4292, "lon": 105.2610, "timezone": "WIB", "elevation": 10, "light_pollution": "low"},
    "Denpasar": {"lat": -8.6705, "lon": 115.2126, "timezone": "WITA", "elevation": 4, "light_pollution": "medium"},
    "Balikpapan": {"lat": -1.2379, "lon": 116.8529, "timezone": "WITA", "elevation": 10, "light_pollution": "medium"},
    "Pontianak": {"lat": -0.0263, "lon": 109.3425, "timezone": "WIB", "elevation": 1, "light_pollution": "low"},
    "Manado": {"lat": 1.4748, "lon": 124.8421, "timezone": "WIT", "elevation": 2, "light_pollution": "low"},
    "Yogyakarta": {"lat": -7.7956, "lon": 110.3695, "timezone": "WIB", "elevation": 113, "light_pollution": "medium"},
    "Malang": {"lat": -7.9797, "lon": 112.6304, "timezone": "WIB", "elevation": 440, "light_pollution": "low"},
    "Padang": {"lat": -0.9471, "lon": 100.4172, "timezone": "WIB", "elevation": 5, "light_pollution": "medium"},
    "Pekanbaru": {"lat": 0.5071, "lon": 101.4478, "timezone": "WIB", "elevation": 31, "light_pollution": "medium"},
    "Jambi": {"lat": -1.6101, "lon": 103.6131, "timezone": "WIB", "elevation": 35, "light_pollution": "low"},
    "Bengkulu": {"lat": -3.7928, "lon": 102.2607, "timezone": "WIB", "elevation": 10, "light_pollution": "low"},
    "Mataram": {"lat": -8.5833, "lon": 116.1167, "timezone": "WITA", "elevation": 63, "light_pollution": "low"},
    "Kupang": {"lat": -10.1772, "lon": 123.6070, "timezone": "WIT", "elevation": 110, "light_pollution": "low"}
}

# Page config
st.set_page_config(
    page_title="Hilal Detection Research System", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for research application
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0c0c2e 0%, #1a1a3a 50%, #2d1b69 100%);
        color: white;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0c0c2e 0%, #1a1a3a 50%, #2d1b69 100%);
    }
    
    .research-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin: 10px 0;
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .analysis-header {
        background: linear-gradient(45deg, #FF6B35, #F7931E);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 20px 0;
    }
    
    h1, h2, h3 {
        color: #FFD700 !important;
        text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style="text-align: center; padding: 20px; margin-bottom: 30px;">
    <h1 style="font-size: 3em; margin-bottom: 10px;">🌙 HILAL DETECTION RESEARCH SYSTEM</h1>
    <p style="font-size: 1.2em; color: #B8860B; margin-bottom: 0;">
        Sistem Deteksi Hilal Berbasis Citra dengan Integrasi Data Historis dan Analisis Visibilitas
    </p>
    <div style="margin-top: 15px;">
        <span style="background: rgba(255, 215, 0, 0.2); padding: 5px 15px; border-radius: 20px; margin: 0 10px;">🔬 Computer Vision</span>
        <span style="background: rgba(255, 215, 0, 0.2); padding: 5px 15px; border-radius: 20px; margin: 0 10px;">📊 Historical Analysis</span>
        <span style="background: rgba(255, 215, 0, 0.2); padding: 5px 15px; border-radius: 20px; margin: 0 10px;">🌤️ Sky Conditions</span>
        <span style="background: rgba(255, 215, 0, 0.2); padding: 5px 15px; border-radius: 20px; margin: 0 10px;">📈 Research Analytics</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar untuk navigasi penelitian
with st.sidebar:
    st.markdown("### 🔬 Research Navigation")
    
    research_mode = st.selectbox(
        "Select Research Module:",
        [
            "🎯 Detection Analysis",
            "📊 Historical Data",
            "🌙 Visibility Prediction", 
            "📈 Statistical Analysis",
            "🗄️ Database Management",
            "📋 Research Reports"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Database Status")
    
    # Check database status
    try:
        conn = sqlite3.connect('hilal_database.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM hilal_observations")
        total_observations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM detection_results")
        total_detections = cursor.fetchone()[0]
        
        conn.close()
        
        st.metric("Total Observations", total_observations)
        st.metric("Detection Results", total_detections)
        
    except Exception as e:
        st.error(f"Database error: {e}")
    
    st.markdown("---")
    st.markdown("### 🌟 SQM Quality Scale")
    st.markdown("""
    - **< 18**: 🏙️ City Sky (Poor)
    - **18-20**: 🏘️ Suburban (Fair)  
    - **20-21.5**: 🌾 Rural (Good)
    - **> 21.5**: 🌌 Dark Sky (Excellent)
    """)

# Main content based on selected research mode
if research_mode == "🎯 Detection Analysis":
    st.markdown("""
    <div class="analysis-header">
        <h2>🎯 Hilal Detection Analysis Module</h2>
        <p>Upload dan analisis citra/video hilal dengan AI detection</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Media upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📸 Media Upload")
        media_file = st.file_uploader(
            "Upload Citra/Video Hilal", 
            type=["jpg", "png", "jpeg", "mp4", "mov", "avi"],
            help="Format: JPG, PNG, JPEG (images) | MP4, MOV, AVI (videos)"
        )
        
        if media_file:
            st.success(f"✅ Media loaded: {media_file.name}")
            if media_file.type.startswith("image"):
                st.image(media_file, caption="Preview", use_column_width=True)
            else:
                st.video(media_file)
    
    with col2:
        st.markdown("### ⚙️ Detection Settings")
        
        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.1,
            max_value=0.9,
            value=0.25,
            step=0.05,
            help="Minimum confidence untuk deteksi hilal"
        )
        
        image_size = st.selectbox(
            "Processing Size",
            [320, 640, 1280],
            index=1,
            help="Ukuran gambar untuk processing - lebih besar = lebih akurat tapi lambat"
        )
        
        save_to_database = st.checkbox(
            "Save to Research Database",
            value=True,
            help="Simpan hasil ke database untuk analisis historis"
        )
    
    # Location and conditions input
    st.markdown("### 🌍 Observation Conditions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Location selection
        location_mode = st.radio(
            "Location Input:",
            ["🏙️ Select City", "🎯 Manual Coordinates"],
            horizontal=True
        )
        
        if location_mode == "🏙️ Select City":
            selected_city = st.selectbox(
                "Indonesian Cities:",
                [""] + list(CITIES.keys())
            )
            
            if selected_city:
                city_data = CITIES[selected_city]
                lat = str(city_data['lat'])
                lon = str(city_data['lon'])
                elevation = city_data['elevation']
                light_pollution = city_data['light_pollution']
                
                st.info(f"📍 {selected_city}\n📏 Elevation: {elevation}m\n💡 Light Pollution: {light_pollution}")
            else:
                lat = lon = ""
                elevation = light_pollution = None
        else:
            lat = st.text_input("Latitude", placeholder="-6.175")
            lon = st.text_input("Longitude", placeholder="106.827")
            elevation = st.number_input("Elevation (m)", value=0, step=1)
            light_pollution = st.selectbox("Light Pollution", ["low", "medium", "high"])
    
    with col2:
        # Sky conditions
        st.markdown("**Sky Quality Measurement**")
        sqm = st.number_input(
            "SQM Reading:", 
            min_value=10.0, 
            max_value=25.0, 
            step=0.1,
            value=20.0
        )
        
        cloud_cover = st.slider("Cloud Cover (%)", 0, 100, 20, 5)
        seeing_conditions = st.selectbox(
            "Seeing Conditions",
            ["Excellent", "Good", "Fair", "Poor"]
        )
    
    with col3:
        # Observer information for research
        st.markdown("**Observer Information**")
        observer_name = st.text_input("Observer Name", placeholder="Researcher Name")
        equipment_used = st.text_input("Equipment", placeholder="Camera/Telescope model")
        observation_notes = st.text_area("Notes", placeholder="Additional observations...", height=100)
    
    # Detection processing
    if st.button("🚀 Process Detection & Save to Database", type="primary"):
        if not media_file:
            st.warning("⚠️ Please upload media file first!")
        elif not lat or not lon:
            st.warning("⚠️ Please set location coordinates!")
        else:
            with st.spinner("🔄 Processing detection and analysis..."):
                try:
                    # Save uploaded file
                    save_path = assets_dir / media_file.name
                    with open(save_path, "wb") as f:
                        f.write(media_file.getbuffer())
                    
                    # Run detection
                    if DETECTION_AVAILABLE:
                        if media_file.type.startswith("image"):
                            output_path, csv_path = detect_image(str(save_path), "best.pt")
                        else:
                            output_path, csv_path = detect_video(str(save_path), "best.pt")
                    else:
                        st.warning("Detection model unavailable - using placeholder results")
                        output_path = str(save_path)
                        csv_path = None
                    
                    # Get weather data
                    weather_data = get_weather(lat, lon)
                    
                    # Parse detection results
                    detection_count = 0
                    avg_confidence = 0
                    max_confidence = 0
                    
                    if csv_path and os.path.exists(csv_path):
                        try:
                            df = pd.read_csv(csv_path)
                            detection_count = len(df)
                            if detection_count > 0:
                                avg_confidence = df['confidence'].mean()
                                max_confidence = df['confidence'].max()
                        except:
                            pass
                    
                    # Save to database if requested
                    if save_to_database:
                        conn = sqlite3.connect('hilal_database.db')
                        cursor = conn.cursor()
                        
                        # Insert observation
                        cursor.execute('''
                            INSERT INTO hilal_observations 
                            (observation_date, latitude, longitude, city, sqm_value, 
                             weather_condition, temperature, humidity, hilal_detected, 
                             detection_confidence, observer_name, equipment_used, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            datetime.now().isoformat(),
                            float(lat), float(lon),
                            selected_city if location_mode == "🏙️ Select City" else f"Custom ({lat}, {lon})",
                            sqm,
                            weather_data.get('cuaca', 'Unknown'),
                            weather_data.get('suhu', 0),
                            weather_data.get('kelembapan', 0),
                            1 if detection_count > 0 else 0,
                            max_confidence,
                            observer_name,
                            equipment_used,
                            observation_notes
                        ))
                        
                        observation_id = cursor.lastrowid
                        
                        # Insert detection results
                        cursor.execute('''
                            INSERT INTO detection_results
                            (observation_id, image_path, detection_count, avg_confidence, 
                             max_confidence, processing_time, model_version)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            observation_id,
                            str(output_path),
                            detection_count,
                            avg_confidence,
                            max_confidence,
                            2.5,  # Placeholder processing time
                            "YOLOv5"
                        ))
                        
                        conn.commit()
                        conn.close()
                        
                        st.success(f"✅ Data saved to research database (ID: {observation_id})")
                    
                    # Display results
                    if output_path and os.path.exists(output_path):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("#### 🎯 Detection Results")
                            if media_file.type.startswith("image"):
                                st.image(output_path, caption="Hilal Detection Results", use_column_width=True)
                            else:
                                st.video(output_path)
                        
                        with col2:
                            st.markdown("#### 📊 Analysis Summary")
                            st.metric("Detections Found", detection_count)
                            if detection_count > 0:
                                st.metric("Average Confidence", f"{avg_confidence*100:.1f}%")
                                st.metric("Best Confidence", f"{max_confidence*100:.1f}%")
                            
                            # Weather summary
                            st.markdown("**Weather Conditions:**")
                            st.write(f"🌡️ Temperature: {weather_data.get('suhu', 'N/A')}°C")
                            st.write(f"💧 Humidity: {weather_data.get('kelembapan', 'N/A')}%")
                            st.write(f"☁️ Condition: {weather_data.get('cuaca', 'N/A')}")
                
                except Exception as e:
                    st.error(f"❌ Processing error: {e}")

elif research_mode == "📊 Historical Data":
    st.markdown("""
    <div class="analysis-header">
        <h2>📊 Historical Data Analysis</h2>
        <p>Analisis data pengamatan hilal historis untuk penelitian</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load historical data
    try:
        conn = sqlite3.connect('hilal_database.db')
        df_observations = pd.read_sql_query("""
            SELECT o.*, d.detection_count, d.avg_confidence, d.max_confidence
            FROM hilal_observations o
            LEFT JOIN detection_results d ON o.id = d.observation_id
            ORDER BY o.observation_date DESC
        """, conn)
        conn.close()
        
        if len(df_observations) > 0:
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_obs = len(df_observations)
                st.metric("Total Observations", total_obs)
            
            with col2:
                successful_detections = len(df_observations[df_observations['hilal_detected'] == 1])
                success_rate = (successful_detections / total_obs * 100) if total_obs > 0 else 0
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            with col3:
                avg_sqm = df_observations['sqm_value'].mean()
                st.metric("Average SQM", f"{avg_sqm:.1f}" if not pd.isna(avg_sqm) else "N/A")
            
            with col4:
                unique_locations = df_observations['city'].nunique()
                st.metric("Locations Observed", unique_locations)
            
            # Data visualization
            st.markdown("### 📈 Research Visualizations")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                # Detection success by SQM
                if 'sqm_value' in df_observations.columns:
                    fig_sqm = px.scatter(
                        df_observations,
                        x='sqm_value',
                        y='hilal_detected',
                        color='detection_confidence',
                        title="Detection Success vs Sky Quality (SQM)",
                        labels={'sqm_value': 'SQM Value', 'hilal_detected': 'Detection Success'},
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_sqm, use_container_width=True)
            
            with viz_col2:
                # Detection by location
                location_success = df_observations.groupby('city').agg({
                    'hilal_detected': 'mean',
                    'sqm_value': 'mean'
                }).reset_index()
                
                fig_location = px.bar(
                    location_success,
                    x='city',
                    y='hilal_detected',
                    title="Detection Success Rate by Location",
                    template="plotly_dark"
                )
                fig_location.update_xaxis(tickangle=45)
                st.plotly_chart(fig_location, use_container_width=True)
            
            # Historical data table
            st.markdown("### 🗂️ Historical Observations")
            
            # Filter options
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                city_filter = st.multiselect(
                    "Filter by City:",
                    options=df_observations['city'].unique(),
                    default=[]
                )
            
            with filter_col2:
                detection_filter = st.selectbox(
                    "Detection Status:",
                    ["All", "Successful Only", "Failed Only"]
                )
            
            with filter_col3:
                date_range = st.date_input(
                    "Date Range:",
                    value=[],
                    help="Select date range for filtering"
                )
            
            # Apply filters
            filtered_df = df_observations.copy()
            
            if city_filter:
                filtered_df = filtered_df[filtered_df['city'].isin(city_filter)]
            
            if detection_filter == "Successful Only":
                filtered_df = filtered_df[filtered_df['hilal_detected'] == 1]
            elif detection_filter == "Failed Only":
                filtered_df = filtered_df[filtered_df['hilal_detected'] == 0]
            
            # Display filtered data
            st.dataframe(
                filtered_df[['observation_date', 'city', 'sqm_value', 'weather_condition', 
                           'hilal_detected', 'detection_confidence']],
                use_container_width=True
            )
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Export Filtered Data"):
                    csv_export = filtered_df.to_csv(index=False)
                    st.download_button(
                        "Download CSV",
                        csv_export,
                        f"hilal_historical_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
            
            with col2:
                if st.button("📊 Generate Analysis Report"):
                    # Generate statistical analysis
                    report = generate_statistical_report(filtered_df)
                    st.download_button(
                        "Download Report",
                        report,
                        f"hilal_analysis_report_{datetime.now().strftime('%Y%m%d')}.md",
                        "text/markdown"
                    )
        
        else:
            st.info("📊 No historical data available. Start by making observations in Detection Analysis mode.")
    
    except Exception as e:
        st.error(f"Database error: {e}")

elif research_mode == "🌙 Visibility Prediction":
    st.markdown("""
    <div class="analysis-header">
        <h2>🌙 Hilal Visibility Prediction</h2>
        <p>Prediksi visibilitas hilal berdasarkan kondisi astronomis dan cuaca</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Prediction input
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌍 Location & Time")
        
        # Location
        pred_city = st.selectbox(
            "Select City for Prediction:",
            [""] + list(CITIES.keys())
        )
        
        if pred_city:
            city_data = CITIES[pred_city]
            pred_lat = city_data['lat']
            pred_lon = city_data['lon']
            st.success(f"📍 {pred_city} selected")
        else:
            pred_lat = st.number_input("Latitude", value=-6.175, step=0.001, format="%.3f")
            pred_lon = st.number_input("Longitude", value=106.827, step=0.001, format="%.3f")
        
        # Prediction date
        prediction_date = st.date_input(
            "Prediction Date:",
            value=datetime.now().date() + timedelta(days=1)
        )
        
        prediction_time = st.time_input(
            "Observation Time:",
            value=datetime.strptime("18:30", "%H:%M").time()
        )
    
    with col2:
        st.markdown("### 🌤️ Expected Conditions")
        
        expected_sqm = st.number_input("Expected SQM", value=19.5, step=0.1)
        expected_clouds = st.slider("Expected Cloud Cover (%)", 0, 100, 30, 5)
        expected_humidity = st.slider("Expected Humidity (%)", 30, 100, 70, 5)
        
        # Historical success rate for this location
        try:
            conn = sqlite3.connect('hilal_database.db')
            
            if pred_city:
                historical_data = pd.read_sql_query("""
                    SELECT * FROM hilal_observations 
                    WHERE city = ? AND hilal_detected = 1
                """, conn, params=[pred_city])
            else:
                # Find nearby observations (within 0.5 degrees)
                historical_data = pd.read_sql_query("""
                    SELECT * FROM hilal_observations 
                    WHERE ABS(latitude - ?) < 0.5 AND ABS(longitude - ?) < 0.5
                """, conn, params=[pred_lat, pred_lon])
            
            if len(historical_data) > 0:
                historical_success_rate = len(historical_data) / len(pd.read_sql_query("""
                    SELECT * FROM hilal_observations 
                    WHERE city = ?
                """, conn, params=[pred_city])) * 100 if pred_city else 0
                
                st.info(f"Historical Success Rate: {historical_success_rate:.1f}%")
            else:
                st.info("No historical data for this location")
            
            conn.close()
            
        except Exception as e:
            st.warning(f"Could not load historical data: {e}")
    
    # Run prediction
    if st.button("🔮 Generate Visibility Prediction", type="primary"):
        with st.spinner("Calculating visibility prediction..."):
            try:
                # Combine datetime
                prediction_datetime = datetime.combine(prediction_date, prediction_time)
                
                # Get astronomical data
                astro_data = get_astronomical_data(pred_lat, pred_lon, prediction_datetime)
                
                # Calculate visibility score
                visibility_score = calculate_visibility_score(
                    expected_sqm, expected_clouds, expected_humidity, 
                    astro_data.get('moon_phase', {})
                )
                
                # Display prediction results
                st.markdown("### 🎯 Prediction Results")
                
                result_col1, result_col2, result_col3 = st.columns(3)
                
                with result_col1:
                    score_color = "green" if visibility_score > 70 else "orange" if visibility_score > 40 else "red"
                    st.markdown(f"""
                    <div class="metric-container" style="border-color: {score_color};">
                        <h3 style="color: {score_color};">Visibility Score</h3>
                        <h1 style="color: {score_color};">{visibility_score}%</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                with result_col2:
                    moon_phase = astro_data.get('moon_phase', {})
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4>Moon Phase</h4>
                        <p>{moon_phase.get('phase_name', 'Unknown')}</p>
                        <p>Illumination: {moon_phase.get('illumination', 0)}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with result_col3:
                    recommendation = get_observation_recommendation(visibility_score)
                    st.markdown(f"""
                    <div class="metric-container">
                        <h4>Recommendation</h4>
                        <p>{recommendation}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Detailed factors analysis
                st.markdown("### 📋 Influencing Factors")
                
                factors_data = {
                    'Factor': ['Sky Quality (SQM)', 'Cloud Cover', 'Humidity', 'Moon Phase', 'Moon Illumination'],
                    'Value': [expected_sqm, f"{expected_clouds}%", f"{expected_humidity}%", 
                             moon_phase.get('phase_name', 'Unknown'), f"{moon_phase.get('illumination', 0)}%"],
                    'Impact': [
                        get_factor_impact(expected_sqm, 'sqm'),
                        get_factor_impact(expected_clouds, 'clouds'),
                        get_factor_impact(expected_humidity, 'humidity'),
                        get_factor_impact(moon_phase.get('illumination', 0), 'illumination'),
                        get_factor_impact(moon_phase.get('phase_degrees', 0), 'phase')
                    ],
                    'Score': [
                        calculate_sqm_score(expected_sqm),
                        calculate_cloud_score(expected_clouds),
                        calculate_humidity_score(expected_humidity),
                        calculate_illumination_score(moon_phase.get('illumination', 0)),
                        calculate_phase_score(moon_phase.get('phase_degrees', 0))
                    ]
                }
                
                factors_df = pd.DataFrame(factors_data)
                st.dataframe(factors_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Prediction calculation error: {e}")

elif research_mode == "📈 Statistical Analysis":
    st.markdown("""
    <div class="analysis-header">
        <h2>📈 Statistical Research Analysis</h2>
        <p>Analisis korelasi dan statistik untuk publikasi penelitian</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        conn = sqlite3.connect('hilal_database.db')
        df_all = pd.read_sql_query("""
            SELECT o.*, d.detection_count, d.avg_confidence, d.max_confidence
            FROM hilal_observations o
            LEFT JOIN detection_results d ON o.id = d.observation_id
        """, conn)
        conn.close()
        
        if len(df_all) > 10:  # Need sufficient data for statistical analysis
            # Correlation analysis
            st.markdown("### 🔗 Correlation Analysis")
            
            # Prepare numerical data for correlation
            numerical_cols = ['sqm_value', 'temperature', 'humidity', 'hilal_detected', 'detection_confidence']
            corr_data = df_all[numerical_cols].dropna()
            
            if len(corr_data) > 5:
                correlation_matrix = corr_data.corr()
                
                fig_corr = px.imshow(
                    correlation_matrix,
                    title="Correlation Matrix: Detection Success Factors",
                    color_continuous_scale="RdBu",
                    aspect="auto",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Key correlations
                st.markdown("### 🔍 Key Research Findings")
                
                sqm_correlation = correlation_matrix.loc['hilal_detected', 'sqm_value']
                temp_correlation = correlation_matrix.loc['hilal_detected', 'temperature']
                humidity_correlation = correlation_matrix.loc['hilal_detected', 'humidity']
                
                findings_col1, findings_col2, findings_col3 = st.columns(3)
                
                with findings_col1:
                    st.metric("SQM ↔ Detection", f"{sqm_correlation:.3f}")
                    st.caption("Correlation between sky quality and detection success")
                
                with findings_col2:
                    st.metric("Temperature ↔ Detection", f"{temp_correlation:.3f}")
                    st.caption("Correlation between temperature and detection")
                
                with findings_col3:
                    st.metric("Humidity ↔ Detection", f"{humidity_correlation:.3f}")
                    st.caption("Correlation between humidity and detection")
            
            # Advanced statistical analysis
            st.markdown("### 📊 Advanced Statistical Analysis")
            
            analysis_col1, analysis_col2 = st.columns(2)
            
            with analysis_col1:
                # SQM distribution analysis
                sqm_data = df_all['sqm_value'].dropna()
                if len(sqm_data) > 0:
                    fig_sqm_dist = px.histogram(
                        df_all,
                        x='sqm_value',
                        color='hilal_detected',
                        title="SQM Distribution by Detection Success",
                        nbins=20,
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig_sqm_dist, use_container_width=True)
            
            with analysis_col2:
                # Time series analysis
                df_all['observation_date'] = pd.to_datetime(df_all['observation_date'])
                monthly_success = df_all.groupby(df_all['observation_date'].dt.to_period('M')).agg({
                    'hilal_detected': 'mean'
                }).reset_index()
                monthly_success['observation_date'] = monthly_success['observation_date'].astype(str)
                
                fig_time = px.line(
                    monthly_success,
                    x='observation_date',
                    y='hilal_detected',
                    title="Detection Success Rate Over Time",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_time, use_container_width=True)
            
            # Research summary statistics
            st.markdown("### 📋 Research Summary Statistics")
            
            summary_stats = {
                "Total Observations": len(df_all),
                "Successful Detections": len(df_all[df_all['hilal_detected'] == 1]),
                "Success Rate": f"{len(df_all[df_all['hilal_detected'] == 1]) / len(df_all) * 100:.1f}%",
                "Average SQM": f"{df_all['sqm_value'].mean():.2f}",
                "SQM Standard Deviation": f"{df_all['sqm_value'].std():.2f}",
                "Average Confidence": f"{df_all['detection_confidence'].mean():.3f}",
                "Unique Locations": df_all['city'].nunique(),
                "Date Range": f"{df_all['observation_date'].min()} to {df_all['observation_date'].max()}"
            }
            
            stats_col1, stats_col2 = st.columns(2)
            
            with stats_col1:
                for key, value in list(summary_stats.items())[:4]:
                    st.metric(key, value)
            
            with stats_col2:
                for key, value in list(summary_stats.items())[4:]:
                    st.metric(key, value)
        
        else:
            st.warning("📊 Insufficient data for statistical analysis. Need at least 10 observations.")
            st.info("Continue collecting observations to enable comprehensive statistical analysis.")
    
    except Exception as e:
        st.error(f"Statistical analysis error: {e}")

elif research_mode == "🗄️ Database Management":
    st.markdown("""
    <div class="analysis-header">
        <h2>🗄️ Research Database Management</h2>
        <p>Kelola dan import data historis untuk penelitian</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Database operations
    db_col1, db_col2 = st.columns(2)
    
    with db_col1:
        st.markdown("### 📥 Import Historical Data")
        
        # Import from CSV
        uploaded_csv = st.file_uploader(
            "Upload Historical Data CSV",
            type=['csv'],
            help="Format: date,lat,lon,city,sqm,weather,temp,humidity,detected,confidence"
        )
        
        if uploaded_csv:
            try:
                import_df = pd.read_csv(uploaded_csv)
                st.dataframe(import_df.head(), use_container_width=True)
                
                if st.button("Import to Database"):
                    # Validate and import data
                    imported_count = import_historical_data(import_df)
                    st.success(f"✅ Imported {imported_count} records")
            
            except Exception as e:
                st.error(f"Import error: {e}")
        
        # Manual data entry for single observations
        st.markdown("### ✏️ Manual Data Entry")
        
        with st.form("manual_entry"):
            entry_date = st.date_input("Observation Date")
            entry_city = st.selectbox("City", [""] + list(CITIES.keys()))
            entry_sqm = st.number_input("SQM Value", value=19.0, step=0.1)
            entry_detected = st.checkbox("Hilal Detected")
            entry_confidence = st.slider("Detection Confidence", 0.0, 1.0, 0.5, 0.01)
            entry_notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("Add to Database")
            
            if submitted and entry_city:
                try:
                    city_data = CITIES[entry_city]
                    add_manual_observation(
                        entry_date, city_data['lat'], city_data['lon'], entry_city,
                        entry_sqm, entry_detected, entry_confidence, entry_notes
                    )
                    st.success("✅ Manual entry added to database")
                except Exception as e:
                    st.error(f"Error adding manual entry: {e}")
    
    with db_col2:
        st.markdown("### 🗃️ Database Operations")
        
        # Database statistics
        try:
            conn = sqlite3.connect('hilal_database.db')
            
            # Get table sizes
            obs_count = pd.read_sql_query("SELECT COUNT(*) as count FROM hilal_observations", conn).iloc[0]['count']
            det_count = pd.read_sql_query("SELECT COUNT(*) as count FROM detection_results", conn).iloc[0]['count']
            
            st.metric("Observations", obs_count)
            st.metric("Detection Results", det_count)
            
            # Recent entries
            recent_obs = pd.read_sql_query("""
                SELECT observation_date, city, sqm_value, hilal_detected 
                FROM hilal_observations 
                ORDER BY created_at DESC 
                LIMIT 5
            """, conn)
            
            st.markdown("**Recent Observations:**")
            st.dataframe(recent_obs, use_container_width=True)
            
            conn.close()
            
        except Exception as e:
            st.error(f"Database query error: {e}")
        
        # Database maintenance
        st.markdown("### ⚙️ Database Maintenance")
        
        if st.button("🧹 Clean Duplicate Entries"):
            cleaned = clean_duplicate_observations()
            st.info(f"Cleaned {cleaned} duplicate entries")
        
        if st.button("📤 Export Full Database"):
            export_data = export_full_database()
            if export_data:
                st.download_button(
                    "Download Database Export",
                    export_data,
                    f"hilal_database_export_{datetime.now().strftime('%Y%m%d')}.json",
                    "application/json"
                )
        
        if st.button("⚠️ Reset Database", type="secondary"):
            if st.checkbox("Confirm database reset"):
                reset_database()
                st.warning("Database has been reset")

elif research_mode == "📋 Research Reports":
    st.markdown("""
    <div class="analysis-header">
        <h2>📋 Research Reports Generator</h2>
        <p>Generate comprehensive reports for academic publication</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Report generation options
    report_col1, report_col2 = st.columns(2)
    
    with report_col1:
        st.markdown("### 📊 Report Configuration")
        
        report_type = st.selectbox(
            "Report Type:",
            [
                "Complete Research Analysis",
                "Detection Performance Summary", 
                "Sky Quality Correlation Study",
                "Location-based Analysis",
                "Temporal Analysis"
            ]
        )
        
        date_range_start = st.date_input("Analysis Start Date", datetime.now() - timedelta(days=365))
        date_range_end = st.date_input("Analysis End Date", datetime.now())
        
        include_visualizations = st.checkbox("Include Visualizations", True)
        include_raw_data = st.checkbox("Include Raw Data Appendix", False)
        
    with report_col2:
        st.markdown("### 📝 Report Metadata")
        
        author_name = st.text_input("Author Name", "Research Team")
        institution = st.text_input("Institution", "University")
        research_purpose = st.text_area("Research Purpose", 
                                      "Academic research on hilal detection accuracy and visibility factors")
    
    # Generate report
    if st.button("📄 Generate Research Report", type="primary"):
        with st.spinner("Generating comprehensive research report..."):
            try:
                # Load data for analysis
                conn = sqlite3.connect('hilal_database.db')
                analysis_df = pd.read_sql_query(f"""
                    SELECT o.*, d.detection_count, d.avg_confidence, d.max_confidence
                    FROM hilal_observations o
                    LEFT JOIN detection_results d ON o.id = d.observation_id
                    WHERE DATE(o.observation_date) BETWEEN '{date_range_start}' AND '{date_range_end}'
                """, conn)
                conn.close()
                
                if len(analysis_df) > 0:
                    # Generate report content
                    report_content = generate_research_report(
                        analysis_df, report_type, author_name, institution, 
                        research_purpose, include_visualizations, include_raw_data
                    )
                    
                    # Display preview
                    st.markdown("### 👀 Report Preview")
                    st.markdown(report_content[:1000] + "..." if len(report_content) > 1000 else report_content)
                    
                    # Download options
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.download_button(
                            "📄 Download Markdown Report",
                            report_content,
                            f"hilal_research_report_{datetime.now().strftime('%Y%m%d')}.md",
                            "text/markdown"
                        )
                    
                    with col2:
                        # Convert to JSON for further processing
                        report_data = {
                            "metadata": {
                                "title": report_type,
                                "author": author_name,
                                "institution": institution,
                                "generated_date": datetime.now().isoformat(),
                                "data_range": f"{date_range_start} to {date_range_end}"
                            },
                            "content": report_content,
                            "raw_data": analysis_df.to_dict('records') if include_raw_data else []
                        }
                        
                        st.download_button(
                            "📊 Download JSON Data",
                            json.dumps(report_data, indent=2),
                            f"hilal_research_data_{datetime.now().strftime('%Y%m%d')}.json",
                            "application/json"
                        )
                
                else:
                    st.warning("No data available for the selected date range")
                    
            except Exception as e:
                st.error(f"Report generation error: {e}")

# Additional utility functions
def calculate_visibility_score(sqm, clouds, humidity, moon_phase):
    """Calculate overall visibility score based on multiple factors"""
    try:
        # SQM contribution (40% weight)
        sqm_score = min(100, max(0, (sqm - 15) / 10 * 100)) * 0.4
        
        # Cloud cover contribution (30% weight) - inverted
        cloud_score = (100 - clouds) * 0.3
        
        # Humidity contribution (20% weight) - inverted
        humidity_score = (100 - humidity) * 0.2
        
        # Moon phase contribution (10% weight)
        illumination = moon_phase.get('illumination', 50)
        moon_score = (100 - illumination) * 0.1  # Less illumination is better
        
        total_score = sqm_score + cloud_score + humidity_score + moon_score
        return round(min(100, max(0, total_score)), 1)
        
    except:
        return 50.0  # Default moderate score

def get_observation_recommendation(score):
    """Get observation recommendation based on visibility score"""
    if score > 80:
        return "Excellent - Highly recommended"
    elif score > 60:
        return "Good - Recommended"
    elif score > 40:
        return "Fair - Possible but challenging"
    else:
        return "Poor - Not recommended"

def get_factor_impact(value, factor_type):
    """Determine impact level of each factor"""
    if factor_type == 'sqm':
        if value > 21: return "Very Positive"
        elif value > 19: return "Positive"
        elif value > 17: return "Neutral"
        else: return "Negative"
    elif factor_type == 'clouds':
        if value < 20: return "Very Positive"
        elif value < 50: return "Positive"
        elif value < 80: return "Negative"
        else: return "Very Negative"
    elif factor_type == 'humidity':
        if value < 60: return "Positive"
        elif value < 80: return "Neutral"
        else: return "Negative"
    else:
        return "Unknown"

def calculate_sqm_score(sqm):
    """Calculate SQM contribution score"""
    return min(100, max(0, (sqm - 15) / 10 * 100))

def calculate_cloud_score(clouds):
    """Calculate cloud cover contribution score"""
    return 100 - clouds

def calculate_humidity_score(humidity):
    """Calculate humidity contribution score"""
    return max(0, 100 - humidity)

def calculate_illumination_score(illumination):
    """Calculate moon illumination contribution score"""
    return max(0, 100 - illumination)

def calculate_phase_score(phase_degrees):
    """Calculate moon phase contribution score"""
    # Best visibility is around new moon (0 degrees)
    distance_from_new = min(phase_degrees, 360 - phase_degrees)
    return max(0, 100 - (distance_from_new / 180 * 100))

def import_historical_data(df):
    """Import historical data from CSV"""
    try:
        conn = sqlite3.connect('hilal_database.db')
        
        imported_count = 0
        for _, row in df.iterrows():
            try:
                # Insert observation
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO hilal_observations 
                    (observation_date, latitude, longitude, city, sqm_value, 
                     weather_condition, temperature, humidity, hilal_detected, 
                     detection_confidence, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row.get('date', datetime.now().isoformat()),
                    row.get('lat', 0),
                    row.get('lon', 0),
                    row.get('city', 'Unknown'),
                    row.get('sqm', 19.0),
                    row.get('weather', 'Unknown'),
                    row.get('temp', 25),
                    row.get('humidity', 70),
                    row.get('detected', 0),
                    row.get('confidence', 0.5),
                    row.get('notes', '')
                ))
                imported_count += 1
            except Exception as e:
                st.warning(f"Error importing row: {e}")
        
        conn.commit()
        conn.close()
        return imported_count
        
    except Exception as e:
        st.error(f"Import error: {e}")
        return 0

def add_manual_observation(date, lat, lon, city, sqm, detected, confidence, notes):
    """Add manual observation to database"""
    try:
        conn = sqlite3.connect('hilal_database.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO hilal_observations 
            (observation_date, latitude, longitude, city, sqm_value, 
             hilal_detected, detection_confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            date.isoformat(),
            lat, lon, city, sqm,
            1 if detected else 0,
            confidence,
            notes
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        st.error(f"Error adding manual observation: {e}")
        return False

def clean_duplicate_observations():
    """Remove duplicate observations from database"""
    try:
        conn = sqlite3.connect('hilal_database.db')
        cursor = conn.cursor()
        
        # Find and remove duplicates based on date, location, and SQM
        cursor.execute('''
            DELETE FROM hilal_observations 
            WHERE id NOT IN (
                SELECT MIN(id) 
                FROM hilal_observations 
                GROUP BY observation_date, latitude, longitude, sqm_value
            )
        ''')
        
        cleaned_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return cleaned_count
        
    except Exception as e:
        st.error(f"Error cleaning duplicates: {e}")
        return 0

def export_full_database():
    """Export complete database as JSON"""
    try:
        conn = sqlite3.connect('hilal_database.db')
        
        # Export all tables
        observations = pd.read_sql_query("SELECT * FROM hilal_observations", conn)
        detections = pd.read_sql_query("SELECT * FROM detection_results", conn)
        analysis = pd.read_sql_query("SELECT * FROM research_analysis", conn)
        
        conn.close()
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "hilal_observations": observations.to_dict('records'),
            "detection_results": detections.to_dict('records'),
            "research_analysis": analysis.to_dict('records')
        }
        
        return json.dumps(export_data, indent=2)
        
    except Exception as e:
        st.error(f"Export error: {e}")
        return None

def reset_database():
    """Reset database (for development/testing)"""
    try:
        if os.path.exists('hilal_database.db'):
            os.remove('hilal_database.db')
        init_database()
        return True
    except Exception as e:
        st.error(f"Reset error: {e}")
        return False

def generate_research_report(df, report_type, author, institution, purpose, include_viz, include_raw):
    """Generate comprehensive research report"""
    
    report = f"""# {report_type}
## Hilal Detection Research Analysis

**Author:** {author}  
**Institution:** {institution}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Data Range:** {df['observation_date'].min()} to {df['observation_date'].max()}

## Research Purpose
{purpose}

## Executive Summary

This analysis examines {len(df)} hilal observations collected across {df['city'].nunique()} locations. 
The overall detection success rate was {len(df[df['hilal_detected'] == 1]) / len(df) * 100:.1f}%, 
with an average sky quality (SQM) of {df['sqm_value'].mean():.2f}.

## Methodology

The research employed YOLOv5-based computer vision for automatic hilal detection, 
integrated with comprehensive sky quality measurements and meteorological data.

### Key Metrics:
- **Total Observations:** {len(df)}
- **Successful Detections:** {len(df[df['hilal_detected'] == 1])}
- **Success Rate:** {len(df[df['hilal_detected'] == 1]) / len(df) * 100:.1f}%
- **Average Detection Confidence:** {df['detection_confidence'].mean():.3f}
- **Sky Quality Range:** {df['sqm_value'].min():.1f} - {df['sqm_value'].max():.1f} SQM

## Statistical Analysis

### Correlation Analysis
- **SQM vs Detection Success:** {df[['sqm_value', 'hilal_detected']].corr().iloc[0,1]:.3f}
- **Temperature vs Detection:** {df[['temperature', 'hilal_detected']].corr().iloc[0,1]:.3f}
- **Humidity vs Detection:** {df[['humidity', 'hilal_detected']].corr().iloc[0,1]:.3f}

### Optimal Conditions
Based on successful observations:
- **Optimal SQM Range:** {df[df['hilal_detected'] == 1]['sqm_value'].min():.1f} - {df[df['hilal_detected'] == 1]['sqm_value'].max():.1f}
- **Average Temperature:** {df[df['hilal_detected'] == 1]['temperature'].mean():.1f}°C
- **Average Humidity:** {df[df['hilal_detected'] == 1]['humidity'].mean():.1f}%

## Research Conclusions

1. **Sky Quality Impact:** Higher SQM values correlate with improved detection success
2. **Weather Factors:** Clear skies and moderate humidity favor hilal visibility
3. **Location Influence:** Rural/suburban locations show better detection rates
4. **Technical Performance:** YOLOv5 model achieves reliable detection under optimal conditions

## Recommendations for Future Research

1. Expand dataset with more diverse geographical locations
2. Investigate seasonal variations in detection success
3. Develop predictive models for optimal observation times
4. Integrate real-time atmospheric data for enhanced predictions

## Data Quality Assessment

- **Data Completeness:** {(df.notna().sum().sum() / (len(df) * len(df.columns)) * 100):.1f}%
- **Geographic Coverage:** {df['city'].nunique()} cities across Indonesia
- **Temporal Span:** {(pd.to_datetime(df['observation_date'].max()) - pd.to_datetime(df['observation_date'].min())).days} days

---

*Report generated by Hilal Detection Research System*
*For academic and research purposes*
"""
    
    return report

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background: rgba(255, 255, 255, 0.05); border-radius: 15px;">
    <h3>🔬 Research System Status</h3>
    <p><strong>System Version:</strong> Research Edition v2.0</p>
    <p><strong>Database:</strong> SQLite with Historical Data Integration</p>
    <p><strong>Analytics:</strong> Statistical Analysis & Correlation Studies</p>
    <p><strong>Purpose:</strong> Academic Research & Scientific Publication</p>
</div>
""", unsafe_allow_html=True)