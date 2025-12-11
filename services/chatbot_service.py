from services.weather_service import get_weather, crop_alert
# later you can import pest + fertilizer services

def chatbot_reply(user_input, file_path=None):
    user_input = user_input.lower()

    # Weather intent
    if "weather" in user_input:
        city = user_input.split()[-1].capitalize()
        weather_data = get_weather(city)
        alerts = crop_alert(weather_data)
        return f"Temp in {city}: {weather_data['temperature']}°C, " \
               f"Humidity: {weather_data['humidity']}%, " \
               f"{weather_data['condition']}.\n" \
               f"Alerts: " + "; ".join(alerts)

    # Pest detection (placeholder)
    if "pest" in user_input and file_path:
        return "Pest detection model not integrated yet."

    # Fertilizer guidance (placeholder)
    if "fertilizer" in user_input:
        return "Fertilizer model not integrated yet."

    return "🤖 I didn’t understand. Try asking about weather, pests, or fertilizer."
