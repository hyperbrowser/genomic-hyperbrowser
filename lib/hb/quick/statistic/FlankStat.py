from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
from quick.track_operations.raw_operations.Flank import flank
from hb.quick.track_operations.TrackOperationsModule import parseBoolean, parseInt, \
    createEmptyTrackView


class FlankStat(MagicStatFactory):
    pass


class FlankStatUnsplittable(Statistic):

    def _init(self, resultNoOverlap=False, useStrands=True, treatMissingAsNegative=False,
            downstream='', upstream='', both='', useFraction=False, **kwargs):
        self._resultNoOverlap = parseBoolean(resultNoOverlap)
        self._useStrands = parseBoolean(useStrands)
        self._treatMissingAsNegative = parseBoolean(treatMissingAsNegative)
        self._downstream = parseInt(downstream)
        self._upstream = parseInt(upstream)
        self._useFraction = parseBoolean(useFraction)
        self._both = parseInt(both)

    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()

        if self._useStrands:
            if strands is None or strands.size == 0:
                self._useStrands = False

        regionSize = len(self._region)

        ret = flank(starts, ends, regionSize, strands=strands,
                    downstream=self._downstream, upstream=self._upstream,
                    both=self._both, useStrands=self._useStrands,
                    useFraction=self._useFraction,
                    treatMissingAsNegative=self._treatMissingAsNegative)

        if ret is not None and len(ret[0]) != 0:
            starts, ends, strands = ret

            return TrackView(self._region, starts, ends, None, strands, None,
                           None, None, borderHandling='crop', allowOverlaps=True)

        else:
            return createEmptyTrackView(tv)

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))

