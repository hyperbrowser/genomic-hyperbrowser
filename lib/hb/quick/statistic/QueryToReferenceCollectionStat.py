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
from quick.statistic.StatisticV2 import StatisticV2
'''
Created on Sep 23, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory


class QueryToReferenceCollectionStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class QueryToReferenceCollectionStatSplittable(StatisticSumResSplittable):
#    pass
            
class QueryToReferenceCollectionStatUnsplittable(StatisticV2):    
    
    def _init(self, pairwiseStat = None, **kwArgs):
        self._pairwiseStat = self.getRawStatisticClass(pairwiseStat)
    
    def _compute(self):
        for child in self._children:
            print child.getResult()
            print '_________'
    
    def _createChildren(self):
        queryTrack = self._trackStructure.getQueryTrackList()[0]
        for refTrack in self._trackStructure.getReferenceTrackList():
            self._addChild(self._pairwiseStat(self._region, queryTrack, refTrack, **self._kwArgs))