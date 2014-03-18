A prototype reimplementation of the [shift-parenthesis concept](http://stevelosh.com/blog/2012/10/a-modern-space-cadet/#shift-parentheses) in Python, for Linux only.

Uses parts of uinputmapper (to read from event devices), but that might be replaced with libevdev someday. 
Needs `xdotool` (install it from your distribution's repositories, and again, might be replaced with libxdo). 
Other than that, no external dependencies.

Similar projects: xcape, keydouble, actkbd, python-uinput. Actkbd is closest to what I'm trying to achieve.

Either run `parens.py` as root, or configure udev permissions for `/dev/input/*` so you can read and write there. If it doesn't detect your keyboard properly (you have more than one), replace the detect call with the correct input device path.

Usage:

By default there are 5 mappings:

* press and release LeftShift: `(`
* press and release RightShift: `)`
* first LeftShift then RightShift (released in either order): `()`
* first RightShift then LeftShift: `)(`
* press and release LeftCtrl: equivalent to pressing ESC
