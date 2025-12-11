# services/weather_service.py
import requests

# Use your OpenWeatherMap API key here
OWM_API_KEY = "399099fc1044b731f5d0201d3e73d438"
OWM_BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


def get_weather(city):
    """
    Fetch weather for a city name (string).
    Returns either a dict with keys:
      temperature, humidity, condition, wind_speed, clouds
    or {"error": "..."} on failure.
    """
    if not city:
        return {"error": "No city provided."}

    params = {
        "q": f"{city},IN",     # your app used IN earlier; remove ,IN if you want global cities
        "appid": OWM_API_KEY,
        "units": "metric"
    }
    try:
        resp = requests.get(OWM_BASE_URL, params=params, timeout=8)
        data = resp.json()
    except Exception as e:
        return {"error": f"Weather request failed: {e}"}

    if resp.status_code != 200:
        # OpenWeather returns { "message": "...", "cod": "..."}
        return {"error": data.get("message", f"HTTP {resp.status_code}")}

    try:
        return {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"],
            "wind_speed": data["wind"]["speed"],
            "clouds": data["clouds"]["all"],
            "raw": data  # optional: raw response for debugging
        }
    except KeyError:
        return {"error": "Unexpected API response structure."}


def general_weather_alerts(weather):
    """
    Return list of general alerts based on the weather dict returned by get_weather.
    If weather contains an 'error' key, returns a single-item list with the error.
    """
    if not weather or "error" in weather:
        return [f"Weather error: {weather.get('error') if weather else 'No data'}"]

    alerts = []
    temp = weather.get("temperature")
    humidity = weather.get("humidity")
    condition = weather.get("condition", "")
    wind_speed = weather.get("wind_speed", 0)

    if temp is not None:
        if temp > 40:
            alerts.append("Heatwave conditions! Stay hydrated.")
        elif temp < 5:
            alerts.append("Cold wave alert! Protect sensitive crops and livestock.")

    if humidity is not None:
        if humidity > 80:
            alerts.append("High humidity, risk of fungal infections.")
        elif humidity < 20:
            alerts.append("Very dry conditions, monitor irrigation.")

    if condition:
        if condition.lower() in ["rain", "drizzle", "thunderstorm"]:
            alerts.append("Heavy rain expected, ensure proper drainage.")
        elif condition.lower() in ["haze", "dust", "smoke"]:
            alerts.append("Poor visibility, avoid pesticide spraying.")

    if wind_speed and wind_speed > 15:
        alerts.append("Strong winds may damage crops and trees.")

    return alerts


def crop_alert(weather):
    """
    Return crop-specific alerts based on temp/humidity.
    """
    if not weather or "error" in weather:
        return [f"Weather error: {weather.get('error') if weather else 'No data'}"]

    alerts = []
    temp = weather.get("temperature")
    humidity = weather.get("humidity")

    if temp is not None and humidity is not None:
        if temp > 35 and humidity < 30:
            alerts.append("Risk of drought stress for sensitive crops.")
        if humidity > 80 and temp > 25:
            alerts.append("High risk of fungal diseases in crops.")

    return alerts
