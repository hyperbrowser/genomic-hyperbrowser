from gold.track.TSResult import TSResult
from quick.statistic.PairedTSStat import PairedTSStat
from quick.statistic.StatisticV2 import StatisticV2
from gold.util.CustomExceptions import InvalidStatArgumentError
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.util.StatUtils import getFilteredSummaryFunctionDict, resolveSummaryFunctionFromLabel


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

    functionDict = getFilteredSummaryFunctionDict([
                    'sum',
                    'avg',
                    'max',
                    'min',
                    'minAndMax',
                    'raw',
                    'minLqMedUqMax'
                    ])
    
    def _init(self, pairwiseStatistic=None, summaryFunc=None, reverse='No', **kwArgs):
        #NB! Any received parameter termed rawStatistic is ignored, as pairwiseStatistic will take this role in children
        self._pairwiseStatistic = self.getRawStatisticClass(pairwiseStatistic)

        self._summaryFunction = resolveSummaryFunctionFromLabel(summaryFunc, self.functionDict)
        self._reversed = reverse
        self._kwArgs = kwArgs

    def _compute(self):
        resTs = TSResult(self._trackStructure)
        rawResults = []
        for key, child in self._childrenDict.iteritems():
            pairRTS = child.getResult()
            resTs[key] = pairRTS
            rawResults.append(pairRTS.getResult() )

        if self._summaryFunction == 'RawResults':
            resTs.setResult(rawResults)
        else:
            resTs.setResult( self._summaryFunction(rawResults) )
        return resTs
            
    def _createChildren(self):
        ts = self._trackStructure
        if self._reversed == 'No':
            pairedTS = ts['query'].makePairwiseCombinations(ts['reference'])
        elif self._reversed == 'Yes':
            pairedTS = ts['reference'].makePairwiseCombinations(ts['query'])
        else:
            raise InvalidStatArgumentError('reverse must be one of "Yes" or "No"')

        self._childrenDict = {}
        for pairTSKey in pairedTS:
            self._childrenDict[pairTSKey] = self._addChild(PairedTSStat(self._region, pairedTS[pairTSKey], pairedTsRawStatistic=self._pairwiseStatistic, **self._kwArgs))
