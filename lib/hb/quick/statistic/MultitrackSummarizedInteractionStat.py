# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.
from gold.util.CommonFunctions import smartMeanWithNones, smartSum
from gold.util.CustomExceptions import ShouldNotOccurError
from quick.statistic.SummarizedInteractionWithOtherTracksStat import SummarizedInteractionWithOtherTracksStat
from quick.util.debug import DebugUtil
'''
Created on Jun 11, 2015

@author: boris
'''


from numpy import mean
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
    
    def _init(self, multitrackSummaryFunc=None, pairwiseStatistic=None, summaryFunc=None, reverse='No', **kwArgs):
        self._multitrackSummaryFunc = self._resolveFunction(multitrackSummaryFunc)
        
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
                           
                           
                           

