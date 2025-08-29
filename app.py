import streamlit as st
import os
from detect import detect_image, detect_video
from utils import extract_gps_from_image, get_weather, search_city

st.set_page_config(page_title="🌙 Deteksi Hilal + Cuaca", layout="centered")

st.title("🌙 Deteksi Hilal Otomatis")
st.write("Unggah gambar/video observasi hilal. Aplikasi akan menampilkan deteksi hilal dan informasi cuaca (suhu & kelembapan).")

# Upload file
uploaded_file = st.file_uploader("Unggah file (gambar/video)", type=["jpg", "jpeg", "png", "mp4", "avi"])

if uploaded_file is not None:
    os.makedirs("temp", exist_ok=True)
    file_path = os.path.join("temp", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Tampilkan preview
    if uploaded_file.type.startswith("image"):
        st.image(file_path, caption="Citra Observasi", use_column_width=True)
        output_img = detect_image(file_path)
        st.image(output_img, caption="Hasil Deteksi", use_column_width=True)

        # --- Cek metadata GPS ---
        lat, lon = extract_gps_from_image(file_path)
        if lat and lon:
            st.success(f"📍 Lokasi terdeteksi: Latitude={lat}, Longitude={lon}")
            weather = get_weather(lat, lon)
            if weather:
                st.subheader("🌤️ Informasi Cuaca")
                st.write(f"Lokasi: {weather['city']}")
                st.write(f"Suhu: {weather['temperature']} °C")
                st.write(f"Kelembapan: {weather['humidity']} %")
                st.write(f"Kondisi: {weather['description']}")
        else:
            st.warning("❗ Metadata GPS tidak ditemukan. Pilih opsi lokasi:")
            opsi = st.radio("Metode lokasi:", ["Cari Kota (Auto-suggest)", "Isi Koordinat Manual"])
            
            if opsi == "Cari Kota (Auto-suggest)":
                city_input = st.text_input("Ketik nama kota (misal: Surabaya, Jakarta, Makkah)")
                if city_input:
                    hasil = search_city(city_input)
                    if hasil:
                        pilihan = st.selectbox(
                            "Pilih kota:",
                            [f"{k['name']} ({k['country']}) - lat:{k['lat']}, lon:{k['lon']}" for k in hasil]
                        )
                        idx = [f"{k['name']} ({k['country']}) - lat:{k['lat']}, lon:{k['lon']}" for k in hasil].index(pilihan)
                        lat, lon = hasil[idx]["lat"], hasil[idx]["lon"]

                        weather = get_weather(lat, lon)
                        if weather:
                            st.subheader("🌤️ Informasi Cuaca")
                            st.write(f"Lokasi: {weather['city']}")
                            st.write(f"Suhu: {weather['temperature']} °C")
                            st.write(f"Kelembapan: {weather['humidity']} %")
                            st.write(f"Kondisi: {weather['description']}")
                    else:
                        st.error("Tidak ditemukan kota dengan nama tersebut.")

            elif opsi == "Isi Koordinat Manual":
                lat = st.number_input("Latitude", format="%.6f")
                lon = st.number_input("Longitude", format="%.6f")
                if lat and lon:
                    weather = get_weather(lat, lon)
                    if weather:
                        st.subheader("🌤️ Informasi Cuaca")
                        st.write(f"Lokasi: {weather['city']}")
                        st.write(f"Suhu: {weather['temperature']} °C")
                        st.write(f"Kelembapan: {weather['humidity']} %")
                        st.write(f"Kondisi: {weather['description']}")

    elif uploaded_file.type.startswith("video"):
        st.video(file_path)
        output_video = detect_video(file_path)
        st.video(output_video, format="video/mp4")
