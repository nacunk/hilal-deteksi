import streamlit as st
from detect import detect_image
from utils import get_exif_data, get_hilal_position, get_sky_brightness
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Deteksi Hilal", layout="centered")
st.title("🌙 Deteksi Hilal Otomatis")

uploaded_file = st.file_uploader("Upload Gambar Hilal", type=["jpg","png","jpeg"])

if uploaded_file:
    # Simpan sementara
    with open(f"uploads/{uploaded_file.name}", "wb") as f:
        f.write(uploaded_file.getbuffer())
    image_path = f"uploads/{uploaded_file.name}"

    st.image(image_path, caption="Gambar Hilal Asli", use_column_width=True)

    # Deteksi hilal
    st.info("Mendeteksi hilal...")
    results = detect_image(image_path)
    st.image(f'outputs/{uploaded_file.name}', caption="Hasil Deteksi", use_column_width=True)

    # Ambil EXIF
    exif = get_exif_data(image_path)
    st.write("📷 Metadata Kamera:", exif)

    # Jika GPS tersedia
    if exif['gps_lat'] and exif['gps_lon']:
        lat = float(exif['gps_lat'].values[0].num)/float(exif['gps_lat'].values[0].den)
        lon = float(exif['gps_lon'].values[0].num)/float(exif['gps_lon'].values[0].den)
    else:
        lat = st.number_input("Latitude", value=0.0)
        lon = st.number_input("Longitude", value=0.0)

    # Hitung posisi hilal
    alt, az = get_hilal_position(lat, lon, datetime.now())
    st.write(f"🔭 Posisi Hilal - Altitude: {alt:.2f}°, Azimut: {az:.2f}°")

    # Kecerlangan langit
    brightness = get_sky_brightness(image_path)
    st.write(f"🌌 Rata-rata kecerlangan langit: {brightness:.2f}")

    # Simpan hasil ke CSV
    df = pd.DataFrame([{
        'filename': uploaded_file.name,
        'altitude': alt,
        'azimuth': az,
        'brightness': brightness,
        'camera': exif['camera']
    }])
    df.to_csv(f"outputs/result_{uploaded_file.name}.csv", index=False)
    st.success(f"Hasil disimpan: outputs/result_{uploaded_file.name}.csv")
