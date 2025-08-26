import streamlit as st
from detect import detect_image, detect_video
from utils import get_weather
import os
from pathlib import Path

# --- Config Streamlit ---
st.set_page_config(page_title="Deteksi Hilal + SQM + Cuaca BMKG", layout="centered")
st.title("🌙 Deteksi Hilal Otomatis")

# --- Pastikan folder assets ada ---
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

# --- Upload Gambar / Video ---
file = st.file_uploader("Upload Gambar / Video", type=["jpg","png","jpeg","mp4","mov"])

# --- Input SQM ---
sqm = st.number_input("Masukkan Nilai SQM", min_value=0.0, max_value=30.0, step=0.1)

# --- Input Lokasi / Koordinat ---
st.subheader("Lokasi Observasi")
input_mode = st.radio("Pilih Mode Input Lokasi:", ("Kota", "Koordinat"))

if input_mode == "Kota":
    city_name = st.text_input("Masukkan Nama Kota")
    lat, lon = None, None
elif input_mode == "Koordinat":
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")
    city_name = None

# --- Tombol Proses ---
if st.button("Deteksi Hilal"):

    if not file:
        st.warning("Silakan upload gambar atau video terlebih dahulu.")
    else:
        # Simpan file sementara
        file_path = ASSETS_DIR / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        # Deteksi
        if file.type.startswith("image"):
            result_path = detect_image(str(file_path))
            st.image(result_path, caption="Hasil Deteksi Hilal", use_column_width=True)
        elif file.type.startswith("video"):
            result_path = detect_video(str(file_path))
            st.video(result_path)
        else:
            st.error("Format file tidak didukung!")

    # --- Tampilkan SQM ---
    st.info(f"Nilai SQM: {sqm}")

    # --- Tampilkan Cuaca ---
    if input_mode == "Kota" and city_name:
        weather = get_weather(city_name=city_name)
    elif input_mode == "Koordinat" and lat is not None and lon is not None:
        weather = get_weather(lat=lat, lon=lon)
    else:
        weather = None

    if weather:
        st.subheader("🌤 Informasi Cuaca")
        st.write(f"🌡 Suhu: {weather['suhu']} °C")
        st.write(f"💧 Kelembapan: {weather['kelembapan']} %")
        st.write(f"☁ Cuaca: {weather['cuaca']}")
