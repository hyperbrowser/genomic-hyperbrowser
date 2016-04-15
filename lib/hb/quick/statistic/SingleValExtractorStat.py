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


class SingleValExtractorStat(MagicStatFactory):
    pass


class SingleValExtractorStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def _init(self, childClass='', resultKey='',  **kwArgs):
        assert childClass, childClass
        assert resultKey, resultKey
        
        if type(childClass) is str:
            childClass = self.getRawStatisticClass(childClass)
        self._childClass = childClass
        self._resultKey = resultKey
        self._kwArgs = kwArgs
    
    def _createChildren(self):
        self._addChild( self._childClass(self._region, self._track, self._track2, **self._kwArgs) )

    def _compute(self):
        result = self._children[0].getResult()
        return result[self._resultKey]
