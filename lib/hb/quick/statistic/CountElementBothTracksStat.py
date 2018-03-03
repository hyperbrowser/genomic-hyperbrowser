from collections import OrderedDict

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountElementStat import CountElementStat


class CountElementBothTracksStat(MagicStatFactory):
    pass


# class CountElementBothTracksStatSplittable(StatisticSumResSplittable):
#     pass


class CountElementBothTracksStatUnsplittable(Statistic):
    def _compute(self):
        return OrderedDict([('track1_count', self._children[0].getResult()),
                            ('track2_count', self._children[1].getResult())])
    
    def _createChildren(self):
        self._addChild( CountElementStat(self._region, self._track) )
        self._addChild( CountElementStat(self._region, self._track2) )
