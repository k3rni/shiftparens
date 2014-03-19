A prototype reimplementation of the [shift-parenthesis concept](http://stevelosh.com/blog/2012/10/a-modern-space-cadet/#shift-parentheses) in Python, for Linux only.

Uses parts of uinputmapper (to read from event devices), but that might be replaced with libevdev someday. 
Needs `xdotool` (install it from your distribution's repositories, and again, might be replaced with libxdo). 
Other than that, no external dependencies.

Similar projects: [xcape](http://github.com/alols/xcape), [keydouble](http://github.com/baskerville/keydouble), [actkbd](http://users.softlab.ece.ntua.gr/~thkala/projects/actkbd/), [python-uinput](http://tjjr.fi/sw/python-uinput). Xcape works exactly like the original concept, but is restricted to X11 and single keys. Actkbd can process sequences, but not precise push-release ones. Python-uinput can only generate, not read keys.

Either run `parens.py` as root, or configure udev permissions for `/dev/input/*` so you can read and write there (refer to [this](http://unix.stackexchange.com/questions/39370/how-to-reload-udev-rules-without-reboot) stackexchange post). If it doesn't detect your keyboard properly (you have more than one), replace the detect call with the correct input device path.

Usage:

By default there are 5 mappings:

* press and release LeftShift: `(`
* press and release RightShift: `)`
* first LeftShift then RightShift (released in either order): `()`
* first RightShift then LeftShift: `)(`
* press and release LeftCtrl: equivalent to pressing ESC
