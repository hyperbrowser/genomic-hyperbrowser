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
from collections import OrderedDict
'''
Created on Jun 30, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.MultitrackCoverageDepthStat import MultitrackCoverageDepthStat
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable


class MultiTrackBpsCoveragePerDepthLevelStat(MagicStatFactory):
    '''
    Returns an ordered dictionary where the key k is the depth level, 
    and the value is the count of base-pairs that are covered by exactly k tracks times k.
    '''
    pass

class MultiTrackBpsCoveragePerDepthLevelStatSplittable(StatisticDictSumResSplittable):
    pass
            
class MultiTrackBpsCoveragePerDepthLevelStatUnsplittable(Statistic):    
    def _compute(self):
        childRes = self._children[0].getResult()
        res = OrderedDict()
        for depthLevel in xrange(1, len(childRes)):
            res[depthLevel-1] = childRes[depthLevel]*depthLevel
        
        return res
    
    def _createChildren(self):
        self._addChild(MultitrackCoverageDepthStat(self._region, self._track, self._track2, **self._kwArgs))
