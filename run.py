import sys
import signal
import threading
from multiprocessing import sharedctypes

import pyglet

import views
import models
import controllers


class SignalHandler:

    def __init__(self, stopper, workers):
        self.stopper = stopper
        self.workers = workers

    def __call__(self, signum, frame):
        self.stopper.set()

        for worker in self.workers:
            worker.join()

        sys.exit(0)


def main():
    channel_models = sharedctypes.Array(
        models.Channel, [
            ('', 0, 0, ' ', 0, False, False, False, False, False),
            ('', 0, 0, ' ', 0, False, False, False, False, False),
        ],
        lock=True
    )

    width, height = 480, 320
    window = pyglet.window.Window(width=width, height=height)
    channel_views, bg, batch = views.build()

    @window.event
    def on_draw():
        window.clear()
        zipped = zip(channel_views, channel_models)
        for view, model in zipped:
            view(model)
        batch.draw()

    def update(dt):
        for view in channel_views:
            view.scroll()

    pyglet.clock.schedule_interval(update, 1.0/25)

    stop = threading.Event()
    controller = controllers.KeyboardInput(channel_models, stop)
    t = threading.Thread(target=controller)
    t.start()

    pyglet.app.run()

    stop.set()
    t.join()


if __name__ == '__main__':
    main()
