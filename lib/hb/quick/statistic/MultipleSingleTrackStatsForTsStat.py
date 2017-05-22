from collections import OrderedDict

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
        ts = TrackStructureV2()
        for title, child in self._childrenDict.iteritems():
            ts[title] = child.getResult()
        return ts

    def _createChildren(self):
        self._childrenDict = OrderedDict()
        for sTS in self._trackStructure.values():
            self._childrenDict[sTS.metadata['title']] = self._addChild(SingleTSStat(
                self._region, sTS, rawStatistic=GenericResultsCombinerStat, **self._kwArgs))