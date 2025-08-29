import streamlit as st
from utils import extract_gps_from_image, get_weather_data, search_city

st.set_page_config(page_title="🌙 Deteksi Hilal + Info Cuaca", layout="centered")

st.title("🌙 Aplikasi Deteksi Hilal dengan Info Cuaca")
st.write(
    "Unggah file observasi hilal (gambar/foto). "
    "Aplikasi akan mencoba mendeteksi lokasi dari metadata gambar, "
    "jika tidak tersedia Anda bisa memilih kota, mencari kota (auto-suggest), atau memasukkan koordinat secara manual."
)

# Upload file
uploaded_file = st.file_uploader("Unggah file gambar observasi", type=["jpg", "jpeg", "png"])

latitude, longitude = None, None

if uploaded_file is not None:
    st.image(uploaded_file, caption="Gambar yang diunggah", use_column_width=True)

    # Ekstrak metadata GPS
    lat, lon = extract_gps_from_image(uploaded_file)

    if lat and lon:
        st.success(f"📍 Lokasi terdeteksi dari metadata: Latitude: {lat}, Longitude: {lon}")
        latitude, longitude = lat, lon
    else:
        st.warning("❗ Tidak ditemukan metadata GPS pada gambar. Silakan pilih opsi lokasi.")

        opsi_lokasi = st.radio("Pilih cara menentukan lokasi:", ["Cari Kota (Auto-suggest)", "Isi Koordinat Manual"])

        if opsi_lokasi == "Cari Kota (Auto-suggest)":
            nama_kota = st.text_input("Ketik nama kota (misalnya: Jakarta, Cairo, Makkah)")
            if nama_kota:
                hasil = search_city(nama_kota)
                if hasil:
                    pilihan = st.selectbox(
                        "Pilih kota yang sesuai:",
                        [f"{h['name']} ({h['country']}) - Lat:{h['lat']}, Lon:{h['lon']}" for h in hasil]
                    )
                    idx = [f"{h['name']} ({h['country']}) - Lat:{h['lat']}, Lon:{h['lon']}" for h in hasil].index(pilihan)
                    latitude, longitude = hasil[idx]["lat"], hasil[idx]["lon"]
                    st.info(f"📍 Lokasi dipilih: {pilihan}")
                else:
                    st.error("Tidak ditemukan kota dengan nama tersebut.")
        
        elif opsi_lokasi == "Isi Koordinat Manual":
            latitude = st.number_input("Masukkan Latitude", value=0.0, format="%.6f")
            longitude = st.number_input("Masukkan Longitude", value=0.0, format="%.6f")

    # Ambil info cuaca
    if st.button("Tampilkan Informasi Cuaca"):
        if latitude and longitude:
            weather = get_weather_data(latitude, longitude)
            if weather:
                st.subheader("🌦 Informasi Cuaca Saat Ini")
                st.write(f"🌡 Suhu: {weather['temperature']} °C")
                st.write(f"💧 Kelembapan: {weather['humidity']} %")
                st.write(f"☁ Kondisi: {weather['description']}")
            else:
                st.error("Gagal mengambil data cuaca. Periksa API key Anda.")
        else:
            st.error("Lokasi tidak valid. Harap isi Latitude dan Longitude.")
