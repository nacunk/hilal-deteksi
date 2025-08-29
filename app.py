import streamlit as st
from utils import get_gps_from_image, get_weather, geocode_city

st.set_page_config(page_title="🌙 Deteksi Hilal + Cuaca", layout="centered")
st.title("🌙 Deteksi Hilal dan Informasi Cuaca")
st.write("Upload foto hilal, sistem akan membaca metadata GPS dan menampilkan cuaca otomatis.")

# Upload File Foto
uploaded_file = st.file_uploader("Upload foto (JPEG/PNG)", type=["jpg","jpeg","png"])
lat, lon = None, None

if uploaded_file:
    lat, lon = get_gps_from_image(uploaded_file)
    if lat and lon:
        st.success(f"Metadata GPS ditemukan: Latitude {lat}, Longitude {lon}")
    else:
        st.info("Metadata GPS tidak ditemukan. Silakan pilih kota atau masukkan koordinat manual.")

# Pilihan fallback
fallback_option = None
if not lat or not lon:
    fallback_option = st.radio(
        "Pilih metode input lokasi:",
        ("Pilih Kota", "Isi Koordinat Manual")
    )

if fallback_option == "Pilih Kota":
    # Dropdown kota default Indonesia
    kota_dict = {
        "Jakarta": (-6.2088, 106.8456),
        "Bandung": (-6.9175, 107.6191),
        "Surabaya": (-7.2575, 112.7521),
        "Yogyakarta": (-7.7956, 110.3695),
        "Medan": (3.5952, 98.6722)
    }

    kota_input = st.text_input("Cari kota global")
    kota_results = geocode_city(kota_input) if kota_input else []

    if kota_results:
        pilihan = st.selectbox("Pilih hasil kota", [f"{c['name']}, {c['country']}" for c in kota_results])
        idx = [f"{c['name']}, {c['country']}" for c in kota_results].index(pilihan)
        lat = kota_results[idx]['lat']
        lon = kota_results[idx]['lon']
    else:
        kota_selected = st.selectbox("Pilih kota Indonesia", list(kota_dict.keys()))
        lat, lon = kota_dict[kota_selected]

elif fallback_option == "Isi Koordinat Manual":
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")

# Tampilkan Cuaca jika koordinat ada
if lat and lon:
    data_cuaca = get_weather(lat, lon)
    if data_cuaca:
        st.subheader(f"Cuaca di {data_cuaca['lokasi']}")
        st.write(f"Suhu: {data_cuaca['suhu']} °C")
        st.write(f"Kelembapan: {data_cuaca['kelembapan']} %")
        st.write(f"Kondisi: {data_cuaca['kondisi']}")
