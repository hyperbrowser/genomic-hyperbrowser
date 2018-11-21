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
                    'sum',
                    'minAndMax',
                    'raw',
                    'minLqMedUqMax'
                    ])

    def _init(self, segregateNodeKey, catSummaryFunc='raw', selectedCategory=None, **kwArgs):
        self._segregateNodeKey = segregateNodeKey
        self._selectedCategory = selectedCategory
        self._catSummaryFuncName = catSummaryFunc
        self._catSummaryFunc = resolveSummaryFunctionFromLabel(catSummaryFunc, self.functionDict)

    def _compute(self):
        tsResult = TSResult(self._trackStructure)

        rawResults = []
        rawResultsDict = {}
        for key, child in self._childrenDict.iteritems():
            childTSR = child.getResult()
            tsResult[key] = childTSR
            rawResults.append(childTSR.getResult())
            print(" Child raw result:")
            print(childTSR.getResult())

            rawResultsDict[key] = childTSR.getResult()
        print("tmp1: %s" % self._catSummaryFunc)
        print("tmp2: %s" % self._kwArgs["summaryFunc"])
        print("Raw results: " + str(rawResults))


        if self._catSummaryFunc == 'RawResults':
            tsResult.setResult(rawResults)
        elif self._catSummaryFuncName == 'diff':
            assert len(rawResults) == 2, "Must have exactly two categories for the diff summary function"
            assert self._selectedCategory is not None, 'Must select a primary category for the diff summary function'
            res1 = 0
            res2 = 0
            for key, res in rawResultsDict.iteritems():
                if key == self._selectedCategory:
                    # print('res1=', key)
                    res1 = res
                else:
                    # print('res2=', key)
                    res2 = res
                tsResult.setResult(res1 - res2)
        else:
            tsResult.setResult(self._catSummaryFunc(rawResults))
        return tsResult

    def _createChildren(self):
        reRootedTS = self._trackStructure.makeTreeSegregatedByCategory(self._trackStructure[self._segregateNodeKey])
        self._childrenDict = OrderedDict()
        for cat, catTS in reRootedTS.iteritems():
            self._childrenDict[cat] = self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, **self._kwArgs))