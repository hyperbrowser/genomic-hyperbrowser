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
from quick.statistic.BinSizeStat import BinSizeStat
from quick.statistic.AggregateOfCoveredBpsInSegmentsStat import AggregateOfCoveredBpsInSegmentsStat
from gold.statistic.SumOverCoveredBpsStat import SumOverCoveredBpsStat
from gold.statistic.CountStat import CountStat
from gold.statistic.RawOverlapStat import RawOverlapStat
import numpy

class MeanInsideOutsideStat(MagicStatFactory):
    pass

#class MeanInsideOutsideStatSplittable(StatisticSumResSplittable):
#    pass

class MeanInsideOutsideStatUnsplittable(Statistic):
    def _init(self, missingVals='treatAsZero', **kwArgs):
        assert( missingVals in ['treatAsZero','exclude'])
        self._missingVals = missingVals
    
    def _compute(self):
        sumInside = self._children[0].getResult()
        sumTotal = self._children[1].getResult()
        res = self._children[4].getResult()
        lengthInside = self._children[2].getResult() if self._missingVals == 'treatAsZero' else  res['Both']
        lengthTotal = self._children[3].getResult() if self._missingVals == 'treatAsZero' else  res['Only2'] + res['Both']
        
        
        meanInside = sumInside / lengthInside if lengthInside>0 else numpy.nan
        meanOutside = (sumTotal-sumInside) / (lengthTotal-lengthInside) if lengthTotal!= lengthInside else numpy.nan
        
        return {'MeanInsideSegments':meanInside, 'MeanOutsideSegments':meanOutside}
        
    def _createChildren(self):
        #self._track: defines inside vs outside
        #self._track2: provides values
        self._addChild(AggregateOfCoveredBpsInSegmentsStat(self._region,  self._track2, self._track, method='sum_of_sum'))
        self._addChild(SumOverCoveredBpsStat(self._region, self._track2))
        self._addChild(CountStat(self._region, self._track))
        self._addChild(BinSizeStat(self._region, self._track))
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        