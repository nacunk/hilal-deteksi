# 🌙 Observatorium Deteksi Hilal Digital

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28.0-red.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Aplikasi web berbasis AI untuk deteksi otomatis hilal (bulan sabit) menggunakan teknologi computer vision YOLOv5/v8, terintegrasi dengan analisis Sky Quality Meter (SQM) dan data cuaca real-time.

## ✨ Fitur Unggulan

### 🔍 **Deteksi Hilal Otomatis**
- Menggunakan model YOLOv8 yang telah dilatih khusus untuk deteksi hilal
- Bounding box visual dengan confidence score untuk setiap deteksi
- Mendukung format gambar (JPG, PNG, JPEG) dan video (MP4, MOV, AVI)
- Analisis multi-frame untuk video

### 📊 **Integrasi Sky Quality Meter (SQM)**
- Input nilai SQM untuk analisis kualitas langit
- Klasifikasi otomatis kondisi observasi (Excellent, Baik, Sedang, Buruk)
- Rekomendasi berdasarkan nilai SQM

### 🌤️ **Informasi Cuaca Real-time**
- Pilihan input lokasi: Pilih kota atau koordinat manual
- Database 45+ kota besar di Indonesia dengan koordinat akurat
- Data cuaca meliputi: suhu, kelembapan, kondisi cuaca, visibilitas
- Analisis skor visibilitas untuk observasi astronomi

### 📍 **Database Lokasi Indonesia**
- Jakarta, Surabaya, Bandung, Medan, dan 40+ kota lainnya
- Koordinat GPS yang akurat untuk setiap kota
- Input koordinat manual untuk lokasi spesifik

### 🎨 **Antarmuka Modern**
- Tema Milky Way dengan efek bintang animasi
- Desain responsif untuk desktop dan mobile
- Progress bar dan status real-time
- Visualisasi data dengan metrics dan charts

### 📥 **Export Multi-Format**
- Download hasil deteksi (gambar/video dengan bounding box)
- Export data CSV dengan detail koordinat dan confidence
- Laporan JSON lengkap untuk dokumentasi observasi

## 🚀 Cara Instalasi

### Persyaratan Sistem
- Python 3.8 atau lebih tinggi
- RAM minimum 4GB (8GB direkomendasikan)
- GPU opsional untuk performa lebih cepat

### Instalasi Lokal

1. **Clone repository**
   ```bash
   git clone https://github.com/username/hilal-detection.git
   cd hilal-detection
   ```

2. **Buat virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # atau
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi**
   ```bash
   streamlit run app.py
   ```

5. **Buka browser** dan akses `http://localhost:8501`

### Deploy ke Streamlit Cloud

1. Fork repository ini ke GitHub Anda
2. Buat akun di [Streamlit Cloud](https://streamlit.io/cloud)
3. Koneksi dengan repository GitHub
4. Deploy dengan mengklik "Deploy"

## 📖 Cara Penggunaan

### 1. **Upload Media**
- Pilih file gambar atau video yang berisi hilal
- Aplikasi mendukung berbagai format populer
- Preview otomatis akan ditampilkan

### 2. **Atur Nilai SQM**
- Masukkan nilai Sky Quality Meter (0-30)
- Sistem akan memberikan klasifikasi kualitas langit
- Rekomendasi observasi berdasarkan nilai SQM

### 3. **Input Lokasi**
- **Pilihan 1**: Pilih dari daftar kota Indonesia
- **Pilihan 2**: Input koordinat manual (lat, lon)
- Informasi cuaca akan ditampilkan otomatis

### 4. **Proses Deteksi**
- Klik "Mulai Deteksi Hilal"
- Tunggu proses analisis selesai
- Lihat hasil dengan bounding box dan confidence score

### 5. **Analisis Hasil**
- Informasi detail setiap deteksi hilal
- Skor kualitas observasi berdasarkan SQM dan cuaca
- Rekomendasi untuk observasi selanjutnya

### 6. **Download Hasil**
- Hasil deteksi (gambar/video dengan bounding box)
- Data CSV untuk analisis lanjutan
- Laporan JSON lengkap

## 🛠️ Konfigurasi

### Model YOLOv8
Letakkan file model `best.pt` di root directory project. Model ini berisi weights yang telah dilatih khusus untuk deteksi hilal.

### API Cuaca (Opsional)
Untuk mendapatkan data cuaca real-time:
1. Daftar di [OpenWeatherMap](https://openweathermap.org/api)
2. Dapatkan API key gratis
3. Edit file `utils.py` dan ganti `"demo_key"` dengan API key Anda

### Kustomisasi Kota
Untuk menambah kota baru, edit dictionary `INDONESIAN_CITIES` di file `utils.py`:

```python
INDONESIAN_CITIES = {
    "Nama Kota": {"lat": latitude, "lon": longitude},
    # Tambahkan kota baru di sini
}
```

## 📊 Data dan Format

### Format CSV Output
```csv
x1,y1,x2,y2,confidence,class,width,height,center_x,center_y,area
123.5,67.2,245.8,189.4,0.85,0,122.3,122.2,184.65,128.3,14937.06
```

### Format JSON Report
```json
{
  "lokasi": "Jakarta",
  "koordinat": "-6.2088, 106.8456",
  "sqm": 18.5,
  "kualitas_observasi": "Sedang",
  "file_media": "hilal_20241215.jpg",
  "cuaca": {
    "suhu": 28.5,
    "kelembapan": 75,
    "cuaca": "Berawan Sebagian"
  }
}
```

## 🧪 Mode Demo

Jika model YOLOv8 tidak tersedia, aplikasi akan berjalan dalam mode demo dengan:
- Deteksi simulasi untuk demonstrasi fitur
- Bounding box demo pada posisi yang realistis
- Data CSV demo untuk testing
- Semua fitur UI tetap berfungsi normal

## 🤝 Kontribusi

Kontribusi sangat diterima! Berikut cara berkontribusi:

1. Fork project ini
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Areas untuk Kontribusi
- Penambahan kota Indonesia
- Peningkatan akurasi model AI
- Fitur analisis astronomis lanjutan
- Optimasi performa
- Dokumentasi dan tutorial

## 📝 Roadmap

### v2.0 (Coming Soon)
- [ ] Integrasi dengan data astronomis real-time
- [ ] Prediksi visibilitas hilal berdasarkan lokasi dan waktu
- [ ] Fitur kalibrasi kamera otomatis
- [ ] Export laporan PDF profesional
- [ ] Mobile app untuk iOS dan Android

### v2.1
- [ ] Machine learning untuk prediksi cuaca
- [ ] Integrasi dengan teleskop digital
- [ ] Fitur collaborative observation
- [ ] API untuk integrasi external

## ⚠️ Disclaimer

Aplikasi ini dikembangkan untuk tujuan edukasi dan penelitian. Untuk keperluan resmi pengamatan hilal, selalu konsultasikan dengan ahli astronomi dan lembaga yang berwenang.

## 📄 Lisensi

Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Tim Pengembang

- **AI/ML Engineering**: Model YOLOv8 untuk deteksi hilal
- **Backend Development**: API integration dan data processing  
- **Frontend Development**: Streamlit UI/UX
- **Astronomy Consultation**: Validasi parameter observasi

## 📞 Kontak & Support

- **Issues**: [GitHub Issues](https://github.com/username/hilal-detection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/hilal-detection/discussions)
- **Email**: support@hilal-detection.com

## 🌟 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Framework AI/ML
- [Streamlit](https://streamlit.io/) - Framework web app
- [OpenCV](https://opencv.org/) - Computer vision processing
- [OpenWeatherMap](https://openweathermap.org/) - Weather data API
- Komunitas astronomi Indonesia untuk data validasi

---

**🌙 Membantu komunitas astronomi Indonesia dalam pengamatan hilal yang akurat dan ilmiah**

⭐ Jika project ini bermanfaat, jangan lupa untuk memberikan star di GitHub!