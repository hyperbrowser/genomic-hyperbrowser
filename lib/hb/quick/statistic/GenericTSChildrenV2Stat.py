from collections import OrderedDict

from gold.track.TSResult import TSResult
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class GenericTSChildrenV2Stat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class GenericTSChildrenV2StatSplittable(StatisticSumResSplittable):
#    pass

class GenericTSChildrenV2StatUnsplittable(StatisticV2):

    def _init(self, genericTSChildrenRawStatistic, **kwargs):
        self._rawStatistic = self.getRawStatisticClass(genericTSChildrenRawStatistic)

    def _compute(self):
        tsResult = TSResult(self._trackStructure)

        rawResults = []
        for key, child in self._childrenDict.iteritems():
            childTSR = child.getResult()
            tsResult[key] = childTSR
            rawResults.append(childTSR.getResult())
        tsResult.setResult(rawResults)
        return tsResult

    def _createChildren(self):
        self._childrenDict = OrderedDict()
        for key, childTS in self._trackStructure.items():
            self._childrenDict[key] = self._addChild(self._rawStatistic(self._region, childTS, **self._kwArgs))
