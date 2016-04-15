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
from quick.statistic.BpLevelArrayRawDataStat import BpLevelArrayRawDataStat
from quick.statistic.KernelUtilStat import KernelUtilStat

class KernelWeightedCountStat(MagicStatFactory):
    "Counts bps covered by track. If specified with intra-track overlaps, it will for each bp count the number of times the bp is covered by a track element."
    pass

class KernelWeightedCountStatSplittable(StatisticSumResSplittable):
    pass
            
class KernelWeightedCountStatUnsplittable(Statistic):
    def _compute(self):
        bpLevelCoverage = self._children[0].getResult()
        kernel = self._children[1].getResult()
        
        assert len(kernel)== len(bpLevelCoverage)# == binSize
        
        weightedCoverage = bpLevelCoverage * kernel
        return sum(weightedCoverage)
        
    def _createChildren(self):
        allowOverlaps=self._configuredToAllowOverlaps(strict=False)
        bpDepthType='coverage' if allowOverlaps else 'binary'
        self._addChild( BpLevelArrayRawDataStat(self._region, self._track, bpDepthType=bpDepthType, useFloatValues=False, **self._kwArgs) )
        self._addChild( KernelUtilStat(self._region, self._track, **self._kwArgs) )
#
#
#class KernelWeightedCountStatUnsplittable(Statistic):
#    def _init(self, kernelType=None, kernelStdev=None, minimumOffsetValue=1, **kwArgs):
#        #assert kernelType in ['gaussian','divideByOffset']
#        #divideByOffset: weigh by 1/x, where x is offset from center, meaning integral of region (on one side) 0-x is log(x).
#        if kernelType in ['gaussian']:
#            assert kernelStdev is not None
#            self._kernelStdev = float(kernelStdev)
#        elif kernelType == 'divideByOffset':
#            assert minimumOffsetValue is not None
#            self._minimumOffsetValue = float(minimumOffsetValue)
#        else:
#            raise ArgumentValueError('Invalid kernelType')
#        self._kernelType = kernelType
#            
#    def _compute(self):
#        bpLevelCoverage = self._children[0].getResult()
#        binSize = self._children[1].getResult()
#        
#        if self._kernelType=='gaussian':
#            from scipy.stats.distributions import norm
#            kernel = norm(0, self._kernelStdev).pdf(numpy.arange(-binSize/2, binSize/2))
#        elif self._kernelType == 'divideByOffset':
#            offsets = numpy.abs(numpy.arange(-binSize/2, binSize/2))
#            
#            kernel = 1.0/numpy.maximum(self._minimumOffsetValue, offsets )
#            
#        #normalize:
#        kernel = 1.0*kernel*binSize/sum(kernel)
#        assert len(kernel)== len(bpLevelCoverage) == binSize
#        
#        weightedCoverage = bpLevelCoverage * kernel
#        return sum(weightedCoverage)
#        #if rawData.trackFormat.reprIsDense():
#        #    return len(rawData.valsAsNumpyArray())
#        #else:
#        #    #return sum(el.end()-el.start() for el in rawData)
#        #    return rawData.endsAsNumpyArray().sum() - rawData.startsAsNumpyArray().sum()
#        
#    def _createChildren(self):
#        allowOverlaps=self._configuredToAllowOverlaps(strict=False)
#        bpDepthType='coverage' if allowOverlaps else 'binary'
#        self._addChild( BpLevelArrayRawDataStat(self._region, self._track, bpDepthType=bpDepthType, useFloatValues=False, **self._kwArgs) )
#        self._addChild( BinSizeStat(self._region, self._track ) )
