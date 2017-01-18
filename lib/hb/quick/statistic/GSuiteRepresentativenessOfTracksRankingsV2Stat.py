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
from quick.statistic.MultitrackSummarizedInteractionV2Stat import MultitrackSummarizedInteractionV2Stat
from gold.statistic.MagicStatFactory import MagicStatFactory
from collections import OrderedDict
from gold.util import CommonConstants
from urllib import unquote


class GSuiteRepresentativenessOfTracksRankingsV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteRepresentativenessOfTracksRankingsV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteRepresentativenessOfTracksRankingsV2StatUnsplittable(StatisticV2):
    
    def _init(self, ascending='No', trackTitles='', **kwArgs):
        assert ascending in ['Yes', 'No'], ascending
        self._ascending = ascending == 'Yes'
        assert isinstance(trackTitles, (basestring, list)), 'Mandatory parameter trackTitles is missing or is of wrong type (allowed types: basestring and list)'
        self._trackTitles = [unquote(t) for t in trackTitles.split(CommonConstants.TRACK_TITLES_SEPARATOR)] if \
        isinstance(trackTitles, basestring) else [unquote(t) for t in trackTitles]
    
    def _compute(self):
        resultsList = self._children[0].getResult()
        assert len(resultsList) == len(self._trackTitles), 'One result per track expected.' 
        titleResultPairs = zip(self._trackTitles, resultsList)
        return OrderedDict(sorted(titleResultPairs, key = lambda t: t[1], reverse=(not self._ascending)))
    
    def _createChildren(self):
        self._addChild(MultitrackSummarizedInteractionV2Stat(self._region, self._trackStructure, multitrackSummaryFunc = 'raw', **self._kwArgs))
