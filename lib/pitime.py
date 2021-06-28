# coding=utf-8

import os
from datetime import datetime
import threading
import time
from sdl2.ext import init, Resources, Color, SpriteFactory
import sdl2
from sdl2.sdlttf import *

from weather_updater import WeatherUpdater


# It's a HyperPixel 4"
SCREEN_WIDTH=800
SCREEN_HEIGHT=480


class Colour:
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)


class Clock:

    def __init__(self, font_manager, sprite_factory, font_size=32, font_colour=Colour.WHITE, font_name=None, x=10, y=10):
        self.font_manager = font_manager
        self.sprite_factory = sprite_factory
        self.font_size = font_size
        self.font_colour = font_colour
        self.font_name = font_name
        self.x = x
        self.y = y

        self.text = ''
        self.sprite = None
        self.last_second = None

    def update(self):
        now = datetime.now()
        if self.last_second != now.second:
            self.text = now.strftime("%H:%M")
            self.last_second = now.second
            self.sprite = None

    def render(self, renderer):
        if self.sprite is None:
            text_surface = self.font_manager.render(self.text, size=self.font_size, color=self.font_colour, alias=self.font_name)
            self.sprite = self.sprite_factory.from_surface(text_surface, free=True)

        renderer.copy(self.sprite, dstrect=(self.x, self.y, self.sprite.size[0], self.sprite.size[1]))


class CurrentWeather:

    def __init__(self, weather_updater, font_manager, sprite_factory, font_size=80, font_colour=Colour.WHITE, font_name=None,
                 weather_font_size=60, weather_font_name="weather", x=10, y=10):
        self.weather_updater = weather_updater
        self.font_manager = font_manager
        self.sprite_factory = sprite_factory
        self.font_size = font_size
        self.font_colour = font_colour
        self.font_name = font_name
        self.weather_font_size = weather_font_size
        self.weather_font_name = weather_font_name
        self.x = x
        self.y = y

        self.text_temp = ''
        self.text_condition = ''
        self.sprite_temp = None
        self.sprite_condition = None
        self.last_temp = None
        self.last_condition = None

    def update(self):
        current_temp = self.weather_updater.temperature()
        if self.last_temp != current_temp:
            self.last_temp = current_temp
            self.text_temp = '%s°' % round(current_temp, 1)
            self.sprite_temp = None

        current_condition = self.weather_updater.condition_id()
        if self.last_condition != current_condition:
            self.last_condition = current_condition
            self.text_condition = self.text_for_weather_condition_id(current_condition)
            self.sprite_condition = None

    def text_for_weather_condition_id(self, condition_id):
        # https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
        # https://erikflowers.github.io/weather-icons/
        if condition_id >= 200 and condition_id < 300: # thunderstorm
            return "\uf01e"
        elif condition_id >= 300 and condition_id < 400: # drizzle
            return "\uf01a"
        elif condition_id >= 500 and condition_id < 600: # rain
            return "\uf019"
        elif condition_id >= 600 and condition_id < 700: # snow
            return "\uf01b"
        elif condition_id >= 700 and condition_id < 800: # atmospheric effects
            if condition_id == 741:
                return "\uf014"
            elif condition_id == 781:
                return "\uf056"
            else:
                return "\uf062"
        elif condition_id == 800: # clear
            return "\uf00d"
        elif condition_id >= 801 and condition_id < 900: # clouds
            if condition_id > 802:
                return "\uf013"
            else:
                return "\uf002"
        else:
            return "\uf07b"

    def render(self, renderer):
        if self.sprite_temp is None:
            temp_text_surface = self.font_manager.render(self.text_temp, size=self.font_size, color=self.font_colour, alias=self.font_name)
            self.sprite_temp = self.sprite_factory.from_surface(temp_text_surface, free=True)

        if self.sprite_condition is None:
            condition_text_surface = self.font_manager.render(self.text_condition, size=self.weather_font_size, color=self.font_colour, alias=self.weather_font_name)
            self.sprite_condition = self.sprite_factory.from_surface(condition_text_surface, free=True)

        renderer.copy(self.sprite_temp, dstrect=(self.x, self.y, self.sprite_temp.size[0], self.sprite_temp.size[1]))
        renderer.copy(self.sprite_condition, dstrect=(self.x, self.y + 100, self.sprite_condition.size[0], self.sprite_condition.size[1]))


class PiTime:

    UPDATE_PERIOD = 60

    def __init__(self, fullscreen=False, weather_api_key=None, weather_latitude=0.0, weather_longitude=0.0):
        self.fullscreen = fullscreen

        self.weather_updater = WeatherUpdater(weather_api_key, weather_latitude, weather_longitude)

    def run_background_updates(self):
        self.weather_updater.update()

        time.sleep(self.UPDATE_PERIOD)

    def run(self):
        init()

        weather_update_thread = threading.Thread(target=self.run_background_updates, daemon=True)
        weather_update_thread.start()

        base_path = os.path.abspath(os.path.dirname(__file__) + "/..")
        resources = Resources(base_path, "resources")

        if self.fullscreen:
            window = sdl2.ext.Window('PiTime', size=(SCREEN_WIDTH, SCREEN_HEIGHT), position=(0,0), flags=sdl2.video.SDL_WINDOW_FULLSCREEN_DESKTOP)
        else:
            window = sdl2.ext.Window('PiTime', size=(SCREEN_WIDTH, SCREEN_HEIGHT))

        font_path = resources.get_path("Roboto-Medium.ttf")
        font_manager = sdl2.ext.FontManager(font_path, alias="roboto-medium")
        font_manager.add(resources.get_path("LandasansUltraLight.otf"), alias="landasans-ultralight")
        font_manager.add(resources.get_path("weathericons-regular-webfont.ttf"), alias="weather")

        renderer = sdl2.ext.Renderer(window)
        renderer.clear(Colour.BLACK)

        sprite_factory = SpriteFactory(sprite_type=sdl2.ext.TEXTURE, renderer=renderer)

        entities = [
            Clock(font_manager, sprite_factory, font_size=400, font_name="landasans-ultralight", x=110, y=50),
            CurrentWeather(self.weather_updater, font_manager, sprite_factory, font_size=80, font_name="landasans-ultralight", x=630, y=105)
        ]

        sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)
        window.show()

        running = True

        while (running):
            events = sdl2.ext.get_events()
            for event in events:
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    break

            for entity in entities:
                entity.update()

            renderer.clear(Colour.BLACK)
            for entity in entities:
                entity.render(renderer)
            renderer.present()

        font_manager.close()

        return 0
