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
from gold.statistic.Statistic import Statistic, StatisticSplittable


class GenericT1T2BinValuesCorrelationStat(MagicStatFactory):
    "takes as parameter another statistic class, gets results for this per bin, then at the global level returns the max of values per bin"
    pass

class GenericT1T2BinValuesCorrelationStatSplittable(StatisticSplittable):
    def _init(self, corrMethod, **kwArgs):
        assert corrMethod in ['pearson','spearman','kendall']
        self._corrMethod = corrMethod
        
    def _combineResults(self):
        from proto.RSetup import robjects, r
        rVec1 = robjects.FloatVector([x[0] for x in self._childResults])
        rVec2 = robjects.FloatVector([x[1] for x in self._childResults])
        return r.cor(rVec1, rVec2, method=self._corrMethod)
        
        
    
class GenericT1T2BinValuesCorrelationStatUnsplittable(Statistic):
    def _init(self, perBinStatistic, **kwArgs):
        self._perBinStatistic = self.getRawStatisticClass(perBinStatistic)
    
    def _compute(self):
        return [self._children[0].getResult(), self._children[1].getResult()]
    
    def _createChildren(self):
        self._addChild( self._perBinStatistic(self._region, self._track, **self._kwArgs) )
        self._addChild( self._perBinStatistic(self._region, self._track2, **self._kwArgs) )
