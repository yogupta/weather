class InvalidLatLon(Exception):
    def __int__(self, msg):
        self.msg = msg
        super().__init__(msg)
        self.status_code = 400


class InvalidCityName(Exception):
    def __int__(self, status_code, msg):
        super().__init__(msg)
        self.status_code = status_code


class ErrorFetchingWeather(Exception):
    def __int__(self, status_code, msg):
        self.msg = msg
        super().__init__(self.msg)
        self.status_code = status_code


class InvalidLanguage(Exception):
    def __int__(self, status_code, msg):
        self.msg = msg
        super().__init__(self.msg)
        self.status_code = status_code
