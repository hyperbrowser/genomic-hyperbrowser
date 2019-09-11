from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
from quick.track_operations.raw_operations.Complement import complement
from quick.track_operations.utils.TrackHandling import createRawResultTrackView, parseBoolean


class ComplementStat(MagicStatFactory):
    pass


class ComplementStatUnsplittable(Statistic):

    def _init(self, useStrands=True, treatMissingAsNegative=False, **kwargs):
        self._useStrands = parseBoolean(useStrands)
        self._treatMissingAsNegative = parseBoolean(treatMissingAsNegative)
        self._resultAllowOverlap = False

    def _compute(self):
        tv1 = self._children[0].getResult()
        t1Starts = tv1.startsAsNumpyArray()
        t1Ends = tv1.endsAsNumpyArray()
        t1Strands = tv1.strandsAsNumpyArray()

        regionSize = len(self._region)

        if self._useStrands and t1Strands is not None:
            assert t1Strands is not None
        else:
            self._useStrands = False
            t1Strands = None
        ret = complement(t1Starts, t1Ends, t1Strands, regionSize, useStrands=self._useStrands,
                         treatMissingAsNegative=self._treatMissingAsNegative)

        if ret is not None and len(ret[0]) != 0:
            # We do not care about info from the base track..
            # the new track will only contain the starts and ends

            starts, ends, strands = ret
            tv = createRawResultTrackView(None, self._region, None,
                                          self._resultAllowOverlap,
                                          newStarts=starts, newEnds=ends,
                                          newStrands=strands)

            return tv

        else:
            return TrackView(genomeAnchor=tv1.genomeAnchor, startList=[],
                             endList=[], valList=None, strandList=None,
                             idList=None, edgesList=None, weightsList=None,
                             borderHandling=tv1.borderHandling, allowOverlaps=False)

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))
