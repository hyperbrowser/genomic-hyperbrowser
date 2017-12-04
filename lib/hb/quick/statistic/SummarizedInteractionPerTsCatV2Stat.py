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

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.track.TSResult import TSResult
from gold.util.CustomExceptions import ShouldNotOccurError
from quick.statistic.StatisticV2 import StatisticV2
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from quick.util.CommonFunctions import smartDiff, smartMeanWithNones, minAndMax, minLqMedUqMax


class SummarizedInteractionPerTsCatV2Stat(MagicStatFactory):
    """
    
    """
    pass


#class SummarizedInteractionPerTsCatV2StatSplittable(StatisticSumResSplittable):
#    pass


class SummarizedInteractionPerTsCatV2StatUnsplittable(StatisticV2):


    functionDict = {
                    'diff': smartDiff,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min,
                    'minAndMax': minAndMax,
                    'raw': 'RawResults',
                    'minLqMedUqMax': minLqMedUqMax,
                    }

    def _init(self, segregateNodeKey, catSummaryFunc='raw', selectedCategory=None, **kwArgs):
        self._segregateNodeKey = segregateNodeKey
        self._selectedCategory = selectedCategory
        self._catSummaryFunc = self._resolveFunction(catSummaryFunc)

    def _compute(self):
        tsResult = TSResult(self._trackStructure)

        rawResults = []
        for key, child in self._childrenDict.iteritems():
            childTSR = child.getResult()
            tsResult[key] = childTSR
            rawResults.append(childTSR.getResult())

        if self._catSummaryFunc == 'RawResults':
            tsResult.setResult(rawResults)
        else:
            tsResult.setResult(self._catSummaryFunc(rawResults))
        return tsResult


    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) +
                                      ' not in list, must be one of ' +
                                      str(sorted(self.functionDict.keys())))
        else:
            return self.functionDict[summaryFunc]

    def _createChildren(self):
        reRootedTS = self._trackStructure.makeTreeSegregatedByCategory(self._trackStructure[self._segregateNodeKey])
        self._childrenDict = OrderedDict()
        for cat, catTS in reRootedTS.iteritems():
            self._childrenDict[cat] = self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, **self._kwArgs))