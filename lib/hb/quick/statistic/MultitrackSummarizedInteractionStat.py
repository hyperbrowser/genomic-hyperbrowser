from gold.util.CustomExceptions import ShouldNotOccurError
from quick.statistic.SummarizedInteractionWithOtherTracksStat import SummarizedInteractionWithOtherTracksStat
from quick.util.StatUtils import getFilteredSummaryFunctionDict, resolveSummaryFunctionFromLabel
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic


class MultitrackSummarizedInteractionStat(MagicStatFactory):
    '''
    STAT Rk,s,i
    
    R_(k,s,1) (A)=[min]_i (Q_(k,s) [(A]_i,A_(-i))) measures the minimum interaction with the other tracks.
    R_(k,s,2) (A)=[max]_i (Q_(k,s) [(A]_i,A_(-i))) measures the maximum interaction with the other tracks.
    R_(k,s,3) (A)=Sum_i[Q_(k,s) [(A_i,A_(-i))]  measures the average interaction with the other tracks.

    R_(k,s,u) (A) measures how similar is the tracks in the collection A
    '''
    pass

#class MultitrackSummarizedInteractionStatSplittable(StatisticSumResSplittable):
#    pass
            
class MultitrackSummarizedInteractionStatUnsplittable(MultipleTrackStatistic):
    
    functionDict = getFilteredSummaryFunctionDict([
                'sum',
                'avg',
                'max',
                'min',
                'raw'])

    def _init(self, multitrackSummaryFunc=None, pairwiseStatistic=None, summaryFunc=None, reverse='No', **kwArgs):
        self._multitrackSummaryFunc = resolveSummaryFunctionFromLabel(multitrackSummaryFunc, self.functionDict)
        
    def _compute(self):
        if self._multitrackSummaryFunc:
            if self._multitrackSummaryFunc == 'RawResults':
                return [child.getResult() for child in self._children]
            else:
                return self._multitrackSummaryFunc([child.getResult() for child in self._children])
        else:
            raise ShouldNotOccurError('The summary function is not defined')
    
    def _createChildren(self):
        for i in range(len(self._tracks)):
            firstTrack = self._tracks[i]
            restTracks = self._tracks[:i] + self._tracks[(i+1):]
            #TODO: is this a good solution?
            if 'extraTracks' in self._kwArgs:
                del self._kwArgs['extraTracks']
            newExtraTracksStr = '&'.join(['^'.join(tn.trackName) for tn in restTracks[1:]])
            self._addChild(SummarizedInteractionWithOtherTracksStat(self._region, firstTrack, restTracks[0], extraTracks=newExtraTracksStr,
                                                                    **self._kwArgs))
                           
                           
                           

