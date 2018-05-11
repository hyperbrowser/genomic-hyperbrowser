from collections import OrderedDict

from gold.track.TSResult import TSResult
from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from gold.util.CustomExceptions import ShouldNotOccurError
from numpy import mean
from gold.track.TrackStructure import TrackStructure, TrackStructureV2
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
'''
Created on Nov 9, 2015

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.StatisticV2 import StatisticV2


class MultitrackSummarizedInteractionV2Stat(MagicStatFactory):
    '''
    (TrackStructure version)
    STAT Rk,s,i
    
    R_(k,s,1) (A)=[min]_i (Q_(k,s) [(A]_i,A_(-i))) measures the minimum interaction with the other tracks.
    R_(k,s,2) (A)=[max]_i (Q_(k,s) [(A]_i,A_(-i))) measures the maximum interaction with the other tracks.
    R_(k,s,3) (A)=Sum_i[Q_(k,s) [(A_i,A_(-i))]  measures the average interaction with the other tracks.

    R_(k,s,u) (A) measures how similar is the tracks in the collection A
    '''
    pass

#class MultitrackSummarizedInteractionV2StatSplittable(StatisticSumResSplittable):
#    pass
            
class MultitrackSummarizedInteractionV2StatUnsplittable(StatisticV2):    
    
    functionDict = {
                'sum': smartSum,
                'avg': smartMeanWithNones,
                'max': max,
                'min': min,
                'raw': 'RawResults'
                }
    
    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) + 
                                      ' is not in the list of allowed summary functions, must be one of ' + 
                                      str(sorted(self.functionDict.keys())))
        else: 
            return self.functionDict[summaryFunc]
    
    def _init(self, multitrackSummaryFunc=None, **kwArgs):
        self._multitrackSummaryFunc = self._resolveFunction(multitrackSummaryFunc)
       
    def _compute(self):

        tsResult = TSResult(self._computeTrackStructure)
        rawResults = []
        for key, child in self._childrenDict.iteritems():
            childRes = child.getResult()
            tsResult[key] = childRes
            rawResults.append(childRes.getResult())

        if self._multitrackSummaryFunc:
            if self._multitrackSummaryFunc == 'RawResults':
                tsResult.setResult(rawResults)
            else:
                tsResult.setResult(self._multitrackSummaryFunc(rawResults))
        else:
            raise ShouldNotOccurError('The summary function is not defined')

        return tsResult
    
    def _createChildren(self):
        # trackList = self._trackStructure[TrackStructure.QUERY_KEY]
        # for i, track in enumerate(trackList):
        #     ts = TrackStructure({TrackStructure.QUERY_KEY : [track], TrackStructure.REF_KEY : trackList[:i]+trackList[i+1:]})
#             print ts
#             for key, val in ts.iteritems():
#                 print key
#                 for t in val:
#                     print t.trackName
        self._childrenDict = OrderedDict()
        self._computeTrackStructure = TrackStructureV2()
        tsLeafNodes = self._trackStructure.getLeafNodes()
        for i, sts in enumerate(tsLeafNodes):
            queryTS = sts
            refTS = TrackStructureV2()
            for currentSts in tsLeafNodes[:i] + tsLeafNodes[i+1:]:
                refTS[currentSts.metadata['title']] = currentSts
            currentTS = TrackStructureV2([(TrackStructure.QUERY_KEY, queryTS), (TrackStructure.REF_KEY, refTS)])
            queryTrackTitle = queryTS.metadata['title']
            self._childrenDict[queryTrackTitle] = self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, currentTS, **self._kwArgs))
            self._computeTrackStructure[queryTrackTitle] = currentTS
            
