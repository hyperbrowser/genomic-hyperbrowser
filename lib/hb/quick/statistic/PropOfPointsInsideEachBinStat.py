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
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.PropOfSegmentsInsideEachBinStat import PropOfSegmentsInsideEachBinStatUnsplittable

class PropOfPointsInsideEachBinStat(MagicStatFactory):
    "For each bin, return the proportion of all points that falls within that specific bin. "
    "This means that if the bins cover the whole genome, the results across all bins will sum to one"
    
class PropOfPointsInsideEachBinStatUnsplittable(PropOfSegmentsInsideEachBinStatUnsplittable):    
    def _createChildren(self):
        globCount1 = CountPointStat(self._globalSource , self._track)
        binCount1 = CountPointStat(self._region, self._track)

        self._addChild(globCount1)
        self._addChild(binCount1)            
