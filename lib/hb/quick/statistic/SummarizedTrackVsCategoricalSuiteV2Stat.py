from gold.track.TSResult import TSResult
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class SummarizedTrackVsCategoricalSuiteV2Stat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class SummarizedTrackVsCategoricalSuiteV2StatSplittable(StatisticSumResSplittable):
#    pass

class SummarizedTrackVsCategoricalSuiteV2StatUnsplittable(StatisticV2):

    def _compute(self):
        tsResult = TSResult(self._trackStructure)
        for cat, catTS in self._catResults.iteritems():
            tsResult[cat] = catTS.getResult()
        return tsResult


    def _createChildren(self):
        self._catResults = {}
        for cat, catTS in self._trackStructure.iteritems():
            self._catResults[cat] = self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, **self._kwArgs))
