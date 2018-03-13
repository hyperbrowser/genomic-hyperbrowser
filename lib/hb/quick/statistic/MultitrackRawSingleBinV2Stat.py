from quick.statistic.StatisticV2 import StatisticV2
from quick.util.StatUtils import getFilteredSummaryFunctionDict, resolveSummaryFunctionFromLabel
from quick.statistic.RawDBGCodedEventsStat import RawDBGCodedEventsStat
import numpy as np
from gold.statistic.MagicStatFactory import MagicStatFactory


class MultitrackRawSingleBinV2Stat(MagicStatFactory):
    '''
    '''
    pass

#class SummarizedInteractionWithOtherTracksStatSplittable(StatisticSumResSplittable):
#    pass

class MultitrackRawSingleBinV2StatUnsplittable(StatisticV2):


    functionDict = getFilteredSummaryFunctionDict([
                    'sum',
                    'avg',
                    'max',
                    'min'])

    def question6stat(self, O,E):
        if not E>0:
            T = 0
        else:
            T = np.sum(np.power((O-E),2)/E);
        return T

    def question7stat(self,O,E):
        if E==0:
            return 0
        T = np.max(O)/E
        return T

    def _init(self, question="question 6", summaryFunc=None, reverse='No', **kwArgs):

        statFuncDict = {
            'question 6':self.question6stat,
            'question 7':self.question7stat,
            }

        self._summaryFunction = resolveSummaryFunctionFromLabel(summaryFunc, self.functionDict)
        self._statistic = statFuncDict[question]

    def _compute(self):
        O,E = self._children[0].getResult()
        return [self._statistic(O,E)]
#        return res
            
            
    def _createChildren(self):
        tracks = self._trackStructure.getQueryTrackList()
        t1 = tracks[0]
        t2 = tracks[1]
        self._addChild(RawDBGCodedEventsStat(self._region, t1, t2, extraTracks = tuple(tracks[2:]), **self._kwArgs))

#        self._binSizeStat = self._addChild( BinSizeStat(self._region, t1))
