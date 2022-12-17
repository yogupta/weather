import logging
import os

import aiohttp
from dotenv import load_dotenv, find_dotenv

from app.exceptions import exceptions


class WeatherService:
    success = 200

    @staticmethod
    def get_api_key():
        try:
            load_dotenv(find_dotenv())
            key = os.environ['SECRET_KEY']
            return key
        except Exception:
            raise exceptions.ErrorFetchingWeather(500, f"Internal server error: Cannot fetch API Key")

    async def fetch(self, city: str, lang: str):
        self.validate_language(lang)
        api_key = self.get_api_key()
        logging.info(f"Fetching weather data for {city}")
        weather_api = f"https://api.openweathermap.org/data/2.5/weather?q={city}" \
                      f"&appid={api_key}&units=metric&lang={lang}"
        async with aiohttp.ClientSession() as session:
            weather_data = await self.download_weather_data(session, weather_api)
            return weather_data

    async def download_weather_data(self, session: aiohttp.ClientSession, url: str):
        async with session.get(url) as response:
            self.validate_response(response)
            json = await response.json()
            return self.parse_json(json)

    @staticmethod
    def deg_to_compass(degree: float):
        directions = ['↑ N', '↗ NE', '→ E', '↘ SE', '↓ S', '↙ SW', '← W', '↖ NW']
        return directions[int(round(degree % 360)) // 45]

    @staticmethod
    def validate_language(lang: str):
        supported_languages = ["en", "hi", "de"]
        if lang.lower() not in supported_languages:
            raise exceptions.InvalidLanguage(400,
                                             f"Invalid language {lang}; supported languages: {supported_languages}")

    @staticmethod
    def validate_response(response):
        if response.status in (401, 403):
            raise exceptions.ErrorFetchingWeather(500,
                                                  "Internal server error: Auth Error")  # exposing app internals
        if response.status == 404:
            raise exceptions.InvalidCityName(400, f"Invalid city name")
        if response.status not in (200, 429):
            raise exceptions.ErrorFetchingWeather(500, f"Error fetching weather data please try again")

    def parse_json(self, json):
        try:
            data = {
                "city": json["name"],
                "description": json["weather"][0]["description"],
                "temperature": {
                    "min": json["main"]["temp_min"],
                    "max": json["main"]["temp_max"]
                },
                "humidity": json["main"]["humidity"],
                "pressure": json["main"]["pressure"],
                "wind": {
                    "speed": json["wind"]["speed"],
                    "direction": self.deg_to_compass(json["wind"]["deg"]),
                    "degree": json["wind"]["deg"]
                }
            }
            return data
        except Exception:
            raise exceptions.ErrorFetchingWeather(500, "Parser error please try again")
