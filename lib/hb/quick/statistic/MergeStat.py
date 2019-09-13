from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from quick.track_operations.raw_operations.Merge import merge
from quick.track_operations.utils.TrackHandling import createRawResultTrackView, parseBoolean, \
    createEmptyTrackView


class MergeStat(MagicStatFactory):
    pass


class MergeStatUnsplittable(Statistic):

    def _init(self, useStrands=False, treatMissingAsNegative=False, **kwargs):
        self._useStrands = parseBoolean(useStrands)
        self._treatMissingAsNegative = parseBoolean(treatMissingAsNegative)

        if 'resultAllowOverlap' in self._kwArgs:
            self._resultAllowOverlap = parseBoolean(self._kwArgs['resultAllowOverlap'])
        else:
            self._resultAllowOverlap = False

    def _compute(self):
        tv = self._children[0].getResult()
        print 'tv: '
        print tv
        
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()
        values = tv.valsAsNumpyArray()
        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()
        weights = tv.weightsAsNumpyArray()

        if self._useStrands:
            if strands is None:
                self._useStrands = False

        if not self._resultAllowOverlap:
            ret = merge(starts, ends, strands=strands, values=values, ids=ids,
                        edges=edges, weights=weights, useStrands=self._useStrands,
                        treatMissingAsNegative=self._treatMissingAsNegative)

            if ret is not None and len(ret[0]) != 0:
                assert len(ret) == 7
                # We do not care about info from the base track..
                # the new track will only contain starts, ends and strands if
                # present.

                # starts, ends, values, strands, ids, edges, weights
                starts, ends, values, strands, ids, edges, weights = ret
            else:
                return createEmptyTrackView(tv)

        tv = createRawResultTrackView(None, self._region, None,
                                      False,
                                      newStarts=starts, newEnds=ends,
                                      newValues=values, newStrands=strands,
                                      newIds=ids, newEdges=edges,
                                      newWeights=weights,
                                      trackFormat=tv.trackFormat)
        return tv



    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))

