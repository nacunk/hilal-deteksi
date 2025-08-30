import requests
import json
from datetime import datetime
import math
import exifread
from skyfield.api import load, wgs84
import hilalpy

def parse_exif_datetime(dt_str):
    """Parse EXIF datetime string to Python datetime object."""
    try:
        return datetime.strptime(str(dt_str), "%Y:%m:%d %H:%M:%S")
    except Exception:
        return None

def parse_exif_gps(gps_tag):
    """Parse EXIF GPS tag to decimal degrees."""
    try:
        if gps_tag == 'Unknown':
            return None
        d, m, s = [float(x.num) / float(x.den) for x in gps_tag.values]
        return d + m/60 + s/3600
    except Exception:
        return None

def extract_exif_metadata(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
        camera = tags.get('Image Model', 'Unknown')
        dt_raw = tags.get('EXIF DateTimeOriginal', 'Unknown')
        gps_lat = tags.get('GPS GPSLatitude', 'Unknown')
        gps_lat_ref = tags.get('GPS GPSLatitudeRef', None)
        gps_lon = tags.get('GPS GPSLongitude', 'Unknown')
        gps_lon_ref = tags.get('GPS GPSLongitudeRef', None)

    dt = parse_exif_datetime(dt_raw)
    lat = parse_exif_gps(gps_lat)
    lon = parse_exif_gps(gps_lon)
    # Adjust for S/W
    if lat and gps_lat_ref and str(gps_lat_ref) == 'S':
        lat = -lat
    if lon and gps_lon_ref and str(gps_lon_ref) == 'W':
        lon = -lon

    return camera, dt, lat, lon

def compute_hilal_position(dt, latitude, longitude):
    if not (dt and latitude is not None and longitude is not None):
        return None, None
    ts = load.timescale()
    t = ts.utc(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    eph = load('de421.bsp')
    observer = wgs84.latlon(latitude, longitude)
    moon = eph['moon']
    astrometric = observer.at(t).observe(moon)
    alt, az, _ = astrometric.apparent().altaz()
    return alt.degrees, az.degrees

def predict_hilal_visibility(dt, latitude, longitude):
    if not (dt and latitude is not None and longitude is not None):
        return "Data tidak lengkap untuk prediksi visibilitas."
    return hilalpy.visibility_prediction(dt, latitude, longitude)

def get_weather(lat, lon):
    """
    Ambil data cuaca dari berbagai sumber API dengan fallback
    """
    try:
        # Convert to float
        lat_f = float(lat)
        lon_f = float(lon)
        
        # Try OpenWeatherMap API first (you need to replace with your API key)
        # For demo purposes, we'll use a mock response based on location
        
        # Attempt 1: Try OpenWeatherMap (requires API key)
        try:
            # Replace 'YOUR_API_KEY' with actual API key
            # api_key = "YOUR_API_KEY"
            # owm_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat_f}&lon={lon_f}&appid={api_key}&units=metric"
            # response = requests.get(owm_url, timeout=5)
            # if response.status_code == 200:
            #     data = response.json()
            #     return parse_openweather_data(data)
            pass
        except:
            pass
        
        # Attempt 2: Try alternative weather service
        try:
            # Using wttr.in service as fallback
            wttr_url = f"https://wttr.in/{lat_f},{lon_f}?format=j1"
            response = requests.get(wttr_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return parse_wttr_data(data)
        except Exception as e:
            print(f"wttr.in failed: {e}")
        
        # Attempt 3: Use geographical estimation
        return get_weather_estimation(lat_f, lon_f)
        
    except Exception as e:
        print(f"Weather API error: {e}")
        return get_default_weather()

def parse_wttr_data(data):
    """
    Parse data dari wttr.in API
    """
    try:
        current = data['current_condition'][0]
        return {
            'suhu': current['temp_C'],
            'kelembapan': current['humidity'],
            'cuaca': current['weatherDesc'][0]['value'],
            'tekanan': current.get('pressure', 'N/A'),
            'angin_kecepatan': current.get('windspeedKmph', 'N/A'),
            'angin_arah': current.get('winddir16Point', 'N/A'),
            'visibility': current.get('visibility', 'N/A'),
            'uv_index': current.get('uvIndex', 'N/A'),
            'feels_like': current.get('FeelsLikeC', 'N/A')
        }
    except:
        return get_default_weather()

def parse_openweather_data(data):
    """
    Parse data dari OpenWeatherMap API
    """
    try:
        return {
            'suhu': data['main']['temp'],
            'kelembapan': data['main']['humidity'],
            'cuaca': data['weather'][0]['description'].title(),
            'tekanan': data['main']['pressure'],
            'angin_kecepatan': data['wind'].get('speed', 'N/A'),
            'angin_arah': data['wind'].get('deg', 'N/A'),
            'visibility': data.get('visibility', 'N/A'),
            'feels_like': data['main'].get('feels_like', 'N/A')
        }
    except:
        return get_default_weather()

def get_weather_estimation(lat, lon):
    """
    Estimasi cuaca berdasarkan lokasi geografis dan waktu
    Ini adalah fallback ketika API tidak tersedia
    """
    try:
        # Basic estimation based on location and season
        current_month = datetime.now().month
        
        # Indonesia generally has tropical climate
        if -11 <= lat <= 6 and 95 <= lon <= 141:  # Indonesia bounds
            # Wet season (Oct-Mar) vs Dry season (Apr-Sep)
            if current_month in [10, 11, 12, 1, 2, 3]:
                # Wet season
                estimated_temp = 26 + (lat * -0.5)  # Cooler at higher latitudes
                estimated_humidity = 80 + (current_month % 3) * 5
                weather_desc = "Cloudy with possible rain"
            else:
                # Dry season
                estimated_temp = 29 + (lat * -0.5)
                estimated_humidity = 65 + (current_month % 3) * 5
                weather_desc = "Partly cloudy"
            
            return {
                'suhu': round(estimated_temp, 1),
                'kelembapan': min(estimated_humidity, 95),
                'cuaca': weather_desc,
                'tekanan': '1013',
                'angin_kecepatan': '10-15',
                'angin_arah': 'SW',
                'visibility': '10',
                'status': 'Estimated'
            }
        
        # For locations outside Indonesia
        else:
            return {
                'suhu': '25',
                'kelembapan': '70',
                'cuaca': 'Data not available for this location',
                'tekanan': '1013',
                'angin_kecepatan': 'N/A',
                'angin_arah': 'N/A',
                'visibility': 'N/A',
                'status': 'Location outside coverage'
            }
            
    except:
        return get_default_weather()

def get_default_weather():
    """
    Return default weather data when all APIs fail
    """
    return {
        'suhu': 'N/A',
        'kelembapan': 'N/A', 
        'cuaca': 'Data tidak tersedia',
        'tekanan': 'N/A',
        'angin_kecepatan': 'N/A',
        'angin_arah': 'N/A',
        'visibility': 'N/A',
        'status': 'API Unavailable'
    }

def calculate_moon_phase(date=None):
    """
    Hitung fase bulan untuk tanggal tertentu
    Returns: fase bulan dalam derajat (0-360)
    """
    if date is None:
        date = datetime.now()
    
    # Simplified moon phase calculation
    # Based on synodic month cycle (29.53 days)
    
    # Known new moon date (reference point)
    known_new_moon = datetime(2000, 1, 6, 18, 14)  # New moon on Jan 6, 2000
    
    # Calculate days since reference
    days_since = (date - known_new_moon).total_seconds() / (24 * 3600)
    
    # Moon cycle length
    synodic_month = 29.530588861
    
    # Calculate current position in cycle
    cycle_position = (days_since % synodic_month) / synodic_month
    
    # Convert to degrees (0 = new moon, 180 = full moon)
    moon_phase_deg = cycle_position * 360
    
    return {
        'phase_degrees': round(moon_phase_deg, 1),
        'phase_name': get_moon_phase_name(moon_phase_deg),
        'illumination': round(50 * (1 - math.cos(math.radians(moon_phase_deg))), 1),
        'days_in_cycle': round(cycle_position * synodic_month, 1)
    }

def get_moon_phase_name(degrees):
    """
    Convert moon phase degrees to readable name
    """
    if degrees < 7 or degrees > 353:
        return "🌑 New Moon"
    elif degrees < 90:
        return "🌒 Waxing Crescent"
    elif degrees < 97:
        return "🌓 First Quarter"
    elif degrees < 173:
        return "🌔 Waxing Gibbous"
    elif degrees < 187:
        return "🌕 Full Moon"
    elif degrees < 263:
        return "🌖 Waning Gibbous"
    elif degrees < 277:
        return "🌗 Last Quarter"
    else:
        return "🌘 Waning Crescent"

def calculate_sun_position(lat, lon, date=None):
    """
    Hitung posisi matahari (elevation dan azimuth) untuk lokasi dan waktu tertentu
    Simplified calculation for sunset/sunrise times
    """
    if date is None:
        date = datetime.now()
    
    try:
        # Convert to radians
        lat_rad = math.radians(lat)
        
        # Day of year
        day_of_year = date.timetuple().tm_yday
        
        # Solar declination angle
        declination = math.radians(23.45) * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        
        # Hour angle for sunrise/sunset (when elevation = 0)
        cos_hour_angle = -math.tan(lat_rad) * math.tan(declination)
        
        # Check if sun rises/sets at this latitude
        if cos_hour_angle < -1:
            return {"status": "Polar day", "sunrise": "No sunset", "sunset": "No sunset"}
        elif cos_hour_angle > 1:
            return {"status": "Polar night", "sunrise": "No sunrise", "sunset": "No sunrise"}
        
        # Hour angle
        hour_angle = math.acos(cos_hour_angle)
        
        # Convert to hours
        hour_angle_hours = math.degrees(hour_angle) / 15
        
        # Calculate sunrise and sunset times (local solar time)
        sunrise_lst = 12 - hour_angle_hours
        sunset_lst = 12 + hour_angle_hours
        
        # Convert to local time (simplified - doesn't account for timezone/DST)
        # Longitude correction: 4 minutes per degree
        time_correction = lon / 15  # hours
        
        sunrise_local = sunrise_lst + time_correction
        sunset_local = sunset_lst + time_correction
        
        # Format times
        def format_time(hours):
            h = int(hours) % 24
            m = int((hours % 1) * 60)
            return f"{h:02d}:{m:02d}"
        
        return {
            "status": "Normal",
            "sunrise": format_time(sunrise_local),
            "sunset": format_time(sunset_local),
            "daylight_hours": round(sunset_local - sunrise_local, 1)
        }
        
    except Exception as e:
        return {"status": "Error", "error": str(e)}

def get_islamic_calendar_info():
    """
    Informasi kalender Islam sederhana
    """
    # This is a simplified version - in reality you'd need accurate Islamic calendar calculations
    current_date = datetime.now()
    
    # Estimated Hijri year (very rough approximation)
    hijri_year_approx = 1445 + ((current_date.year - 2024) * 354.37 / 365.25)
    
    islamic_months = [
        "Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani",
        "Jumada al-Awwal", "Jumada al-Thani", "Rajab", "Sha'ban",
        "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
    ]
    
    # Simplified month estimation
    estimated_month_index = (current_date.month - 1 + current_date.day // 15) % 12
    
    return {
        "estimated_hijri_year": int(hijri_year_approx),
        "estimated_month": islamic_months[estimated_month_index],
        "note": "Perkiraan kasar - gunakan perhitungan hisab yang akurat untuk keperluan resmi"
    }

def validate_coordinates(lat, lon):
    """
    Validasi koordinat latitude dan longitude
    """
    try:
        lat_f = float(lat)
        lon_f = float(lon)
        
        if not (-90 <= lat_f <= 90):
            return {"valid": False, "error": "Latitude harus antara -90 dan 90"}
        
        if not (-180 <= lon_f <= 180):
            return {"valid": False, "error": "Longitude harus antara -180 dan 180"}
        
        return {
            "valid": True,
            "latitude": lat_f,
            "longitude": lon_f,
            "location_type": get_location_type(lat_f, lon_f)
        }
        
    except ValueError:
        return {"valid": False, "error": "Format koordinat tidak valid"}

def get_location_type(lat, lon):
    """
    Tentukan jenis lokasi berdasarkan koordinat
    """
    # Indonesia bounds check
    if -11 <= lat <= 6 and 95 <= lon <= 141:
        return "Indonesia"
    
    # Other regions
    elif 20 <= lat <= 50 and -10 <= lon <= 40:
        return "Middle East/Mediterranean"
    elif -40 <= lat <= 40 and -180 <= lon <= 180:
        return "Tropical/Subtropical"
    else:
        return "Other Region"

def calculate_qibla_direction(lat, lon):
    """
    Hitung arah kiblat dari koordinat yang diberikan
    Arah ke Makkah (21.4225°N, 39.8262°E)
    """
    try:
        # Koordinat Makkah
        makkah_lat = math.radians(21.4225)
        makkah_lon = math.radians(39.8262)
        
        # Koordinat lokasi
        loc_lat = math.radians(float(lat))
        loc_lon = math.radians(float(lon))
        
        # Perbedaan longitude
        delta_lon = makkah_lon - loc_lon
        
        # Hitung bearing menggunakan formula great circle
        y = math.sin(delta_lon) * math.cos(makkah_lat)
        x = (math.cos(loc_lat) * math.sin(makkah_lat) - 
             math.sin(loc_lat) * math.cos(makkah_lat) * math.cos(delta_lon))
        
        # Bearing dalam radian
        bearing_rad = math.atan2(y, x)
        
        # Convert ke derajat dan normalisasi ke 0-360
        bearing_deg = (math.degrees(bearing_rad) + 360) % 360
        
        return {
            "qibla_direction": round(bearing_deg, 1),
            "cardinal_direction": get_cardinal_direction(bearing_deg),
            "distance_km": calculate_distance(float(lat), float(lon), 21.4225, 39.8262)
        }
        
    except Exception as e:
        return {"error": f"Error calculating qibla: {e}"}

def get_cardinal_direction(degrees):
    """
    Convert degrees to cardinal direction
    """
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    
    index = round(degrees / 22.5) % 16
    return directions[index]

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Hitung jarak antara dua koordinat menggunakan formula Haversine
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth radius in kilometers
    r = 6371
    
    return round(c * r, 1)

def get_astronomical_data(lat, lon, date=None):
    """
    Dapatkan data astronomis lengkap untuk lokasi dan waktu tertentu
    """
    if date is None:
        date = datetime.now()
    
    try:
        lat_f = float(lat)
        lon_f = float(lon)
        
        return {
            "moon_phase": calculate_moon_phase(date),
            "sun_position": calculate_sun_position(lat_f, lon_f, date),
            "qibla": calculate_qibla_direction(lat_f, lon_f),
            "islamic_calendar": get_islamic_calendar_info(),
            "location_info": {
                "latitude": lat_f,
                "longitude": lon_f,
                "location_type": get_location_type(lat_f, lon_f)
            },
            "observation_time": date.strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        return {"error": f"Error calculating astronomical data: {e}"}

# Test function untuk debugging
def test_weather_api():
    """
    Test function untuk memastikan API cuaca berfungsi
    """
    test_locations = [
        ("-6.175", "106.827", "Jakarta"),
        ("-7.257", "112.752", "Surabaya"),
        ("3.595", "98.672", "Medan")
    ]
    
    print("Testing Weather API...")
    for lat, lon, city in test_locations:
        print(f"\nTesting {city} ({lat}, {lon}):")
        result = get_weather(lat, lon)
        print(f"Result: {result}")
    
    print("\nTesting Astronomical Data...")
    astro_data = get_astronomical_data("-6.175", "106.827")
    print(f"Astronomical data: {astro_data}")

if __name__ == "__main__":
    test_weather_api()