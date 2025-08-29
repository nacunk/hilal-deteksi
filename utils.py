import requests
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# Masukkan API key OpenWeatherMap Anda
OPENWEATHER_API_KEY = "API_key_kamu"

# -----------------------------
# Ekstrak GPS dari EXIF
# -----------------------------
def extract_gps_from_image(image_file):
    """Ekstrak metadata GPS dari gambar (jika ada)."""
    try:
        image = Image.open(image_file)
        exif_data = image._getexif()
        if not exif_data:
            return None, None

        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag)
            if tag_name == "GPSInfo":
                for key in value.keys():
                    gps_info[GPSTAGS.get(key)] = value[key]

        if gps_info:
            lat = gps_info.get("GPSLatitude")
            lat_ref = gps_info.get("GPSLatitudeRef")
            lon = gps_info.get("GPSLongitude")
            lon_ref = gps_info.get("GPSLongitudeRef")

            def convert_to_degrees(value):
                d, m, s = value
                return d[0] / d[1] + (m[0] / m[1]) / 60 + (s[0] / s[1]) / 3600

            latitude = convert_to_degrees(lat)
            longitude = convert_to_degrees(lon)

            if lat_ref != "N":
                latitude = -latitude
            if lon_ref != "E":
                longitude = -longitude

            return latitude, longitude
        else:
            return None, None
    except Exception:
        return None, None


# -----------------------------
# Ambil cuaca dari API
# -----------------------------
def get_weather(lat, lon):
    """Ambil data cuaca dari OpenWeatherMap berdasarkan koordinat."""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=id"
        res = requests.get(url).json()
        return {
            "city": res.get("name", ""),
            "temperature": res["main"]["temp"],
            "humidity": res["main"]["humidity"],
            "description": res["weather"][0]["description"]
        }
    except Exception as e:
        print("Error ambil cuaca:", e)
        return None


# -----------------------------
# Auto-suggest nama kota
# -----------------------------
def search_city(city_name):
    """Cari kota menggunakan OpenWeatherMap Geocoding API."""
    try:
        if "," not in city_name:
            city_name = city_name.strip() + ",ID"  # default ke Indonesia

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
