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
from gold.util.CommonFunctions import smartMeanWithNones
from quick.statistic.StatisticV2 import StatisticV2
from gold.track.TrackStructure import TrackStructure
from quick.util.debug import DebugUtil
from quick.statistic.RawDBGCodedEventsStat import RawDBGCodedEventsStat
import numpy as np
from _collections import defaultdict
from quick.statistic.BinSizeStat import BinSizeStat
from gold.track.Track import Track
'''
Created on Nov 3, 2015

@author: boris
'''


from gold.util.CustomExceptions import ShouldNotOccurError
from numpy import mean
from gold.statistic.MagicStatFactory import MagicStatFactory


class MultitrackRawSingleBinV2Stat(MagicStatFactory):
    '''
    '''
    pass

#class SummarizedInteractionWithOtherTracksStatSplittable(StatisticSumResSplittable):
#    pass
            
class MultitrackRawSingleBinV2StatUnsplittable(StatisticV2):
    

    functionDict = {
                    'sum': sum,
                    'avg': smartMeanWithNones,
                    'max': max,
                    'min': min
                    }

    
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
        
        self._summaryFunction = self._resolveFunction(summaryFunc)
        self._statistic = statFuncDict[question]
    
    def _resolveFunction(self, summaryFunc):
        if summaryFunc not in self.functionDict:
            raise ShouldNotOccurError(str(summaryFunc) + 
                                      ' not in list, must be one of ' + 
                                      str(sorted(self.functionDict.keys())))
        else: 
            return self.functionDict[summaryFunc]
        
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
