# Shiftparens

A simple reimplementation of the [shift-parenthesis concept](http://stevelosh.com/blog/2012/10/a-modern-space-cadet/#shift-parentheses) in Python, for Linux only.

Uses parts of uinputmapper (to read from event devices), but that might be replaced with libevdev someday. 
Uses `xdotool` if you choose it as emitter (install it from your distribution's repositories). Requires [python-daemon](https://pypi.python.org/pypi/python-daemon/) if you want to run daemonized.

## Rationale

Similar projects: [xcape](http://github.com/alols/xcape), [keydouble](http://github.com/baskerville/keydouble), [actkbd](http://users.softlab.ece.ntua.gr/~thkala/projects/actkbd/), [python-uinput](http://tjjr.fi/sw/python-uinput). Xcape works exactly like the original concept, but is restricted to X11 and single keys. Actkbd can process sequences, but not precise push-release ones. Python-uinput can only generate, not read keys.

# Usage

Run `python parens.py`. If you see "permission denied" errors, you might need to [configure your udev](/../../wiki/UDev-setup). In case it doesn't detect your keyboard properly (you have more than one), pass the correct device path with a command-line option.


By default there are 5 mappings:

* press and release LeftShift: `(`
* press and release RightShift: `)`
* first LeftShift then RightShift (released in either order): `()`
* first RightShift then LeftShift: `)(`
* press and release LeftCtrl: equivalent to pressing ESC

## Emitters

Emitters are modules which do the actual insertion of events into what you're typing. At the moment, you can choose from several:

* xdo: uses xdotool command-line app to send X11 events
* uinput: emits keys via kernel input ioctls, no dependencies except write permissions on /dev/input
* xtest: FFI interface to libXTest, no dependencies, your X server probably supports XTest and has it enabled
* vim: sends commands to a vim instance. Only if vim has focus and is in insert or replace mode
