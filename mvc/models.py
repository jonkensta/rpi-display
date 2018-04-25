import ctypes


class Channel(ctypes.Structure):

    _fields_ = [
        ('name',          ctypes.c_char_p),
        ('meter',         ctypes.c_int),
        ('ctcss',         ctypes.c_char_p),
        ('frequency',     ctypes.c_char_p),
        ('encode',        ctypes.c_bool),
        ('decode',        ctypes.c_bool),
        ('decode_detect', ctypes.c_bool),
        ('transmit',      ctypes.c_bool),
        ('receive',       ctypes.c_bool),
        ('timeout',       ctypes.c_bool),
    ]

    def reset(self):
        self.name = ''
        self.meter = 0
        self.ctcss = '---.-'
        self.frequency = '!----------'
        self.encode = False
        self.decode = False
        self.decode_detect = False
        self.transmit = False
        self.receive = False
        self.timeout = False
