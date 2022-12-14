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

    async def fetch(self, city: str):
        api_key = self.get_api_key()
        lat_lon = await self.get_city_lat_lon(city, api_key)
        weather_api = f"https://api.openweathermap.org/data/2.5/weather?lat={lat_lon['lat']}&lon={lat_lon['lon']}" \
                      f"&appid={api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(weather_api) as response:
                json = await response.json()
                if response.status in (401, 403):
                    raise exceptions.ErrorFetchingWeather(500,
                                                          "Internal server error: Auth Error")  # don't show to user
                if response.status not in (200, 429):
                    raise exceptions.ErrorFetchingWeather(500, f"Error fetching weather data please try again")

                try:

                    data = {
                        "city": city,
                        "description": json["weather"][0]["description"],
                        "temperature": {
                            "min": round(json["main"]["temp_min"] - 273.15, 2),
                            "max": round(json["main"]["temp_max"] - 273.15, 2)
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
                    raise exceptions.ErrorFetchingWeather(500, f"Parser error please try again")

    async def get_city_lat_lon(self, city_name: str, api_key: str):
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={1}&appid={api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status in (401, 403):
                    raise exceptions.ErrorFetchingWeather(500,
                                                          "Internal server error: Auth Error")  # don't show to user
                if response.status not in (200, 429):
                    raise exceptions.InvalidCityName(400, f"Invalid city {city_name}")

                resp = await response.json()
                if len(resp) == 0:
                    raise exceptions.InvalidCityName(400, f"Invalid city {city_name}")
                json = resp[0]
                lat_lon = {
                    "lat": json["lat"],
                    "lon": json["lon"]
                }
                return lat_lon

    def deg_to_compass(self, degree: float):
        directions = ['↑ N', '↗ NE', '→ E', '↘ SE', '↓ S', '↙ SW', '← W', '↖ NW']
        return directions[int(round(degree % 360)) // 45]
