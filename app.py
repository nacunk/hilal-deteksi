import streamlit as st
from detect import detect_image, detect_video
from utils import get_weather
import os

st.set_page_config(page_title="Deteksi Hilal YOLOv5 + SQM & Cuaca", layout="centered")
st.title("🌙 Deteksi Hilal Otomatis")

file = st.file_uploader("Upload Gambar/Video", type=["jpg", "png", "mp4", "mov"])
sqm = st.number_input("Masukkan Nilai SQM", min_value=0.0, max_value=30.0, step=0.1)
lat = st.number_input("Latitude", format="%.6f")
lon = st.number_input("Longitude", format="%.6f")

if st.button("Deteksi Hilal"):
    if file:
        os.makedirs("assets", exist_ok=True)
        file_path = os.path.join("assets", file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        if file.type.startswith("image"):
            result_img = detect_image(file_path)
            st.image(result_img, caption="Hasil Deteksi", use_column_width=True)
        elif file.type.startswith("video"):
            result_video_path = detect_video(file_path)
            st.video(result_video_path)
        else:
            st.error("Format file tidak didukung!")

    st.info(f"Nilai SQM: {sqm}")

    if lat != 0 and lon != 0:
        weather = get_weather(lat, lon)
        st.write(f"🌡 Suhu: {weather['suhu']} °C")
        st.write(f"💧 Kelembapan: {weather['kelembapan']} %")
        st.write(f"☁ Cuaca: {weather['cuaca']}")
