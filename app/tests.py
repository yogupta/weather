import aiohttp
from aioresponses import aioresponses
from django.test import TestCase

from app.exceptions import exceptions
from app.service.weather_service import WeatherService


class WeatherTestCase(TestCase):
    response_200 = {
        "coord": {
            "lon": 72.8479,
            "lat": 19.0144
        },
        "weather": [
            {
                "id": 721,
                "main": "Haze",
                "description": "haze",
                "icon": "50n"
            }
        ],
        "base": "stations",
        "main": {
            "temp": 302.14,
            "feels_like": 304.32,
            "temp_min": 302.14,
            "temp_max": 302.14,
            "pressure": 1012,
            "humidity": 61
        },
        "visibility": 3000,
        "wind": {
            "speed": 0,
            "deg": 0
        },
        "clouds": {
            "all": 40
        },
        "dt": 1671039354,
        "sys": {
            "type": 1,
            "id": 9052,
            "country": "IN",
            "sunrise": 1670981597,
            "sunset": 1671021185
        },
        "timezone": 19800,
        "id": 1275339,
        "name": "Mumbai",
        "cod": 200
    }

    async def test_download_data(self):
        city = "Mumbai"
        lang = "en"
        api_key = "1234"
        weather_api = f"https://api.openweathermap.org/data/2.5/weather?q={city}" \
                      f"&appid={api_key}&units=metric&lang={lang}"
        expected_response = {
            'city': 'Mumbai', 'description': 'haze', 'temperature': {'min': 302.14, 'max': 302.14},
            'humidity': 61, 'pressure': 1012, 'wind': {'speed': 0, 'direction': '↑ N', 'degree': 0}
        }
        with aioresponses() as mocked:
            mocked.get(weather_api, status=200, payload=self.response_200, )
            async with aiohttp.ClientSession() as session:
                service = WeatherService()
                resp = await service.download_weather_data(session, weather_api)
                assert resp == expected_response
                mocked.assert_called_once_with(weather_api, method="GET")

    @staticmethod
    async def test_invalid_api_key_raise_correct_exception():
        city = "Mumbai"
        lang = "en"
        api_key = "1234"
        weather_api = f"https://api.openweathermap.org/data/2.5/weather?q={city}" \
                      f"&appid={api_key}&units=metric&lang={lang}"

        invalid_api_key_resp = {
            "cod": 401,
            "message": "Invalid API key. Please see https://openweathermap.org/faq#error401 for more info."
        }
        with aioresponses() as mocked:
            mocked.get(weather_api, status=401, payload=invalid_api_key_resp)
            async with aiohttp.ClientSession() as session:
                service = WeatherService()
                try:
                    await service.download_weather_data(session, weather_api)
                except exceptions.ErrorFetchingWeather as e:
                    status_code = e.args[0]
                    msg = e.args[1]
                    assert status_code == 500
                    assert msg == "Internal server error: Auth Error"
                    mocked.assert_called_once_with(weather_api, method="GET")

    @staticmethod
    async def test_parser_error_raise_correct_exception():
        city = "Mumbai"
        lang = "en"
        api_key = "1234"
        weather_api = f"https://api.openweathermap.org/data/2.5/weather?q={city}" \
                      f"&appid={api_key}&units=metric&lang={lang}"

        with aioresponses() as mocked:
            mocked.get(weather_api, status=200, payload={})
            async with aiohttp.ClientSession() as session:
                service = WeatherService()
                try:
                    await service.download_weather_data(session, weather_api)
                except exceptions.ErrorFetchingWeather as e:
                    status_code = e.args[0]
                    msg = e.args[1]
                    assert status_code == 500
                    assert msg == "Parser error please try again"
                    mocked.assert_called_once_with(weather_api, method="GET")

    @staticmethod
    async def test_invalid_city_name_raise_correct_exception():
        city = "Mumbaiiiiiii"
        lang = "en"
        api_key = "1234"
        weather_api = f"https://api.openweathermap.org/data/2.5/weather?q={city}" \
                      f"&appid={api_key}&units=metric&lang={lang}"

        invalid_city_name_resp = {
            "cod": "404",
            "message": "city not found"
        }
        with aioresponses() as mocked:
            mocked.get(weather_api, status=404, payload=invalid_city_name_resp)
            async with aiohttp.ClientSession() as session:
                service = WeatherService()
                try:
                    await service.download_weather_data(session, weather_api)
                except exceptions.InvalidCityName as e:
                    status_code = e.args[0]
                    assert status_code == 400
                    mocked.assert_called_once_with(weather_api, method="GET")

    @staticmethod
    def test_invalid_language_raise_correct_exception():
        service = WeatherService()
        try:
            service.validate_language("eng")
            assert False
        except exceptions.InvalidLanguage as e:
            assert True

    @staticmethod
    def test_invalid_language_does_not_raise_exception():
        service = WeatherService()
        service.validate_language("en")
        service.validate_language("hi")
        service.validate_language("de")
        assert True
