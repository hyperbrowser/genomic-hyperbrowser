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
from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from quick.statistic.StatisticV2 import StatisticV2
from gold.util.CustomExceptions import ShouldNotOccurError
from gold.statistic.MagicStatFactory import MagicStatFactory


class SummarizedStat(MagicStatFactory):
    '''
    STAT Q k,n
    Calculate the summary function (min, max, avg, sum) for all the interactions of first track
    in self._tracks with the rest of the tracks. An interaction is defined by the pair-wise statistic
    whose name is passed in as the argument rawStatistic.
    @rawStatistic - str
    @summaryFunc - function
    @reverse - boolean
    '''
    pass


class SummarizedStatUnsplittable(StatisticV2):

    functionDict = {
                    'sum': smartSum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min,
                    'raw': 'RawResults'
                    }

    def _init(self, pairwiseStatistic=None, summaryFunc=None,
              reverse='No', **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(pairwiseStatistic)
        self._summaryFunction = self._resolveFunction(summaryFunc)
        assert reverse in ['Yes', 'No'], 'reverse must be one of "Yes" or "No"'
        self._reversed = reverse

    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) +
                                      ' not in list, must be one of ' +
                                      str(sorted(self.functionDict.keys())))
        else:
            return self.functionDict[summaryFunc]

    def _compute(self):
        if self._summaryFunction:
            if self._summaryFunction == 'RawResults':
                return [child.getResult() for child in self._children]
            else:
                return self._summaryFunction([child.getResult()
                                              for child in self._children])
        else:
            raise ShouldNotOccurError('The summary function is not defined. Must be one of %' % str(sorted(self.functionDict.keys())))
            #we could return the list of results to make it more generic
            #but we should add this only if needed in the future

    def _createChildren(self):
        for t1 in self._trackStructure.getQueryTrackList():
            self._addChild(self._rawStatistic(self._region,
                                              t1, **self._kwArgs))
