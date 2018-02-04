import operator
from random import randint

import pyglet
import pyglet.image


GREEN = (0, 255, 0, 0)
WHITE = (255, 255, 255, 0)


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


class BarBuilder(object):

    def __init__(self, x, y, width=480, height=50):
        self._x, self._y = x, y
        self._width, self._height = int(width), int(height)
        self._percentage = 0.

    def __call__(self, x, y, percentage):
        percentage = max(0., min(100., float(percentage)))
        percentage /= 100

        x, y = self._x, self._y
        w0 = float(self._width) * percentage
        h = float(self._height)
        pyglet.graphics.draw(*build_box(x, y, w0, h, GREEN))

        w1 = float(self._width) - w0
        pyglet.graphics.draw(*build_box(x + w0, y, w1, h, WHITE))


def main():
    width, height = 480, 320
    window = pyglet.window.Window(width=width, height=height)

    image = pyglet.image.load('display.png')

    meter = MeterTape(0, 0, 400, 50)

    @window.event
    def on_draw():
        window.clear()
        image.blit(0, 0)

    def update(*args):
        percentage = percentage + randint(-5, 5)
        percentage = max(0., min(100., float(percentage)))

    pyglet.clock.schedule_interval(update, 0.5)
    pyglet.app.run()


if __name__ == '__main__':
    main()
