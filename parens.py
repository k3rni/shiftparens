#! /usr/bin/env python

import select
from itertools import izip
from time import time 
from pprint import pprint
from uinputmapper.cinput import *
from emitters.nop import NopEmitter
from emitters.xdotool import XdotoolEmitter
from emitters.uinput import UInputEmitter
from keytracker import KeyTracker

LETTERS = {KEY_LEFTSHIFT: 'lL', KEY_RIGHTSHIFT: 'rR',
    KEY_LEFTCTRL: 'cC', KEY_RIGHTCTRL: 'dD',
    KEY_LEFTALT: 'aA', KEY_RIGHTALT: 'bB',
    KEY_LEFTMETA: 'wW', KEY_RIGHTMETA: 'vV',
    KEY_SPACE: 'sS'}

keyboard = InputDevice('/dev/input/event3') # TODO: cmdline
kt = KeyTracker(XdotoolEmitter())

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
        # ignore non-key events and key repeats
        if ev.type != EV_KEY or ev.value > 1:
            continue
        # translate key to tape symbol
        letter = LETTERS.get(ev.code, 'oO')[ev.value]
        kt.record(letter, time())
        if ev.value == 0:
            kt.analyze_tape()
        print kt

