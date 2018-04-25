#!/usr/bin/env python2

import sys
import argparse
import threading
from multiprocessing import sharedctypes

import pyglet

from mvc import views
from mvc import models
from mvc import controllers


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
    """run radio display"""

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--device', default='/dev/ttyS0')
    parser.add_argument('--baud', default=115200, type=int)
    parser.add_argument('--timeout', default=10, type=float)
    args = parser.parse_args()

    channel_models = sharedctypes.Array(
        models.Channel, [
            ('', 0, '---.-', '!----------') + 6*(False,),
            ('', 0, '---.-', '!----------') + 6*(False,),
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
    controller = controllers.SerialInput(
        channel_models, stop,
        port=args.device, baudrate=args.baud, timeout=args.timeout
    )
    t = threading.Thread(target=controller)
    t.start()

    pyglet.app.run()

    stop.set()
    t.join()


if __name__ == '__main__':
    main()
