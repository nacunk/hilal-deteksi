from PIL import Image
import exifread
from skyfield.api import load, wgs84
import numpy as np

# 1. Ambil metadata EXIF
def get_exif_data(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
    return {
        'camera': tags.get('Image Model'),
        'datetime': tags.get('EXIF DateTimeOriginal'),
        'gps_lat': tags.get('GPS GPSLatitude'),
        'gps_lon': tags.get('GPS GPSLongitude')
    }

# 2. Hitung posisi hilal
def get_hilal_position(lat, lon, date_time):
    eph = load('de421.bsp')
    sun, moon, earth = eph['sun'], eph['moon'], eph['earth']
    location = wgs84.latlon(lat, lon)
    astrometric = location.at(date_time).observe(moon)
    alt, az, distance = astrometric.apparent().altaz()
    return alt.degrees, az.degrees

# 3. Analisis kecerlangan langit (brightness)
def get_sky_brightness(image_path):
    img = Image.open(image_path).convert('L')
    arr = np.array(img)
    brightness = np.mean(arr)
    return brightness
