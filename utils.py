import requests

# Database kota-kota besar di Indonesia dengan koordinatnya
INDONESIAN_CITIES = {
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Surabaya": {"lat": -7.2575, "lon": 112.7521},
    "Bandung": {"lat": -6.9175, "lon": 107.6191},
    "Medan": {"lat": 3.5952, "lon": 98.6722},
    "Semarang": {"lat": -6.9667, "lon": 110.4167},
    "Makassar": {"lat": -5.1477, "lon": 119.4327},
    "Palembang": {"lat": -2.9761, "lon": 104.7754},
    "Tangerang": {"lat": -6.1783, "lon": 106.6319},
    "Depok": {"lat": -6.4025, "lon": 106.7942},
    "Bekasi": {"lat": -6.2383, "lon": 106.9756},
    "Bogor": {"lat": -6.5971, "lon": 106.8060},
    "Yogyakarta": {"lat": -7.7956, "lon": 110.3695},
    "Malang": {"lat": -7.9797, "lon": 112.6304},
    "Solo": {"lat": -7.5601, "lon": 110.8316},
    "Denpasar": {"lat": -8.6705, "lon": 115.2126},
    "Balikpapan": {"lat": -1.2379, "lon": 116.8529},
    "Banjarmasin": {"lat": -3.3194, "lon": 114.5906},
    "Samarinda": {"lat": -0.5017, "lon": 117.1536},
    "Batam": {"lat": 1.1307, "lon": 104.0530},
    "Pekanbaru": {"lat": 0.5071, "lon": 101.4478},
    "Jambi": {"lat": -1.6101, "lon": 103.6131},
    "Bengkulu": {"lat": -3.7928, "lon": 102.2608},
    "Lampung": {"lat": -5.4292, "lon": 105.2619},
    "Serang": {"lat": -6.1169, "lon": 106.1539},
    "Cirebon": {"lat": -6.7063, "lon": 108.5579},
    "Tasikmalaya": {"lat": -7.3506, "lon": 108.2281},
    "Purwokerto": {"lat": -7.4197, "lon": 109.2342},
    "Tegal": {"lat": -6.8694, "lon": 109.1402},
    "Pekalongan": {"lat": -6.8883, "lon": 109.6753},
    "Kudus": {"lat": -6.8048, "lon": 110.8405},
    "Magelang": {"lat": -7.4797, "lon": 110.2175},
    "Klaten": {"lat": -7.7058, "lon": 110.6061},
    "Pontianak": {"lat": -0.0263, "lon": 109.3425},
    "Kupang": {"lat": -10.1718, "lon": 123.6044},
    "Mataram": {"lat": -8.5833, "lon": 116.1167},
    "Manado": {"lat": 1.4748, "lon": 124.8421},
    "Palu": {"lat": -0.8917, "lon": 119.8707},
    "Kendari": {"lat": -3.9450, "lon": 122.4989},
    "Ambon": {"lat": -3.6954, "lon": 128.1814},
    "Jayapura": {"lat": -2.5167, "lon": 140.7167},
    "Sorong": {"lat": -0.8833, "lon": 131.2500},
    "Ternate": {"lat": 0.7833, "lon": 127.3667},
    "Banda Aceh": {"lat": 5.5483, "lon": 95.3238},
    "Padang": {"lat": -0.9471, "lon": 100.4172},
    "Bukittinggi": {"lat": -0.3073, "lon": 100.3706},
    "Batam": {"lat": 1.1307, "lon": 104.0530},
    "Tanjung Pinang": {"lat": 0.9186, "lon": 104.4489}
}

def get_weather(lat, lon):
    """
    Ambil data cuaca dari OpenWeatherMap API (gratis)
    """
    try:
        # Menggunakan OpenWeatherMap API (gratis dengan registrasi)
        # Ganti YOUR_API_KEY dengan API key dari openweathermap.org
        api_key = "demo_key"  # Perlu diganti dengan API key yang valid
        
        # URL untuk current weather
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=id"
        
        # Jika API key tidak tersedia, gunakan data mock
        if api_key == "demo_key":
            return get_mock_weather(lat, lon)
            
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "suhu": round(data['main']['temp'], 1),
                "kelembapan": data['main']['humidity'],
                "cuaca": data['weather'][0]['description'].title(),
                "tekanan": data['main']['pressure'],
                "kecepatan_angin": data.get('wind', {}).get('speed', 0),
                "visibilitas": data.get('visibility', 10000) / 1000  # dalam km
            }
        else:
            return get_mock_weather(lat, lon)
            
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return get_mock_weather(lat, lon)

def get_mock_weather(lat, lon):
    """
    Berikan data cuaca simulasi berdasarkan koordinat
    """
    import random
    import math
    
    # Simulasi cuaca berdasarkan lokasi geografis
    # Suhu berdasarkan lintang (latitude)
    base_temp = 28 - (abs(lat) * 0.6)  # Semakin jauh dari khatulistiwa, semakin dingin
    temp_variation = random.uniform(-3, 3)
    temperature = round(base_temp + temp_variation, 1)
    
    # Kelembapan berdasarkan kedekatan dengan laut (simulasi)
    base_humidity = 75
    humidity_variation = random.uniform(-15, 15)
    humidity = max(40, min(95, int(base_humidity + humidity_variation)))
    
    # Kondisi cuaca random tapi realistis
    weather_conditions = [
        "Cerah", "Berawan Sebagian", "Berawan", 
        "Mendung", "Hujan Ringan", "Kabut"
    ]
    
    # Probabilitas cuaca berdasarkan kelembapan
    if humidity > 85:
        weather_weights = [0.1, 0.2, 0.3, 0.2, 0.15, 0.05]
    elif humidity > 70:
        weather_weights = [0.3, 0.3, 0.2, 0.1, 0.05, 0.05]
    else:
        weather_weights = [0.5, 0.3, 0.15, 0.03, 0.01, 0.01]
    
    weather = random.choices(weather_conditions, weights=weather_weights)[0]
    
    return {
        "suhu": temperature,
        "kelembapan": humidity,
        "cuaca": weather,
        "tekanan": random.randint(1008, 1025),
        "kecepatan_angin": round(random.uniform(0.5, 8.0), 1),
        "visibilitas": round(random.uniform(8, 15), 1)
    }

def get_city_coordinates(city_name):
    """
    Ambil koordinat dari nama kota
    """
    return INDONESIAN_CITIES.get(city_name, None)

def calculate_moon_visibility_score(sqm, weather_data):
    """
    Hitung skor visibilitas bulan berdasarkan SQM dan cuaca
    """
    # Skor berdasarkan SQM (0-10)
    if sqm >= 22:
        sqm_score = 10
    elif sqm >= 21:
        sqm_score = 8
    elif sqm >= 20:
        sqm_score = 6
    elif sqm >= 19:
        sqm_score = 4
    else:
        sqm_score = 2
    
    # Skor berdasarkan cuaca (0-10)
    weather_condition = weather_data.get('cuaca', '').lower()
    if 'cerah' in weather_condition:
        weather_score = 10
    elif 'berawan sebagian' in weather_condition:
        weather_score = 7
    elif 'berawan' in weather_condition:
        weather_score = 5
    elif 'mendung' in weather_condition:
        weather_score = 3
    else:
        weather_score = 1
    
    # Skor berdasarkan kelembapan (0-10)
    humidity = weather_data.get('kelembapan', 50)
    if humidity < 60:
        humidity_score = 10
    elif humidity < 75:
        humidity_score = 7
    elif humidity < 85:
        humidity_score = 4
    else:
        humidity_score = 1
    
    # Total skor (rata-rata tertimbang)
    total_score = (sqm_score * 0.5 + weather_score * 0.3 + humidity_score * 0.2)
    
    return {
        'total_score': round(total_score, 1),
        'sqm_score': sqm_score,
        'weather_score': weather_score,
        'humidity_score': humidity_score,
        'recommendation': get_observation_recommendation(total_score)
    }

def get_observation_recommendation(score):
    """
    Berikan rekomendasi observasi berdasarkan skor
    """
    if score >= 8:
        return "🌟 Sangat ideal untuk observasi hilal!"
    elif score >= 6:
        return "✅ Baik untuk observasi hilal"
    elif score >= 4:
        return "⚠️ Cukup, tapi tidak optimal"
    else:
        return "❌ Tidak disarankan untuk observasi"