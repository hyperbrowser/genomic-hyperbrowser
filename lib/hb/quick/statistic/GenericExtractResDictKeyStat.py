#See SingleValExtractorStat..
# GenericExtractResDictKeyStat is a better name, so code should be merged and name changed to start with generic..

## Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
## This file is part of The Genomic HyperBrowser.
##
##    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    The Genomic HyperBrowser is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.
#
#from gold.statistic.MagicStatFactory import MagicStatFactory
#from gold.statistic.Statistic import Statistic
#import re
#
#class GenericExtractResDictKeyStat(MagicStatFactory):
#    pass
#
##class GenericExtractResDictKeyStatSplittable(StatisticSumResSplittable):
##    pass
#            
#class GenericExtractResDictKeyStatUnsplittable(Statistic):
#    def _init(self, rawStatistic=None, resDictKey=None, **kwArgs):
#        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
#        self._resDictKey = resDictKey
#        
#    def _compute(self):
#        resDict = self._children[0].getResult()
#        return resDict.get(self._resDictKey) if (resDict is not None and resDict is not None) else None
#            
#    
#    def _createChildren(self):
#        self._addChild( self._rawStatistic(self._region, self._track, **self._kwArgs) )
