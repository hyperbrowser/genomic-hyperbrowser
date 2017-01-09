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
from quick.statistic.RankOfCountPerBinStat import RankOfCountPerBinStat

class HotSpotRegionsStat(MagicStatFactory):
    "Statistic description"
    pass

class HotSpotRegionsStatUnsplittable(Statistic):
    def _init(self, numberOfTopHotSpots='', **kwArgs):
        if numberOfTopHotSpots!='':
            self._numberOfTopHotSpots = numberOfTopHotSpots
    
    def _compute(self):
        #numberOfBins = len(list(self._globalSource))   
        return [[str(self._region), self._localCount.getResult()[0]]]
        
#         if (self._localCount.getResult()[0] <= self._numberOfTopHotSpots):
#             return [self._region]
#             #return [self._localCount.getResult()[0], self._numberOfTopHotSpots]
#         else:
#             return []        
        
    
    def _createChildren(self):
        self._localCount = self._addChild( RankOfCountPerBinStat(self._region, self._track))
        #self._allGlobalCounts = self._addChild( RankOfCountPerBinStat(self._globalSource, self._track))

from gold.statistic.Statistic import StatisticConcatResSplittable
class HotSpotRegionsStatSplittable(StatisticConcatResSplittable):
    pass
