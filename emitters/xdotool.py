__all__ = ['XdotoolEmitter']

import subprocess

class XdotoolEmitter:
    def __init__(self, quiet=False):
        self.quiet = quiet
        self.log("Using XDo emitter")

    def key(self, symbol):
        self.log("KEY %s" % symbol)
        self.xdotool('key', symbol)

    def type(self, keys):
        self.log("TYPING %r" % keys)
        self.xdotool('type', keys)

    def xdotool(self, *args):
        subprocess.call(['xdotool'] + list(args), shell=False)

    def log(self, text):
        if not self.quiet:
            print text

