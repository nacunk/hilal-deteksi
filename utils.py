import requests

def get_weather(lat, lon):
    # Mock API BMKG (ganti endpoint resmi jika ada)
    try:
        url = f"https://api.bmkg.go.id/cuaca?lat={lat}&lon={lon}"
        res = requests.get(url).json()
        return {
            "suhu": res.get("temperature", "N/A"),
            "kelembapan": res.get("humidity", "N/A"),
            "cuaca": res.get("weather", "N/A")
        }
    except:
        return {"suhu": "N/A", "kelembapan": "N/A", "cuaca": "N/A"}
