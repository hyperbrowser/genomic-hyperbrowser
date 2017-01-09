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
from quick.statistic.PointCountPerMicroBinV2Stat import PointCountPerMicroBinV2Stat


class PointCountPerMicroBinQuantileStat(MagicStatFactory):
    '''
    Computes a given quantile from the counts per microbin, both within user bins and at the global level
    '''
    pass

class PointCountPerMicroBinQuantileStatUnsplittable(Statistic):
    def _init(self, quantile, **kwArgs):
        self._quantile = quantile

    def _createChildren(self):
        self._addChild( PointCountPerMicroBinV2Stat(self._region, self._track, **self._kwArgs) )

    def _compute(self):
        counts = self._children[0].getResult()
        if self._quantile == 'avg':
            return sum(counts) / float(len(counts))
        else:
            quantIndex = int(round(float(self._quantile)/100*(len(counts)-1)) )
            return sorted(counts)[quantIndex]

