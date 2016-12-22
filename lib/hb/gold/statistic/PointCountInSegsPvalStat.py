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
from gold.statistic.Statistic import Statistic
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.PointCountInsideSegsStat import PointCountInsideSegsStat
from gold.statistic.ProportionCountStat import ProportionCountStat
#from proto.RSetup import r
import math
from collections import OrderedDict

class PointCountInSegsPvalStat(MagicStatFactory):
    pass

#class PointCountInSegsPvalStatSplittable(StatisticSumResSplittable):
#    pass
            
class PointCountInSegsPvalStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, assumptions='poissonPoints', tail='different', **kwArgs):
        assert( tail in ['less','more','different'])
        assert assumptions=='poissonPoints'
        
        self._tail = tail
        Statistic.__init__(self, region, track, track2, assumptions=assumptions, tail=tail, **kwArgs)
    
    def _compute(self):
        from proto.RSetup import r
        #r("require(Defaults)")
        #r('setDefaults(q, save="no")')
        #r("useDefaults(q)")

        x = self._numPointsInside.getResult() 
        size = self._numPointsTotal.getResult()
        prob = self._segmentCoverProportion.getResult()
        se = math.sqrt(1.0*(prob)*(1-prob)/size)
        if size < 1 or prob in [0,1]:
            return None
        if self._tail=='less':
            pval = r.pbinom(x,size,prob)
        elif self._tail=='more':
            pval = 1 - r.pbinom(x-1,size,prob)
        elif self._tail=='different':
            pval = min(1, 2*min( r.pbinom(x,size,prob), 1 - r.pbinom(x-1,size,prob)))
            
        #return {'P-value':pval, 'SegCover':prob, 'PointsInside':x, 'PointsTotal':size}
        return OrderedDict([ ('P-value', float(pval)), ('Test statistic: PointsInside', x), ('E(Test statistic): ExpPointsInside', prob*size), \
                             ('DiffFromExpected', x-prob*size), ('PointsTotal', size), ('SegCoverage', prob) ])
    
    def _createChildren(self):
        self._numPointsInside = self._addChild( PointCountInsideSegsStat(self._region, self._track, self._track2))
        self._numPointsTotal = self._addChild( CountPointStat(self._region, self._track))
        self._segmentCoverProportion = self._addChild( ProportionCountStat(self._region, self._track2))
