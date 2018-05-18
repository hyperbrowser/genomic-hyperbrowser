from collections import MutableMapping, OrderedDict

from quick.application.SignatureDevianceLogging import takes


class TSResult(MutableMapping):
    def __init__(self, ts, result=None, *args, **kwArgs):
        self._dict = OrderedDict(*args, **kwArgs)
        self._ts = ts
        self.setResult(result)

    def __getitem__(self, key):
        return self._dict[key]

    @takes('TSResult', basestring, 'TSResult')
    def __setitem__(self, key, value):
        assert key in self._ts.keys(), (key, self._ts.keys())
        # assert value._ts in self._ts.values(), 'Intention is to control that rts hierarchy is corresponding to ts hierarchy, but maybe not always the case, e.g. in MC (then remove..)'
        self._dict[key] = value

    def __delitem__(self, key):
        del self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __copy__(self):
        return type(self)(self._ts, self._result, self._dict)

    def __nonzero__(self):
        """
        Seems the safest thing to do. If not, TSResult objects with no children will fail
        tests like "if ts:", which often leads to hard-to-find bugs.
        """
        return True

    def setResult(self, result):
        self._result = result

    def getResult(self):
        return self._result

    def getTrackStructure(self):
        return self._ts
