import streamlit as st
import os
from detect import detect_image, detect_video
from utils import extract_gps_from_image, get_weather, search_city

# Wajib Streamlit config
st.set_page_config(page_title="🌙 Deteksi Hilal YOLOv5 + Cuaca", layout="centered")

st.title("🌙 Deteksi Hilal Otomatis")
st.write("Aplikasi ini menggunakan YOLOv5 untuk mendeteksi hilal dari citra/video observasi, "
         "serta menampilkan informasi cuaca (suhu & kelembapan).")

# Upload file gambar/video
uploaded_file = st.file_uploader("Unggah gambar atau video observasi hilal", type=["jpg", "jpeg", "png", "mp4", "avi"])

if uploaded_file is not None:
    file_path = os.path.join("temp", uploaded_file.name)
    os.makedirs("temp", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Deteksi gambar/video
    if uploaded_file.type.startswith("image"):
        st.image(file_path, caption="Citra Observasi", use_container_width=True)
        output_img = detect_image(file_path)
        st.image(output_img, caption="Hasil Deteksi", use_container_width=True)

        # --- GPS Metadata ---
        lat, lon = extract_gps_from_image(file_path)
        if lat and lon:
            st.success(f"Metadata GPS terdeteksi: Latitude={lat}, Longitude={lon}")
            weather = get_weather(lat, lon)
            if weather:
                st.subheader("🌤️ Informasi Cuaca")
                st.write(f"Lokasi: {weather['city']}")
                st.write(f"Suhu: {weather['temperature']} °C")
                st.write(f"Kelembapan: {weather['humidity']} %")
            else:
                st.error("Gagal mengambil data cuaca.")
        else:
            st.warning("Metadata GPS tidak ditemukan pada gambar.")

            # --- Opsi input lokasi manual ---
            pilihan = st.radio("Pilih cara menentukan lokasi:", ["Cari Kota (Auto-suggest)", "Isi Koordinat Manual"])

            if pilihan == "Cari Kota (Auto-suggest)":
                city_name = st.text_input("Ketik nama kota (misalnya: Surabaya, Jakarta, Cairo, Makkah)")

                if city_name:
                    # Jika user tidak menulis kode negara, otomatis tambah ",ID"
                    if "," not in city_name:
                        city_name = city_name.strip() + ",ID"

                    results = search_city(city_name)
                    if results:
                        kota_terpilih = st.selectbox(
                            "Pilih kota:",
                            [f"{k['name']} ({k['country']}) - lat:{k['lat']}, lon:{k['lon']}" for k in results]
                        )
                        idx = [f"{k['name']} ({k['country']}) - lat:{k['lat']}, lon:{k['lon']}" for k in results].index(kota_terpilih)
                        lat, lon = results[idx]["lat"], results[idx]["lon"]

                        weather = get_weather(lat, lon)
                        if weather:
                            st.subheader("🌤️ Informasi Cuaca")
                            st.write(f"Lokasi: {weather['city']}")
                            st.write(f"Suhu: {weather['temperature']} °C")
                            st.write(f"Kelembapan: {weather['humidity']} %")
                    else:
                        st.error("Tidak ditemukan kota dengan nama tersebut.")

            elif pilihan == "Isi Koordinat Manual":
                lat = st.number_input("Latitude", format="%.6f")
                lon = st.number_input("Longitude", format="%.6f")
                if lat and lon:
                    weather = get_weather(lat, lon)
                    if weather:
                        st.subheader("🌤️ Informasi Cuaca")
                        st.write(f"Lokasi: {weather['city']}")
                        st.write(f"Suhu: {weather['temperature']} °C")
                        st.write(f"Kelembapan: {weather['humidity']} %")

    elif uploaded_file.type.startswith("video"):
        st.video(file_path)
        output_video = detect_video(file_path)
        st.video(output_video, format="video/mp4")
