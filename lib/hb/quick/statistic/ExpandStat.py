from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq, TrackFormat
from quick.track_operations.raw_operations.Expand import expand
from quick.track_operations.utils.TrackHandling import createRawResultTrackView
from hb.quick.track_operations.TrackOperationsModule import parseBoolean, parseInt, \
    createEmptyTrackView


class ExpandStat(MagicStatFactory):
    pass


class ExpandStatUnsplittable(Statistic):

    def _init(self, resultNoOverlap=False, useStrands=False, treatMissingAsNegative=False,
            both='', downstream='', upstream='', useFraction=False, **kwargs):
        self._resultNoOverlap = parseBoolean(resultNoOverlap)
        self._useStrands = parseBoolean(useStrands)
        self._both = parseInt(both)
        self._treatMissingAsNegative = parseBoolean(treatMissingAsNegative)
        self._downstream = parseInt(downstream)
        self._upstream = parseInt(upstream)
        self._useFraction = parseBoolean(useFraction)

    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()

        if self._useStrands:
            if strands is None or strands.size == 0:
                self._useStrands = False

        regionSize = len(self._region)

        ret = expand(regionSize, starts=starts, ends=ends, strands=strands,
                     downstream=self._downstream, upstream=self._upstream,
                     useFraction=self._useFraction,
                     useStrands=self._useStrands,
                     treatMissingAsNegative=self._treatMissingAsNegative)

        if ret is not None and len(ret[0]) != 0:
            starts, ends, index = ret

            resultTrackFormat = self._getResultTrackFormat(tv)
            return createRawResultTrackView(index, self._region, tv,
                                            self._resultNoOverlap,
                                            newStarts=starts, newEnds=ends,
                                            trackFormat=resultTrackFormat)

        else:
            return createEmptyTrackView(tv)


    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))

    def _getResultTrackFormat(self, tv1):
        """
        Creates the correct TrackFormatReq according to the input track
        :return:
        """

        tr = tv1.trackFormat

        if tr.hasStrand():
            strands = []
        else:
            strands = None

        if tr.isValued():
            values = []
        else:
            values = None

        if tr.isLinked:
            ids = []
            edges = []
        else:
            ids = None
            edges = None

        if tr.isWeighted():
            weights = []
        else:
            weights = None

        return TrackFormat(startList=[], endList=[],
                                              strandList=strands,
                                              valList=values,idList=ids,
                                              edgesList=edges,
                                              weightsList=weights)

