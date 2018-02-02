import operator
from random import randint

import ipdb
import pyglet
import pyglet.image


BLACK = (0, 0, 0, 0)
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

    def __init__(self, width=500, height=50):
        self._width, self._height = int(width), int(height)
        self._percentage = 0.

    def __call__(self, x, y, percentage):
        percentage = max(0., min(100., float(percentage)))
        percentage /= 100

        w0 = float(self._width) * percentage
        h = float(self._height)
        pyglet.graphics.draw(*build_box(x, y, w0, h, BLACK))

        w1 = float(self._width) - w0
        pyglet.graphics.draw(*build_box(x + w0, y, w1, h, WHITE))


percentage = 50


def main():
    width, height = 500, 500
    window = pyglet.window.Window(width=width, height=height)

    background = (
        pyglet.image
        .SolidColorImagePattern(WHITE)
        .create_image(width, height)
    )

    bar = BarBuilder()

    @window.event
    def on_draw():
        window.clear()
        background.blit(0, 0)
        bar(0, 0, percentage)

    def update(*args):
        global percentage
        percentage = percentage + randint(-5, 5)
        percentage = max(0., min(100., float(percentage)))

    pyglet.clock.schedule_interval(update, 0.5)
    pyglet.app.run()


if __name__ == '__main__':
    main()
