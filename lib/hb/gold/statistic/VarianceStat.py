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
from gold.statistic.CountStat import CountStat
from gold.statistic.SumStat import SumStat
from gold.statistic.SumOfSquaresStat import SumOfSquaresStat

class VarianceStat(MagicStatFactory):
    pass

class VarianceStatUnsplittable(Statistic):    
    def _compute(self):
        if self._children[2].getResult() < 2:
            return None
        else:
            #print [self._children[i].getResult() for i in range(3)]
            MeanSq = 1.0 * self._sumOfSquares.getResult() / (self._count.getResult())
            Mean = 1.0 * self._sum.getResult() / (self._count.getResult())
            #print 'and',MeanSq ,Mean, Mean**2
            mlVar = MeanSq - Mean**2
            n = self._count.getResult()
            unbiasedVar = 1.0 * mlVar * n / (n-1)
            if unbiasedVar < 0:
                #could happen if about zero variance, due to rounding errors
                return 0.0
            else:
                return unbiasedVar
        
        #tv = self._children[0].getResult()
        #try:
        #    return tv.asBpLevelNumpyArray().var()
        #except Exception:
        #    return array([el.val() for el in tv]).var()
        
    def _createChildren(self):
        self._sumOfSquares = self._addChild( SumOfSquaresStat(self._region, self._track) )
        self._sum = self._addChild( SumStat(self._region, self._track) )
        self._count = self._addChild( CountStat(self._region, self._track) )


