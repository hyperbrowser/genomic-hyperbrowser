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
from gold.statistic.RawOverlapStat import RawOverlapStat
'''
Created on Apr 27, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class RatioOfOverlapToUnionStat(MagicStatFactory):
    '''
    STAT T3
     
    For tracks t1 (target track) and t2 (reference track) calculate
    bp(t1 intersection t2)/bp(t1 U t2) where bp is the number of basepairs covered.
    '''
    pass

#class RatioOfOverlapToUnionStatSplittable(StatisticSumResSplittable):
#    pass
            
class RatioOfOverlapToUnionStatUnsplittable(Statistic):    
    def _compute(self):
        only1,only2,both = [ self._children[0].getResult()[key] for key in ['Only1','Only2','Both'] ]
        if only1 + only2 + both == 0:
            return 0.0
        return float(both)/(only1 + only2 + both)
        
    def _createChildren(self):
        self._addChild(RawOverlapStat(self._region, self._track, self._track2))