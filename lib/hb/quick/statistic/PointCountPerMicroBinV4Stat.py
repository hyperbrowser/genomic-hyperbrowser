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
#from gold.statistic.CountStat import CountStatSplittable, CountStatUnsplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np
import math
from gold.track.TrackView import TrackView

class PointCountPerMicroBinV4Stat(MagicStatFactory):
    "Gives PointCountPerMicroBin, as a mapping from Genome Region object to count"
    pass

#class PointCountPerMicroBinV4StatSplittable(StatisticConcatResSplittable):
#    pass
            
class PointCountPerMicroBinV4StatUnsplittable(Statistic):
    def _init(self, microBin=10000, **kwArgs):
        self.microBin = int(microBin)
            
    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        binArray = starts/self.microBin
        binCounts = np.bincount(binArray)
        numMicroBins = int( math.ceil( float(len(self._region)) / self.microBin) )
        binCounts = np.concatenate([binCounts, np.zeros(numMicroBins-len(binCounts), dtype='int')])
        #print 'temp1: ', len(binCounts)
        assert [i*self.microBin for i in xrange(len(binCounts))] == range(0, len(self._region), self.microBin), ([i*self.microBin for i in xrange(len(binCounts))], range(0, len(self._region), self.microBin) )
        startList = [i*self.microBin for i in xrange(len(binCounts))]
        assert [min( (i+1)*self.microBin, len(self._region)) for i in xrange(len(binCounts))] == startList[1:] + [len(self._region)]
        endList = [min( (i+1)*self.microBin, len(self._region)) for i in xrange(len(binCounts))]
        #print ','.join([str(x) for x in binCounts])
        return TrackView(genomeAnchor=tv.genomeAnchor, startList=np.array(startList), endList=np.array(endList), valList=binCounts, \
                          strandList=None, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=False)
        #return [GenomeElement(self._region.genome, self._region.chr, 
        #        self._region.start+i*self.microBin, min(self._region.start+(i+1)*self.microBin, self._region.end), 
        #        binCounts[i])
        #        for i in xrange(len(binCounts))]            
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False, allowOverlaps=True)) )
