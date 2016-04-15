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
from quick.statistic.TrackSimilarityToCollectionHypothesisV2Stat import TrackSimilarityToCollectionHypothesisV2Stat
'''
Created on Nov 3, 2015

@author: boris
'''


from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic


class TrackSimilarityToCollectionHypothesisWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class TrackSimilarityToCollectionHypothesisWrapperStatSplittable(StatisticSumResSplittable):
#    pass
            
class TrackSimilarityToCollectionHypothesisWrapperStatUnsplittable(MultipleTrackStatistic):    
    
    def _compute(self):
        return self._children[0].getResult()

    def getTrackStructureFromTracks(self, tracks):
        ts = TrackStructure()
        queryTracks = [tracks[0]]
        refTracks = tracks[1:]
            
        ts[TrackStructure.QUERY_KEY] = queryTracks
        ts[TrackStructure.REF_KEY] = refTracks
        return ts
    
    def _createChildren(self):
        trackStructure = self.getTrackStructureFromTracks(self._tracks)
        self._addChild(TrackSimilarityToCollectionHypothesisV2Stat(self._region, trackStructure, **self._kwArgs))