import os
import subprocess
from StringIO import StringIO

import pyglet.image

from . import base


SPRITES_FOLDER = os.path.join(base.ASSETS, 'sprites')


def _get_xcf_path(basename):
    return os.path.join(SPRITES_FOLDER, basename + '.xcf')


class ImageReadFailed(Exception):
    pass


def _read_image_layer(filepath, index):
    index = int(index)

    input_ = '\'{}[{}]\''.format(filepath, index)
    cmd = ' '.join(['convert', input_, 'png:-'])
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()

    if p.returncode != 0:
        msg = "Failed to read image {}".format(input_)
        raise ImageReadFailed(msg)

    image_name = '{}_{}.png'.format(filepath, index)
    output = StringIO(p.communicate()[0])
    return pyglet.image.load(image_name, file=output)


LED_IMAGE_PATH = _get_xcf_path('led')
led = {
    'off':    _read_image_layer(LED_IMAGE_PATH, 0),
    'red':    _read_image_layer(LED_IMAGE_PATH, 1),
    'yellow': _read_image_layer(LED_IMAGE_PATH, 2),
    'green':  _read_image_layer(LED_IMAGE_PATH, 3),
}

METER_TAPE_IMAGE_PATH = _get_xcf_path('meter_tape')
meter = {
    'tape':  _read_image_layer(METER_TAPE_IMAGE_PATH, 0),
    'white': _read_image_layer(METER_TAPE_IMAGE_PATH, 1),
    'black': _read_image_layer(METER_TAPE_IMAGE_PATH, 2),
}
BACKGROUND_IMAGE_PATH = os.path.join(base.ASSETS, 'background.xcf')
background = {
    'black': _read_image_layer(BACKGROUND_IMAGE_PATH, 0),
    'white': _read_image_layer(BACKGROUND_IMAGE_PATH, 1),
}
