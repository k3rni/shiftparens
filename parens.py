#! /usr/bin/env python

import select
from itertools import izip
from time import time, sleep
from pprint import pprint
from sys import stdout
from uinputmapper.cinput import *
from emitters.xdotool import XdotoolEmitter
from emitters.uinput import UInputEmitter

class State:
    LETTERS = {KEY_LEFTSHIFT: 'lL', KEY_RIGHTSHIFT: 'rR',
            KEY_LEFTCTRL: 'cC', KEY_RIGHTCTRL: 'dD',
            KEY_LEFTALT: 'aA', KEY_RIGHTALT: 'bB',
            KEY_LEFTMETA: 'wW', KEY_RIGHTMETA: 'vV',
            KEY_SPACE: 'sS'}

    def __init__(self, emitter=None):
        self.tape = []
        self.timetape = []
        self.emitter = emitter
        self.patterns = (
            (['rlRL', 'rRlL'], 0.3, self.type, '()'),
            (['lRLR', 'lLrR'], 0.3, self.type, ')('),
            (['srSR'], 0.3, self.type, ')'),
            (['lL'], 0.3, self.type, '('),
            (['rR'], 0.3, self.type, ')'),
            (['cC'], 0.3, self.key, 'Escape')
        )

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

    def fast_enough(self, count, timeout=0.3):
        return len(self.timetape) >= count and (self.timetape[0] - self.timetape[count-1] < timeout)

    def analyze_tape(self):
        # patterns must be sorted descending by length
        for patterns, timeout, command, value in self.patterns:
            if any((self.match(pat) and self.fast_enough(len(pat), timeout)) for pat in patterns):
                command(value)
                return
    
    def type(self, keys):
        self.emitter.type(keys)

    def key(self, symbol):
        self.emitter.key(symbol)

    def __str__(self):
        return '[%s]' % (''.join(self.tape))


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

