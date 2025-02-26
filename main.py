import os
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from aiogram.filters import Command


def transliterate_city(city_name: str) -> str:
    return translit(city_name, 'ru', reversed=True)  # Транслитерация с русского на английский

# Замените на ваш API-ключ OpenWeather
WEATHER_API_KEY = "ea9030b8737d1eee50490137ab901546"
GEONAMES_USERNAME = "gusskov"  # Укажите ваш логин Geonames

bot = Bot(token="7776585087:AAE32dsoo1nd8SeFGCl_lzbOQhf_jrNapsw")
dp = Dispatcher()  # Создаем Dispatcher без аргументов


@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply("Привет! Напиши мне название города, и я пришлю сводку погоды.")


@dp.message()
async def get_weather(message: Message):
    city = message.text.strip()
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "lang": "ru",
        "units": "metric",
        "appid": WEATHER_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        country = data["sys"].get("country", "")

        location_type = "городе" if city.lower() != country.lower() else "стране"

        weather_message = (
            f"\U0001F3D9 Погода в {location_type} {city} ({country}):\n"
            f"\U0001F321 Температура: {temp}°C\n"
            f"☁ {weather_desc}\n"
            f"\U0001F4A7 Влажность: {humidity}%\n"
            f"\U0001F32C Ветер: {wind_speed} м/с"
        )
        await message.reply(weather_message)
    else:
        similar_cities = get_similar_city_names(city)
        # Перед созданием клавиатуры проверяем, есть ли похожие города
        if similar_cities:
            keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=name)] for name in similar_cities],  # Указываем text=
                resize_keyboard=True
            )
            await message.reply(
                f"Не удалось найти погоду для '{city}'. Возможно, вы имели в виду:",
                reply_markup=keyboard
            )


def get_similar_city_names(city):
    url = "http://api.geonames.org/searchJSON"
    params = {
        "q": city,
        "maxRows": 5,
        "username": GEONAMES_USERNAME
        ##"lang": "ru",
        ##"fclass": "P"  # Искать только населенные пункты
    }
    response = requests.get(url, params=params)
    response = get_city_data(city)  # Запрос к API
    if not response['geonames']:  # Если пусто, пробуем транслитерацию
        city_translit = transliterate_city(city)
        response = get_city_data(city_translit)

    data = response.json()
    print(data)
    if "geonames" in data:
        return [f"{item['name']} ({item['countryName']})" for item in data["geonames"]]
    return []


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)  # Передаем bot при запуске


if __name__ == "__main__":
    asyncio.run(main())  # Запускаем через asyncio.run()
