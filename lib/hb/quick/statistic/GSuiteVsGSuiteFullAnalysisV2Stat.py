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
Created on Feb 29, 2016

@author: boris
'''

from collections import OrderedDict

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.GenericGSuiteVsGSuiteV2Stat import GenericGSuiteVsGSuiteV2Stat
from quick.statistic.SingleValueOverlapStat import SingleValueOverlapStat
from quick.statistic.StatisticV2 import StatisticV2

RAW_OVERLAP_TABLE_RESULT_KEY = 'Raw_overlap_table'
SIMILARITY_SCORE_TABLE_RESULT_KEY = 'Similarity_score_table'

class GSuiteVsGSuiteFullAnalysisV2Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class GSuiteVsGSuiteFullAnalysisV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class GSuiteVsGSuiteFullAnalysisV2StatUnsplittable(StatisticV2):
    
    def _init(self, similarityStatClassName=None, **kwArgs):
        self._similarityStatClassName = similarityStatClassName

    def _compute(self):
        res = OrderedDict()
        res[RAW_OVERLAP_TABLE_RESULT_KEY] = self._rawOverlapTable.getResult()
        res[SIMILARITY_SCORE_TABLE_RESULT_KEY] = self._similarityScoreTable.getResult()
        return res
    
    def _createChildren(self):
        self._rawOverlapTable = self._addChild(GenericGSuiteVsGSuiteV2Stat(self._region, self._trackStructure, pairwiseStatistic = SingleValueOverlapStat, **self._kwArgs))
        self._similarityScoreTable = self._addChild(GenericGSuiteVsGSuiteV2Stat(self._region, self._trackStructure, pairwiseStatistic = self._similarityStatClassName, **self._kwArgs))