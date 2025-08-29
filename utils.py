import exifread
import requests

# FUNGSI METADATA FOTO
def get_gps_from_image(file):
    try:
        tags = exifread.process_file(file, details=False)
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            lat_ref = str(tags['GPS GPSLatitudeRef'])
            lon_ref = str(tags['GPS GPSLongitudeRef'])
            lat = tags['GPS GPSLatitude'].values
            lon = tags['GPS GPSLongitude'].values

            lat = float(lat[0].num)/float(lat[0].den) + \
                  float(lat[1].num)/(float(lat[1].den)*60) + \
                  float(lat[2].num)/(float(lat[2].den)*3600)
            lon = float(lon[0].num)/float(lon[0].den) + \
                  float(lon[1].num)/(float(lon[1].den)*60) + \
                  float(lon[2].num)/(float(lon[2].den)*3600)
            
            if lat_ref != 'N':
                lat = -lat
            if lon_ref != 'E':
                lon = -lon
            return lat, lon
    except:
        pass
    return None, None

# FUNGSI WEATHER API
OPENWEATHER_API_KEY = "ISI_API_KEY_ANDA"

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=id"
    try:
        response = requests.get(url).json()
        data = {
            "lokasi": response.get("name"),
            "suhu": response["main"]["temp"],
            "kelembapan": response["main"]["humidity"],
            "kondisi": response["weather"][0]["description"].capitalize()
        }
        return data
    except:
        return None

# FUNGSI GEOCODING
def geocode_city(city_name):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=5&appid={OPENWEATHER_API_KEY}"
    try:
        results = requests.get(url).json()
        return results
    except:
        return []
