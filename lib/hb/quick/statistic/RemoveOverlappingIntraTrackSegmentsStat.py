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
from gold.track.TrackView import TrackView
import numpy as np
#from gold.application.LogSetup import logMessage

class RemoveOverlappingIntraTrackSegmentsStat(MagicStatFactory):
    pass

#class RemoveOverlappingIntraTrackSegmentsStatSplittable(StatisticSumResSplittable):
#    pass
            
class RemoveOverlappingIntraTrackSegmentsStatUnsplittable(Statistic):
    
        
    def _compute(self):
        
        tv = self._children[0].getResult()
        startL, endL, valL = list(tv.startsAsNumpyArray()), list(tv.endsAsNumpyArray()), tv.valsAsNumpyArray()
        index = 0
        numSegments = len(startL)
        overlapTreshold = 0
        startRes, endRes, valRes = [], [], []
        
        while index<numSegments-1:
            start = startL[index]
            end = endL[index]
            if start>=overlapTreshold and startL[index+1] >= end:
                startRes.append(start)
                endRes.append(end)
                valRes.append(valL[index])
            overlapTreshold = max(overlapTreshold, end)
            index+=1
        
        
        if startL[-1]>=overlapTreshold:
            startRes.append(startL[index])
            endRes.append(endL[index])
            valRes.append(valL[index])
                
            
        
            
        return TrackView(genomeAnchor=tv.genomeAnchor, startList=np.array(startRes), endList=np.array(endRes), valList=np.array(valRes), \
                         strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=False)
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True)) )

