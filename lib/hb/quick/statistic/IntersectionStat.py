from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq, TrackFormat
from gold.track.TrackView import TrackView
from quick.track_operations.raw_operations.Intersect import intersect
from quick.track_operations.utils.TrackHandling import createRawResultTrackView, parseBoolean


class IntersectionStat(MagicStatFactory):
    pass


class IntersectionStatUnsplittable(Statistic):

    def _init(self, resultAllowOverlap=False, useStrands=True, treatMissingAsNegative=True, **kwargs):
        self._resultAllowOverlap = parseBoolean(resultAllowOverlap)
        self._useStrands = parseBoolean(useStrands)
        self._treatMissingAsNegative = parseBoolean(treatMissingAsNegative)

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()
        ret = intersect(t1Starts, t1Ends, t2Starts, t2Ends)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 4

            starts, ends, index, encoding = ret

            tv = createRawResultTrackView(index, self._region, [tv1, tv2],
                                            self._resultAllowOverlap,
                                            newStarts=starts, newEnds=ends,
                                            encoding=encoding,
                                            trackFormat=TrackFormat(startList=[], endList=[]))

            return tv
        else:
            return TrackView(genomeAnchor=tv1.genomeAnchor, startList=[],
                             endList=[], valList=None, strandList=None,
                             idList=None, edgesList=None, weightsList=None,
                             borderHandling=tv1.borderHandling, allowOverlaps=False)

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))
        self._addChild(RawDataStat(self._region, self._track2, TrackFormatReq(dense=False)))
