import requests

def get_weather(lat, lon):
    """
    Ambil data cuaca dari BMKG (mock API)
    """
    try:
        # Contoh endpoint mock BMKG, ganti sesuai API resmi
        url = f"https://api.bmkg.go.id/cuaca?lat={lat}&lon={lon}"
        res = requests.get(url, timeout=5).json()
        return {
            "suhu": res.get('temperature', 'N/A'),
            "kelembapan": res.get('humidity', 'N/A'),
            "cuaca": res.get('weather', 'N/A')
        }
    except:
        return {"suhu": "N/A", "kelembapan": "N/A", "cuaca": "N/A"}
