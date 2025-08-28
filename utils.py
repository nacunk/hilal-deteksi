import requests
import json
import random
import datetime
import os

# Daftar kota-kota di Indonesia dengan koordinat lengkap
INDONESIAN_CITIES = {
    "Jakarta": {"lat": -6.175, "lon": 106.827, "timezone": "WIB", "province": "DKI Jakarta"},
    "Surabaya": {"lat": -7.257, "lon": 112.752, "timezone": "WIB", "province": "Jawa Timur"},
    "Bandung": {"lat": -6.917, "lon": 107.619, "timezone": "WIB", "province": "Jawa Barat"},
    "Medan": {"lat": 3.595, "lon": 98.672, "timezone": "WIB", "province": "Sumatra Utara"},
    "Semarang": {"lat": -6.966, "lon": 110.420, "timezone": "WIB", "province": "Jawa Tengah"},
    "Makassar": {"lat": -5.147, "lon": 119.432, "timezone": "WITA", "province": "Sulawesi Selatan"},
    "Palembang": {"lat": -2.998, "lon": 104.756, "timezone": "WIB", "province": "Sumatra Selatan"},
    "Tangerang": {"lat": -6.178, "lon": 106.631, "timezone": "WIB", "province": "Banten"},
    "Depok": {"lat": -6.402, "lon": 106.794, "timezone": "WIB", "province": "Jawa Barat"},
    "Bekasi": {"lat": -6.238, "lon": 106.976, "timezone": "WIB", "province": "Jawa Barat"},
    "Padang": {"lat": -0.947, "lon": 100.414, "timezone": "WIB", "province": "Sumatra Barat"},
    "Denpasar": {"lat": -8.650, "lon": 115.216, "timezone": "WITA", "province": "Bali"},
    "Samarinda": {"lat": -0.502, "lon": 117.154, "timezone": "WITA", "province": "Kalimantan Timur"},
    "Banjarmasin": {"lat": -3.319, "lon": 114.590, "timezone": "WITA", "province": "Kalimantan Selatan"},
    "Batam": {"lat": 1.130, "lon": 104.053, "timezone": "WIB", "province": "Kepulauan Riau"},
    "Pekanbaru": {"lat": 0.533, "lon": 101.447, "timezone": "WIB", "province": "Riau"},
    "Bogor": {"lat": -6.595, "lon": 106.816, "timezone": "WIB", "province": "Jawa Barat"},
    "Malang": {"lat": -7.977, "lon": 112.633, "timezone": "WIB", "province": "Jawa Timur"},
    "Yogyakarta": {"lat": -7.797, "lon": 110.370, "timezone": "WIB", "province": "DIY Yogyakarta"},
    "Balikpapan": {"lat": -1.268, "lon": 116.831, "timezone": "WITA", "province": "Kalimantan Timur"},
    "Pontianak": {"lat": -0.026, "lon": 109.343, "timezone": "WIB", "province": "Kalimantan Barat"},
    "Manado": {"lat": 1.487, "lon": 124.845, "timezone": "WIT", "province": "Sulawesi Utara"},
    "Jambi": {"lat": -1.588, "lon": 103.613, "timezone": "WIB", "province": "Jambi"},
    "Cirebon": {"lat": -6.706, "lon": 108.557, "timezone": "WIB", "province": "Jawa Barat"},
    "Serang": {"lat": -6.120, "lon": 106.150, "timezone": "WIB", "province": "Banten"},
    "Mataram": {"lat": -8.583, "lon": 116.116, "timezone": "WITA", "province": "Nusa Tenggara Barat"},
    "Jayapura": {"lat": -2.533, "lon": 140.717, "timezone": "WIT", "province": "Papua"},
    "Kupang": {"lat": -10.167, "lon": 123.583, "timezone": "WIT", "province": "Nusa Tenggara Timur"},
    "Banda Aceh": {"lat": 5.548, "lon": 95.324, "timezone": "WIB", "province": "Aceh"},
    "Ambon": {"lat": -3.710, "lon": 128.181, "timezone": "WIT", "province": "Maluku"},
    "Bandar Lampung": {"lat": -5.429, "lon": 105.261, "timezone": "WIB", "province": "Lampung"},
    "Kendari": {"lat": -3.945, "lon": 122.515, "timezone": "WITA", "province": "Sulawesi Tenggara"},
    "Palu": {"lat": -0.901, "lon": 119.870, "timezone": "WITA", "province": "Sulawesi Tengah"},
    "Gorontalo": {"lat": 0.544, "lon": 123.058, "timezone": "WITA", "province": "Gorontalo"}
}

def get_city_coordinates(city_name):
    """
    Mendapatkan koordinat lengkap dari nama kota
    
    Args:
        city_name (str): Nama kota
    
    Returns:
        dict: Informasi koordinat dan zona waktu atau None jika tidak ditemukan
    """
    return INDONESIAN_CITIES.get(city_name, None)

def get_weather_from_api(lat, lon, api_key=None):
    """
    Ambil data cuaca dari OpenWeatherMap API
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        api_key (str): API key OpenWeatherMap (opsional)
    
    Returns:
        dict: Data cuaca atau None jika gagal
    """
    try:
        if not api_key:
            # Gunakan API key dari environment variable jika tersedia
            api_key = os.environ.get('OPENWEATHER_API_KEY', 'demo_key')
        
        # URL OpenWeatherMap API
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric',
            'lang': 'id'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "suhu": round(data['main']['temp'], 1),
                "kelembapan": data['main']['humidity'],
                "cuaca": data['weather'][0]['description'].title(),
                "tekanan": data['main']['pressure'],
                "angin_kecepatan": data.get('wind', {}).get('speed', 0),
                "angin_arah": data.get('wind', {}).get('deg', 0),
                "visibilitas": data.get('visibility', 10000) / 1000,  # Convert to km
                "awan": data.get('clouds', {}).get('all', 0),
                "sunrise": datetime.datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                "sunset": datetime.datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                "source": "OpenWeatherMap API"
            }
        else:
            print(f"OpenWeatherMap API error: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error getting weather: {e}")
        return None
    except Exception as e:
        print(f"Error parsing weather data: {e}")
        return None

def get_simulated_weather(lat, lon):
    """
    Generate data cuaca simulasi yang realistis berdasarkan lokasi dan musim di Indonesia
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
    
    Returns:
        dict: Data cuaca simulasi
    """
    try:
        current_time = datetime.datetime.now()
        current_month = current_time.month
        current_hour = current_time.hour
        
        # Pola iklim Indonesia
        # Musim hujan: November-Maret, Musim kemarau: April-Oktober
        is_rainy_season = current_month in [11, 12, 1, 2, 3]
        is_transition = current_month in [4, 10]
        
        # Simulasi suhu berdasarkan lokasi dan waktu
        # Suhu dasar berdasarkan lintang
        if lat > 5:  # Sumatra Utara
            base_temp = 25
        elif lat > 0:  # Kalimantan Utara, Sulawesi Utara
            base_temp = 27
        elif lat > -5:  # Sumatra, Kalimantan
            base_temp = 28
        elif lat > -8:  # Jawa, Bali
            base_temp = 26
        else:  # Nusa Tenggara
            base_temp = 29
        
        # Variasi suhu berdasarkan waktu
        if 6 <= current_hour <= 11:  # Pagi
            temp_factor = random.uniform(-2, 1)
        elif 12 <= current_hour <= 16:  # Siang
            temp_factor = random.uniform(2, 6)
        elif 17 <= current_hour <= 20:  # Sore
            temp_factor = random.uniform(0, 3)
        else:  # Malam
            temp_factor = random.uniform(-4, -1)
        
        # Variasi musiman
        if is_rainy_season:
            temp_factor -= random.uniform(0, 2)
        
        simulated_temp = round(base_temp + temp_factor, 1)
        simulated_temp = max(20.0, min(simulated_temp, 38.0))  # Limit realistic range
        
        # Simulasi kelembapan
        if is_rainy_season:
            humidity = random.randint(75, 95)
            weather_conditions = [
                "Hujan Ringan", "Berawan", "Mendung", "Gerimis", 
                "Hujan Sedang", "Berawan Gelap"
            ]
        elif is_transition:
            humidity = random.randint(65, 85)
            weather_conditions = [
                "Berawan Sebagian", "Cerah Berawan", "Mendung Sebagian", 
                "Cerah", "Berawan"
            ]
        else:  # Musim kemarau
            humidity = random.randint(55, 75)
            weather_conditions = [
                "Cerah", "Cerah Berawan", "Berawan Sebagian", 
                "Terang", "Cerah Cerah"
            ]
        
        # Simulasi data tambahan
        pressure = random.randint(1008, 1018)  # hPa
        wind_speed = random.uniform(0.5, 8.0)  # m/s
        wind_direction = random.randint(0, 359)  # degrees
        visibility = random.uniform(8.0, 15.0) if not is_rainy_season else random.uniform(3.0, 10.0)  # km
        cloud_cover = random.randint(20, 90) if is_rainy_season else random.randint(0, 60)  # %
        
        # Simulasi sunrise/sunset (approximate untuk Indonesia)
        sunrise_hour = random.randint(5, 6)
        sunrise_minute = random.randint(30, 59)
        sunset_hour = random.randint(17, 19)
        sunset_minute = random.randint(0, 45)
        
        return {
            "suhu": simulated_temp,
            "kelembapan": humidity,
            "cuaca": random.choice(weather_conditions),
            "tekanan": pressure,
            "angin_kecepatan": round(wind_speed, 1),
            "angin_arah": wind_direction,
            "visibilitas": round(visibility, 1),
            "awan": cloud_cover,
            "sunrise": f"{sunrise_hour:02d}:{sunrise_minute:02d}",
            "sunset": f"{sunset_hour:02d}:{sunset_minute:02d}",
            "source": "Simulated Data"
        }
        
    except Exception as e:
        print(f"Error in simulated weather: {e}")
        return {
            "suhu": 27.5,
            "kelembapan": 75,
            "cuaca": "Data tidak tersedia",
            "tekanan": 1013,
            "angin_kecepatan": 2.0,
            "angin_arah": 0,
            "visibilitas": 10.0,
            "awan": 50,
            "sunrise": "06:00",
            "sunset": "18:00",
            "source": "Fallback Data"
        }

def get_weather(lat, lon, use_api=True):
    """
    Fungsi utama untuk mendapatkan data cuaca
    Mencoba API terlebih dahulu, jika gagal menggunakan simulasi
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        use_api (bool): Apakah menggunakan API atau langsung simulasi
    
    Returns:
        dict: Data cuaca lengkap
    """
    if use_api:
        # Coba ambil dari API
        weather_data = get_weather_from_api(lat, lon)
        if weather_data:
            return weather_data
    
    # Fallback ke data simulasi
    return get_simulated_weather(lat, lon)

def get_location_info(lat, lon):
    """
    Mendapatkan informasi lokasi berdasarkan koordinat
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
    
    Returns:
        dict: Informasi lokasi
    """
    try:
        # Cari kota terdekat dari database lokal
        closest_city = None
        min_distance = float('inf')
        
        for city, coords in INDONESIAN_CITIES.items():
            city_lat, city_lon = coords["lat"], coords["lon"]
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                closest_city = city
        
        if closest_city and min_distance < 0.5:  # Dalam radius ~55km
            city_data = INDONESIAN_CITIES[closest_city]
            return {
                "address": f"Sekitar {closest_city}",
                "city": closest_city,
                "province": city_data.get("province", "Indonesia"),
                "timezone": city_data.get("timezone", "WIB"),
                "distance_km": round(min_distance * 111, 1)  # Convert to km approximately
            }
    except Exception as e:
        print(f"Error getting location info: {e}")
    
    # Fallback berdasarkan koordinat
    timezone = "WIB" if lon < 120 else "WITA" if lon < 135 else "WIT"
    return {
        "address": f"Koordinat {lat:.3f}, {lon:.3f}",
        "city": "Lokasi Custom",
        "province": "Indonesia",
        "timezone": timezone,
        "distance_km": 0
    }

def calculate_moon_visibility(sqm_value, weather_data):
    """
    Hitung perkiraan visibilitas bulan berdasarkan SQM dan cuaca
    Menggunakan skala yang lebih realistis dan detailed
    
    Args:
        sqm_value (float): Nilai SQM
        weather_data (dict): Data cuaca
    
    Returns:
        dict: Analisis visibilitas
    """
    visibility_score = 0
    conditions = []
    recommendations = []
    
    # Skor berdasarkan SQM (40 poin maksimal)
    if sqm_value >= 22:
        visibility_score += 40
        conditions.append("Langit sangat gelap (Excellent untuk observasi)")
        recommendations.append("Kondisi SQM ideal untuk deteksi hilal")
    elif sqm_value >= 21:
        visibility_score += 35
        conditions.append("Langit sangat gelap (Sangat baik)")
        recommendations.append("SQM sangat mendukung observasi")
    elif sqm_value >= 20:
        visibility_score += 28
        conditions.append("Langit cukup gelap (Baik)")
        recommendations.append("SQM mendukung observasi dengan baik")
    elif sqm_value >= 19:
        visibility_score += 22
        conditions.append("Langit sedang (Cukup baik)")
        recommendations.append("SQM masih dapat mendukung observasi")
    elif sqm_value >= 18:
        visibility_score += 15
        conditions.append("Langit terang (Sedang)")
        recommendations.append("SQM terbatas, gunakan filter atau teknik khusus")
    else:
        visibility_score += 8
        conditions.append("Langit sangat terang (Buruk)")
        recommendations.append("SQM tidak ideal, pertimbangkan lokasi yang lebih gelap")
    
    # Skor berdasarkan cuaca (25 poin maksimal)
    weather_desc = weather_data.get('cuaca', '').lower()
    cloud_cover = weather_data.get('awan', 50)
    
    if any(word in weather_desc for word in ['cerah', 'terang', 'clear']):
        visibility_score += 25
        conditions.append("Cuaca cerah")
        recommendations.append("Kondisi cuaca optimal")
    elif 'cerah berawan' in weather_desc or 'berawan sebagian' in weather_desc:
        visibility_score += 18
        conditions.append("Cuaca cerah berawan")
        recommendations.append("Cuaca cukup mendukung")
    elif any(word in weather_desc for word in ['berawan', 'mendung']):
        if cloud_cover < 70:
            visibility_score += 12
            conditions.append("Berawan sedang")
        else:
            visibility_score += 6
            conditions.append("Berawan tebal")
        recommendations.append("Tunggu celah awan atau ubah waktu observasi")
    elif any(word in weather_desc for word in ['hujan', 'gerimis']):
        visibility_score += 2
        conditions.append("Cuaca hujan/gerimis")
        recommendations.append("Tidak disarankan observasi dalam kondisi ini")
    else:
        visibility_score += 10
        conditions.append("Kondisi cuaca tidak pasti")
    
    # Skor berdasarkan kelembapan (15 poin maksimal)
    humidity = weather_data.get('kelembapan', 0)
    if humidity < 50:
        visibility_score += 15
        conditions.append("Kelembapan rendah (Sangat baik)")
    elif humidity < 60:
        visibility_score += 12
        conditions.append("Kelembapan sedang-rendah (Baik)")
    elif humidity < 70:
        visibility_score += 9
        conditions.append("Kelembapan sedang")
    elif humidity < 80:
        visibility_score += 6
        conditions.append("Kelembapan tinggi")
        recommendations.append("Kelembapan tinggi dapat mengurangi visibilitas")
    else:
        visibility_score += 3
        conditions.append("Kelembapan sangat tinggi")
        recommendations.append("Kelembapan sangat tinggi, pertimbangkan waktu yang lebih kering")
    
    # Skor berdasarkan visibilitas atmosfer (10 poin maksimal)
    atmospheric_visibility = weather_data.get('visibilitas', 10)
    if atmospheric_visibility >= 10:
        visibility_score += 10
        conditions.append("Visibilitas atmosfer sangat baik")
    elif atmospheric_visibility >= 7:
        visibility_score += 8
        conditions.append("Visibilitas atmosfer baik")
    elif atmospheric_visibility >= 5:
        visibility_score += 5
        conditions.append("Visibilitas atmosfer sedang")
    else:
        visibility_score += 2
        conditions.append("Visibilitas atmosfer buruk")
        recommendations.append("Visibilitas rendah dapat mempengaruhi deteksi")
    
    # Bonus berdasarkan angin (5 poin maksimal)
    wind_speed = weather_data.get('angin_kecepatan', 0)
    if 1 <= wind_speed <= 5:
        visibility_score += 5
        conditions.append("Angin sedang (Membantu kejernihan)")
    elif wind_speed < 1:
        visibility_score += 2
        conditions.append("Angin tenang")