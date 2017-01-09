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

#Note: Not yet tested. Should have unit and intTest.
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.CountPointStat import CountPointStat
from gold.util.CustomExceptions import SplittableStatNotAvailableError
#from quick.application.UserBinSource import GlobalBinSource, MinimalBinSource, UserBinSource
from gold.util.CommonFunctions import isIter
from collections import OrderedDict
from quick.statistic.BinSizeStat import BinSizeStat
from quick.statistic.CommonStatisticalTests import BinomialTools
import numpy
#from quick.util.GenomeInfo import GenomeInfo
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStatUnsplittable
from gold.util.CustomExceptions import IncompatibleAssumptionsError

class BinPreferencePValStat(MagicStatFactory):
    resultLabel = 'P-value'
    MIN_POP_FOR_GAUSSIAN_APPROXIMATION = 5
    #cfgGlobalSource = GlobalBinSource(DEFAULT_GENOME)
    
    #@classmethod
    #def minimize(cls, genome):
        #cls.cfgGlobalSource = MinimalBinSource(genome)

class BinPreferencePValStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, tail='more', globalSource='chrs', minimal=False, **kwArgs):
        if isIter(region):
            raise SplittableStatNotAvailableError()
        
        self._globalSource = GenericRelativeToGlobalStatUnsplittable.getGlobalSource(globalSource, region.genome, minimal)        
        #if minimal == True:
        #    self._globalSource = MinimalBinSource(region.genome)
        #elif globalSource == 'test':
        #    self._globalSource = UserBinSource('TestGenome:chr21:10000000-15000000','1000000')
        #elif globalSource == 'chrs':
        #    self._globalSource = GenomeInfo.getChrRegs(region.genome)
        #elif globalSource == 'chrarms':
        #    self._globalSource = GenomeInfo.getChrArmRegs(region.genome)
        #elif globalSource == 'ensembl':
        #    self._globalSource = GenomeInfo.getStdGeneRegs(region.genome)
        #elif globalSource == 'userbins':
        #    from gold.application.StatRunner import StatJob
        #    assert StatJob.USER_BIN_SOURCE is not None
        #    self._globalSource = StatJob.USER_BIN_SOURCE
        #    #self._globalSource = kwArgs['userBins']
        #else:
        #    raise ShouldNotOccurError('globalSource not recognized')
        #    #self._globalSource = GlobalBinSource(region.genome)
        
        assert tail in ['more', 'less', 'different']
        self._tail = tail
        
        super(self.__class__, self).__init__(region, track, track2, tail=tail, globalSource=globalSource, minimal=minimal, **kwArgs)
    
    def _checkAssumptions(self, assumptions):
        if not assumptions == 'poissonPoints':
            raise IncompatibleAssumptionsError

    def _compute(self):
        prob = 1.0 * self._binSizeStat.getResult() / self._globalSizeStat.getResult()
        x = self._pointsInBinStat.getResult()
        size = self._pointsGloballyStat.getResult()
        
        pval = BinomialTools._computeBinomialTail(x, size, prob, self._tail)
        
        expPoints = prob*size
        ratioToMean = 1.0 * x / expPoints if expPoints>0 else numpy.nan
        
        return OrderedDict([('P-value', pval), ('Test statistic: Points in bin', x), ('E(Test statistic): Expected points in bin', expPoints), \
                            ('DiffFromMean', x-prob*size), ('RatioTowardsMean',ratioToMean)])
            

    def _createChildren(self):
        self._pointsInBinStat = self._addChild(CountPointStat(self._region , self._track))
        self._pointsGloballyStat = self._addChild(CountPointStat(self._globalSource , self._track))
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track))
        self._globalSizeStat = self._addChild( BinSizeStat(self._globalSource, self._track))

