import requests
from config import OWM_API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_current_weather(city: str) -> str:
    """
    Функция 1 — Текущая погода по названию города.
    Получает данные через HTTP API OpenWeatherMap.
    """
    url = f"{BASE_URL}/weather"
    params = {
        "q": city,
        "appid": OWM_API_KEY,
        "units": "metric",   # температура в Цельсиях
        "lang": "ru"         # описание на русском
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        # Если город не найден
        if response.status_code == 404:
            return f"❌ Город «{city}» не найден. Проверь название."

        # Если другая ошибка API
        if response.status_code != 200:
            return f"❌ Ошибка API: {response.status_code}"

        data = response.json()

        # Достаём нужные данные из ответа
        city_name    = data["name"]
        country      = data["sys"]["country"]
        temp         = data["main"]["temp"]
        feels_like   = data["main"]["feels_like"]
        humidity     = data["main"]["humidity"]
        wind_speed   = data["wind"]["speed"]
        description  = data["weather"][0]["description"].capitalize()

        return (
            f"🌤 Погода в {city_name}, {country}:\n\n"
            f"🌡 Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"💧 Влажность: {humidity}%\n"
            f"💨 Ветер: {wind_speed} м/с\n"
            f"☁️ {description}"
        )

    except requests.exceptions.ConnectionError:
        return "❌ Нет соединения с интернетом."
    except requests.exceptions.Timeout:
        return "❌ Сервер не отвечает. Попробуй позже."
    except Exception as e:
        return f"❌ Неизвестная ошибка: {e}"


def get_forecast(city: str) -> str:
    """
    Функция 2 — Прогноз погоды на 5 дней по названию города.
    Получает данные через HTTP API OpenWeatherMap (каждые 3 часа).
    Показываем по одному значению на день (в полдень).
    """
    url = f"{BASE_URL}/forecast"
    params = {
        "q": city,
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 404:
            return f"❌ Город «{city}» не найден. Проверь название."

        if response.status_code != 200:
            return f"❌ Ошибка API: {response.status_code}"

        data = response.json()
        city_name = data["city"]["name"]
        country   = data["city"]["country"]

        result = f"📅 Прогноз на 5 дней для {city_name}, {country}:\n\n"

        # Фильтруем записи — берём только время около 12:00
        seen_dates = set()
        for item in data["list"]:
            dt_txt = item["dt_txt"]          # например "2024-06-03 12:00:00"
            date, time = dt_txt.split(" ")

            if time == "12:00:00" and date not in seen_dates:
                seen_dates.add(date)
                temp        = item["main"]["temp"]
                description = item["weather"][0]["description"].capitalize()
                wind        = item["wind"]["speed"]

                result += (
                    f"📆 {date}\n"
                    f"   🌡 {temp}°C  💨 {wind} м/с  ☁️ {description}\n\n"
                )

        return result if seen_dates else "❌ Не удалось получить прогноз."

    except requests.exceptions.ConnectionError:
        return "❌ Нет соединения с интернетом."
    except requests.exceptions.Timeout:
        return "❌ Сервер не отвечает. Попробуй позже."
    except Exception as e:
        return f"❌ Неизвестная ошибка: {e}"