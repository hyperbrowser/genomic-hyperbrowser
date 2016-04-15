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
'''
Created on Nov 3, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.RandomizationManagerV3Stat import RandomizationManagerV3Stat
from quick.statistic.StatisticV2 import StatisticV2


class CollectionBinnedHypothesisV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class TrackSimilarityToCollectionHypothesisV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class CollectionBinnedHypothesisV2StatUnsplittable(StatisticV2):    
    def _compute(self):
        res = self._children[0].getResult()
        return res
    
    def _createChildren(self):
        self._addChild(RandomizationManagerV3Stat(self._region, self._trackStructure, **self._kwArgs))
