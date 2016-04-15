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

class XYPairStat(MagicStatFactory):
    pass

class XYPairStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, statClass1=None, statClass2=None, **kwArgs):
        self._statClass1 = statClass1
        self._statClass2 = statClass2                
        Statistic.__init__(self, region, track, track2, statClass1=statClass1, statClass2=statClass2, **kwArgs)
    
    def _createChildren(self): 
        self._addChild( self._statClass1(self._region, self._track, **self._kwArgs) )
        self._addChild( self._statClass2(self._region, self._track2, **self._kwArgs) )
    
    def _compute(self):
        return [self._children[0].getResult(), self._children[1].getResult()]
    
