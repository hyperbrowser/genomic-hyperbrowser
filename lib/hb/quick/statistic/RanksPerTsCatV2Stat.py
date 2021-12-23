from collections import defaultdict

from gold.track.TSResult import TSResult
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat


class RanksPerTsCatV2Stat(MagicStatFactory):
    """
    For each category in the categorical track structure, calculate the overall ranks.
    Ties are handled as in a Wilcoxon test (see https://www.stat.auckland.ac.nz/~wild/ChanceEnc/Ch10.wilcoxon.pdf)
    """
    pass


#class RanksPerTsCatV2StatSplittable(StatisticSumResSplittable):
#    pass

class RanksPerTsCatV2StatUnsplittable(StatisticV2):

    def _compute(self):
        import numpy as np
        tsResult = TSResult(self._trackStructure)
        childTsResult = self._children[0].getResult()
        rawResults = []
        sumResults = defaultdict(list)
        for catLbl, catTsResult in childTsResult.iteritems():
            rawResults.extend([(x.getResult(), catLbl) for x in catTsResult.values()])
            sumResults[catLbl] = []
        sortedRawResults = sorted(rawResults, reverse=False)
        cursor1 = 0
        while cursor1 < len(sortedRawResults):
            currentRanks = [cursor1 + 1]
            cursor2 = cursor1 + 1
            while cursor2 < len(sortedRawResults) and sortedRawResults[cursor1][0] == sortedRawResults[cursor2][0]:
                cursor2 += 1
                currentRanks.append(cursor2)
            currentRank = np.array(currentRanks).mean()
            for currentCursor in range(cursor1, cursor2):
                currentRes = sortedRawResults[currentCursor]
                sumResults[currentRes[1]].append(currentRank)
            cursor1 = cursor2

        tsResult.setResult(sumResults)
        return tsResult

    def _createChildren(self):
        self._addChild(SummarizedInteractionPerTsCatV2Stat(self._region, self._trackStructure,
                                                           catSummaryFunc='raw',
                                                           summaryFunc='raw',
                                                           **self._kwArgs))
