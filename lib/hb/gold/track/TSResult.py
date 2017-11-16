from quick.application.SignatureDevianceLogging import takes


class TSResult(dict):
    def __init__(self, ts, result=None):
        dict.__init__(self)
        self._ts = ts
        self.setResult(result)

    def setResult(self, result):
        self._result = result

    def getResult(self):
        return self._result

    @takes('TSResult', basestring, 'TSResult')
    def __setitem__(self, key, value):
        assert key in self._ts.keys(), (key, self._ts.keys())
        # assert value._ts in self._ts.values(), 'Intention is to control that rts hierarchy is corresponding to ts hierarchy, but maybe not always the case, e.g. in MC (then remove..)'
        dict.__setitem__(self, key, value)
