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
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import AutonomousTrackElement

class SimilarSegmentStat(MagicStatFactory):
    pass

#class SimilarSegmentStatSplittable(StatisticSumResSplittable):
#    pass
            
class SimilarSegmentStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, maxRelDifference=0, maxAbsDifference=0, **kwArgs):
        self._maxRelDifference = float(maxRelDifference)
        self._maxAbsDifference = int(maxAbsDifference)
        assert( 0 <= self._maxRelDifference <= 1 )
        assert( 0 <= self._maxAbsDifference )
        
        Statistic.__init__(self, region, track, track2, maxRelDifference=maxRelDifference, \
                           maxAbsDifference=maxAbsDifference, **kwArgs)
    
    def _compute(self):
        similarCount = 0
        s2Iter = self._children[1].getResult().__iter__()
        s2Exhausted = False
        s2List = []

        #Intuition behind algorithm:
        #For each track1-segment, incrementally update a window of track2-candidates that may be similar
        #For a next track1-segment, add the next track2-elements to the candidate window until the last candidate segment occurs completely after the track1-element.
        #Then pop first element of candidate window as long as this element is completely before current track2-element.
        #Pairwise compare the track1-element against all track2-candidates in window, counting any similarity above threshold
        
        try:
            s2Cur = s2Iter.next()
        except StopIteration:
            return 0
        
        for s1 in self._children[0].getResult():
            s1 = AutonomousTrackElement(trackEl=s1)
            
            firstKeepIndex = 0
            for i,s2Existing in enumerate(s2List):
                if s2Existing.end() <= s1.start():
                    firstKeepIndex = i+1
                else:
                    break
            s2List = s2List[firstKeepIndex:]
                
            while not s2Exhausted and s2Cur.start() < s1.end():
                if s2Cur.end() > s1.start():
                    s2List.append( AutonomousTrackElement(trackEl=s2Cur) )
                try:
                    s2Cur = s2Iter.next()
                except StopIteration:
                    s2Exhausted = True
                    break
                
            for s2Candidate in s2List:
                if self._similar(s1, s2Candidate):
                    similarCount += 1
        
        return similarCount
    
    def _similar(self, s1, s2):
        absDifference = abs(s1.start()-s2.start()) + abs(s1.end()-s2.end()) 
        unionLen = max(s1.end(), s2.end()) - min(s1.start(), s2.start())
        relSimilarities = (1.0*len(s1)/unionLen, 1.0*len(s2)/unionLen )
        relDifference = max( 1.0-similarity for similarity in relSimilarities)
        return absDifference <= self._maxAbsDifference and relDifference <= self._maxRelDifference
    
    def _createChildren(self):
        #the settings of allowOverlaps is somewhat arbitrary for now..
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True, allowOverlaps=False)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True, allowOverlaps=False)) )