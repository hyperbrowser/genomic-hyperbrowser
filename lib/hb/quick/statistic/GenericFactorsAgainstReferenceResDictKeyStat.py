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

class GenericFactorsAgainstReferenceResDictKeyStat(MagicStatFactory):
    pass

#class GenericFactorsAgainstReferenceResDictKeyStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericFactorsAgainstReferenceResDictKeyStatUnsplittable(Statistic):    
    def _init(self, rawStatistic=None, referenceResDictKey='Result', **kwArgs):
        self._referenceResDictKey = referenceResDictKey
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        
    def _compute(self):
        rawNumbers = self._children[0].getResult()
        referenceNumber = float(rawNumbers[self._referenceResDictKey])
        return dict([(key,val/referenceNumber) for key,val in rawNumbers.items()])
    
    def _createChildren(self):
        self._addChild( self._rawStatistic(self._region, self._track, self._track2, **self._kwArgs))
