from collections import OrderedDict

from gold.track.TSResult import TSResult
from gold.util.CustomExceptions import ShouldNotOccurError
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from quick.util.CommonFunctions import smartMeanWithNones, smartDiff, minAndMax, minLqMedUqMax


class SummarizedQueryTrackVsCategoricalGSuiteForSelectedCategoryV2Stat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class SummarizedQueryTrackVsCategoricalGSuiteForSelectedCategoryV2StatSplittable(StatisticSumResSplittable):
#    pass

class SummarizedQueryTrackVsCategoricalGSuiteForSelectedCategoryV2StatUnsplittable(StatisticV2):


    functionDict = {
                    'diff': smartDiff,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min,
                    'minAndMax': minAndMax,
                    'raw': 'RawResults',
                    'minLqMedUqMax': minLqMedUqMax,
                    }

    def _init(self, selectedCategory, catSummaryFunc, **kwArgs):
        self._selectedCategory = selectedCategory
        self._kwArgs = kwArgs
        self._summaryFunction = self._resolveFunction(catSummaryFunc)

    def _compute(self):
        tsResult = TSResult(self._trackStructure)

        rawResults = []
        for key, child in self._childrenDict.iteritems():
            childTSR = child.getResult()
            tsResult[key] = childTSR
            rawResults.append(childTSR.getResult() )

        if self._summaryFunction == 'RawResults':
            tsResult.setResult(rawResults)
        else:
            tsResult.setResult( self._summaryFunction(rawResults) )
        return tsResult


    def _createChildren(self):
        self._childrenDict = OrderedDict()
        for cat, catTS in self._trackStructure.iteritems():
            # if cat == self._selectedCategory:
            self._childrenDict[cat] = self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, **self._kwArgs))

    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) +
                                      ' not in list, must be one of ' +
                                      str(sorted(self.functionDict.keys())))
        else:
            return self.functionDict[summaryFunc]