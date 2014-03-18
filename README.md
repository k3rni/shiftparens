A prototype reimplementation of the [shift-parenthesis concept](http://stevelosh.com/blog/2012/10/a-modern-space-cadet/#shift-parentheses) in Python.

Uses parts of uinputmapper (to read from event devices), but that might be replaced with libevdev someday. 
Needs `xdotool` (install it from your distribution's repositories, and again, might be replaced with libxdo). 
Other than that, no external dependencies.

Similar projects: xcape, keydouble, actkbd, python-uinput. Actkbd is closest to what I'm trying to achieve.

To run:

1. check out the code
2. check which device in `/dev/input` is your keyboard, replace hardcoded /dev/input/event3 with the correct path
3. run as root (or setup your input devices with proper permissions, I don't care)

Usage:

By default there are 5 mappings:

* press and release LeftShift: `(`
* press and release RightShift: `)`
* first LeftShift then RightShift (released in either order): `()`
* first RightShift then LeftShift: `)(`
* press and release LeftCtrl: equivalent to pressing ESC
