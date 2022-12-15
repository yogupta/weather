import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync, sync_to_async
from app.exceptions import exceptions
from app.service import weather_service


@csrf_exempt
@async_to_sync
async def index(request):
    if request.method == "POST":
        resp = None
        try:
            service = weather_service.WeatherService()  # should be singleton
            data = json.loads(request.body)
            city = data["city"]
            lang = data.get("lang", "en")
            resp = await service.fetch(city, lang)
            return HttpResponse(json.dumps(resp), content_type='application/json')
        except exceptions.InvalidLatLon as e:
            args = e.args
            msg = args[1]
            status_code = args[0]
            resp = HttpResponse(json.dumps({"error": msg}), content_type='application/json', status=status_code)
        except exceptions.ErrorFetchingWeather as e:
            args = e.args
            msg = args[1]
            status_code = args[0]
            resp = HttpResponse(json.dumps({"error": msg}), content_type='application/json', status=status_code)
        except exceptions.InvalidCityName as e:
            args = e.args
            msg = args[1]
            status_code = args[0]
            resp = HttpResponse(json.dumps({"error": msg}), content_type='application/json', status=status_code)
        except exceptions.InvalidLanguage as e:
            args = e.args
            msg = args[1]
            status_code = args[0]
            resp = HttpResponse(json.dumps({"error": msg}), content_type='application/json', status=status_code)

        return resp

    return HttpResponse(f"Invalid Method {request.method}", content_type='application/json', status=400)
