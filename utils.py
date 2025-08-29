import requests
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# Masukkan API key Anda di sini
OPENWEATHER_API_KEY = "API_key_kamu"

def get_weather_data(lat, lon):
    """
    Ambil data cuaca dari OpenWeatherMap berdasarkan koordinat GPS.
    """
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=id&appid={OPENWEATHER_API_KEY}"
        res = requests.get(url).json()
        suhu = res["main"]["temp"]
        kelembapan = res["main"]["humidity"]
        kondisi = res["weather"][0]["description"]
        return {"temperature": suhu, "humidity": kelembapan, "description": kondisi}
    except Exception as e:
        print("Error saat mengambil data cuaca:", e)
        return None


def extract_gps_from_image(file):
    """
    Ekstrak koordinat GPS (latitude, longitude) dari metadata EXIF gambar.
    """
    try:
        image = Image.open(file)
        exif_data = image._getexif()

        if not exif_data:
            return None, None

        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag)
            if tag_name == "GPSInfo":
                for key in value:
                    gps_tag = GPSTAGS.get(key, key)
                    gps_info[gps_tag] = value[key]

        if not gps_info:
            return None, None

        def convert_to_degress(value):
            d, m, s = value
            return float(d[0]) / float(d[1]) + \
                   float(m[0]) / float(m[1]) / 60.0 + \
                   float(s[0]) / float(s[1]) / 3600.0

        lat = convert_to_degress(gps_info["GPSLatitude"])
        if gps_info["GPSLatitudeRef"] != "N":
            lat = -lat

        lon = convert_to_degress(gps_info["GPSLongitude"])
        if gps_info["GPSLongitudeRef"] != "E":
            lon = -lon

        return lat, lon
    except Exception as e:
        print("Error membaca metadata GPS:", e)
        return None, None


def search_city(city_name):
    """
    Cari kota dengan OpenWeatherMap Geocoding API.
    """
    try:
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={OPENWEATHER_API_KEY}"
        res = requests.get(url).json()
        hasil = []
        for kota in res:
            hasil.append({
                "name": kota["name"],
                "lat": kota["lat"],
                "lon": kota["lon"],
                "country": kota["country"]
            })
        return hasil
    except Exception as e:
        print("Error mencari kota:", e)
        return []
