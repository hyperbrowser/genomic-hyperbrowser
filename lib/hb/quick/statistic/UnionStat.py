
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.UniquifyLinksStat import UniquifyLinksStat
from quick.track_operations.raw_operations.Union import union
from quick.track_operations.utils.TrackHandling import createRawResultTrackView
from hb.quick.track_operations.TrackOperationsModule import parseBoolean, createEmptyTrackView


class UnionStat(MagicStatFactory):
    pass


class UnionStatUnsplittable(Statistic):

    def _init(self, resultNoOverlap=False, useStrands=True, treatMissingAsNegative=True, **kwargs):
        self._resultNoOverlap = parseBoolean(resultNoOverlap)
        self._useStrands = parseBoolean(useStrands)
        self._treatMissingAsNegative = parseBoolean(treatMissingAsNegative)
        if 'rawStatistic' in self._kwArgs:
            del self._kwArgs['rawStatistic']

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        if tv1.trackFormat != tv2.trackFormat:
            raise NotImplementedError

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()
        ret = union(t1Starts, t1Ends, t2Starts, t2Ends,
                    self._resultNoOverlap)

        if ret is not None and len(ret[0]) != 0:
            starts, ends, index, encoding = ret

            return createRawResultTrackView(index, self._region, [tv1, tv2],
                                          self._resultNoOverlap,
                                          newStarts=starts, newEnds=ends,
                                          encoding=encoding,
                                          trackFormat=tv1.trackFormat)
        else:
            return createEmptyTrackView(tv1)

    def _createChildren(self):
        self._addChild(UniquifyLinksStat(self._region, self._track, identifier="track-1"))
        self._addChild(UniquifyLinksStat(self._region, self._track2, identifier="track-2"))
