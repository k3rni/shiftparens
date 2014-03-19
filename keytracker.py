__all__ = ['KeyTracker']

from itertools import izip

class KeyTracker:
    def __init__(self, emitter=None, quiet=False):
        self.quiet = quiet
        self.tape = []
        self.timetape = []
        self.emitter = emitter 
        self.patterns = (
            (['rlRL', 'rRlL'], 0.3, self.type, '()'),
            (['lRLR', 'lLrR'], 0.3, self.type, ')('),
            (['srSR'], 0.3, self.type, ')'),
            (['lL'], 0.3, self.type, '('),
            (['rR'], 0.3, self.type, ')'),
            (['cC'], 0.3, self.key, 'Escape')
        )

    def record(self, letter, tm):
        self.tape.insert(0, letter)
        self.timetape.insert(0, tm)
        if len(self.tape) > 5:
            self.tape.pop()
            self.timetape.pop()

    def match(self, seq):
        return all([left == right for (left, right) in izip(self.tape, seq)])

    def fast_enough(self, count, timeout=0.3):
        return len(self.timetape) >= count and (self.timetape[0] - self.timetape[count-1] < timeout)

    def analyze_tape(self):
        # patterns must be sorted descending by length
        for patterns, timeout, command, value in self.patterns:
            if any((self.match(pat) and self.fast_enough(len(pat), timeout)) for pat in patterns):
                command(value)
                return
    
    def type(self, keys):
        self.emitter.type(keys)

    def key(self, symbol):
        self.emitter.key(symbol)

    def __str__(self):
        return '[%s]' % (''.join(self.tape))

