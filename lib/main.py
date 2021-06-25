import sys
import os

from pitime import PiTime


def main(args):
    fullscreen = bool(os.environ.get('FULLSCREEN', False))

    weather_api_key = os.environ.get('WEATHER_API_KEY', None)
    weather_latitude = float(os.environ.get('WEATHER_LATITUDE', 51.752239))
    weather_longitude = float(os.environ.get('WEATHER_LONGITUDE', -0.338650))

    if '--fullscreen' in args:
        fullscreen = True

    return PiTime(fullscreen=fullscreen,
                  weather_api_key=weather_api_key,
                  weather_latitude=weather_latitude,
                  weather_longitude=weather_longitude).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
