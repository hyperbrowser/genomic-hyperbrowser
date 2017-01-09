# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope tha it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2, StatisticV2Splittable

class GenericMaxBinValueStat(MagicStatFactory):
    "takes as parameter another statistic class, gets results for this per bin, then at the global level returns the max of values per bin"
    pass

class GenericMaxBinValueStatSplittable(StatisticV2Splittable):
    def _combineResults(self):
        self._result = max(self._childResults)

    
class GenericMaxBinValueStatUnsplittable(StatisticV2):
    def _init(self, perBinStatistic, **kwArgs):
        self._perBinStatistic = self.getRawStatisticClass(perBinStatistic)
    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild( self._perBinStatistic(self._region, self._trackStructure, **self._kwArgs) )

#from gold.statistic.Statistic import StatisticSumResSplittable
#class StatisticTemplateStatSplittable(StatisticSumResSplittable):
#   pass
