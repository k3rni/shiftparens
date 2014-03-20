#! /usr/bin/env python

import select, glob, os.path
from time import time 
from pprint import pprint
import argparse
from uinputmapper.cinput import *
from emitters import EMITTERS
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

parser = argparse.ArgumentParser(description="Capture and modify key sequences")
parser.add_argument('-k', '--keyboard', metavar='DEV', dest="keyboard_device", help="Override autodetected keyboard device. Pass a path under /dev/input")
parser.add_argument('-e', '--emitter', metavar='MODULE', dest="emitter", help="Select emitter module. Available ones are: %s" % ', '.join(EMITTERS.keys()), default="xdo", choices=EMITTERS.keys())
parser.add_argument('-d', '--daemon', action='store_true', dest='daemon', help="Daemonize (implies -q)")
parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', help="Don't log anything to stdout")


def main(args):
    keyboard = InputDevice(args.keyboard_device or detect_keyboard_device()) 
    em = EMITTERS[args.emitter](quiet=args.quiet)
    kt = KeyTracker(em, quiet=args.quiet)

    poll_obj, poll_mask = (select.epoll, select.EPOLLIN)
    pp = poll_obj()
    pp.register(keyboard.get_fd(), poll_mask)

    while True:
        events = pp.poll()
        for (fd, ev_mask) in events:
            ev = keyboard.next_event()
            if not args.quiet:
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
            if not args.quiet:
                print kt

args = parser.parse_args()
if args.daemon:
    args.quiet = True
    from daemon import DaemonContext
    with DaemonContext():
        main(args)
else:
    main(args)
