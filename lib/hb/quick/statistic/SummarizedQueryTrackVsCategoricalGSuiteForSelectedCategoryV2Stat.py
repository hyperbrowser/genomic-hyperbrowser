from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat


class SummarizedQueryTrackVsCategoricalGSuiteForSelectedCategoryV2Stat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class SummarizedQueryTrackVsCategoricalGSuiteForSelectedCategoryV2StatSplittable(StatisticSumResSplittable):
#    pass

class SummarizedQueryTrackVsCategoricalGSuiteForSelectedCategoryV2StatUnsplittable(StatisticV2):

    def _init(self, selectedCategory, **kwArgs):
        self._selectedCategory = selectedCategory
        self._kwArgs = kwArgs

    def _compute(self):
        ts = self._trackStructure._copyTreeStructure()
        ts.result = self._children[0].getResult().result
        return ts


    def _createChildren(self):
        for cat, catTS in self._trackStructure.iteritems():
            if cat == self._selectedCategory:
                self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, **self._kwArgs))
