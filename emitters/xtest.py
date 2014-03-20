from ctypes import CDLL, c_void_p, c_int, c_char_p, c_ulong, c_uint, byref, POINTER, c_bool
p_int = POINTER(c_int)

class XTestException(Exception):
    pass

class XTestEmitter:
    def __init__(self, quiet=False):
        self.quiet = quiet
        self.setup_x11()
        self.setup_xtest()
        self.xtest_start()

    def __del__(self):
        self.xtest_stop()

    def setup_x11(self):
        self.x11 = CDLL('libX11.so')
        self.x11.XOpenDisplay.argtypes = [c_char_p]
        self.x11.XOpenDisplay.restype = c_void_p
        self.x11.XStringToKeysym.argtypes = [c_char_p]
        self.x11.XStringToKeysym.restype = c_int
        self.x11.XKeysymToKeycode.argtypes = [c_void_p, c_int]
        self.x11.XKeysymToKeycode.restype = c_int
        self.x11.XSync.argtypes = [c_void_p, c_bool]
        # TODO: pass options here
        self.display = self.x11.XOpenDisplay("")

    def setup_xtest(self):
        self.xtest = CDLL('libXtst.so')
        self.xtest.XTestQueryExtension.restype = c_bool
        self.xtest.XTestFakeKeyEvent.argtypes = [c_void_p, c_uint, c_bool, c_ulong]
        self.xtest.XTestGrabControl.argtypes = [c_void_p, c_bool]

    def xtest_start(self):
        event_base, error_base, major, minor = c_int(0), c_int(0), c_int(0), c_int(0)
        if not self.xtest.XTestQueryExtension(self.display, byref(event_base), byref(error_base), byref(major), byref(minor)):
            raise XTestException("XTest not supported")
        self.xtest.XTestGrabControl(self.display, True)

    def xtest_stop(self):
        self.xtest.XTestGrabControl(self.display, False)

    LETTERS = {
        '(': ('Shift_L', '9'),
        ')': ('Shift_L', '0')
    }
    def type(self, keys):
        for key in keys:
            seq = self.LETTERS.get(key, [key])
            for symbol in seq:
                keycode = self.lookup_keycode(symbol)
                self.xtest.XTestFakeKeyEvent(self.display, keycode, True, 0)
            for symbol in seq[::-1]:
                keycode = self.lookup_keycode(symbol)
                self.xtest.XTestFakeKeyEvent(self.display, keycode, False, 0)
        self.x11.XSync(self.display, False)


    def lookup_keycode(self, symbol):
        return self.x11.XKeysymToKeycode(self.display, self.x11.XStringToKeysym(symbol))

    def key(self, symbol):
        keycode = self.lookup_keycode(symbol)
        self.log("sending XFKE(%r, %x)" % (self.display, keycode))
        self.xtest.XTestFakeKeyEvent(self.display, keycode, True, 0)
        self.xtest.XTestFakeKeyEvent(self.display, keycode, False, 100)
        self.x11.XSync(self.display, False)

    def log(self, message):
        if quiet: return
        print message


