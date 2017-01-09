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
from gold.statistic.RawOverlapStat import RawOverlapStatUnsplittable
from gold.track.TrackView import TrackView
from numpy import array

class TrackIntersectionWithValStat(MagicStatFactory):
    pass

#class TrackIntersectionWithValStatSplittable(StatisticSumResSplittable):
#    pass

class TrackIntersectionWithValStatUnsplittable(RawOverlapStatUnsplittable):
    #def _init(self, operation="intersect"):
    #    assert operation in ['intersect', 'union', 'subtract1from2', 'subtract2from1', 'notcovered']

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()

        t1s = tv1.startsAsNumpyArray()
        t1e = tv1.endsAsNumpyArray()
        t1vals = tv1.valsAsNumpyArray()
        t2s = tv2.startsAsNumpyArray()
        t2e = tv2.endsAsNumpyArray()

        allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus = \
            self._findAllStartAndEndEvents(t1s, t1e, t2s, t2e)

        allResultStarts = allSortedDecodedEvents[cumulativeCoverStatus[:-1] == 3]
        allResultLengths = allEventLengths[cumulativeCoverStatus[:-1] == 3]
        allResultEnds = allResultStarts + allResultLengths
        
        valList = []
        cursor = 0
        for rs, re in zip(allResultStarts, allResultEnds):
            for i in xrange(cursor, len(t1s)):
                if rs >= t1s[i] and re <= t1e[i]:
                    valList.append(float(t1vals[i]))
                    cursor = i
                    break
        
        assert len(valList) == len(allResultStarts), valList
            
        return TrackView(genomeAnchor=tv1.genomeAnchor, startList=allResultStarts,
                         endList=allResultEnds, valList=array(valList), strandList=None,
                         idList=None, edgesList=None, weightsList=None,
                         borderHandling=tv1.borderHandling, allowOverlaps=False)
