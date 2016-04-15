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
from quick.statistic.BinSizeStat import BinSizeStat
from gold.util.CustomExceptions import ArgumentValueError
import numpy

class KernelUtilStat(MagicStatFactory):
    "Counts bps covered by track. If specified with intra-track overlaps, it will for each bp count the number of times the bp is covered by a track element."
    pass

class KernelUtilStatSplittable(StatisticSumResSplittable):
    pass
            
class KernelUtilStatUnsplittable(Statistic):
    KERNEL_CACHE = {}
    
    @classmethod
    def getKernel(cls, kernelSize, kernelType, spreadParam, useKernelCache=True):
        if useKernelCache:
            cacheKey = (kernelSize, kernelType, spreadParam)
            if cacheKey in cls.KERNEL_CACHE:
                return cls.KERNEL_CACHE[cacheKey]
        
        if kernelType=='gaussian':
            from scipy.stats.distributions import norm
            kernel = norm(0, spreadParam).pdf(numpy.arange(-kernelSize/2, kernelSize/2))
        elif kernelType == 'divideByOffset':
            offsets = numpy.abs(numpy.arange(-kernelSize/2, kernelSize/2))
            #print 'tEMP3: ',offsets[0:10], type(offsets), numpy.maximum(spreadParam, offsets ), type(numpy.maximum(spreadParam, offsets ))
            kernel = 1.0/numpy.maximum(spreadParam, offsets )
        elif kernelType == 'binSizeNormalized':
            kernel = numpy.zeros(kernelSize) + 1.0/kernelSize #uniform kernel of 1/binSize...
        else:
            raise
        #normalize:
        if kernelType in ['gaussian', 'divideByOffset']:
            kernel = 1.0*kernel*kernelSize/sum(kernel)
        if useKernelCache:
            cls.KERNEL_CACHE[cacheKey] = kernel
        return kernel
    
    def _init(self, kernelType=None, kernelStdev=None, minimumOffsetValue=1, **kwArgs):
        #assert kernelType in ['gaussian','divideByOffset']
        #divideByOffset: weigh by 1/x, where x is offset from center, meaning integral of region (on one side) 0-x is log(x).
        if kernelType == 'gaussian':
            assert kernelStdev is not None
            self._kernelStdev = float(kernelStdev)
        elif kernelType == 'divideByOffset':
            assert minimumOffsetValue is not None
            self._minimumOffsetValue = float(minimumOffsetValue)
        else:
            raise ArgumentValueError('Invalid kernelType')
        self._kernelType = kernelType
            
    def _compute(self):
        binSize = self._children[0].getResult()        
        if self._kernelType == 'gaussian':
            spreadParam = self._kernelStdev
        elif self._kernelType == 'divideByOffset':
            spreadParam = self._minimumOffsetValue
        else:
            raise
        kernel = self.getKernel(binSize, self._kernelType, spreadParam)
        assert len(kernel)== binSize
        return kernel
        #assert len(kernel)== len(bpLevelCoverage) == binSize
        
        #weightedCoverage = bpLevelCoverage * kernel
        #return sum(weightedCoverage)
        #if rawData.trackFormat.reprIsDense():
        #    return len(rawData.valsAsNumpyArray())
        #else:
        #    #return sum(el.end()-el.start() for el in rawData)
        #    return rawData.endsAsNumpyArray().sum() - rawData.startsAsNumpyArray().sum()
        
    def _createChildren(self):
        self._addChild( BinSizeStat(self._region, self._track ) )
