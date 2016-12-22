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
from gold.statistic.Statistic import StatisticConcatNumpyArrayResSplittable
import numpy as np
import math

class PointCountPerMicroBinV2Stat(MagicStatFactory):
    "Gives PointCountPerMicroBin, as a plain numpy array of values"
    pass

class PointCountPerMicroBinV2StatSplittable(StatisticConcatNumpyArrayResSplittable):
    pass
            
class PointCountPerMicroBinV2StatUnsplittable(Statistic):
    def _init(self, microBin=10000, **kwArgs):
        self.microBin = int(microBin)
            
    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        binArray = starts/self.microBin
        binCounts = np.bincount(binArray)
        numMicroBins = int( math.ceil( float(len(self._region)) / self.microBin) )
        binCounts = np.concatenate([binCounts, np.zeros(numMicroBins-len(binCounts), dtype='int')])
        
        return binCounts
    
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
