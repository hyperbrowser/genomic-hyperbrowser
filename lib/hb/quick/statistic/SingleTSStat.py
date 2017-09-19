from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class SingleTSStat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class SingleTSStatSplittable(StatisticSumResSplittable):
#    pass

class SingleTSStatUnsplittable(StatisticV2):
    def _init(self, rawStatistic, **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)

    def _compute(self):
        ts = self._trackStructure._copyTreeStructure()
        ts.result = self._children[0].getResult()
        return ts

    def _createChildren(self):
        assert self._trackStructure.isSingleTs(), "SingleTS expected, got %s" % str(type(self._trackStructure))
        self._addChild(self._rawStatistic(self._region, self._trackStructure.track, **self._kwArgs))
