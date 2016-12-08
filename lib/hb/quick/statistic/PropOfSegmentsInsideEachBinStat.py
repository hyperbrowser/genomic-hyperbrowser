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
from gold.statistic.CountSegmentStat import CountSegmentStat
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from quick.application.UserBinSource import GlobalBinSource, MinimalBinSource, UserBinSource
from quick.util.CommonFunctions import isIter


class PropOfSegmentsInsideEachBinStat(MagicStatFactory):
    """
    For each bin, return the proportion of all bps (segments) that falls within that specific bin.
    This means that if the bins cover the whole genome, the results across all bins will sum to one
    """


class PropOfSegmentsInsideEachBinStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def _init(self, globalSource='', minimal=False):
        if isIter(self._region):
            raise SplittableStatNotAvailableError()

        if minimal:
            self._globalSource = MinimalBinSource(self._region.genome)
        elif globalSource == 'test':
            self._globalSource = UserBinSource('TestGenome:chr21:10000000-15000000','1000000')
        else:
            self._globalSource = GlobalBinSource(self._region.genome)

    def _createChildren(self):
        globCount = CountSegmentStat(self._globalSource, self._track)
        binCount = CountSegmentStat(self._region, self._track)

        self._addChild(globCount)
        self._addChild(binCount)

    def _compute(self):    
        n1 = self._children[0].getResult()
        c1 = self._children[1].getResult()
        return 1.0*c1/n1
