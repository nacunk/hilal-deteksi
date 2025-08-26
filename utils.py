import requests

def get_weather(city_name=None, lat=None, lon=None):
    """
    Ambil data cuaca BMKG
    city_name : string, nama kota
    lat, lon  : float, koordinat
    """
    try:
        if city_name:
            url = f"https://api.bmkg.go.id/cuaca?city={city_name}"
        elif lat is not None and lon is not None:
            url = f"https://api.bmkg.go.id/cuaca?lat={lat}&lon={lon}"
        else:
            return None

        res = requests.get(url).json()
        return {
            "suhu": res.get("temperature", "N/A"),
            "kelembapan": res.get("humidity", "N/A"),
            "cuaca": res.get("weather", "N/A")
        }
    except:
        return {"suhu":"N/A","kelembapan":"N/A","cuaca":"N/A"}
