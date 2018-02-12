from __future__ import division

import os
import string
import random
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

    output = StringIO(p.communicate()[0])
    return pyglet.image.load('.png', file=output)


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

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)
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

    @property
    def frequency(self):
        return float(self._doc.text.replace('!', ''))

    @frequency.setter
    def frequency(self, value):
        self._doc.text = "{:.1f}".format(float(value)).rjust(5, '!')
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

    @property
    def frequency(self):
        return float(self._doc.text.replace('!', ''))

    @frequency.setter
    def frequency(self, value):
        self._doc.text = "{:.6f}".format(float(value)).rjust(11, '!')
        self._doc.set_style(0,  8, LARGE_FONT)
        self._doc.set_style(8, 12, SMALL_FONT)


class LED(object):

    def __init__(self, batch, **kwargs):
        leds = {
            'red':    read_image_layer(LED_IMAGE, 0),
            'yellow': read_image_layer(LED_IMAGE, 1),
            'green':  read_image_layer(LED_IMAGE, 2),
        }

        self._color = str(kwargs.pop('color', 'red')).lower()

        Sprite = pyglet.sprite.Sprite
        for color in leds:
            leds[color] = Sprite(leds[color], **kwargs)

        self._led = leds[self._color]
        self._led.batch = batch

        self._leds = leds
        self._batch = batch

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        value = str(value).lower()
        try:
            self._led = self._leds[value]
        except KeyError:
            raise ValueError("Invalid color")
        else:
            self._color = value
            for color in self._leds:
                self._leds[color].batch = None
            self._leds[value].batch = self._batch


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

    @property
    def percentage(self):
        return self._percent

    @percentage.setter
    def percentage(self, value):
        self._percent = max(0., min(100., float(value)))
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
        self._led = LED(batch, x=x+115, y=y+30, group=group)
        self._name = ChannelName(batch, x=x+5, y=y+125, w=w, group=group)
        self._freq = ChannelFrequency(batch, x=x, y=y+65, group=group)
        self._ctcss = CTCSSFrequency(batch, x=x, y=y+25, group=group)
        self._meter = MeterTape(batch, x=x+155, y=y+25, group=group)

        Label = pyglet.text.Label

        red_led = LED(batch, x=x+355, y=y+65, color='red', group=group)
        red_label = Label(
            'R', x=x+380, y=y+70,
            batch=batch, anchor_y='center', group=group, **SMALL_FONT
        )

        green_led = LED(batch, x=x+355, y=y+95, color='green', group=group)
        green_label = Label(
            'T', x=x+380, y=y+100,
            batch=batch, anchor_y='center', group=group, **SMALL_FONT
        )

        self._legend = {
            'red': (red_led, red_label), 'green': (green_led, green_label)
        }

    @property
    def name(self):
        return self._name.name

    @name.setter
    def name(self, value):
        self._name.name = value

    @property
    def frequency(self):
        return self._freq.frequency

    @frequency.setter
    def frequency(self, value):
        self._freq.frequency = value

    @property
    def ctcss(self):
        return self._ctcss.frequency

    @ctcss.setter
    def ctcss(self, value):
        self._ctcss.frequency = value

    @property
    def indicator(self):
        return self._led.color

    @indicator.setter
    def indicator(self, value):
        self._led.color = value

    @property
    def meter(self):
        return self._meter.percentage

    @meter.setter
    def meter(self, value):
        self._meter.percentage = value

    def scroll(self):
        self._name.scroll()


def main():
    width, height = 480, 320
    window = pyglet.window.Window(width=width, height=height)

    batch = pyglet.graphics.Batch()

    bg = pyglet.graphics.OrderedGroup(0)
    background = pyglet.image.load('background.png')
    background = pyglet.sprite.Sprite(background, group=bg, batch=batch)

    groups = (
        pyglet.graphics.OrderedGroup(1, parent=bg),
        pyglet.graphics.OrderedGroup(2, parent=bg),
    )

    channels = [
        Channel(batch, x=5, y=0,   group=groups[0]),
        Channel(batch, x=5, y=150, group=groups[1]),
    ]

    channels[0].name = 'ABCDEF'
    channels[0].frequency = 0500.000000
    channels[0].ctcss = 050.0
    channels[0].meter = 50
    channels[0].indicator = 'green'

    channels[1].name = string.ascii_uppercase
    channels[1].frequency = 5500.000000
    channels[1].ctcss = 550.0
    channels[1].meter = 50
    channels[1].indicator = 'red'

    fps_display = pyglet.clock.ClockDisplay()

    @window.event
    def on_draw():
        window.clear()
        batch.draw()
        fps_display.draw()

    colors = ['red', 'yellow', 'green']

    def update_values(*args):
        normal = random.normalvariate

        for channel in channels:
            channel.frequency += normal(0, 1)
            channel.ctcss += normal(0, 1)
            channel.meter += normal(0, 5)
            channel.indicator = random.choice(colors)

    def update_scroll(*args):
        for channel in channels:
            channel.scroll()

    pyglet.clock.schedule_interval(update_scroll, 1/30)
    pyglet.clock.schedule_interval(update_values, 3)
    pyglet.app.run()


if __name__ == '__main__':
    main()
