from gold.track.TSResult import TSResult
from quick.statistic.RanksPerTsCatV2Stat import RanksPerTsCatV2Stat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class DiffOfSummarizedRanksPerTsCatV2Stat(MagicStatFactory):
    """
    Get difference of summarized (currently average) ranks for a 2-category track structure.
    """
    pass


#class DiffOfSummarizedRanksPerTsCatV2StatSplittable(StatisticSumResSplittable):
#    pass

class DiffOfSummarizedRanksPerTsCatV2StatUnsplittable(StatisticV2):

    def _init(self, selectedCategory, **kwArgs):
        self._selectedCategory = selectedCategory
        self._kwArgs = kwArgs

    def _compute(self):
        import numpy as np
        tsResult = TSResult(self._trackStructure)

        rawResultsDict = {}
        for catLbl, catRes in self._children[0].getResult().getResult().iteritems():
            rawResultsDict[catLbl] = catRes
        assert len(rawResultsDict) == 2, "Must have exactly two categories"
        assert self._selectedCategory is not None, 'Must select a primary category'
        res1 = [0]
        res2 = [0]
        for key, res in rawResultsDict.iteritems():
            if key == self._selectedCategory:
                res1 = res
            else:
                res2 = res
        tsResult.setResult(np.array(res1).mean() - np.array(res2).mean())
        return tsResult

    def _createChildren(self):
        self._addChild(RanksPerTsCatV2Stat(self._region, self._trackStructure,
                                           selectedCategory=self._selectedCategory,
                                           **self._kwArgs))
