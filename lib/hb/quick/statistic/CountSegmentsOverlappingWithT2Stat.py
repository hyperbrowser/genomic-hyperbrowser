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
from quick.statistic.BpCoveragePerT1SegStat import BpCoveragePerT1SegStat
'''
Created on Feb 15, 2016

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class CountSegmentsOverlappingWithT2Stat(MagicStatFactory):
    '''
    Count the number of segments in track 1 that are covered by at least 1 bp from track 2.
    '''
    pass

#class CountSegmentsOverlappingWithT2StatSplittable(StatisticSumResSplittable):
#    pass
            
class CountSegmentsOverlappingWithT2StatUnsplittable(Statistic):    
    def _compute(self):
        return sum(self._children[0].getResult() > 0)
    
    def _createChildren(self):
        self._addChild(BpCoveragePerT1SegStat(self._region, self._track, self._track2, **self._kwArgs))