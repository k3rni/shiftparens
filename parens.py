#! /usr/bin/env python

import uinputmapper
import uinputmapper.linux_uinput
from uinputmapper.cinput import *
from uinputmapper.mapper import KeyMapper
import select, subprocess
from ctypes import CDLL, byref, c_void_p
from itertools import izip
from time import time, sleep
from pprint import pprint
from sys import stdout

libc = CDLL('libc.so.6')
libc.gettimeofday.argtypes = [c_void_p, c_void_p]

class State:
    LETTERS = {KEY_LEFTSHIFT: 'lL', KEY_RIGHTSHIFT: 'rR',
            KEY_LEFTCTRL: 'cC', KEY_RIGHTCTRL: 'dD',
            KEY_LEFTALT: 'aA', KEY_RIGHTALT: 'bB'}
    def __init__(self, emitter=None):
        self.tape = []
        self.timetape = []
        self.emitter = emitter

    def record(self, letters, state, tm):
        letter = letters[int(state)]
        self.tape.insert(0, letter)
        if len(self.tape) > 5: self.tape.pop()
        self.timetape.insert(0, tm)
        if len(self.timetape) > 5: self.timetape.pop()

    def push(self, key):
        self.alter_state(key, True)

    def release(self, key):
        self.alter_state(key, False)
        self.analyze_tape()

    def alter_state(self, key, state, tm=None):
        if tm is None: tm = time()
        self.record(State.LETTERS.get(key, 'oO'), state, tm)

    def match(self, seq):
        return all([left == right for (left, right) in izip(self.tape, seq)])

    def fast_enough(self, count):
        return len(self.timetape) >= count and (self.timetape[0] - self.timetape[count-1] < 0.3)

    def analyze_tape(self):
        tape = self.tape
        # TODO: read this from some config file.
        if self.match('rlRL') or self.match('rRlL') and self.fast_enough(4):
            self.type('()')
        elif self.match('lrLR') or self.match('lLrR') and self.fast_enough(4):
            self.type(')(')
        elif self.match('lL') and self.fast_enough(2):
            self.type('(')
        elif self.match('rR') and self.fast_enough(2):
            self.type(')')
        elif self.match('cC') and self.fast_enough(2):
            self.key("Escape")


    def type(self, keys):
        self.emitter.type(keys)

    def key(self, symbol):
        self.emitter.key(symbol)

    def __str__(self):
        return '[%s]' % (''.join(self.tape))


class EvdevEmitter:
    # Tried emitting keys by writing to uinput. Not useful, cannot send shifted keys.
    KEYSEQ = {
        '(': [(KEY_LEFTSHIFT, 1), ('syn', 0), (KEY_9, 1), ('syn', 0), (KEY_9, 0), ('syn', 0), (KEY_LEFTSHIFT, 0)],
        ')': [(KEY_LEFTSHIFT, 1), ('syn', 0), (KEY_0, 1), (KEY_0, 0), (KEY_LEFTSHIFT, 0)],
        # '(': [(KEY_KPLEFTPAREN, 1), ('syn', 0), (KEY_KPLEFTPAREN, 0)],
        "\033": [(KEY_ESC, 1), ('syn', 0), (KEY_ESC, 0)]
    }

    def __init__(self):
        dev = self.dev = UInputDevice()
        # Must expose first, setup later
        dev.expose_event_type(EV_KEY)
        dev.expose_event(EV_KEY, KEY_9)
        dev.expose_event(EV_KEY, KEY_0)
        dev.setup('ParenMapper%s' % (time()))

    def emit_syn(self):
        tmval = timeval()
        libc.gettimeofday(byref(tmval), None)
        ev = input_event(tmval, EV_SYN, SYN_REPORT, 0)
        dev.fire_event(ev)
        
    def type(self, keys):
        for chr in keys:
            for (ev_code, ev_value) in KEYSEQ[chr]:
                if ev_code == 'syn':
                    self.emit_syn()
                    sleep(0.001)
                else:
                    tmval = timeval()
                    libc.gettimeofday(byref(tmval), None)
                    print "%d:%d %s %s %d" % (tmval.tv_sec, tmval.tv_usec, rev_events[EV_KEY], rev_event_keys[EV_KEY][ev_code], ev_value)
                    ev = input_event(tmval, EV_KEY, ev_code, ev_value)
                    dev.fire_event(ev)
            self.emit_syn()
    
    def key(self, symbol):
        pass

class XdotoolEmitter:
    def key(self, symbol):
        print "KEY %s" % symbol
        self.xdotool('key', symbol)

    def type(self, keys):
        print "TYPING %r" % keys
        self.xdotool('type', keys)

    def xdotool(self, *args):
        subprocess.call(['xdotool'] + list(args), shell=False)

state = State(XdotoolEmitter())

keyboard = InputDevice('/dev/input/event3') # TODO: cmdline

poll_obj, poll_mask = (select.epoll, select.EPOLLIN)
pp = poll_obj()
pp.register(keyboard.get_fd(), poll_mask)

while True:
    events = pp.poll()
    for (fd, ev_mask) in events:
        ev = keyboard.next_event()
        s = '%s %s %d' % (rev_events[ev.type],
                rev_event_keys[ev.type][ev.code], ev.value)
        print 'Event type:', s
        if ev.type != EV_KEY:
            continue
        if ev.value == 1:
            state.push(ev.code)
        elif ev.value == 0:
            state.release(ev.code)
        print state

