#! /usr/bin/env python

import select, glob, os.path
from time import time 
from pprint import pprint
from uinputmapper.cinput import *
from emitters.nop import NopEmitter
from emitters.xdotool import XdotoolEmitter
from emitters.uinput import UInputEmitter
from keytracker import KeyTracker

def detect_keyboard_device():
    for devpath in glob.glob('/sys/class/input/event*'):
        uev = os.path.join(devpath, 'device/uevent')
        props = dict(line.strip().split('=') for line in open(uev))
        if 'KEY' in props and 'LED' in props:
            # has keys, has leds, it's a keyboard. TODO: better logic
            return os.path.join('/dev/input', os.path.basename(devpath))

LETTERS = {KEY_LEFTSHIFT: 'lL', KEY_RIGHTSHIFT: 'rR',
    KEY_LEFTCTRL: 'cC', KEY_RIGHTCTRL: 'dD',
    KEY_LEFTALT: 'aA', KEY_RIGHTALT: 'bB',
    KEY_LEFTMETA: 'wW', KEY_RIGHTMETA: 'vV',
    KEY_SPACE: 'sS'}

keyboard = InputDevice(detect_keyboard_device()) # TODO: cmdline
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

