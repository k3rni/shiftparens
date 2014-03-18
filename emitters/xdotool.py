__all__ = ['XdotoolEmitter']

import subprocess

class XdotoolEmitter:
    def key(self, symbol):
        print "KEY %s" % symbol
        self.xdotool('key', symbol)

    def type(self, keys):
        print "TYPING %r" % keys
        self.xdotool('type', keys)

    def xdotool(self, *args):
        subprocess.call(['xdotool'] + list(args), shell=False)

