import requests
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# =====================
# Ekstrak GPS dari EXIF
# =====================
def extract_gps_from_image(image_file):
    """Ekstrak metadata GPS dari gambar (jika ada)."""
    try:
        image = Image.open(image_file)
        exif_data = image._getexif()
        if not exif_data:
            return None

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
            return None
    except Exception:
        return None


# =====================
# Ambil Cuaca dari API
# =====================
def get_weather(lat, lon, api_key):
    """Ambil data cuaca dari OpenWeatherMap berdasarkan koordinat."""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=id"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None


# =====================
# Auto-suggest Nama Kota
# =====================
def search_city(city_name, api_key):
    """
    Cari kota dengan nama tertentu menggunakan OpenWeatherMap Geocoding API.
    """
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data:
            # ambil hanya data penting
            return [{"name": f"{c['name']}, {c.get('country','')}", "lat": c["lat"], "lon": c["lon"]} for c in data]
        else:
            return []
    else:
        return []
