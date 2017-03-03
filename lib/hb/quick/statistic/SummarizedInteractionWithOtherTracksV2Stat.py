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

"""
Created on Nov 3, 2015

@author: boris
"""
from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from quick.statistic.PairedTSStat import PairedTSStat
from quick.statistic.StatisticV2 import StatisticV2
from gold.util.CustomExceptions import ShouldNotOccurError, InvalidStatArgumentError
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.track.TrackStructure import TrackStructureV2
from quick.util.CommonFunctions import minAndMax


class SummarizedInteractionWithOtherTracksV2Stat(MagicStatFactory):
    """
    STAT Q k,n

    Calculate the summary function (min, max, avg, sum) for all the interactions of first track
    in self._tracks with the rest of the tracks. An interaction is defined by the pair-wise statistic
    whose name is passed in as the argument rawStatistic.
    @rawStatistic - str
    @summaryFunc - function
    @reverse - boolean
    """
    pass

#class SummarizedInteractionWithOtherTracksStatSplittable(StatisticSumResSplittable):
#    pass

class SummarizedInteractionWithOtherTracksV2StatUnsplittable(StatisticV2):

    functionDict = {
                    'sum': smartSum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min,
                    'minAndMax': minAndMax,
                    'raw': 'RawResults'
                    }
    
    def _init(self, pairwiseStatistic=None, summaryFunc=None, reverse='No', **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(pairwiseStatistic)
        self._summaryFunction = self._resolveFunction(summaryFunc)
        #self._summaryFunction = self[summaryFunc] #TODO: Should we replace the whole _resolveFunction with this one. Is such an error not clear enough?
        self._reversed = reverse
    
    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) + 
                                      ' not in list, must be one of ' + 
                                      str(sorted(self.functionDict.keys())))
        else: 
            return self.functionDict[summaryFunc]
        
    def _compute(self):
        listOfPairTSs = [child.getResult() for child in self._children]
        fullTs = TrackStructureV2()
        for i,pairTS in enumerate(listOfPairTSs):
            fullTs[str(i)] = pairTS
        #rawResults = [ts.results for ts in listOfPairTSs]
        rawResults = fullTs.result.values()
        if self._summaryFunction == 'RawResults':
            fullTs.result = rawResults
        else:
            fullTs.result = self._summaryFunction(rawResults)
        return fullTs
            
    def _createChildren(self):
        ts = self._trackStructure
        if self._reversed == 'No':
            pairedTS = ts['query'].makePairwiseCombinations(ts['reference'])
        elif self._reversed == 'Yes':
            pairedTS = ts['reference'].makePairwiseCombinations(ts['query'])
        else:
            raise InvalidStatArgumentError('reverse must be one of "Yes" or "No"')

        for pairTSKey in pairedTS:
            self._addChild(PairedTSStat(self._region, pairedTS[pairTSKey], rawStatistic=self._rawStatistic, **self._kwArgs))
