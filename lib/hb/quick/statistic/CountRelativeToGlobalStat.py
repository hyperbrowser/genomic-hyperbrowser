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
from gold.statistic.CountPointStat import CountPointStat
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from quick.application.UserBinSource import GlobalBinSource, MinimalBinSource, UserBinSource
from gold.util.CommonFunctions import isIter

class CountRelativeToGlobalStat(MagicStatFactory):
    pass

class CountRelativeToGlobalStatUnsplittable(Statistic):
#    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, globalSource='', minimal=False, **kwArgs):
        if isIter(region):
            raise SplittableStatNotAvailableError()

        if minimal == True:
            self._globalSource = MinimalBinSource(region.genome)
        elif globalSource == 'test':
            self._globalSource = UserBinSource('TestGenome:chr21:10000000-15000000','1000000')
        else:
            self._globalSource = GlobalBinSource(region.genome)
        
        super(self.__class__, self).__init__(region, track, track2, globalSource=globalSource, minimal=minimal, **kwArgs)
    
    def _createChildren(self):
        globCount1 = CountPointStat(self._globalSource , self._track)
        binCount1 = CountPointStat(self._region, self._track)

        self._addChild(globCount1)
        self._addChild(binCount1)

    def _compute(self):    
        n1 = self._children[0].getResult()
        c1 = self._children[1].getResult()
        #print '*',c1,c2,n1,n2
        
        return 1.0*c1/n1
            
