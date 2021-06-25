import os
from sdl2.ext import init, Resources, Color, SpriteFactory
import sdl2
from datetime import datetime

from sdl2.sdlttf import *


# It's a HyperPixel 4"
SCREEN_WIDTH=800
SCREEN_HEIGHT=480


class Colour:
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)


class Clock:

    def __init__(self, font_manager, sprite_factory, font_size=32, font_colour=Colour.WHITE, x=10, y=10):
        self.font_manager = font_manager
        self.sprite_factory = sprite_factory
        self.font_size = font_size
        self.font_colour = font_colour
        self.x = x
        self.y = y

        self.text = ''
        self.sprite = None
        self.last_second = None

    def update(self):
        now = datetime.now()
        if self.last_second != now.second:
            self.text = now.strftime("%H:%M:%S")
            self.last_second = now.second
            self.sprite = None

    def render(self, renderer):
        if self.sprite is None:
            text_surface = self.font_manager.render(self.text, size=self.font_size, color=self.font_colour)
            self.sprite = self.sprite_factory.from_surface(text_surface, free=True)

        renderer.copy(self.sprite, dstrect=(self.x, self.y, self.sprite.size[0], self.sprite.size[1]))


class PiTime:

    def __init__(self, fullscreen=False):
        self.fullscreen = fullscreen


    def run(self):
        init()

        base_path = os.path.abspath(os.path.dirname(__file__) + "/..")
        resources = Resources(base_path, "resources")

        if self.fullscreen:
            window = sdl2.ext.Window('PiTime', size=(SCREEN_WIDTH, SCREEN_HEIGHT), position=(0,0), flags=sdl2.video.SDL_WINDOW_FULLSCREEN_DESKTOP)
        else:
            window = sdl2.ext.Window('PiTime', size=(SCREEN_WIDTH, SCREEN_HEIGHT))

        font_path = resources.get_path("Roboto-Medium.ttf")
        font_manager = sdl2.ext.FontManager(font_path, alias="roboto-medium")

        renderer = sdl2.ext.Renderer(window)
        renderer.clear(Colour.WHITE)

        sprite_factory = SpriteFactory(sprite_type=sdl2.ext.TEXTURE, renderer=renderer)

        entities = [
            Clock(font_manager, sprite_factory, font_size=172, x=50, y=50)
        ]

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
