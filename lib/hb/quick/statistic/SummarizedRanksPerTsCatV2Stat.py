from collections import OrderedDict

from gold.track.TSResult import TSResult
from quick.statistic.RanksPerTsCatV2Stat import RanksPerTsCatV2Stat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.util.StatUtils import getFilteredSummaryFunctionDict, resolveSummaryFunctionFromLabel


class SummarizedRanksPerTsCatV2Stat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class SummarizedRanksPerTsCatV2StatSplittable(StatisticSumResSplittable):
#    pass

class SummarizedRanksPerTsCatV2StatUnsplittable(StatisticV2):

    functionDict = getFilteredSummaryFunctionDict([
                    'avg',
                    'max',
                    'min',
                    'sum',
                    'raw',
                    ])

    def _init(self, rankSummaryFunc, **kwArgs):
        self._summaryFunction = resolveSummaryFunctionFromLabel(rankSummaryFunc, self.functionDict)
        self._kwArgs = kwArgs

    def _compute(self):
        tsResult = TSResult(self._trackStructure)

        sumResults = OrderedDict()
        for catLbl, catRes in self._children[0].getResult().getResult().iteritems():
            sumResults[catLbl] = self._summaryFunction(catRes)
        assert len(sumResults) == 2, "Must have exactly two categories"
        tsResult.setResult(sumResults)
        return tsResult

    def _createChildren(self):
        self._addChild(RanksPerTsCatV2Stat(self._region, self._trackStructure,
                                           **self._kwArgs))
