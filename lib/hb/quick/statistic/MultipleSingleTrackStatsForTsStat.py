from collections import OrderedDict

from gold.track.TSResult import TSResult
from gold.track.TrackStructure import TrackStructureV2
from quick.statistic.GenericResultsCombinerStat import GenericResultsCombinerStat
from quick.statistic.SingleTSStat import SingleTSStat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class MultipleSingleTrackStatsForTsStat(MagicStatFactory):
    """
    Will run all statistics given by rawStatistics parameter for each member of a flat TS.
    """
    pass


#class MultipleSingleTrackStatsForTsStatSplittable(StatisticSumResSplittable):
#    pass

class MultipleSingleTrackStatsForTsStatUnsplittable(StatisticV2):

    def _compute(self):
        res = TSResult(self._trackStructure)
        for title, child in self._childrenDict.iteritems():
            res[title] = child.getResult()
        return res

    def _createChildren(self):
        self._childrenDict = OrderedDict()
        for key, sTS in self._trackStructure.iteritems():
            self._childrenDict[key] = self._addChild(SingleTSStat(
                self._region, sTS, rawStatistic=GenericResultsCombinerStat, **self._kwArgs))