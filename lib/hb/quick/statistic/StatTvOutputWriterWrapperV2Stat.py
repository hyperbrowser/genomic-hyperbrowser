from quick.statistic.StatTvOutputWriterStat import StatTvOutputWriterStat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.track.TrackStructure import SingleTrackTS


class StatTvOutputWriterWrapperV2Stat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class StatTvOutputWriterWrapperV2StatSplittable(StatisticSumResSplittable):
#    pass

class StatTvOutputWriterWrapperV2StatUnsplittable(StatisticV2):

    def _compute(self):
        return self._children[0].getResult()

    def _createChildren(self):
        assert isinstance(self._trackStructure, SingleTrackTS), 'Statistic supports only SingleTrackTS'
        track = self._trackStructure.track
        self._addChild(StatTvOutputWriterStat(self._region, track, **self._kwArgs))