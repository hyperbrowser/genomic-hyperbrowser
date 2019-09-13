from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq, TrackFormat
from quick.statistic.ExpandWithoutOverlapsStat import ExpandWithoutOverlapsStat
from quick.track_operations.raw_operations.Expand import expand
from quick.track_operations.utils.TrackHandling import createRawResultTrackView, parseBoolean, \
    parseInt, createEmptyTrackView


class ExpandStat(MagicStatFactory):
    pass


class ExpandStatUnsplittable(Statistic):

    def _compute(self):
        tv = self._children[0].getResult()

        return tv

    def _createChildren(self):
        self._addChild(ExpandWithoutOverlapsStat(self._region, self._track, **self._kwArgs))



