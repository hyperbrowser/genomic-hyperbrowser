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
from gold.statistic.DiscreteMarksHistStat import DiscreteMarksHistStat
from numpy import arange

class HistReducerStat(MagicStatFactory):
    pass

#class HistReducerStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class HistReducerStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, **kwArgs):
        self._numDiscreteVals = int(numDiscreteVals)
        self._reducedNumDiscreteVals = int(reducedNumDiscreteVals)
        assert numDiscreteVals is not None and numDiscreteVals==reducedNumDiscreteVals
        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, reducedNumDiscreteVals=reducedNumDiscreteVals, **kwArgs)

    def _compute(self):
        return arange(self._numDiscreteVals)
    
    def _createChildren(self):
        self._addChild( DiscreteMarksHistStat(self._region, self._track, numDiscreteVals=self._numDiscreteVals) )
        
