
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from quick.track_operations.raw_operations.ValueSelect import valueSelect
from quick.track_operations.utils.TrackHandling import createRawResultTrackView
from hb.quick.track_operations.TrackOperationsModule import createEmptyTrackView


class ValueSelectStat(MagicStatFactory):
    pass


class ValueSelectStatUnsplittable(Statistic):

    def _init(self, limit=None, **kwargs):
        if limit == 'None':
            self._limit = None
        else:
            self._limit = limit

    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        values = tv.valsAsNumpyArray()

        ret = valueSelect(starts, ends, values=values, limit=self._limit,
                          allowOverlap=True)

        if ret is not None and len(ret) != 0:
            starts, ends, index = ret

            return createRawResultTrackView(index, self._region, tv, True,
                                         newStarts=starts, newEnds=ends)

        else:
            return createEmptyTrackView(tv)

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))
