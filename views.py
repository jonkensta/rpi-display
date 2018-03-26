from __future__ import division

import os
import operator
import functools
import subprocess
from StringIO import StringIO

import pyglet
import pyglet.image
import numpy as np


pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

pyglet.font.add_file('DSEG14Classic-Regular.ttf')

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

LARGE_FONT = {
    'font_name': 'DSEG14 Classic',
    'font_size': 36,
    'bold': True,
    'color': BLACK,
}

MEDIUM_FONT = {
    'font_name': 'DSEG14 Classic',
    'font_size': 32,
    'bold': True,
    'color': BLACK,
}

SMALL_FONT = {
    'font_name': 'DSEG14 Classic',
    'font_size': 22,
    'bold': True,
    'color': BLACK,
}

SPRITES = 'sprites'
LED_IMAGE = os.path.join(SPRITES, 'led.xcf')
METER_TAPE = os.path.join(SPRITES, 'meter_tape.xcf')


def content_width(text, **kwargs):
    return pyglet.text.Label(text, **kwargs).content_width


def build_box(x, y, w, h, c, group=None):
    vertices = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
    num_vertices = len(vertices)
    vertices = functools.reduce(operator.add, vertices)

    colors = num_vertices * [c]
    colors = functools.reduce(operator.add, colors)

    return (
        num_vertices, pyglet.gl.GL_POLYGON, group,
        ('v2f', vertices), ('c4B', colors)
    )


class ImageReadFailed(Exception):
    pass


def read_image_layer(filepath, index):
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


def img_horizontal_extents(image):
    shape = (image.height, image.width, 4)
    image = np.frombuffer(image.data, dtype=np.uint8).reshape(shape)
    alpha = image[:, :, 3]
    non_zero_cols = np.nonzero(np.any(alpha > 0, axis=0))[0]
    start, stop = non_zero_cols[0], non_zero_cols[-1] + 1
    return start, stop


class ChannelName(object):

    def __init__(self, batch, **kwargs):
        x = float(kwargs.pop('x', 0))
        y = float(kwargs.pop('y', 0))
        w = float(kwargs.pop('w', 300))
        rate = float(kwargs.pop('rate', 1))

        doc = pyglet.text.document.UnformattedDocument()
        doc.text = '-'

        h = pyglet.text.Label(" ", **SMALL_FONT).content_height

        Layout = pyglet.text.layout.ScrollableTextLayout
        layout = Layout(doc, w, h, batch=batch, **kwargs)
        layout.wrap_lines = False
        layout.x, layout.y = x, y

        self._doc = doc
        self._layout = layout
        self._name = '--------'

        self._w = w
        self._view_x = 0
        self._rate = rate
        self._scroll_w = 1

    def __call__(self, name):
        self._name = str(name)
        self._doc.text = self._name
        cw = content_width(self._name, **SMALL_FONT)

        if cw <= self._w:
            self._doc.text = self._name
            self._scroll_w = 1

        else:
            self._doc.text = ' ' + self._name + ' '
            cw = content_width(self._doc.text, **SMALL_FONT)
            self._scroll_w = cw
            self._doc.text *= 2

        self._doc.set_style(0, len(self._doc.text), SMALL_FONT)

    def scroll(self):
        self._layout.view_x += self._rate
        self._layout.view_x %= self._scroll_w


class CTCSSFrequency(object):

    def __init__(self, batch, **kwargs):
        x = float(kwargs.pop('x', 0))
        y = float(kwargs.pop('y', 0))
        doc = pyglet.text.document.FormattedDocument()

        Layout = pyglet.text.layout.TextLayout
        layout = Layout(doc, batch=batch, **kwargs)
        layout.wrap_lines = False
        layout.x, layout.y = x, y

        self._doc = doc
        self._layout = layout

    def __call__(self, frequency):
        self._doc.text = "{:.1f}".format(float(frequency)).rjust(5, '!')
        self._doc.set_style(0, 5, SMALL_FONT)


class ChannelFrequency(object):

    def __init__(self, batch, **kwargs):
        x = float(kwargs.pop('x', 0))
        y = float(kwargs.pop('y', 0))
        doc = pyglet.text.document.FormattedDocument()

        Layout = pyglet.text.layout.TextLayout
        layout = Layout(doc, batch=batch, **kwargs)
        layout.wrap_lines = False
        layout.x, layout.y = x, y

        self._doc = doc
        self._layout = layout

    def __call__(self, sign, frequency):
        sign = '!' if sign == ' ' else sign
        frequency_text = "{:011.6f}".format(float(frequency))
        self._doc.text = sign + frequency_text
        self._doc.set_style(0,  9, LARGE_FONT)
        self._doc.set_style(9, 13, SMALL_FONT)


led_images = {
    'off':    read_image_layer(LED_IMAGE, 0),
    'red':    read_image_layer(LED_IMAGE, 1),
    'yellow': read_image_layer(LED_IMAGE, 2),
    'green':  read_image_layer(LED_IMAGE, 3),
}


class LED(object):

    def __init__(self, batch, **kwargs):
        color = str(kwargs.pop('color', 'off')).lower()

        leds = {}
        Sprite = pyglet.sprite.Sprite
        for c in led_images:
            leds[c] = Sprite(led_images[c], **kwargs)

        led = leds[color]
        led.batch = batch

        self._leds = leds
        self._batch = batch

    def __call__(self, color):
        color = str(color).lower()
        try:
            self._leds[color]
        except KeyError:
            raise ValueError("Invalid color")
        else:
            for c in self._leds:
                self._leds[c].batch = None
            self._leds[color].batch = self._batch


class MeterTape(object):

    def __init__(self, batch, group=None, **kwargs):
        color = str(kwargs.pop('color', 'black')).lower()

        if color == 'white':
            meter = read_image_layer(METER_TAPE, 1)
        elif color == 'black':
            meter = read_image_layer(METER_TAPE, 2)
        else:
            raise ValueError("Invalid color choice")

        self._bar_color = color

        Sprite = pyglet.sprite.Sprite

        bar = read_image_layer(METER_TAPE, 0)
        extents = img_horizontal_extents(bar)
        self._bar_start, self._bar_stop = extents

        g0 = pyglet.graphics.OrderedGroup(0, parent=group)
        self._bar = Sprite(bar, batch=batch, group=g0, **kwargs)

        self._percent = 0.0
        self._group = pyglet.graphics.OrderedGroup(1, parent=group)
        self._batch = batch
        self._mask = self._build_mask()

        g2 = pyglet.graphics.OrderedGroup(2, parent=group)
        self._meter = Sprite(meter, batch=batch, group=g2, **kwargs)

    def __call__(self, percentage):
        self._percent = max(0., min(100., float(percentage)))
        self._mask.delete()
        self._mask = self._build_mask()

    def _build_mask(self):
        percent = 1.0 - self._percent / 100
        bar_width = self._bar_stop - self._bar_start

        w = int(round(bar_width * percent))
        x = self._bar.x + self._bar_start + bar_width - w
        y = self._bar.y
        h = self._bar.height

        # background color is opposite of the bar color
        c = WHITE if self._bar_color == 'black' else BLACK
        args = build_box(x, y, w, h, c, self._group)
        return self._batch.add(*args)


class Channel(object):

    def __init__(self, batch, x=0, y=0, w=425, group=None):
        x, y = float(x), float(y)

        self._name = ChannelName(batch, x=x+5, y=y+125, w=w, group=group)
        self._freq = ChannelFrequency(batch, x=x, y=y+65, group=group)
        self._ctcss = CTCSSFrequency(batch, x=x, y=y+25, group=group)
        self._meter = MeterTape(batch, x=x+175, y=y+25, group=group)

        self._tx_led = LED(batch, x=x+400, y=y+95, color='off', group=group)
        tx_label = pyglet.text.Label(
            'T', x=x+425, y=y+100,
            batch=batch, anchor_y='center', group=group,
            **SMALL_FONT
        )

        self._rx_led = LED(batch, x=x+400, y=y+65, color='off', group=group)
        rx_label = pyglet.text.Label(
            'R', x=x+425, y=y+70,
            batch=batch, anchor_y='center', group=group,
            **SMALL_FONT
        )

        # Encode/Decode/(Decode detect) leds
        self._encode_led = LED(batch, x=x+100, y=y+30, color='off', group=group)  # noqa
        self._decode_led = LED(batch, x=x+125, y=y+30, color='off', group=group)  # noqa
        self._decode_detect_led = LED(batch, x=x+150, y=y+30, color='off', group=group)  # noqa

        self._labels = [rx_label, tx_label]

    def __call__(self, model):
        self._name(model.name)
        self._meter(model.meter)
        self._ctcss(model.ctcss)
        self._freq(model.sign, model.frequency)

        self._encode_led('red' if model.encode else 'off')
        self._decode_led('green' if model.decode else 'off')
        self._decode_detect_led('yellow' if model.decode_detect else 'off')

        self._rx_led('red' if model.receive else 'off')
        self._tx_led('green' if model.transmit else 'off')

    def scroll(self):
        self._name.scroll()


def build():
    batch = pyglet.graphics.Batch()

    groups = (
        pyglet.graphics.OrderedGroup(0),
        pyglet.graphics.OrderedGroup(1),
        pyglet.graphics.OrderedGroup(2),
    )

    bg = pyglet.sprite.Sprite(
        pyglet.image.load('background.png'),
        group=groups[0], batch=batch
    )

    channels = (
        Channel(batch, x=5, y=0,   group=groups[1]),
        Channel(batch, x=5, y=150, group=groups[2]),
    )

    return channels, bg, batch
