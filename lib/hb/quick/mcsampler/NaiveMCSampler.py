from gold.track.TrackStructure import TrackStructureV2
from quick.application.SignatureDevianceLogging import takes, anything
from quick.statistic.StatisticV2 import StatisticV2


class NaiveMCSampler(object):

    #TODO: determine region type
   # @takes("NaiveMCSampler", StatisticV2, anything, TrackStructureV2, type)
    def __init__(self, rawStatistic, region, ts, genericSamplerClass, **kwArgs):
        self._rawStatistic = rawStatistic
        self._region = region
        self._trackStructure = ts
        self._genericSamplerClass = genericSamplerClass
        self._kwArgs = kwArgs
        self._realResult = None
        self._randResultList = []

    def computeRealResult(self):
        self._realResult = self._rawStatistic(self._region, self._trackStructure["real"], **self._kwArgs).getResult()

    def computeAdditionalRandomResult(self):
        self._randResultList.append(
            self._genericSamplerClass(
                self._rawStatistic,
                self._region,
                self._trackStructure['rand'],
                **self._kwArgs).drawRandomResult())

    def getAllResults(self):
        if self._rawStatistic is None:
            self.computeRealResult()
        return self._realResult, self._randResultList