class GenericMCSampler(object):

    def __init__(self, rawStatistic, region, ts, **kwArgs):
        self._rawStatistic = rawStatistic
        self._region = region
        self._trackStructure = ts
        self._kwArgs = kwArgs

    def drawRandomResult(self):
        return self._rawStatistic(self._region, self._trackStructure, **self._kwArgs).getResult()