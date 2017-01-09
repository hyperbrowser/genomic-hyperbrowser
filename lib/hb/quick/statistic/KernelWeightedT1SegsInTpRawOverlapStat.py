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
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BpLevelArrayRawDataStat import BpLevelArrayRawDataStat

class KernelWeightedT1SegsInTpRawOverlapStat(MagicStatFactory):
    pass

class KernelWeightedT1SegsInTpRawOverlapStatSplittable(StatisticSumResSplittable):
    pass
            
class KernelWeightedT1SegsInTpRawOverlapStatUnsplittable(Statistic):
    def _init(self, kernelType=None, spreadParam=None, **kwArgs):
        self._kernelType = kernelType
        self._spreadParam = int(spreadParam)
        
    def _compute(self):
        segsTv = self._children[0].getResult()
        numData= self._children[1].getResult()
        aggregateInside = numData.dtype.type(0)
        #for el,i in enumerate(self._children[1].getResult()):
        for i,el in enumerate(segsTv):
            slicedData = numData[el.start():el.end()]
            elementLen = el.end()-el.start()
            from quick.statistic.KernelUtilStat import KernelUtilStatUnsplittable
            kernel = KernelUtilStatUnsplittable.getKernel(elementLen, self._kernelType, self._spreadParam)
            weightedSlice = slicedData*kernel
            aggregateInside += weightedSlice.sum(dtype='float64')
        
        return aggregateInside
    
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, dense=False)) )
        self._addChild( BpLevelArrayRawDataStat(self._region, self._track2) )
        
        

