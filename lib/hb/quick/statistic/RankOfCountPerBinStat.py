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
from quick.statistic.CountPerBinStat import CountPerBinStat
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable

class RankOfCountPerBinStat(MagicStatFactory):
    "Statistic description"
    pass

class RankOfCountPerBinStatUnsplittable(Statistic):
    def __init__(self, region, track, track2=None, minimal=False, **kwArgs):
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource('userbins', region.genome, minimal)
        super(self.__class__, self).__init__(region, track, track2, minimal=minimal, **kwArgs)
        
    def _compute(self):
        localVal = self._localCount.getResult()[0]
        globalVals = self._allGlobalCounts.getResult()
        
        return [sum(x>localVal for x in globalVals) + 1]
    
    def _createChildren(self):
        self._localCount = self._addChild( CountPerBinStat(self._region, self._track))
        self._allGlobalCounts = self._addChild( CountPerBinStat(self._globalSource, self._track))

from gold.statistic.Statistic import StatisticConcatResSplittable
class RankOfCountPerBinStatSplittable(StatisticConcatResSplittable):
    pass
# 