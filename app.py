import streamlit as st
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import with error handling
try:
    from detect import detect_image, detect_video
    from utils import get_weather, get_astronomical_data, calculate_moon_phase
    DETECTION_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    DETECTION_AVAILABLE = False

# Auto-create directories
for dir_name in ["assets", "data", "reports", "models"]:
    Path(dir_name).mkdir(exist_ok=True)

# Indonesian cities with enhanced data
CITIES = {
    "Jakarta": {"lat": -6.2088, "lon": 106.8456, "timezone": "WIB", "elevation": 8},
    "Surabaya": {"lat": -7.2575, "lon": 112.7521, "timezone": "WIB", "elevation": 3},
    "Bandung": {"lat": -6.9175, "lon": 107.6191, "timezone": "WIB", "elevation": 768},
    "Medan": {"lat": 3.5952, "lon": 98.6722, "timezone": "WIB", "elevation": 25},
    "Semarang": {"lat": -6.9667, "lon": 110.4167, "timezone": "WIB", "elevation": 3},
    "Makassar": {"lat": -5.1477, "lon": 119.4327, "timezone": "WITA", "elevation": 8},
    "Palembang": {"lat": -2.9761, "lon": 104.7754, "timezone": "WIB", "elevation": 8},
    "Bandar Lampung": {"lat": -5.4292, "lon": 105.2610, "timezone": "WIB", "elevation": 52},
    "Denpasar": {"lat": -8.6705, "lon": 115.2126, "timezone": "WITA", "elevation": 4},
    "Balikpapan": {"lat": -1.2379, "lon": 116.8529, "timezone": "WITA", "elevation": 6},
    "Pontianak": {"lat": -0.0263, "lon": 109.3425, "timezone": "WIB", "elevation": 2},
    "Manado": {"lat": 1.4748, "lon": 124.8421, "timezone": "WIT", "elevation": 5},
    "Yogyakarta": {"lat": -7.7956, "lon": 110.3695, "timezone": "WIB", "elevation": 113},
    "Malang": {"lat": -7.9797, "lon": 112.6304, "timezone": "WIB", "elevation": 440},
    "Padang": {"lat": -0.9471, "lon": 100.4172, "timezone": "WIB", "elevation": 3}
}

# Page configuration
st.set_page_config(
    page_title="Hilal Detection Research System", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/hilal-research',
        'Report a bug': 'https://github.com/yourusername/hilal-research/issues',
        'About': "Sistem Penelitian Deteksi Hilal untuk Skripsi - Computer Vision & Astronomical Analysis"
    }
)

# Enhanced CSS for research theme
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0c0c2e 0%, #1a1a3a 50%, #2d1b69 100%);
        color: white;
    }
    
    .research-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        border: 2px solid rgba(255, 215, 0, 0.3);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        backdrop-filter: blur(10px);
    }
    
    .research-note {
        background: rgba(255, 215, 0, 0.1);
        border-left: 4px solid #FFD700;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    
    .data-section {
        background: rgba(0, 100, 150, 0.1);
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(0, 150, 255, 0.3);
        margin: 15px 0;
    }
    
    .upload-area {
        border: 2px dashed rgba(255, 215, 0, 0.5);
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        background: rgba(255, 215, 0, 0.05);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Research Header
st.markdown("""
<div class="research-header">
    <h1>🌙 SISTEM PENELITIAN DETEKSI HILAL</h1>
    <h3>Computer Vision & Astronomical Data Analysis</h3>
    <p><strong>Research Focus:</strong> Pengembangan Sistem Deteksi Hilal Berbasis Citra dan Integrasi Data Historis</p>
    <div style="margin-top: 15px;">
        <span style="background: rgba(255, 215, 0, 0.3); padding: 8px 15px; border-radius: 20px; margin: 5px;">
            🔬 Computer Vision Research
        </span>
        <span style="background: rgba(0, 150, 255, 0.3); padding: 8px 15px; border-radius: 20px; margin: 5px;">
            📊 Data Analysis
        </span>
        <span style="background: rgba(50, 205, 50, 0.3); padding: 8px 15px; border-radius: 20px; margin: 5px;">
            🌌 Astronomical Integration
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for research data
if 'research_data' not in st.session_state:
    st.session_state.research_data = []

if 'observation_log' not in st.session_state:
    st.session_state.observation_log = []

# Sidebar for research controls
with st.sidebar:
    st.markdown("### 🔬 Research Dashboard")
    
    # Research mode selection
    research_mode = st.selectbox(
        "Research Mode:",
        ["📊 Data Collection", "🔍 Analysis Mode", "📈 Statistical Review", "📋 Export Results"]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Current Session")
    st.metric("Observations", len(st.session_state.observation_log))
    st.metric("Detections", len(st.session_state.research_data))
    
    # Research settings
    st.markdown("---")
    st.markdown("### ⚙️ Research Settings")
    
    confidence_threshold = st.slider("Detection Confidence", 0.1, 0.9, 0.25, 0.05)
    auto_save = st.checkbox("Auto-save Results", True)
    include_weather = st.checkbox("Include Weather Data", True)
    include_astronomical = st.checkbox("Include Astronomical Data", True)
    
    st.markdown("---")
    st.markdown("### 📚 Research Notes")
    research_notes = st.text_area(
        "Session Notes:",
        placeholder="Add research observations, methodology notes, or findings...",
        height=100
    )

# Main content based on research mode
if research_mode == "📊 Data Collection":
    st.markdown("## 📊 Data Collection Module")
    
    # Data collection interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="upload-area">
            <h3>🎬 Media Upload for Analysis</h3>
            <p>Upload hilal images or videos for computer vision analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        media_file = st.file_uploader(
            "Upload Image/Video", 
            type=["jpg", "png", "jpeg", "mp4", "mov", "avi"],
            help="Supported formats: JPG, PNG, JPEG (images) | MP4, MOV, AVI (videos)"
        )
        
        if media_file:
            # Media preview and metadata
            st.success(f"✅ **Media Loaded:** {media_file.name}")
            
            file_size = len(media_file.getvalue()) / 1024  # KB
            st.info(f"📁 File Size: {file_size:.1f} KB | Type: {media_file.type}")
            
            if media_file.type.startswith("image"):
                st.image(media_file, caption="🖼️ Preview - Ready for Analysis", use_column_width=True)
            else:
                st.video(media_file)
    
    with col2:
        st.markdown("### 📋 Observation Metadata")
        
        # Observation details
        observation_date = st.date_input("Observation Date", datetime.now())
        observation_time = st.time_input("Observation Time", datetime.now().time())
        
        observer_name = st.text_input("Observer Name", placeholder="Research Team Member")
        observation_type = st.selectbox(
            "Observation Type:",
            ["Research Data", "Validation Sample", "Test Case", "Field Observation"]
        )
        
        weather_condition = st.selectbox(
            "Visual Weather:",
            ["Clear", "Partly Cloudy", "Cloudy", "Hazy", "Rainy"]
        )
        
        moon_visibility = st.selectbox(
            "Moon Visibility:",
            ["Clearly Visible", "Faintly Visible", "Not Visible", "Uncertain"]
        )
        
        equipment_used = st.text_input("Equipment", placeholder="Camera model, telescope, etc.")

    # Location and environmental data
    st.markdown("### 🌍 Location & Environmental Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        location_mode = st.radio(
            "Location Method:",
            ["🏙️ Select City", "🎯 Manual Coordinates"],
            horizontal=True
        )
        
        if location_mode == "🏙️ Select City":
            selected_city = st.selectbox(
                "Indonesian City:",
                [""] + list(CITIES.keys())
            )
            
            if selected_city:
                city_data = CITIES[selected_city]
                lat = str(city_data['lat'])
                lon = str(city_data['lon'])
                st.success(f"📍 {selected_city} selected")
        else:
            lat = st.text_input("Latitude", placeholder="-6.175")
            lon = st.text_input("Longitude", placeholder="106.827")
    
    with col2:
        # Sky Quality Meter
        sqm = st.number_input(
            "Sky Quality Meter (SQM):", 
            min_value=0.0, 
            max_value=30.0, 
            step=0.1,
            value=20.0,
            help="Higher values = darker skies = better observation conditions"
        )
        
        # Additional atmospheric parameters
        humidity = st.number_input("Humidity (%)", 0, 100, 70)
        wind_speed = st.number_input("Wind Speed (km/h)", 0.0, 50.0, 5.0)
        
    with col3:
        # Observation conditions
        seeing_conditions = st.selectbox(
            "Atmospheric Seeing:",
            ["Excellent (< 1\")", "Good (1-2\")", "Fair (2-3\")", "Poor (> 3\")"]
        )
        
        moon_altitude = st.number_input("Moon Altitude (°)", -90.0, 90.0, 15.0)
        sun_altitude = st.number_input("Sun Altitude (°)", -90.0, 90.0, -10.0)

elif research_mode == "🔍 Analysis Mode":
    st.markdown("## 🔍 Analysis & Detection Module")
    
    # Analysis parameters
    st.markdown("### ⚙️ Analysis Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        detection_model = st.selectbox(
            "Detection Model:",
            ["YOLOv5s", "YOLOv5m", "YOLOv5l", "YOLOv8n", "YOLOv8s"]
        )
        
        image_size = st.selectbox("Input Size:", [320, 416, 640, 832])
        
    with col2:
        confidence_min = st.slider("Min Confidence", 0.1, 0.9, confidence_threshold)
        iou_threshold = st.slider("IoU Threshold", 0.1, 0.9, 0.45)
        
    with col3:
        augmentation = st.checkbox("Data Augmentation", False)
        tta = st.checkbox("Test Time Augmentation", False)
    
    # Processing button
    if st.button("🚀 Run Complete Analysis", type="primary"):
        if 'media_file' in locals() and media_file:
            with st.spinner("🔄 Running comprehensive analysis..."):
                
                # Create analysis container
                analysis_container = st.container()
                
                with analysis_container:
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        # Phase 1: Preprocessing
                        status_text.text("📊 Preprocessing data...")
                        progress_bar.progress(20)
                        
                        # Save file
                        save_path = Path("assets") / media_file.name
                        with open(save_path, "wb") as f:
                            f.write(media_file.getbuffer())
                        
                        # Phase 2: Detection
                        status_text.text("🤖 Running detection model...")
                        progress_bar.progress(50)
                        
                        if DETECTION_AVAILABLE:
                            if media_file.type.startswith("image"):
                                output_path, csv_path = detect_image(str(save_path), "best.pt")
                            else:
                                output_path, csv_path = detect_video(str(save_path), "best.pt")
                        else:
                            st.warning("⚠️ Detection model unavailable - using fallback")
                            output_path = str(save_path)
                            csv_path = None
                        
                        # Phase 3: Data integration
                        status_text.text("🌍 Integrating environmental data...")
                        progress_bar.progress(75)
                        
                        # Collect all analysis data
                        analysis_data = {
                            'timestamp': datetime.now(),
                            'file_name': media_file.name,
                            'file_size': len(media_file.getvalue()),
                            'detection_model': detection_model,
                            'confidence_threshold': confidence_min,
                            'sqm_value': sqm,
                            'weather_condition': weather_condition,
                            'moon_visibility': moon_visibility,
                            'observer': observer_name,
                            'location_lat': float(lat) if lat else None,
                            'location_lon': float(lon) if lon else None,
                        }
                        
                        # Add weather data if enabled
                        if include_weather and lat and lon:
                            weather_data = get_weather(lat, lon)
                            analysis_data.update({
                                'weather_temp': weather_data.get('suhu', 'N/A'),
                                'weather_humidity': weather_data.get('kelembapan', 'N/A'),
                                'weather_condition_api': weather_data.get('cuaca', 'N/A')
                            })
                        
                        # Add astronomical data if enabled
                        if include_astronomical and lat and lon:
                            astro_data = get_astronomical_data(lat, lon)
                            if 'error' not in astro_data:
                                analysis_data.update({
                                    'moon_phase_deg': astro_data['moon_phase']['phase_degrees'],
                                    'moon_phase_name': astro_data['moon_phase']['phase_name'],
                                    'moon_illumination': astro_data['moon_phase']['illumination']
                                })
                        
                        # Store in session
                        st.session_state.research_data.append(analysis_data)
                        
                        # Complete
                        status_text.text("✅ Analysis complete!")
                        progress_bar.progress(100)
                        
                        # Display results
                        st.success("🎉 **Analysis Complete!**")
                        
                        result_col1, result_col2 = st.columns([2, 1])
                        
                        with result_col1:
                            st.markdown("#### 🎯 Detection Results")
                            if output_path and os.path.exists(output_path):
                                if media_file.type.startswith("image"):
                                    st.image(output_path, caption="🌙 Hilal Detection Results", use_column_width=True)
                                else:
                                    st.video(output_path)
                        
                        with result_col2:
                            st.markdown("#### 📊 Analysis Summary")
                            
                            # Detection statistics
                            if csv_path and os.path.exists(csv_path):
                                try:
                                    df = pd.read_csv(csv_path, comment='#')
                                    if len(df) > 0:
                                        st.metric("🎯 Detections", len(df))
                                        st.metric("📈 Avg Confidence", f"{df['confidence'].mean()*100:.1f}%")
                                        st.metric("🏆 Best Detection", f"{df['confidence'].max()*100:.1f}%")
                                    else:
                                        st.metric("🎯 Detections", "0")
                                        st.info("No hilal detected")
                                except:
                                    st.warning("Unable to parse detection data")
                            
                            # Save observation log
                            log_entry = {
                                'timestamp': datetime.now(),
                                'file': media_file.name,
                                'sqm': sqm,
                                'visibility': moon_visibility,
                                'weather': weather_condition,
                                'detections': len(df) if 'df' in locals() and len(df) > 0 else 0
                            }
                            st.session_state.observation_log.append(log_entry)
                            
                            # Auto-save if enabled
                            if auto_save:
                                save_research_data()
                                st.success("💾 Data auto-saved")
                        
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        progress_bar.empty()
                        status_text.empty()
        
        else:
            st.warning("⚠️ No research data available for report generation")

# Processing and detection section (moved from analysis mode)
if research_mode == "📊 Data Collection" and 'media_file' in locals() and media_file:
    st.markdown("### 🔬 Research Processing")
    
    if st.button("🚀 Process for Research", type="primary"):
        with st.spinner("🔄 Processing research sample..."):
            
            # Create comprehensive research processing
            progress_container = st.container()
            
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Phase 1: Data preparation
                    status_text.text("📊 Preparing research data...")
                    progress_bar.progress(15)
                    
                    # Save uploaded file
                    save_path = Path("assets") / media_file.name
                    with open(save_path, "wb") as f:
                        f.write(media_file.getbuffer())
                    
                    # Phase 2: Computer vision detection
                    status_text.text("🤖 Running computer vision model...")
                    progress_bar.progress(40)
                    
                    detection_results = {}
                    if DETECTION_AVAILABLE:
                        if media_file.type.startswith("image"):
                            output_path, csv_path = detect_image(str(save_path), "best.pt")
                        else:
                            output_path, csv_path = detect_video(str(save_path), "best.pt")
                        
                        # Parse detection results
                        if csv_path and os.path.exists(csv_path):
                            try:
                                df_det = pd.read_csv(csv_path, comment='#')
                                detection_results = {
                                    'detection_count': len(df_det),
                                    'avg_confidence': df_det['confidence'].mean() if len(df_det) > 0 else 0,
                                    'max_confidence': df_det['confidence'].max() if len(df_det) > 0 else 0,
                                    'detection_areas': df_det['area'].tolist() if 'area' in df_det.columns and len(df_det) > 0 else []
                                }
                            except:
                                detection_results = {'detection_count': 0, 'avg_confidence': 0, 'max_confidence': 0}
                    else:
                        output_path = str(save_path)
                        csv_path = None
                        detection_results = {'detection_count': 0, 'error': 'Model unavailable'}
                    
                    # Phase 3: Environmental data integration
                    status_text.text("🌍 Collecting environmental data...")
                    progress_bar.progress(65)
                    
                    environmental_data = {}
                    if lat and lon and include_weather:
                        weather_data = get_weather(lat, lon)
                        environmental_data.update(weather_data)
                    
                    if lat and lon and include_astronomical:
                        astro_data = get_astronomical_data(lat, lon)
                        if 'error' not in astro_data:
                            environmental_data.update({
                                'moon_phase': astro_data.get('moon_phase', {}),
                                'sun_position': astro_data.get('sun_position', {}),
                                'qibla': astro_data.get('qibla', {})
                            })
                    
                    # Phase 4: Compile research record
                    status_text.text("📝 Compiling research record...")
                    progress_bar.progress(85)
                    
                    # Create comprehensive research entry
                    research_entry = {
                        'timestamp': datetime.now(),
                        'observation_id': f"OBS_{len(st.session_state.research_data) + 1:04d}",
                        'file_name': media_file.name,
                        'file_size_kb': len(media_file.getvalue()) / 1024,
                        'media_type': media_file.type.split('/')[0],
                        'observer': observer_name,
                        'observation_date': observation_date,
                        'observation_time': observation_time,
                        'observation_type': observation_type,
                        'location_lat': float(lat) if lat else None,
                        'location_lon': float(lon) if lon else None,
                        'location_name': selected_city if location_mode == "🏙️ Select City" else "Custom",
                        'sqm_value': sqm,
                        'humidity_manual': humidity,
                        'wind_speed_manual': wind_speed,
                        'weather_condition_visual': weather_condition,
                        'moon_visibility_visual': moon_visibility,
                        'seeing_conditions': seeing_conditions,
                        'moon_altitude_manual': moon_altitude,
                        'sun_altitude_manual': sun_altitude,
                        'equipment_used': equipment_used,
                        'confidence_threshold': confidence_threshold,
                        **detection_results,
                        **environmental_data,
                        'research_notes': research_notes
                    }
                    
                    # Store in research database
                    st.session_state.research_data.append(research_entry)
                    
                    # Create observation log entry
                    log_entry = {
                        'timestamp': datetime.now(),
                        'observation_id': research_entry['observation_id'],
                        'file': media_file.name,
                        'location': selected_city if location_mode == "🏙️ Select City" else f"{lat}, {lon}",
                        'sqm': sqm,
                        'visibility': moon_visibility,
                        'weather': weather_condition,
                        'detections': detection_results.get('detection_count', 0),
                        'success': detection_results.get('detection_count', 0) > 0
                    }
                    st.session_state.observation_log.append(log_entry)
                    
                    # Complete processing
                    status_text.text("✅ Research processing complete!")
                    progress_bar.progress(100)
                    
                    # Display research results
                    st.success("🎉 **Research Data Collected Successfully!**")
                    
                    # Results display
                    result_col1, result_col2 = st.columns([2, 1])
                    
                    with result_col1:
                        st.markdown("#### 🎯 Detection Results")
                        if output_path and os.path.exists(output_path):
                            if media_file.type.startswith("image"):
                                st.image(output_path, caption="Detection Analysis Results", use_column_width=True)
                            else:
                                st.video(output_path)
                    
                    with result_col2:
                        st.markdown("#### 📊 Research Summary")
                        
                        st.metric("🆔 Observation ID", research_entry['observation_id'])
                        st.metric("🎯 Detections Found", detection_results.get('detection_count', 0))
                        
                        if detection_results.get('avg_confidence', 0) > 0:
                            st.metric("📈 Avg Confidence", f"{detection_results['avg_confidence']*100:.1f}%")
                        
                        st.metric("🌌 SQM Reading", f"{sqm}")
                        
                        # Research quality indicators
                        quality_score = calculate_research_quality(research_entry)
                        st.metric("🏆 Data Quality", f"{quality_score:.1f}/10")
                        
                        # Auto-save research data
                        if auto_save:
                            save_research_data()
                            st.success("💾 Research data saved")
                
                except Exception as e:
                    st.error(f"❌ Research processing failed: {str(e)}")
                finally:
                    progress_bar.empty()
                    status_text.empty()

# Research data management functions
def save_research_data():
    """Save research data to files"""
    try:
        # Save research data
        if st.session_state.research_data:
            df_research = pd.DataFrame(st.session_state.research_data)
            df_research.to_csv("data/research_database.csv", index=False)
        
        # Save observation log
        if st.session_state.observation_log:
            df_log = pd.DataFrame(st.session_state.observation_log)
            df_log.to_csv("data/observation_log.csv", index=False)
            
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def calculate_research_quality(entry):
    """Calculate data quality score for research purposes"""
    score = 0
    max_score = 10
    
    # Detection quality (3 points)
    if entry.get('detection_count', 0) > 0:
        score += 2
        if entry.get('avg_confidence', 0) > 0.5:
            score += 1
    
    # Environmental data completeness (3 points)
    if entry.get('sqm_value', 0) > 0:
        score += 1
    if entry.get('weather_temp') not in [None, 'N/A']:
        score += 1
    if entry.get('moon_phase'):
        score += 1
    
    # Metadata completeness (2 points)
    if entry.get('observer'):
        score += 1
    if entry.get('equipment_used'):
        score += 1
    
    # Location accuracy (2 points)
    if entry.get('location_lat') and entry.get('location_lon'):
        score += 2
    
    return score

def generate_research_report(research_data, observation_log, title, author, institution, include_methodology):
    """Generate comprehensive research report"""
    
    df_research = pd.DataFrame(research_data)
    df_log = pd.DataFrame(observation_log)
    
    report = f"""# {title}

**Author:** {author}  
**Institution:** {institution}  
**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Observations:** {len(research_data)}

## Executive Summary

This research analyzes hilal (crescent moon) detection using computer vision techniques combined with astronomical and environmental data. The study collected {len(research_data)} observations across various conditions to evaluate detection accuracy and environmental factors affecting visibility.

### Key Findings

- **Total Observations:** {len(research_data)}
- **Successful Detections:** {(df_research['detection_count'] > 0).sum() if 'detection_count' in df_research.columns else 0}
- **Average SQM:** {df_research['sqm_value'].mean():.2f}
- **Detection Success Rate:** {(df_research['detection_count'] > 0).mean() * 100 if 'detection_count' in df_research.columns else 0:.1f}%

## Research Methodology
"""
    
    if include_methodology:
        report += """
### 1. Data Collection Protocol

The research employed a systematic approach to hilal detection combining:

- **Computer Vision Analysis:** YOLOv5/v8 deep learning models for object detection
- **Environmental Monitoring:** Sky Quality Meter (SQM) readings and weather data
- **Astronomical Integration:** Moon phase calculations and positional astronomy
- **Standardized Documentation:** Consistent metadata collection for each observation

### 2. Detection System

- **Model Architecture:** YOLO (You Only Look Once) neural network
- **Confidence Threshold:** 25% minimum for valid detections
- **Image Processing:** OpenCV for preprocessing and annotation
- **Output Format:** Annotated images with bounding boxes and CSV data export

### 3. Environmental Parameters

- **Sky Quality:** Measured using SQM scale (0-30, higher = darker sky)
- **Weather Integration:** Real-time meteorological data via API
- **Location Services:** GPS coordinates with timezone and elevation data
- **Visibility Assessment:** Multi-factor analysis including atmospheric conditions

"""
    
    # Statistical analysis
    if 'detection_count' in df_research.columns:
        successful_obs = df_research[df_research['detection_count'] > 0]
        report += f"""
## Statistical Analysis

### Detection Performance

- **Total Samples Processed:** {len(df_research)}
- **Successful Detections:** {len(successful_obs)}
- **Detection Rate:** {len(successful_obs)/len(df_research)*100:.1f}%
- **Average Confidence:** {df_research['avg_confidence'].mean()*100:.1f}% (successful detections)
- **Confidence Range:** {df_research['avg_confidence'].min()*100:.1f}% - {df_research['avg_confidence'].max()*100:.1f}%

### Environmental Correlation

**SQM Analysis:**
- **Average SQM (All):** {df_research['sqm_value'].mean():.2f}
- **Average SQM (Successful):** {successful_obs['sqm_value'].mean():.2f if len(successful_obs) > 0 else 'N/A'}
- **SQM Range:** {df_research['sqm_value'].min():.1f} - {df_research['sqm_value'].max():.1f}

**Weather Conditions:**
- **Most Common Condition:** {df_research['weather_condition_visual'].mode().iloc[0] if len(df_research) > 0 else 'N/A'}
- **Visibility Assessment:** {df_research['moon_visibility_visual'].mode().iloc[0] if len(df_research) > 0 else 'N/A'}

"""
    
    # Data summary table
    report += f"""
## Data Summary

### Observation Distribution

| Parameter | Count | Percentage |
|-----------|-------|------------|
"""
    
    if len(df_research) > 0:
        # Weather distribution
        weather_dist = df_research['weather_condition_visual'].value_counts()
        for condition, count in weather_dist.items():
            percentage = (count / len(df_research)) * 100
            report += f"| {condition} Weather | {count} | {percentage:.1f}% |\n"
        
        report += "\n"
        
        # Visibility distribution
        visibility_dist = df_research['moon_visibility_visual'].value_counts()
        for visibility, count in visibility_dist.items():
            percentage = (count / len(df_research)) * 100
            report += f"| {visibility} | {count} | {percentage:.1f}% |\n"
    
    # Conclusions and recommendations
    report += """

## Research Conclusions

### Technical Performance

The computer vision system demonstrated varying performance across different environmental conditions. Key observations include:

1. **Sky Quality Impact:** Higher SQM values correlate with improved detection accuracy
2. **Weather Sensitivity:** Clear conditions significantly improve detection rates
3. **Model Robustness:** System maintains functionality across diverse input conditions

### Recommendations for Future Research

1. **Dataset Expansion:** Collect more samples under extreme weather conditions
2. **Model Optimization:** Fine-tune detection thresholds based on environmental parameters
3. **Validation Studies:** Compare results with expert astronomer observations
4. **Temporal Analysis:** Investigate seasonal and lunar cycle patterns

### Limitations

- Model accuracy depends on training data quality and diversity
- Weather API availability may affect real-time environmental integration
- Manual validation required for critical astronomical determinations

## Technical Specifications

**System Requirements:**
- Python 3.8+
- YOLOv5/v8 framework
- OpenCV for image processing
- Streamlit for web interface

**Model Details:**
- Architecture: YOLO object detection
- Input Resolution: 640x640 pixels
- Confidence Threshold: 25%
- Processing Time: ~2-5 seconds per image

**Data Storage:**
- Research database: CSV format
- Detection results: Annotated images/videos + coordinate data
- Environmental data: Real-time API integration

---

*Report generated by Hilal Detection Research System*  
*For questions or clarifications, contact the research team*
"""
    
    return report

# Load existing research data if available
@st.cache_data
def load_existing_research_data():
    """Load previously saved research data"""
    research_file = Path("data/research_database.csv")
    log_file = Path("data/observation_log.csv")
    
    loaded_data = {}
    
    if research_file.exists():
        try:
            loaded_data['research'] = pd.read_csv(research_file)
        except:
            loaded_data['research'] = pd.DataFrame()
    else:
        loaded_data['research'] = pd.DataFrame()
    
    if log_file.exists():
        try:
            loaded_data['log'] = pd.read_csv(log_file)
        except:
            loaded_data['log'] = pd.DataFrame()
    else:
        loaded_data['log'] = pd.DataFrame()
    
    return loaded_data

# Footer with research information
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 30px; background: rgba(255, 255, 255, 0.05); border-radius: 15px; margin-top: 50px;">
    <h3>🎓 Research System Specifications</h3>
    
    <div style="display: flex; justify-content: space-around; flex-wrap: wrap; margin: 20px 0;">
        <div class="metric-card" style="margin: 10px; min-width: 200px;">
            <h4>🔬 Research Focus</h4>
            <p>Computer Vision<br>Astronomical Analysis<br>Environmental Integration</p>
        </div>
        
        <div class="metric-card" style="margin: 10px; min-width: 200px;">
            <h4>📊 Data Output</h4>
            <p>Detection Coordinates<br>Confidence Scores<br>Environmental Parameters</p>
        </div>
        
        <div class="metric-card" style="margin: 10px; min-width: 200px;">
            <h4>📈 Analysis Tools</h4>
            <p>Statistical Analysis<br>Correlation Studies<br>Visualization Charts</p>
        </div>
        
        <div class="metric-card" style="margin: 10px; min-width: 200px;">
            <h4>📋 Export Formats</h4>
            <p>Research Reports<br>CSV Datasets<br>Statistical Summaries</p>
        </div>
    </div>
    
    <div class="research-note">
        <strong>🎯 Research Objectives:</strong>
        <ol style="text-align: left; display: inline-block;">
            <li>Develop robust hilal detection using computer vision</li>
            <li>Integrate environmental and astronomical data for visibility analysis</li>
            <li>Create comprehensive database for historical analysis</li>
            <li>Validate system accuracy across diverse observation conditions</li>
            <li>Provide tools for Islamic calendar determination support</li>
        </ol>
    </div>
    
    <p style="margin-top: 20px; color: #B8860B;">
        <strong>🎓 Academic Purpose:</strong> This system supports undergraduate thesis research in computer vision and astronomical applications<br>
        <strong>🔬 Methodology:</strong> Quantitative analysis with statistical validation and environmental correlation studies<br>
        <strong>📊 Output:</strong> Comprehensive dataset for academic analysis and publication
    </p>
</div>
""", unsafe_allow_html=True)

# Research data persistence
if st.sidebar.button("💾 Save Research Session"):
    if save_research_data():
        st.sidebar.success("✅ Session saved successfully")
    else:
        st.sidebar.error("❌ Failed to save session")

# Load previous research data option
if st.sidebar.button("📂 Load Previous Data"):
    try:
        existing_data = load_existing_research_data()
        
        if not existing_data['research'].empty:
            # Convert back to list of dicts for session state
            st.session_state.research_data = existing_data['research'].to_dict('records')
            st.sidebar.success(f"📊 Loaded {len(existing_data['research'])} research entries")
        
        if not existing_data['log'].empty:
            st.session_state.observation_log = existing_data['log'].to_dict('records')
            st.sidebar.success(f"📋 Loaded {len(existing_data['log'])} log entries")
            
    except Exception as e:
        st.sidebar.error(f"Error loading data: {e}")

# Debug panel for research
if st.sidebar.checkbox("🔧 Research Debug"):
    with st.expander("System Diagnostics"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📊 Research Data Status:**")
            st.write(f"- Research Entries: {len(st.session_state.research_data)}")
            st.write(f"- Observation Log: {len(st.session_state.observation_log)}")
            st.write(f"- Detection System: {'✅ Available' if DETECTION_AVAILABLE else '❌ Unavailable'}")
            st.write(f"- Data Auto-save: {'✅ Enabled' if auto_save else '❌ Disabled'}")
            
        with col2:
            st.write("**🗂️ File System:**")
            for dir_name in ["assets", "data", "reports", "models"]:
                dir_path = Path(dir_name)
                if dir_path.exists():
                    file_count = len(list(dir_path.glob("*")))
                    st.write(f"- {dir_name}/: {file_count} files")
                else:
                    st.write(f"- {dir_name}/: Not found")
        
        # Session state preview
        if st.button("👀 Preview Session Data"):
            if st.session_state.research_data:
                st.write("**Last Research Entry:**")
                st.json(st.session_state.research_data[-1])
            else:
                st.info("No research data in current session")

# Performance monitoring for research
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Performance Metrics")

if len(st.session_state.research_data) > 0:
    df_temp = pd.DataFrame(st.session_state.research_data)
    
    # Calculate session statistics
    total_detections = df_temp['detection_count'].sum() if 'detection_count' in df_temp.columns else 0
    avg_quality = df_temp.apply(calculate_research_quality, axis=1).mean()
    
    st.sidebar.metric("🎯 Total Detections", total_detections)
    st.sidebar.metric("🏆 Avg Data Quality", f"{avg_quality:.1f}/10")
    
    # Session duration
    if len(df_temp) > 1:
        start_time = pd.to_datetime(df_temp['timestamp'].iloc[0])
        end_time = pd.to_datetime(df_temp['timestamp'].iloc[-1])
        duration = end_time - start_time
        st.sidebar.metric("⏱️ Session Duration", f"{duration.total_seconds()/3600:.1f}h")

else:
    st.sidebar.info("Start collecting data to see metrics")

# Research tips
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Research Tips")
st.sidebar.markdown("""
**For Best Results:**
- Use high-resolution images (>640px)
- Record accurate SQM readings
- Document weather conditions
- Include observation metadata
- Process multiple samples per condition

**Data Quality Checklist:**
- ✅ Clear location coordinates
- ✅ Accurate timing information  
- ✅ Environmental measurements
- ✅ Equipment specifications
- ✅ Observer identification
""")

# Emergency data export
if st.sidebar.button("🚨 Emergency Export"):
    if st.session_state.research_data:
        emergency_export = {
            'export_timestamp': datetime.now().isoformat(),
            'research_data': st.session_state.research_data,
            'observation_log': st.session_state.observation_log,
            'session_notes': research_notes
        }
        
        st.sidebar.download_button(
            "📦 Download Emergency Backup",
            str(emergency_export),
            file_name=f"emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )
    else:
        st.sidebar.info("No data to export")

# End of main application⚠️ Please upload a media file first!")

elif research_mode == "📈 Statistical Review":
    st.markdown("## 📈 Statistical Analysis & Research Insights")
    
    if len(st.session_state.research_data) == 0:
        st.info("📊 No research data available yet. Please collect some data first!")
    else:
        # Convert session data to DataFrame
        df_research = pd.DataFrame(st.session_state.research_data)
        
        # Research statistics overview
        st.markdown("### 🔍 Research Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Total Samples</h3>
                <h2>{}</h2>
                <p>Research observations</p>
            </div>
            """.format(len(df_research)), unsafe_allow_html=True)
        
        with col2:
            detection_rate = df_research['detection_count'].mean() if 'detection_count' in df_research.columns else 0
            st.markdown("""
            <div class="metric-card">
                <h3>🎯 Avg Detections</h3>
                <h2>{:.1f}</h2>
                <p>Per observation</p>
            </div>
            """.format(detection_rate), unsafe_allow_html=True)
        
        with col3:
            avg_sqm = df_research['sqm_value'].mean()
            st.markdown("""
            <div class="metric-card">
                <h3>🌌 Avg SQM</h3>
                <h2>{:.1f}</h2>
                <p>Sky quality</p>
            </div>
            """.format(avg_sqm), unsafe_allow_html=True)
        
        with col4:
            success_rate = (df_research['detection_count'] > 0).mean() * 100 if 'detection_count' in df_research.columns else 0
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Success Rate</h3>
                <h2>{:.1f}%</h2>
                <p>Detection success</p>
            </div>
            """.format(success_rate), unsafe_allow_html=True)
        
        # Detailed analysis charts
        st.markdown("### 📊 Research Data Visualization")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # SQM vs Detection success
            if 'detection_count' in df_research.columns:
                fig = px.scatter(
                    df_research, 
                    x='sqm_value', 
                    y='detection_count',
                    color='weather_condition',
                    title="🌌 SQM vs Detection Success",
                    labels={'sqm_value': 'Sky Quality Meter', 'detection_count': 'Detections Found'}
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            # Moon visibility distribution
            visibility_counts = df_research['moon_visibility'].value_counts()
            fig = px.pie(
                values=visibility_counts.values,
                names=visibility_counts.index,
                title="👁️ Moon Visibility Distribution"
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Time series analysis
        st.markdown("### 📅 Temporal Analysis")
        
        # Group by date
        df_research['date'] = pd.to_datetime(df_research['timestamp']).dt.date
        daily_stats = df_research.groupby('date').agg({
            'detection_count': ['count', 'sum', 'mean'],
            'sqm_value': 'mean'
        }).round(2)
        
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Observations', 'Average SQM by Date'),
            vertical_spacing=0.1
        )
        
        # Daily observation count
        fig.add_trace(
            go.Scatter(
                x=daily_stats.index,
                y=daily_stats[('detection_count', 'count')],
                mode='lines+markers',
                name='Observations',
                line=dict(color='#FFD700')
            ),
            row=1, col=1
        )
        
        # Daily average SQM
        fig.add_trace(
            go.Scatter(
                x=daily_stats.index,
                y=daily_stats[('sqm_value', 'mean')],
                mode='lines+markers',
                name='Avg SQM',
                line=dict(color='#00CED1')
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Correlation analysis
        st.markdown("### 🔗 Correlation Analysis")
        
        # Select numeric columns for correlation
        numeric_cols = df_research.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df_research[numeric_cols].corr()
            
            fig = px.imshow(
                corr_matrix,
                title="🧮 Variable Correlations",
                color_continuous_scale='RdBu',
                aspect='auto'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)

elif research_mode == "📋 Export Results":
    st.markdown("## 📋 Export & Documentation Module")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📄 Research Report Generation")
        
        report_type = st.selectbox(
            "Report Type:",
            ["📊 Complete Research Report", "📈 Statistical Summary", "🔍 Detection Analysis", "📋 Observation Log"]
        )
        
        include_charts = st.checkbox("Include Charts", True)
        include_raw_data = st.checkbox("Include Raw Data", True)
        include_methodology = st.checkbox("Include Methodology", True)
        
        # Report customization
        report_title = st.text_input(
            "Report Title:", 
            "Hilal Detection Research Analysis"
        )
        
        author_name = st.text_input("Author:", "Research Team")
        institution = st.text_input("Institution:", "University Name")
        
    with col2:
        st.markdown("### 💾 Export Options")
        
        # Data export buttons
        if len(st.session_state.research_data) > 0:
            
            # Export research data
            df_export = pd.DataFrame(st.session_state.research_data)
            csv_data = df_export.to_csv(index=False)
            
            st.download_button(
                "📊 Download Research Data (CSV)",
                csv_data,
                file_name=f"hilal_research_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # Export observation log
            if len(st.session_state.observation_log) > 0:
                df_log = pd.DataFrame(st.session_state.observation_log)
                log_csv = df_log.to_csv(index=False)
                
                st.download_button(
                    "📋 Download Observation Log (CSV)",
                    log_csv,
                    file_name=f"observation_log_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        # Clear data option
        if st.button("🗑️ Clear Session Data"):
            st.session_state.research_data = []
            st.session_state.observation_log = []
            st.success("✅ Session data cleared")
    
    # Generate comprehensive report
    if st.button("📑 Generate Research Report", type="primary"):
        if len(st.session_state.research_data) > 0:
            report_content = generate_research_report(
                st.session_state.research_data,
                st.session_state.observation_log,
                report_title,
                author_name,
                institution,
                include_methodology
            )
            
            st.download_button(
                "📄 Download Complete Report (MD)",
                report_content,
                file_name=f"hilal_research_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
            
            # Preview report
            with st.expander("👀 Preview Report"):
                st.markdown(report_content)
        else:
            st.warning("hfksjhfiijkwd")