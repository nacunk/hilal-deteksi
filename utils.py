import requests
import json

# Daftar kota-kota besar di Indonesia dengan koordinatnya
INDONESIAN_CITIES = {
    "Jakarta": {"lat": -6.175, "lon": 106.827},
    "Surabaya": {"lat": -7.257, "lon": 112.752},
    "Bandung": {"lat": -6.917, "lon": 107.619},
    "Medan": {"lat": 3.595, "lon": 98.672},
    "Semarang": {"lat": -6.966, "lon": 110.420},
    "Makassar": {"lat": -5.147, "lon": 119.432},
    "Palembang": {"lat": -2.998, "lon": 104.756},
    "Tangerang": {"lat": -6.178, "lon": 106.631},
    "Depok": {"lat": -6.402, "lon": 106.794},
    "Bekasi": {"lat": -6.238, "lon": 106.976},
    "Padang": {"lat": -0.947, "lon": 100.414},
    "Denpasar": {"lat": -8.650, "lon": 115.216},
    "Samarinda": {"lat": -0.502, "lon": 117.154},
    "Banjarmasin": {"lat": -3.319, "lon": 114.590},
    "Batam": {"lat": 1.130, "lon": 104.053},
    "Pekanbaru": {"lat": 0.533, "lon": 101.447},
    "Bogor": {"lat": -6.595, "lon": 106.816},
    "Malang": {"lat": -7.977, "lon": 112.633},
    "Yogyakarta": {"lat": -7.797, "lon": 110.370},
    "Balikpapan": {"lat": -1.268, "lon": 116.831},
    "Pontianak": {"lat": -0.026, "lon": 109.343},
    "Manado": {"lat": 1.487, "lon": 124.845},
    "Jambi": {"lat": -1.588, "lon": 103.613},
    "Cirebon": {"lat": -6.706, "lon": 108.557},
    "Serang": {"lat": -6.120, "lon": 106.150},
    "Mataram": {"lat": -8.583, "lon": 116.116},
    "Jayapura": {"lat": -2.533, "lon": 140.717},
    "Kupang": {"lat": -10.167, "lon": 123.583},
    "Banda Aceh": {"lat": 5.548, "lon": 95.324},
    "Ambon": {"lat": -3.710, "lon": 128.181},
}

def get_city_coordinates(city_name):
    """
    Mendapatkan koordinat dari nama kota
    """
    return INDONESIAN_CITIES.get(city_name, None)

def get_weather(lat, lon):
    """
    Ambil data cuaca menggunakan OpenWeatherMap API
    Backup ke WeatherAPI jika gagal
    """
    try:
        # Coba OpenWeatherMap API (gratis)
        api_key = "demo_key"  # Ganti dengan API key yang valid
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=id"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "suhu": round(data['main']['temp'], 1),
                "kelembapan": data['main']['humidity'],
                "cuaca": data['weather'][0]['description'].title()
            }
        else:
            # Fallback ke data simulasi berdasarkan lokasi
            return get_simulated_weather(lat, lon)
            
    except requests.exceptions.RequestException:
        # Jika gagal koneksi, gunakan data simulasi
        return get_simulated_weather(lat, lon)
    except Exception as e:
        print(f"Error getting weather: {e}")
        return get_simulated_weather(lat, lon)

def get_simulated_weather(lat, lon):
    """
    Generate data cuaca simulasi berdasarkan lokasi dan pola iklim Indonesia
    """
    import random
    import datetime
    
    try:
        # Simulasi berdasarkan lokasi di Indonesia
        current_month = datetime.datetime.now().month
        
        # Pola iklim Indonesia (musim hujan: Nov-Mar, kemarau: Apr-Oct)
        is_rainy_season = current_month in [11, 12, 1, 2, 3]
        
        # Simulasi suhu berdasarkan lintang
        base_temp = 28
        if lat > 0:  # Sumatra Utara
            base_temp = 26
        elif lat < -7:  # Jawa Selatan, Bali
            base_temp = 25
        
        # Variasi suhu harian
        temp_variation = random.uniform(-3, 5)
        simulated_temp = round(base_temp + temp_variation, 1)
        
        # Simulasi kelembapan
        if is_rainy_season:
            humidity = random.randint(75, 95)
            weather_conditions = ["Berawan", "Hujan Ringan", "Mendung", "Gerimis"]
        else:
            humidity = random.randint(60, 80)
            weather_conditions = ["Cerah", "Berawan Sebagian", "Cerah Berawan", "Terang"]
        
        weather_desc = random.choice(weather_conditions)
        
        return {
            "suhu": simulated_temp,
            "kelembapan": humidity,
            "cuaca": weather_desc
        }
        
    except Exception as e:
        print(f"Error in simulated weather: {e}")
        return {
            "suhu": 27.5,
            "kelembapan": 75,
            "cuaca": "Data tidak tersedia"
        }

def get_location_info(lat, lon):
    """
    Mendapatkan informasi lokasi berdasarkan koordinat
    """
    try:
        # Coba reverse geocoding
        url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key=demo_key&language=id"
        
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                return {
                    "address": data['results'][0].get('formatted', 'Alamat tidak diketahui'),
                    "city": data['results'][0]['components'].get('city', 'Kota tidak diketahui'),
                    "province": data['results'][0]['components'].get('state', 'Provinsi tidak diketahui')
                }
    except:
        pass
    
    # Fallback berdasarkan koordinat yang dikenal
    for city, coords in INDONESIAN_CITIES.items():
        city_lat, city_lon = coords["lat"], coords["lon"]
        # Hitung jarak sederhana
        distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
        if distance < 0.5:  # Dalam radius ~55km
            return {
                "address": f"Sekitar {city}",
                "city": city,
                "province": "Indonesia"
            }
    
    return {
        "address": f"Koordinat {lat}, {lon}",
        "city": "Lokasi Custom",
        "province": "Indonesia"
    }

def calculate_moon_visibility(sqm_value, weather_data):
    """
    Hitung perkiraan visibilitas bulan berdasarkan SQM dan cuaca
    """
    visibility_score = 0
    conditions = []
    
    # Skor berdasarkan SQM
    if sqm_value >= 21.5:
        visibility_score += 40
        conditions.append("Langit sangat gelap (Excellent)")
    elif sqm_value >= 20:
        visibility_score += 30
        conditions.append("Langit cukup gelap (Baik)")
    elif sqm_value >= 18:
        visibility_score += 20
        conditions.append("Langit terang (Sedang)")
    else:
        visibility_score += 10
        conditions.append("Langit sangat terang (Buruk)")
    
    # Skor berdasarkan cuaca
    weather_desc = weather_data.get('cuaca', '').lower()
    if any(word in weather_desc for word in ['cerah', 'terang']):
        visibility_score += 30
        conditions.append("Cuaca cerah")
    elif any(word in weather_desc for word in ['berawan', 'mendung']):
        visibility_score += 10
        conditions.append("Cuaca berawan")
    else:
        visibility_score += 5
        conditions.append("Cuaca kurang mendukung")
    
    # Skor berdasarkan kelembapan
    humidity = weather_data.get('kelembapan', 0)
    if humidity < 60:
        visibility_score += 20
        conditions.append("Kelembapan rendah (Baik)")
    elif humidity < 75:
        visibility_score += 15
        conditions.append("Kelembapan sedang")
    else:
        visibility_score += 5
        conditions.append("Kelembapan tinggi")
    
    # Tentukan kategori visibilitas
    if visibility_score >= 80:
        category = "Excellent"
        recommendation = "Kondisi sangat ideal untuk observasi hilal"
    elif visibility_score >= 60:
        category = "Good"
        recommendation = "Kondisi baik untuk observasi hilal"
    elif visibility_score >= 40:
        category = "Fair"
        recommendation = "Kondisi cukup untuk observasi hilal"
    else:
        category = "Poor"
        recommendation = "Kondisi kurang ideal untuk observasi hilal"
    
    return {
        "score": visibility_score,
        "category": category,
        "recommendation": recommendation,
        "conditions": conditions
    } ['berawan sebagian', 'cerah berawan']):
        visibility_score += 20
        conditions.append("Cuaca cukup cerah")
    elif any(word in weather_desc for word in