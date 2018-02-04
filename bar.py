import operator
from random import randint

import pyglet
import pyglet.image


pyglet.font.add_file('DSEG14Classic-Regular.ttf')
font = pyglet.font.load('DSEG14 Classic', bold=True)


BLACK = (0, 0, 0, 255)
GREEN = (0, 255, 0, 255)
WHITE = (255, 255, 255, 255)
YELLOW = (255, 255, 0, 255)
RED = (255, 0, 0, 255)


def build_box(x, y, w, h, c):
    vertices = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
    num_vertices = len(vertices)
    vertices = reduce(operator.add, vertices)

    colors = num_vertices * [c]
    colors = reduce(operator.add, colors)

    return (
        num_vertices,
        pyglet.gl.GL_POLYGON,
        ('v2f', vertices),
        ('c4B', colors),
    )


class MeterTape(object):

    def __init__(self, x, y, width=480, height=50):
        self._x, self._y = x, y
        self._width, self._height = int(width), int(height)
        self._percentage = 0.

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, value):
        self._percentage = max(0., min(100., float(value)))

    def draw(self):
        fraction = self._percentage / 100

        x, y = self._x, self._y
        w = 0
        h = float(self._height)

        w0 = float(self._width) * min(fraction, 0.675)
        pyglet.graphics.draw(*build_box(x, y, w0, h, GREEN))

        w += w0
        w1 = float(self._width) * (min(0.875, max(fraction, 0.675)) - 0.675)
        pyglet.graphics.draw(*build_box(x + w, y, w1, h, YELLOW))

        w += w1
        w2 = float(self._width) * (max(fraction, 0.875) - 0.875)
        pyglet.graphics.draw(*build_box(x + w, y, w2, h, RED))

        w += w2
        w3 = float(self._width) - w
        pyglet.graphics.draw(*build_box(x + w, y, w3, h, WHITE))


def main():
    width, height = 480, 320
    window = pyglet.window.Window(width=width, height=height)
    image = pyglet.image.load('display.png')

    meter0 = MeterTape(173,  39, 274, 8)
    meter1 = MeterTape(173, 191, 274, 8)

    @window.event
    def on_draw():
        window.clear()
        image.blit(0, 0)
        meter0.draw()
        meter1.draw()

    def update(*args):
        meter0.percentage += randint(-5, 5)
        meter1.percentage += randint(-5, 5)

    pyglet.clock.schedule_interval(update, 0.1)
    pyglet.app.run()


if __name__ == '__main__':
    main()
