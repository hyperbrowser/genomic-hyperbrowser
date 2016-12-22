# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticConcatResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CommonConstants import BINARY_MISSING_VAL

class PointPositionsInSegsStat(MagicStatFactory):
    pass

# Assumes that no segments cross from one user bin to the next
class PointPositionsInSegsStatSplittable(StatisticConcatResSplittable, OnlyGloballySplittable):
    pass

class PointPositionsInSegsStatUnsplittable(Statistic):
    "Computes a list of positions of points relative to segments they occur inside. Ignores points outside segments. Currently only supports scaled positions of points, that is scaled between 0 at upstream end and 1 at downstream end." #could also support absolute offsets inside segs..

    def _init(self, scaledPositions='True', **kwArgs):
        self._scaledPositions = eval(scaledPositions)

    def _compute(self):
        tvSegs = self._children[1].getResult()
        tvPoints = self._children[0].getResult()
        dists = []
        tvPointIter = tvPoints.__iter__()

        relPosList = []
        try:
            point = tvPointIter.next()
        except StopIteration:
            return relPosList

                #print '*'+point.start()
        for seg in tvSegs:
            if len(seg) < 3: #len 1 or 2 will give strong bias towards borders..
                continue
            #print '**'+seg.start()+', '+seg.end()
            #assert( seg.strand() in [None,True])
            while point.start() < seg.end():
                if point.start() >= seg.start():
                    if point.strand() in [None, BINARY_MISSING_VAL] or seg.strand() in [None, BINARY_MISSING_VAL] or point.strand() == seg.strand() :
                        if self._scaledPositions:
                            relPos = 1.0 * (point.start()-seg.start()) / ( (seg.end()-1) - seg.start() )
                            if seg.strand() == False:
                                relPos = 1-relPos
                        else:
                            if seg.strand() == False:
                                relPos = seg.end()-1-point.start()
                            else:
                                relPos = point.start()-seg.start()
                        relPosList.append(relPos)
                try:
                    point = tvPointIter.next()
                except StopIteration:
                    return relPosList

        return relPosList


    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(interval=True)) )
