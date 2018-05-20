#!/usr/bin/env python2

import sys
import argparse
import threading
from multiprocessing import sharedctypes

import pyglet

from mvc import views
from mvc import models
from mvc import controllers


def main():
    """run radio display"""

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--color', default='black')
    subparsers = parser.add_subparsers(dest='subparser')

    serial_parser = subparsers.add_parser('serial')
    serial_parser.add_argument('--device',  default='/dev/ttyS0')
    serial_parser.add_argument('--timeout', default=10,     type=float)
    serial_parser.add_argument('--baud',    default=115200, type=int)

    subparsers.add_parser('keyboard')
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
    channel_views, bg, batch = views.build(color=args.color)

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

    if args.subparser == 'keyboard':
        controller = controllers.KeyboardInput(
            channel_models, stop
        )
    else:
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
