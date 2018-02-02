import operator
from random import randint

import pyglet
import pyglet.image


def main():
    image = pyglet.image.load('display.png')

    @window.event
    def on_draw():
        window.clear()
        image.draw()

    pyglet.app.run()


if __name__ == '__main__':
    main()
