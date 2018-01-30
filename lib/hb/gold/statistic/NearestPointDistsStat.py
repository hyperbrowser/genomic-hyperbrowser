from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import NotSupportedError


class NearestPointDistsStat(MagicStatFactory):
    pass

class NearestPointDistsStatSplittable(StatisticConcatResSplittable, OnlyGloballySplittable):
    pass

class NearestPointDistsStatUnsplittable(Statistic):
    'For each point in track1, finds the distance to the right/left/both to the next point of track2..'
    def __init__(self, region, track, track2, distDirection='both', **kwArgs):
        assert( distDirection in ['left','right','both'])
        
        self._distDirection = distDirection
        Statistic.__init__(self, region, track, track2, distDirection=distDirection, **kwArgs)

    def _compute(self):
        if self._region.strand == False and self._distDirection != 'both':
            raise NotSupportedError() #support by switching between left/right-computation..

        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        return self._determineClosestDistPerQuery(tv1.startsAsNumpyArray().tolist(), tv2.startsAsNumpyArray().tolist(), self._distDirection)

    @staticmethod
    def _determineClosestDistPerQuery(ql, rl, distDirection):
        dist = [-1] * len(ql)
        if len(rl) == 0:
            return [None] * len(ql)
        ri = 0
        for qi in range(len(ql)):
            q = ql[qi]
            while ri<len(rl) and rl[ri]<q:
                ri+=1
            leftDist = q - rl[ri-1] if ri>0 else None
            rightDist = rl[ri]-q if ri<len(rl) else None
            assert leftDist is not None or rightDist is not None
            if distDirection == 'left':
                dist[qi] = 0 if rightDist==0 else leftDist
            elif distDirection == 'right':
                dist[qi] = 0 if leftDist == 0 else rightDist
            else:
                if rightDist is None or (leftDist is not None and leftDist < rightDist):
                    dist[qi] = leftDist
                else:
                    dist[qi] = rightDist

        return dist

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=False)) )
