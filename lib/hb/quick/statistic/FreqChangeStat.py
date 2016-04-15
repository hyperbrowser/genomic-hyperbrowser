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
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.BinScaledPointCoverageStat import BinScaledPointCoverageStat
from numpy import array
#from gold.application.LogSetup import logMessage
class FreqChangeStat(MagicStatFactory):
    pass

class FreqChangeStatSplittable(StatisticSumResSplittable):
    def _combineResults(self):
        #logMessage(str(self._childResults))
        relevantMins = [x[0] for x in self._childResults]# if x is not None and not any(numpy.isnan(x))]
        relevantMaxs = [x[1] for x in self._childResults]
        if len(relevantMins)==0:
            return []
        else:
            avgMin = array(relevantMins).mean(dtype='float64')
            avgMax = array(relevantMaxs).mean(dtype='float64')
            return [avgMin, avgMax ]
                        
class FreqChangeStatUnsplittable(Statistic):    
    def _compute(self):
        freqs = self._children[0].getResult()
        return [min(freqs), max(freqs)]
    
    def _createChildren(self):
        self._addChild( BinScaledPointCoverageStat(self._region, self._track, numSubBins=2))
