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
from gold.statistic.Statistic import RatioDictSingleDenomStatUnsplittable
from quick.statistic.BinSizeStat import BinSizeStat

class GenericProportionalToBinSizeStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericProportionalToBinSizeStatUnsplittable(RatioDictSingleDenomStatUnsplittable):        
    #def _compute(self):
    #    pass
    
    def _createChildren(self):
        rawStat = self.getRawStatisticClass( self._kwArgs['rawStatistic'] )
        self._addChild( rawStat(self._region, self._track, self._track2 if hasattr(self, '_track2') else None, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
