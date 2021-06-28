import requests


class WeatherUpdater:

    def __init__(self, api_key, latitude, longitude):
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.current_temp = 0.0
        self.current_condition_id = 800

    def temperature(self):
        return self.current_temp

    def condition_id(self):
        return self.current_condition_id

    def update(self):
        if self.api_key is None:
            return

        weather_response = requests.get('https://api.openweathermap.org/data/2.5/onecall',
                                        params={
                                            'lat': self.latitude,
                                            'lon': -0.338650,
                                            'units': 'metric',
                                            'lang': 'en',
                                            'exclude': 'minutely,hourly,daily,alerts',
                                            'appid': self.api_key
                                        })

        weather_response.raise_for_status()

        weather = weather_response.json()

        self.current_temp = weather['current']['temp']
        self.current_condition_id = weather['current']['weather'][0]['id']
