import os

import pyglet

from . import base
from . import colors


DSEG14 = os.path.join(base.ASSETS, 'DSEG14Classic-Regular.ttf')
pyglet.font.add_file(DSEG14)

large = {
    'font_name': 'DSEG14 Classic',
    'font_size': 36,
    'bold': True,
    'color': colors.black,
}

medium = {
    'font_name': 'DSEG14 Classic',
    'font_size': 32,
    'bold': True,
    'color': colors.black,
}

small = {
    'font_name': 'DSEG14 Classic',
    'font_size': 22,
    'bold': True,
    'color': colors.black,
}
