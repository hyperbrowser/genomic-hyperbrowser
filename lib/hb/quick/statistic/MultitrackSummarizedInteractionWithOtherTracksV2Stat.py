from collections import OrderedDict

from gold.track.TSResult import TSResult
from gold.track.TrackStructure import TrackStructureV2
from quick.statistic.StatisticV2 import StatisticV2
from quick.util.StatUtils import getFilteredSummaryFunctionDict, resolveSummaryFunctionFromLabel
from gold.statistic.MagicStatFactory import MagicStatFactory


class MultitrackSummarizedInteractionWithOtherTracksV2Stat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class MultitrackSummarizedInteractionWithOtherTracksV2StatSplittable(StatisticSumResSplittable):
#    pass

class MultitrackSummarizedInteractionWithOtherTracksV2StatUnsplittable(StatisticV2):

    functionDict = getFilteredSummaryFunctionDict([
                # 'diff',
                'avg',
                'max',
                'min',
                'minAndMax',
                'raw',
                'minLqMedUqMax'])

    def _init(self, multitrackRawStatistic, multitrackSummaryFunc=None, **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(multitrackRawStatistic)
        self._multitrackSummaryFunc = resolveSummaryFunctionFromLabel(multitrackSummaryFunc, self.functionDict)

    def _compute(self):
        tsResult = TSResult(self._trackStructure)

        rawResults = []
        for key, child in self._childrenDict.iteritems():
            childTSR = child.getResult()
            tsResult[key] = childTSR
            rawResults.append(childTSR.getResult())

        if self._multitrackSummaryFunc == 'RawResults':
            tsResult.setResult(rawResults)
        else:
            tsResult.setResult(self._multitrackSummaryFunc(rawResults))
        return tsResult

    def _createChildren(self):
        reRootedTS = self._trackStructure.makeTreeSegregatedByCategory(self._trackStructure[TrackStructureV2.QUERY_KEY])
        self._childrenDict = OrderedDict()
        for key, childTS in reRootedTS.items():
            self._childrenDict[key] = self._addChild(self._rawStatistic(self._region, childTS, **self._kwArgs))


