# 🌙 Hilal Detection Observatory

Advanced Crescent Moon Detection System with YOLOv5, Sky Quality Meter Integration, and Astronomical Data.

## ✨ Features

### 🤖 AI Detection System
- **YOLOv5/v8 Neural Network** for accurate hilal detection
- **Enhanced Bounding Boxes** with confidence indicators and visual effects
- **Real-time Processing** for both images and videos
- **Confidence Scoring** with detailed analytics

### 🌌 Astronomical Integration
- **Sky Quality Meter (SQM)** integration and analysis
- **Weather Data** from multiple API sources
- **Moon Phase Calculations** and Islamic calendar info
- **Qibla Direction** and solar position calculations

### 🌍 Location Services
- **15 Pre-configured Indonesian Cities** with coordinates
- **Manual Coordinate Input** for custom locations
- **Automatic Weather Retrieval** based on location
- **Geographic Validation** and location type detection

### 🎨 Astronomical Theme
- **Dark Space Theme** with animated stars background
- **Golden Accents** and space-inspired color scheme
- **Interactive UI Elements** with hover effects and animations
- **Professional Layout** optimized for astronomical observations

### 📊 Data Export
- **Enhanced CSV Reports** with detection statistics
- **Visual Result Downloads** (annotated images/videos)
- **Comprehensive Analysis Reports** in Markdown format
- **Detection Summaries** with confidence metrics

## 🚀 Quick Deployment

### Prerequisites
- Python 3.8+
- Git account
- Streamlit Cloud account (free)

### 1. Repository Setup

```bash
# Clone or create your repository
git clone https://github.com/yourusername/hilal-deteksi.git
cd hilal-deteksi

# Create required files (copy from artifacts above)
```

### 2. File Structure
```
hilal-deteksi/
├── app.py                 # Main Streamlit application
├── detect.py              # Enhanced detection with bounding boxes
├── utils.py               # Weather API and astronomical calculations
├── requirements.txt       # Python dependencies
├── packages.txt           # System dependencies
├── best.pt               # YOLOv5 model file (add your trained model)
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── assets/               # Auto-created output directory
└── README.md             # This file
```

### 3. Model Setup
1. **Train your YOLOv5 model** for hilal detection or use a pre-trained model
2. **Rename your model** to `best.pt`
3. **Upload to repository root** directory
4. **Ensure model size < 100MB** (use Git LFS for larger models)

### 4. Deploy to Streamlit Cloud

#### Method 1: Direct Deployment
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set main file path: `app.py`
5. Click "Deploy"

#### Method 2: From GitHub
1. Push all files to GitHub repository
2. In repository, go to Settings → Pages
3. Add link to Streamlit Cloud in repository description
4. Use automatic deployment via GitHub Actions (optional)

### 5. Configuration Options

#### Environment Variables (optional)
Create `.streamlit/secrets.toml` for API keys:
```toml
[weather]
openweather_api_key = "your_api_key_here"

[general]
debug_mode = false
```

#### Advanced Configuration
Modify `.streamlit/config.toml`:
```toml
[server]
maxUploadSize = 200  # MB
enableCORS = false

[theme]
primaryColor = "#FFD700"
backgroundColor = "#0c0c2e"
secondaryBackgroundColor = "#1a1a3a"
textColor = "#FFFFFF"
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Model Loading Error
```bash
Error: Model file 'best.pt' not found
```
**Solution:** Ensure `best.pt` is in the root directory and < 100MB

#### 2. Memory Issues
```bash
Your app has gone over the resource limits
```
**Solutions:**
- Reduce model size or use quantized version
- Process smaller images/videos
- Add memory optimization in `detect.py`

#### 3. Package Import Error
```bash
ModuleNotFoundError: No module named 'ultralytics'
```
**Solution:** Check `requirements.txt` and ensure all dependencies are listed

#### 4. Weather API Timeout
```bash
Weather data unavailable
```
**Solution:** App includes automatic fallbacks and geographic estimation

### Performance Optimization

#### 1. Model Optimization
```python
# In detect.py, add these optimizations:
model = YOLO(model_path)
model.fuse()  # Fuse layers for faster inference

# Use smaller image size for faster processing
results = model.predict(source=image, imgsz=320)  # Instead of 640
```

#### 2. Memory Management
```python
# Add garbage collection
import gc
gc.collect()

# Clear CUDA cache if using GPU
if torch.cuda.is_available():
    torch.cuda.empty_cache()
```

#### 3. Caching
```python
# Add Streamlit caching
@st.cache_data
def load_model(model_path):
    return YOLO(model_path)
```

## 📱 Usage Guide

### 1. Upload Media
- Support formats: JPG, PNG, JPEG (images), MP4, MOV, AVI (videos)
- Maximum size: 200MB
- Preview available before processing

### 2. Set Sky Quality
- Input SQM value (0-30)
- Automatic quality assessment
- Visibility prediction based on SQM

### 3. Choose Location
- **Option A:** Select from 15 Indonesian cities
- **Option B:** Input manual coordinates
- Automatic timezone detection

### 4. Process Detection
- Click "🚀 Launch Detection Analysis"
- Real-time progress tracking
- Enhanced results with bounding boxes

### 5. Download Results
- Annotated images/videos with detection boxes
- CSV data with coordinates and confidence scores
- Comprehensive analysis reports

## 🔧 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Access at http://localhost:8501
```

### Adding New Features
1. **New Detection Classes:** Modify model training data
2. **Additional Weather Sources:** Add to `utils.py` weather functions
3. **Custom Cities:** Update `CITIES` dictionary in `app.py`
4. **UI Improvements:** Modify CSS in `app.py`

### Testing
```bash
# Test weather API
python utils.py

# Test detection system
python detect.py
```

## 📊 API Integration

### Weather APIs Supported
1. **wttr.in** - Primary free weather service
2. **OpenWeatherMap** - Requires API key
3. **Geographic Estimation** - Fallback based on location

### Adding New Weather APIs
```python
# In utils.py
def get_weather_from_new_api(lat, lon):
    url = f"https://api.newweather.com/data?lat={lat}&lon={lon}"
    response = requests.get(url)
    return parse_response(response.json())
```

## 🌟 Advanced Features

### 1. Batch Processing
Process multiple images automatically:
```python
def batch_detect(image_folder):
    results = []
    for image_file in Path(image_folder).glob("*.jpg"):
        result = detect_image(str(image_file))
        results.append(result)
    return results
```

### 2. Real-time Analysis
Stream processing for live cameras:
```python
def live_detection(camera_source=0):
    cap = cv2.VideoCapture(camera_source)
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            results = model.predict(frame)
            # Process and display
```

### 3. API Endpoint
Create REST API for external integration:
```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/detect', methods=['POST'])
def api_detect():
    file = request.files['image']
    result = detect_image(file)
    return jsonify(result)
```

## 📞 Support

### Community
- **GitHub Issues:** Report bugs and request features
- **Discussions:** Share observations and improvements
- **Wiki:** Extended documentation and tutorials

### Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit Pull Request

### Citation
If you use this system in research:
```bibtex
@software{hilal_detection_observatory,
  title={Hilal Detection Observatory: Advanced Crescent Moon Detection System},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/hilal-deteksi}
}
```

## 📄 License

MIT License - Feel free to use for research, educational, and commercial purposes.

---

**🌙 May this system assist in accurate hilal observations for the Islamic community worldwide.**

---

### 🚨 Important Notes

1. **Model Accuracy:** Detection accuracy depends on training data quality
2. **Weather Data:** Use multiple sources for critical observations
3. **Islamic Calendar:** Consult official authorities for religious determinations
4. **Coordinates:** Verify coordinates for precise calculations

### 📈 Performance Metrics

- **Detection Speed:** ~2-5 seconds per image
- **Supported Resolution:** Up to 1920x1080 optimal
- **Confidence Threshold:** 25% minimum
- **API Response Time:** < 10 seconds
- **Uptime Target:** 99.5%

**Ready to deploy your Hilal Detection Observatory! 🚀**