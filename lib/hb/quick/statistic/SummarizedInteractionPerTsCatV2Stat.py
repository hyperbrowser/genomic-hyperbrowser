from collections import OrderedDict

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.track.TSResult import TSResult
from quick.statistic.StatisticV2 import StatisticV2
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from quick.util.StatUtils import getFilteredSummaryFunctionDict, resolveSummaryFunctionFromLabel


class SummarizedInteractionPerTsCatV2Stat(MagicStatFactory):
    """
    
    """
    pass


#class SummarizedInteractionPerTsCatV2StatSplittable(StatisticSumResSplittable):
#    pass


class SummarizedInteractionPerTsCatV2StatUnsplittable(StatisticV2):


    functionDict = getFilteredSummaryFunctionDict([
                    'diff',
                    'avg',
                    'max',
                    'min',
                    'minAndMax',
                    'raw',
                    'minLqMedUqMax'])

    def _init(self, segregateNodeKey, catSummaryFunc='raw', selectedCategory=None, **kwArgs):
        self._segregateNodeKey = segregateNodeKey
        self._selectedCategory = selectedCategory
        self._catSummaryFunc = resolveSummaryFunctionFromLabel(catSummaryFunc, self.functionDict)

    def _compute(self):
        tsResult = TSResult(self._trackStructure)

        rawResults = []
        for key, child in self._childrenDict.iteritems():
            childTSR = child.getResult()
            tsResult[key] = childTSR
            rawResults.append(childTSR.getResult())

        if self._catSummaryFunc == 'RawResults':
            tsResult.setResult(rawResults)
        else:
            tsResult.setResult(self._catSummaryFunc(rawResults))
        return tsResult

    def _createChildren(self):
        reRootedTS = self._trackStructure.makeTreeSegregatedByCategory(self._trackStructure[self._segregateNodeKey])
        self._childrenDict = OrderedDict()
        for cat, catTS in reRootedTS.iteritems():
            self._childrenDict[cat] = self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, **self._kwArgs))