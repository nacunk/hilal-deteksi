import streamlit as st
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# Import dengan error handling
try:
    # Import debug version
    from detect_debug import detect_image, check_model_file
    from utils import get_weather, get_city_coordinates, INDONESIAN_CITIES
    DETECTION_AVAILABLE = True
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    DETECTION_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="🌙 Deteksi Hilal - Debug Mode", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌙 Deteksi Hilal - Debug Mode")

# Sidebar untuk debugging
with st.sidebar:
    st.header("🔧 Debug Controls")
    
    debug_mode = st.checkbox("🧪 Force Debug Mode (Dummy Detection)", value=False)
    show_model_info = st.checkbox("📊 Show Model Info", value=True)
    show_detection_details = st.checkbox("🔍 Show Detection Details", value=True)
    
    st.header("⚙️ Detection Settings")
    conf_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.05)
    iou_threshold = st.slider("IoU Threshold", 0.0, 1.0, 0.45, 0.05)

# Model check section
if show_model_info:
    st.header("📊 Model Information")
    
    model_path = st.text_input("Model Path", value="best.pt")
    
    if st.button("🔍 Check Model"):
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
            st.success(f"✅ Model found: {file_size:.1f} MB")
            
            # Try to load model
            try:
                from ultralytics import YOLO
                model = YOLO(model_path)
                st.success("✅ Model loaded successfully")
                
                # Model info
                st.write("**Model Details:**")
                st.write(f"- Model type: {type(model)}")
                st.write(f"- Device: {model.device}")
                
                # Try a dummy prediction
                import numpy as np
                dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
                try:
                    results = model.predict(dummy_image, verbose=False)
                    st.success("✅ Model can make predictions")
                    
                    if len(results) > 0:
                        st.write(f"- Output classes: {model.names}")
                        st.write(f"- Number of classes: {len(model.names) if model.names else 'Unknown'}")
                except Exception as e:
                    st.error(f"❌ Model prediction failed: {e}")
                    
            except Exception as e:
                st.error(f"❌ Cannot load model: {e}")
        else:
            st.error(f"❌ Model file not found: {model_path}")
            st.info("💡 **Solusi:**")
            st.write("1. Upload file model `best.pt` ke root directory")
            st.write("2. Pastikan file tidak corrupt (size > 1MB)")
            st.write("3. Download model yang sudah trained untuk hilal detection")

# Main detection interface
st.header("1. 📤 Upload Media untuk Testing")

media_file = st.file_uploader(
    "Upload gambar untuk test deteksi", 
    type=["jpg", "png", "jpeg"],
    help="Upload gambar untuk testing bounding box"
)

if media_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📷 Original Image")
        st.image(media_file, caption="Original", use_column_width=True)
    
    with col2:
        st.subheader("🎯 Detection Results")
        
        if st.button("🔍 Run Detection Test", type="primary"):
            # Save uploaded file
            assets_dir = Path("assets")
            assets_dir.mkdir(exist_ok=True)
            
            save_path = assets_dir / media_file.name
            with open(save_path, "wb") as f:
                f.write(media_file.getbuffer())
            
            st.info(f"💾 File saved: {save_path}")
            
            # Run detection with debug info
            with st.spinner("🔍 Running detection..."):
                try:
                    output_path, csv_path, detection_count = detect_image(
                        str(save_path), 
                        model_path=model_path,
                        debug_mode=debug_mode
                    )
                    
                    if output_path and os.path.exists(output_path):
                        st.success(f"✅ Detection complete! Found {detection_count} objects")
                        st.image(output_path, caption="Detection Result", use_column_width=True)
                        
                        # Show detection stats
                        if csv_path and os.path.exists(csv_path):
                            import pandas as pd
                            df = pd.read_csv(csv_path)
                            
                            if len(df) > 0:
                                st.subheader("📊 Detection Statistics")
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("Total Detections", len(df))
                                with col2:
                                    st.metric("Avg Confidence", f"{df['confidence'].mean():.1%}")
                                with col3:
                                    st.metric("Max Confidence", f"{df['confidence'].max():.1%}")
                                
                                if show_detection_details:
                                    st.subheader("🔍 Detection Details")
                                    st.dataframe(df)
                            else:
                                st.warning("⚠️ No detections found")
                        
                        # Download buttons
                        st.subheader("📥 Download Results")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            with open(output_path, "rb") as f:
                                st.download_button(
                                    "📷 Download Detected Image",
                                    f,
                                    file_name=f"detected_{media_file.name}",
                                    mime="image/jpeg"
                                )
                        
                        with col2:
                            if csv_path and os.path.exists(csv_path):
                                with open(csv_path, "rb") as f:
                                    st.download_button(
                                        "📊 Download CSV Data",
                                        f,
                                        file_name=f"detections_{Path(media_file.name).stem}.csv",
                                        mime="text/csv"
                                    )
                    else:
                        st.error("❌ Detection failed")
                        
                except Exception as e:
                    st.error(f"❌ Detection error: {str(e)}")
                    import traceback
                    with st.expander("🐛 Error Details"):
                        st.code(traceback.format_exc())

# Troubleshooting section
st.header("🛠️ Troubleshooting Guide")

with st.expander("❓ Mengapa bounding box tidak muncul?"):
    st.write("""
    **Kemungkinan penyebab:**
    
    1. **Model tidak ada/corrupt:**
       - File `best.pt` tidak ada di root directory
       - File corrupt atau ukuran terlalu kecil (<1MB)
       - Model bukan untuk deteksi hilal
    
    2. **Confidence threshold terlalu tinggi:**
       - Default 0.25 mungkin terlalu tinggi untuk model Anda
       - Coba turunkan ke 0.1 atau 0.05
    
    3. **Model tidak cocok dengan data:**
       - Model ditraining untuk dataset yang berbeda
       - Gambar test tidak mengandung objek yang ditraining
    
    4. **Format gambar/resolusi:**
       - Gambar terlalu kecil atau besar
       - Format yang tidak didukung
    
    **Solusi:**
    1. ✅ Pastikan file `best.pt` ada dan valid (>1MB)
    2. ✅ Gunakan debug mode untuk testing
    3. ✅ Turunkan confidence threshold
    4. ✅ Test dengan gambar yang jelas dan berkualitas baik
    5. ✅ Download model baru yang sudah ditraining untuk hilal
    """)

with st.expander("🔗 Download Model Baru"):
    st.write("""
    **Untuk mendapatkan model `best.pt` yang valid:**
    
    1. **YOLOv5 Pretrained:**
       ```
       # Download YOLOv5 general model untuk testing
       wget https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt
       mv yolov5s.pt best.pt
       ```
    
    2. **YOLOv8 Pretrained:**
       ```python
       from ultralytics import YOLO
       model = YOLO('yolov8n.pt')  # Download otomatis
       model.save('best.pt')
       ```
    
    3. **Custom Training:**
       - Kumpulkan dataset gambar hilal (500+ images)
       - Annotate dengan tools seperti LabelImg
       - Train model dengan YOLOv5/v8
    
    **Note:** Model pretrained mungkin tidak akurat untuk hilal, tapi akan menunjukkan bounding box untuk testing UI.
    """)

with st.expander("🧪 Test dengan Dummy Data"):
    if st.button("🎮 Generate Test Detection"):
        st.info("Membuat deteksi dummy untuk testing UI...")
        
        # Create a test image
        import numpy as np
        import cv2
        
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:] = (50, 50, 100)  # Dark background
        
        # Add some "hilal-like" shapes
        cv2.ellipse(test_image, (200, 150), (30, 80), 45, 0, 180, (200, 200, 255), -1)
        cv2.ellipse(test_image, (450, 300), (25, 70), -30, 0, 180, (180, 180, 255), -1)
        
        # Save test image
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)
        test_path = assets_dir / "test_hilal.jpg"
        cv2.imwrite(str(test_path), test_image)
        
        # Run detection on test image
        from detect_debug import create_test_detection, draw_enhanced_bounding_box
        
        boxes, confidences, classes = create_test_detection(test_image, num_boxes=2)
        result_image = draw_enhanced_bounding_box(test_image, boxes, confidences, classes)
        
        result_path = assets_dir / "test_result.jpg"
        cv2.imwrite(str(result_path), result_image)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(str(test_path), caption="Test Image")
        with col2:
            st.image(str(result_path), caption="With Bounding Boxes")
        
        st.success("✅ Dummy detection berhasil! Jika ini muncul, berarti kode bounding box berfungsi.")

# System info
with st.expander("💻 System Information"):
    st.write("**Python Environment:**")
    st.write(f"- Python version: {sys.version}")
    st.write(f"- Working directory: {os.getcwd()}")
    st.write(f"- Available files: {list(Path('.').glob('*'))}")
    
    st.write("**Installed Packages:**")
    try:
        import ultralytics
        st.write(f"- ultralytics: {ultralytics.__version__}")
    except:
        st.write("- ultralytics: ❌ Not installed")
    
    try:
        import cv2
        st.write(f"- opencv: {cv2.__version__}")
    except:
        st.write("- opencv: ❌ Not installed")
    
    try:
        import torch
        st.write(f"- torch: {torch.__version__}")
        st.write(f"- CUDA available: {torch.cuda.is_available()}")
    except:
        st.write("- torch: ❌ Not installed")

# Quick fixes section
st.header("🚀 Quick Fixes")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Download YOLOv8 Model"):
        try:
            from ultralytics import YOLO
            with st.spinner("Downloading model..."):
                model = YOLO('yolov8n.pt')  # This will download the model
                model.save('best.pt')
            st.success("✅ Model downloaded as best.pt")
        except Exception as e:
            st.error(f"❌ Failed to download: {e}")

with col2:
    if st.button("🧹 Clear Assets Folder"):
        assets_dir = Path("assets")
        if assets_dir.exists():
            import shutil
            shutil.rmtree(assets_dir)
            assets_dir.mkdir()
            st.success("✅ Assets folder cleared")
        else:
            st.info("ℹ️ Assets folder doesn't exist")

with col3:
    if st.button("🔄 Reload Modules"):
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("""
### 🔍 Debug Mode Instructions

1. **Test dengan model existing**: Upload gambar dan jalankan deteksi
2. **Jika tidak ada bounding box**: Aktifkan "Force Debug Mode" 
3. **Download model baru**: Gunakan tombol "Download YOLOv8 Model"
4. **Check model info**: Pastikan model loaded dengan benar

**Catatan**: Mode debug akan selalu menampilkan bounding box dummy untuk testing UI.
""")