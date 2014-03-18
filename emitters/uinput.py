__all__ = ['UInputEmitter']


from time import time, sleep
from ctypes import CDLL, byref, c_void_p
import uinputmapper
import uinputmapper.linux_uinput
from uinputmapper.cinput import *

class UInputEmitter:
    # Tried emitting keys by writing to uinput. Not useful, cannot send shifted keys.
    KEYSEQ = {
        '(': [(KEY_LEFTSHIFT, 1), ('syn', 0), (KEY_9, 1), ('syn', 0), (KEY_9, 0), ('syn', 0), (KEY_LEFTSHIFT, 0)],
        ')': [(KEY_LEFTSHIFT, 1), ('syn', 0), (KEY_0, 1), (KEY_0, 0), (KEY_LEFTSHIFT, 0)],
        # '(': [(KEY_KPLEFTPAREN, 1), ('syn', 0), (KEY_KPLEFTPAREN, 0)],
        "\033": [(KEY_ESC, 1), ('syn', 0), (KEY_ESC, 0)]
    }

    def __init__(self):
        self.libc = CDLL('libc.so.6')
        self.libc.gettimeofday.argtypes = [c_void_p, c_void_p]
        dev = self.dev = UInputDevice()
        # Must expose first, setup later
        dev.expose_event_type(EV_KEY)
        dev.expose_event(EV_KEY, KEY_9)
        dev.expose_event(EV_KEY, KEY_0)
        dev.setup('ParenMapper%s' % (time()))

    def emit_syn(self):
        tmval = timeval()
        self.libc.gettimeofday(byref(tmval), None)
        ev = input_event(tmval, EV_SYN, SYN_REPORT, 0)
        self.dev.fire_event(ev)
        
    def type(self, keys):
        for chr in keys:
            for (ev_code, ev_value) in self.KEYSEQ[chr]:
                if ev_code == 'syn':
                    self.emit_syn()
                    sleep(0.001)
                else:
                    tmval = timeval()
                    self.libc.gettimeofday(byref(tmval), None)
                    print "%d:%d %s %s %d" % (tmval.tv_sec, tmval.tv_usec, rev_events[EV_KEY], rev_event_keys[EV_KEY][ev_code], ev_value)
                    ev = input_event(tmval, EV_KEY, ev_code, ev_value)
                    self.dev.fire_event(ev)
            self.emit_syn()
    
    def key(self, symbol):
        pass

