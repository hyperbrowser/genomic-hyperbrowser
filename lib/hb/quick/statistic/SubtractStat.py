from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.MergeStat import MergeStat
from quick.track_operations.raw_operations.Subtract import subtract
from quick.track_operations.utils.TrackHandling import createRawResultTrackView
from hb.quick.track_operations.TrackOperationsModule import parseBoolean, createEmptyTrackView


class SubtractStat(MagicStatFactory):
    pass


class SubtractStatUnsplittable(Statistic):

    def _init(self, useStrands=True, treatMissingAsNegative=True, **kwargs):
        self._useStrands = parseBoolean(useStrands)
        self._treatMissingAsNegative = parseBoolean(treatMissingAsNegative)
        if 'rawStatistic' in self._kwArgs:
            del self._kwArgs['rawStatistic']

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()

        t2Starts = tv2.startsAsNumpyArray()
        t2Ends = tv2.endsAsNumpyArray()

        if self._useStrands:
            t1Strands = tv1.strandsAsNumpyArray()
            t2Strands = tv2.strandsAsNumpyArray()

            if t1Strands is None or t2Strands is None:
                self._useStrands = None
                t1Strands = None
                t2Strands = None

        else:
            t1Strands = None
            t2Strands = None

        ret = subtract(t1Starts, t1Ends, t2Starts, t2Ends,
                       t1Strands=t1Strands, t2Strands=t2Strands,
                       useStrands=self._useStrands,
                       treatMissingAsNegative=self._treatMissingAsNegative)

        if ret is not None and len(ret[0]) != 0:
            starts, ends, index = ret

            return createRawResultTrackView(index, self._region, tv1,
                                            False,
                                            newStarts=starts, newEnds=ends,
                                            trackFormat=tv1.trackFormat)
        else:
            return createEmptyTrackView(tv1)

    def _createChildren(self):
        self._addChild(MergeStat(self._region, self._track, **self._kwArgs))
        self._addChild(MergeStat(self._region, self._track2, **self._kwArgs))
