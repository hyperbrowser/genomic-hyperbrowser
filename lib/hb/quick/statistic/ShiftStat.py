from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from quick.track_operations.raw_operations.Shift import shift

from quick.track_operations.utils.TrackHandling import createRawResultTrackView
from hb.quick.track_operations.TrackOperationsModule import parseBoolean, parseInt, \
    createEmptyTrackView


class ShiftStat(MagicStatFactory):
    pass


class ShiftStatUnsplittable(Statistic):

    def _init(self, resultNoOverlap=True, useStrands=True, treatMissingAsNegative=False,
            shiftLength='', useFraction=True, **kwargs):
        self._resultNoOverlap = parseBoolean(resultNoOverlap)
        self._useFraction = parseBoolean(useFraction)
        self._useStrands = parseBoolean(useStrands)
        self._shiftLength = parseInt(shiftLength)
        self._treatMissingAsNegative = parseBoolean(treatMissingAsNegative)

    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()

        if self._useStrands:
            if strands is None or strands.size == 0:
                self._useStrands = False

        regionSize = len(self._region)
        ret = shift(starts, ends, regionSize, strands=strands, shiftLength=self._shiftLength,
                     useFraction=self._useFraction, useStrands=self._useStrands,
                     treatMissingAsNegative=self._treatMissingAsNegative)

        if ret is not None and len(ret[0]) != 0:
            starts, ends, index, strands = ret

            return createRawResultTrackView(index, self._region, tv,
                                            self._resultNoOverlap,
                                            newStarts=starts, newEnds=ends,
                                            trackFormat=tv.trackFormat)

        else:
            return createEmptyTrackView(tv)

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))

