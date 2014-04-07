#! /usr/bin/env python

import select, glob, os.path
import argparse
from time import time 
from pprint import pprint
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

class SetEmitter(argparse.Action):
    def __call__(self, parser, ns, values, option_string=None):
        setattr(ns, 'emitter', values)
        if hasattr(EMITTERS[values], 'setup_argparse'):
            # NOTE: needs --help after -e to work
            group = parser.add_argument_group('Options for %s' % values)
            EMITTERS[values].setup_argparse(group)

parser = argparse.ArgumentParser(description="Turn your shift keys into parentheses")
parser.add_argument('-k', '--keyboard', metavar='DEV', dest="keyboard_device", 
    help="Override autodetected keyboard device. Pass a path under /dev/input.")
parser.add_argument('-e', '--emitter', metavar='MODULE', action=SetEmitter, 
    help="""Select emitter module. Default: %%(default)s.
    Available emitters: %s. 
    With this option, --help also displays the emitter's options.""" % ', '.join(EMITTERS.keys()), default="xdo", choices=EMITTERS.keys())
parser.add_argument('-D', '--daemon', action='store_true', dest='daemon', 
    help="Daemonize (implies -q).")
parser.add_argument('-q', '--quiet', action='store_true', dest='quiet', 
    help="Don't log anything to stdout.")

def main(args, rest):
    keyboard = InputDevice(args.keyboard_device or detect_keyboard_device()) 
    emclass = EMITTERS[args.emitter]

    # Parse and merge extra options
    if hasattr(emclass, 'setup_argparse'):
      parser = argparse.ArgumentParser()
      emclass.setup_argparse(parser)
      em_args = parser.parse_args(rest)
      vars(args).update(vars(em_args)) # vars(X) exposes underlying dict

    em = emclass(args)
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

args, rest = parser.parse_known_args()
if args.daemon:
    args.quiet = True
    from daemon import DaemonContext
    with DaemonContext():
        main(args, rest)
else:
    main(args, rest)
