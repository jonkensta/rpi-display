from __future__ import division, print_function

import re

import serial


class QuitException(Exception):
    pass


def build_commands(channels):
    callbacks = []

    def register_command(regexp):
        regexp = re.compile(regexp)

        def register_callback(callback):
            callbacks.append((regexp, callback))
            return callback

        return register_callback

    @register_command(r'reset')
    def reset():
        return ['OK']

    @register_command(r'v')
    def version():
        return ['0.1', 'OK']

    @register_command(r'F([ +-])( [0-9]{9}|1[0-9]{9})')
    def display_main_freq(s, GMMMKKKhhh):
        f = float(GMMMKKKhhh) / 1e6
        channels[0].frequency = f
        return ['OK']

    @register_command(r'f([ +-])( [0-9]{9}|1[0-9]{9})')
    def display_sub_freq(s, GMMMKKKhhh):
        f = float(GMMMKKKhhh) / 1e6
        channels[0].frequency = f
        return ['OK']

    @register_command(r'S([TR0])')
    def switch_main_rxtx(tx_rx_or_none):
        if tx_rx_or_none == 'T':
            channels[0].receive = False
            channels[0].transmit = True

        elif tx_rx_or_none == 'R':
            channels[0].receive = True
            channels[0].transmit = False

        else:
            channels[0].receive = False
            channels[0].transmit = False

        return ['OK']

    @register_command(r's([TR0])')
    def switch_sub_rxtx(tx_rx_or_none):
        if tx_rx_or_none == 'T':
            channels[1].receive = False
            channels[1].transmit = True

        elif tx_rx_or_none == 'R':
            channels[1].receive = True
            channels[1].transmit = False

        else:
            channels[1].receive = False
            channels[1].transmit = False

        return ['OK']

    @register_command(r'P([f]*.?[f]*)')
    def display_PL_freq(format_):
        return ['OK']

    @register_command(r'pE([01])')
    def switch_encode(on_or_off):
        channels[0].encode = bool(int(on_or_off))
        return ['OK']

    @register_command(r'pD([01])')
    def switch_decode(on_or_off):
        channels[0].decode = bool(int(on_or_off))
        return ['OK']

    @register_command(r'ps([01])')
    def switch_decode_detect(on_or_off):
        channels[0].decode_detect = bool(int(on_or_off))
        return ['OK']

    @register_command(r'B(100|0[0-9]{2})')
    def display_main_bar(level):
        channels[0].meter = int(level)
        return ['OK']

    @register_command(r'b(100|0[0-9]{2})')
    def display_sub_bar(level):
        channels[1].meter = int(level)
        return ['OK']

    @register_command(r'O([01])')
    def switch_display(on_or_off):
        return ['OK']

    @register_command(r'D([LMH])')
    def switch_dimness(low_med_or_high):
        return ['OK']

    @register_command(r'U[01]')
    def switch_user_led(on_or_off):
        return ['OK']

    @register_command(r'i')
    def reset_watchdog():
        return ['OK']

    @register_command(r'T')
    def fetch_mcu_temp():
        return ['OK']

    @register_command(r'M(.*)')
    def display_main_msg(msg):
        channels[0].name = msg
        return ['OK']

    @register_command(r'm(.*)')
    def display_sub_msg(msg):
        channels[1].name = msg
        return ['OK']

    @register_command(r'.*')
    def otherwise():
        return ['NOTOK']

    return callbacks


class KeyboardInput(object):

    def __init__(self, channels, stop):
        self._stop = stop
        self._channels = channels
        self._callbacks = build_commands(channels)

    def __call__(self):
        while not self._stop.is_set():
            input_ = raw_input()  # noqa

            if input_ is None:
                self._channels[0].reset()
                self._channels[1].reset()
                continue

            match = None
            for regexp, callback in self._callbacks:
                match = regexp.match(input_)
                if match is not None:
                    break

            if match is not None:
                args = match.groups()
                output = callback(*args)

                if output is not None:
                    print('\n'.join(output))

            else:
                return


class SerialInput(object):

    def __init__(self, channels, stop, *args, **kwargs):
        self._stop = stop
        self._channels = channels
        self._args = args
        self._kwargs = kwargs

    def __call__(self):
        pass