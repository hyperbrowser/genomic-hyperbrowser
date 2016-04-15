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
from gold.track.TrackStructure import TrackStructure
'''
Created on Sep 23, 2015

@author: boris
'''


from quick.statistic.QueryToReferenceCollectionStat import QueryToReferenceCollectionStatUnsplittable
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic


class QueryToReferenceCollectionWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class QueryToReferenceCollectionWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class QueryToReferenceCollectionWrapperStatUnsplittable(MultipleTrackStatistic):
    
    def _compute(self):
        #2. call the new type statistic
        #3. return the result
        return self._newStat._compute()
    
    def _createChildren(self):
        queryTracks = self._tracks[:1]
        refTracks = self._tracks[1:]
        trackStructure = TrackStructure()
        trackStructure[TrackStructure.QUERY_KEY] = queryTracks
        trackStructure[TrackStructure.REF_KEY] = refTracks
        if 'extraTracks' in self._kwArgs:
            del self._kwArgs['extraTracks']
#         self._kwArgs['trackStructure'] = trackStructure
        self._newStat = QueryToReferenceCollectionStatUnsplittable(self._region, trackStructure, **self._kwArgs)        
        self._newStat._createChildren()