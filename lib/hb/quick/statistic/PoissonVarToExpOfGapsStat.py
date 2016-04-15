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
from gold.statistic.Statistic import RatioStatUnsplittable
#from gold.statistic.RawDataStat import RawDataStat
#from quick.statistic.BinSizeStat import BinSizeStat
#from quick.statistic.SegmentDistancesStat import SegmentDistancesStat
from quick.statistic.VarOfGapsStat import VarOfGapsStat
from quick.statistic.MeanOfGapsStat import MeanOfGapsStat

class PoissonVarToExpOfGapsStat(MagicStatFactory):
    pass

#class PoissonVarToExpOfGapsStatSplittable(StatisticSumResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class PoissonVarToExpOfGapsStatUnsplittable(RatioStatUnsplittable):                    
    def _createChildren(self):
        self._addChild(VarOfGapsStat(self._region, self._track) )
        self._addChild(MeanOfGapsStat(self._region, self._track) )