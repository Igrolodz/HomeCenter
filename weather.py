import requests

def get_weather(api_key, lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url).json()
    return {
        'temp': response['main']['temp'],
        'condition': response['weather'][0]['main'],
        'icon': response['weather'][0]['icon']
    }