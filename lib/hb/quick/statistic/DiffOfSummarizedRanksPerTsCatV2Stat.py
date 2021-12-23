from collections import OrderedDict

from gold.track.TSResult import TSResult
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.SummarizedRanksPerTsCatV2Stat import SummarizedRanksPerTsCatV2Stat


class DiffOfSummarizedRanksPerTsCatV2Stat(MagicStatFactory):
    """
    Get difference of summarized (currently average) ranks for a 2-category track structure.
    """
    pass


#class DiffOfSummarizedRanksPerTsCatV2StatSplittable(StatisticSumResSplittable):
#    pass

class DiffOfSummarizedRanksPerTsCatV2StatUnsplittable(StatisticV2):

    def _init(self, selectedCategory, segregateNodeKey, **kwArgs):
        self._segregateNodeKey = segregateNodeKey
        self._selectedCategory = selectedCategory
        self._kwArgs = kwArgs

    def _compute(self):
        tsResult = TSResult(self._trackStructure)

        rawResultsDict = OrderedDict()
        for catLbl, catRes in self._children[0].getResult().getResult().iteritems():
            rawResultsDict[catLbl] = catRes
        reRootedTS = self._trackStructure.makeTreeSegregatedByCategory(self._trackStructure[self._segregateNodeKey])
        assert len(rawResultsDict) == 2, "Must have exactly two categories"
        assert self._selectedCategory is not None, 'Must select a primary category'
        res1 = [0]
        res2 = [0]
        for key, res in rawResultsDict.iteritems():
            if key == self._selectedCategory:
                res1 = res

            else:
                res2 = res
            tsResult[key] = TSResult(reRootedTS[key], res)
        tsResult.setResult(res1 - res2)
        return tsResult


    def _createChildren(self):
        self._addChild(SummarizedRanksPerTsCatV2Stat(self._region, self._trackStructure,
                                                     selectedCategory=self._selectedCategory,
                                                     segregateNodeKey = self._segregateNodeKey,
                                                     rankSummaryFunc='avg',
                                                     **self._kwArgs))
