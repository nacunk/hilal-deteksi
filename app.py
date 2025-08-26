import streamlit as st
from detect import detect_image, detect_video
from utils import get_weather
import os
os.environ["OPENCV_VIDEOIO_PRIORITY_MSMF"] = "0"  # khusus video capture di headles

st.set_page_config(page_title="Deteksi Hilal YOLOv5 + SQM/Hisab", layout="centered")
st.title("🌙 Deteksi Hilal Otomatis")

# --- Upload Gambar atau Video ---
st.header("1. Upload Media")
media_file = st.file_uploader("Upload Gambar/Video Hilal", type=["jpg","png","jpeg","mp4","mov"])

# --- Input SQM ---
st.header("2. Input SQM")
sqm = st.number_input("Masukkan Nilai SQM:", min_value=0.0, max_value=30.0, step=0.1)

# --- Input Lokasi ---
st.header("3. Input Lokasi / Koordinat")
lat = st.text_input("Latitude (contoh: -6.175)")
lon = st.text_input("Longitude (contoh: 106.827)")

# --- Tombol Proses ---
if st.button("Proses Deteksi"):
    if not media_file:
        st.warning("Silakan upload file gambar atau video terlebih dahulu!")
    else:
        # Simpan sementara file upload
        save_path = os.path.join("assets", media_file.name)
        with open(save_path, "wb") as f:
            f.write(media_file.getbuffer())
        
        # Deteksi gambar atau video
        if media_file.type.startswith("image"):
            output_path = detect_image(save_path, "best.pt")
            st.image(output_path, caption="Hasil Deteksi", use_column_width=True)
        else:
            output_path = detect_video(save_path, "best.pt")
            st.video(output_path)
        
        # Tampilkan SQM
        st.success(f"Nilai SQM: {sqm}")

        # Tampilkan Cuaca
        if lat and lon:
            weather = get_weather(lat, lon)
            st.info(f"Cuaca di lokasi ({lat},{lon}): {weather.get('cuaca')}\nSuhu: {weather.get('suhu')} °C\nKelembapan: {weather.get('kelembapan')}%")
