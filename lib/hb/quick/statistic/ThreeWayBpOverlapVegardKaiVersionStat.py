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
from gold.statistic.Statistic import MultipleRawDataStatistic
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.VennDataStat import VennDataStatUnsplittable, VennDataStatSplittable
from collections import defaultdict

class ThreeWayBpOverlapVegardKaiVersionStat(MagicStatFactory):
    '''Computes the combined overlap of different subsets of supplied tracks.
    Note that coverage by subsets is not disjunct, so that e.g. result for '01',
    denoting coverage by track2 (for two track overlap) also includes bps covered by both tracks
    '''
    pass

#class ThreeWayBpOverlapVegardKaiVersionStatSplittable(StatisticDictSumResSplittable):
#    pass

class ThreeWayBpOverlapVegardKaiVersionStatSplittable(VennDataStatSplittable):
    pass
    
class ThreeWayBpOverlapVegardKaiVersionStatUnsplittable(MultipleRawDataStatistic):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        
        tvs = [child.getResult() for child in self._children]
        categoryBedList = defaultdict(list)
        categoryNames = ['t'+str(i) for i in range(len(tvs))]

        for tv,cat in zip(tvs, categoryNames):        
            rawData = tv
            ends = list(rawData.endsAsNumpyArray())
            starts = list(rawData.startsAsNumpyArray())
            for i in range(len(starts)):
                categoryBedList[chr].append((starts[i], ends[i], cat))
        
        
        return VennDataStatUnsplittable._calculateIntersections(categoryBedList, categoryNames, 'dummyTNforNow')
        


    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
