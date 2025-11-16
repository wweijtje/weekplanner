import requests

def get_weather_openmeteo(lat, lon):
    """
    Get current weather from Open-Meteo (no API key required).
    Returns temperature, wind speed, and a numeric weather code.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code"],
        #"timezone": "Europe%2FBerlin",
        "forecast_days":3
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()

    return data

def get_weather_icon(weather_code):
    """Return a short string (e.g., 'clear', 'rain', 'snow') for the given weather code."""
    code_map = {
        0: "sun",
        1: "partly_cloudy",#"mostly_clear",
        2: "partly_cloudy",
        3: "cloudy",
        45: "fog",
        48: "fog",
        51: "light_rain",#"light_drizzle",
        53: "light_rain",#"drizzle",
        55: "light_rain",#heavy_drizzle",
        56: "light_rain",#"freezing_drizzle",
        57: "hail",#"freezing_drizzle",
        61: "light_rain",
        63: "rain",
        65: "heavy_rain",
        66: "hail",#"freezing_rain",
        67: "hail",#"freezing_rain",
        71: "light_snow",
        73: "snow",
        75: "snow",#"heavy_snow",
        77: "snow",#"snow_grains",
        80: "rain",##"light_rain_showers",
        81: "rain",#,"rain_showers",
        82: "heavy_rain",#"violent_rain_showers",
        85: "snow",#"light_snow_showers",
        86: "snow",#"snow_showers",
        95: "thunder",
        96: "thunder", # "thunderstorm_with_hail",
        99: "thunder",#"thunderstorm_with_hail"
    }
    return code_map.get(weather_code, "unknown")