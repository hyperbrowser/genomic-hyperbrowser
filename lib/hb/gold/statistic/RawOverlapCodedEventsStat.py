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
from gold.track.TrackFormat import TrackFormatReq
'''
Created on Jun 18, 2015

@author: boris
'''


from numpy import concatenate, add
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleRawDataStatistic


class RawOverlapCodedEventsStat(MagicStatFactory):
    '''
    Encode start and end events for multiple tracks. Needed to calculate the raw overlap for all combinations of a set of tracks.
    Because of the encoding it is limited to 33 tracks.
    '''
    pass

#class RawOverlapCodedEventsStatSplittable(StatisticSumResSplittable):
#    pass
            
class RawOverlapCodedEventsStatUnsplittable(MultipleRawDataStatistic):    
    def _compute(self):
        tvs = [x.getResult() for x in self._children]
        
        from numpy import array
#         tvStartsOld = [x.startsAsNumpyArray()for x in tvs]
#         tvEndsOld = [x.endsAsNumpyArray() for x in tvs]
        tvStarts = [array(x.startsAsNumpyArray(), dtype='int64') for x in tvs]
        tvEnds = [array(x.endsAsNumpyArray(), dtype='int64') for x in tvs]
        
        numTracks = len(tvStarts)
        assert numTracks < 34, 'Maximum supported nr. of tracks for this statistic is 33'
        multiplier = 2**(numTracks+1)
        #assert no overlaps..
        #create arrays multiplied by 8 to use last three bits to code event type,
        #Last three bits: relative to 4 (100): +/- 1 for start/end of track1, +/- 2 for track2..
        
        tvCodedStarts = []
        tvCodedEnds = []
        for i in xrange(numTracks):
            tvCodedStarts.append(tvStarts[i] * multiplier + (2**numTracks) + (2**i))
            tvCodedEnds.append(tvEnds[i] * multiplier + (2**numTracks) - (2**i))
        
#         t1CodedStarts = t1s * 8 +5
#         t1CodedEnds= t1e  * 8 +3
#         t2CodedStarts = t2s * 8 +6
#         t2CodedEnds= t2e * 8 +2

        allSortedCodedEvents = concatenate((concatenate(tvCodedStarts), concatenate(tvCodedEnds) ))
        allSortedCodedEvents.sort()

        allEventCodes = (allSortedCodedEvents % multiplier) - (2**numTracks)

        allSortedDecodedEvents = allSortedCodedEvents / multiplier
        allEventLengths = allSortedDecodedEvents[1:] - allSortedDecodedEvents[:-1]

        #due to the coding, the last bit now has status of track1, and the second last bit status of track2
        #thus, 3 is cover by both, 2 is cover by only track2, 1 is cover by only track1, 0 is no cover
        #this works as there are no overlaps, and bits will thus not "spill over"..
        cumulativeCoverStatus = add.accumulate(allEventCodes)

        return allSortedDecodedEvents, allEventLengths, cumulativeCoverStatus

    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
