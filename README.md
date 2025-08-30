# Panduan Deployment Sistem Deteksi Hilal untuk Penelitian Skripsi

## Ringkasan Sistem

Sistem yang telah dimodifikasi ini mengubah aplikasi deteksi hilal menjadi platform penelitian yang komprehensif dengan fitur:

### Fitur Penelitian Tambahan
- **Data Collection Module**: Pencatatan metadata observasi sistematis
- **Statistical Analysis**: Analisis korelasi dan visualisasi data
- **Research Database**: Penyimpanan data terstruktur untuk analisis
- **Quality Assessment**: Scoring kualitas data untuk standar penelitian
- **Export Capabilities**: Multiple format export untuk dokumentasi akademik

### Output Penelitian
1. **Dataset Terstruktur**: CSV dengan metadata lengkap setiap observasi
2. **Analisis Statistik**: Korelasi antara kondisi lingkungan dan akurasi deteksi
3. **Visualisasi Data**: Charts dan graphs untuk publikasi
4. **Laporan Penelitian**: Template laporan akademik otomatis
5. **Validasi Sistem**: Metrics untuk evaluasi performa model

## Langkah Deployment ke Streamlit Cloud

### 1. Persiapan Repository GitHub

```bash
# Buat repository baru
git init hilal-research
cd hilal-research

# Setup struktur direktori
mkdir -p .streamlit data assets models reports
```

### 2. Upload File Sistem

Salin file-file berikut ke repository:

```
hilal-research/
├── app.py                 # Aplikasi utama (enhanced research version)
├── detect.py              # Detection module (sudah ada)
├── utils.py               # Enhanced utils dengan research features
├── requirements.txt       # Dependencies untuk deployment
├── packages.txt           # System dependencies
├── runtime.txt            # Python version
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── .gitignore            # Git ignore patterns
└── README.md             # Dokumentasi lengkap
```

### 3. Model Setup

**Option A: Model Kecil (<25MB)**
```bash
# Upload langsung ke repository
git add best.pt
git commit -m "Add detection model"
```

**Option B: Model Besar (>25MB)**
```bash
# Gunakan Git LFS
git lfs install
git lfs track "*.pt"
git add .gitattributes
git add best.pt
git commit -m "Add large model with LFS"
```

**Option C: Cloud Storage**
```python
# Modifikasi detect.py untuk download otomatis
import urllib.request

def download_model():
    model_url = "https://drive.google.com/your-model-link"
    urllib.request.urlretrieve(model_url, "best.pt")
```

### 4. Deploy ke Streamlit Cloud

1. **Login ke Streamlit Cloud**
   - Kunjungi https://share.streamlit.io
   - Login dengan GitHub account

2. **Create New App**
   - Klik "New app"
   - Select repository: `hilal-research`
   - Main file path: `app.py`
   - Branch: `main`

3. **Advanced Settings**
   ```
   Python version: 3.10
   Secrets: (opsional untuk API keys)
   ```

4. **Deploy**
   - Klik "Deploy"
   - Monitor build process (~3-5 menit)

### 5. Troubleshooting Deployment

#### Error Umum dan Solusi

**1. Module Import Error**
```
ModuleNotFoundError: No module named 'ultralytics'
```
**Solusi:**
- Pastikan `requirements.txt` lengkap
- Check Python version compatibility
- Tambahkan `--no-deps` flag jika diperlukan

**2. Memory Limit Exceeded**
```
Your app has gone over the resource limits
```
**Solusi:**
```python
# Tambahkan di awal app.py
import gc
import torch

# Memory optimization
@st.cache_resource
def load_model():
    model = YOLO('best.pt')
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return model

# Clear memory after processing
def cleanup_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
```

**3. File Upload Issues**
```python
# Tambahkan size validation
if uploaded_file:
    if uploaded_file.size > 200 * 1024 * 1024:  # 200MB limit
        st.error("File terlalu besar. Maximum 200MB.")
    else:
        # Process file
```

**4. Model Loading Error**
```python
# Fallback jika model tidak ada
try:
    model = YOLO('best.pt')
    DETECTION_AVAILABLE = True
except:
    st.warning("Model tidak tersedia - menggunakan mode demo")
    DETECTION_AVAILABLE = False
```

### 6. Optimization untuk Penelitian

#### Performance Optimization
```python
# Cache expensive operations
@st.cache_data
def process_weather_data(lat, lon):
    return get_weather(lat, lon)

@st.cache_data  
def calculate_astronomical_data(lat, lon, date):
    return get_astronomical_data(lat, lon, date)

# Reduce model size for deployment
model.half()  # Use FP16 precision
```

#### Data Persistence
```python
# Auto-save research data
def auto_save_research_data():
    if len(st.session_