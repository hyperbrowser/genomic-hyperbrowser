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

from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from quick.statistic.StatisticV2 import StatisticV2
from collections import OrderedDict
from gold.statistic.RandomizationManagerStat import RandomizationManagerStat
from gold.util import CommonConstants
from urllib import unquote
'''
Created on Dec 22, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory


class GSuiteSimilarityToQueryTrackRankingsAndPValuesV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteSimilarityToQueryTrackRankingsAndPValuesV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteSimilarityToQueryTrackRankingsAndPValuesV2StatUnsplittable(StatisticV2):    
    
    def _init(self, trackTitles='', **kwArgs):
        assert isinstance(trackTitles, (basestring, list)), 'Mandatory parameter trackTitles is missing or is of wrong type (allowed types: basestring and list)'
        self._trackTitles = [unquote(t) for t in trackTitles.split(CommonConstants.TRACK_TITLES_SEPARATOR)] if \
        isinstance(trackTitles, basestring) else [unquote(t) for t in trackTitles]
     
    def _compute(self):
        resultTuples = []
        observedResults = self._children[0].getResult()
        assert len(observedResults) == len(self._children[1:]), 'Observed results list and MC children list must be of same length'
        for i, chld in enumerate(self._children[1:]):
            chldRes = chld.getResult()
            resultTuples.append((self._trackTitles[i+1], [observedResults[i], chldRes['P-value']]))
         
        return OrderedDict(sorted(resultTuples, key = lambda t: (-t[1][1], t[1][0]), reverse = True))
    
    def _createChildren(self):
        self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, self._trackStructure, summaryFunc='raw', **self._kwArgs))
        t1 = self._trackStructure.getQueryTrackList()[0]
        for t2 in self._trackStructure.getReferenceTrackList():
            self._addChild(RandomizationManagerStat(self._region, t1, t2, **self._kwArgs) )
