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

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.util.CustomExceptions import ShouldNotOccurError

class ResultPerTrackCombinerStat(MagicStatFactory):
    pass

#class ResultPerTrackCombinerStatSplittable(StatisticSumResSplittable):
#    pass
            
class ResultPerTrackCombinerStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, rawStatisticTrack1=None, rawStatisticTrack2=None, combineOperation=None, **kwArgs):
        #Note: Could take parameter track1kwArgs which could be a dict to be sent further as kwArgs to rawStatisticTrack1, and correspondingly for track2

        #assert combineOperation in ['product']
        self._combineOperation = combineOperation
        
        Statistic.__init__(self, region, track, track2, rawStatisticTrack1=rawStatisticTrack1, rawStatisticTrack2=rawStatisticTrack2, combineOperation=combineOperation, **kwArgs)
        
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        if type(rawStatisticTrack1) is str:            
            rawStatisticTrack1 = STAT_CLASS_DICT[rawStatisticTrack1]
        if type(rawStatisticTrack2) is str:            
            rawStatisticTrack2 = STAT_CLASS_DICT[rawStatisticTrack2]
     
        self._rawStatisticTrack1 = rawStatisticTrack1
        self._rawStatisticTrack2 = rawStatisticTrack2

    from gold.util.CommonFunctions import repackageException
    @repackageException(Exception, ShouldNotOccurError)        
    def _compute(self):
        #x,y = self._children[0], self._children[1]
        x,y = self._children[0].getResult(), self._children[1].getResult()
        if self._combineOperation == 'product':
            return x*y
        elif self._combineOperation == 'concatenate':
            return {'t1':x, 't2':y}
        else:            
            raise ShouldNotOccurError
            
    
    def _createChildren(self):
        self._addChild( self._rawStatisticTrack1(self._region, self._track) )
        self._addChild( self._rawStatisticTrack2(self._region, self._track2) )
