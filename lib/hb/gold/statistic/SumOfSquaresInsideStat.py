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

class SumOfSquaresInsideStat(MagicStatFactory):
    pass

class SumOfSquaresInsideStatSplittable(StatisticSumResSplittable):
    pass

class SumOfSquaresInsideStatUnsplittable(Statistic):    
    def _compute(self):
        numData = self._children[1].getResult().valsAsNumpyArray()
        sumInside = numData.dtype.type(0)
        for el in self._children[0].getResult():
            vec = numData[el.start():el.end()]
            sumInside += (vec*vec).sum(dtype='float64')
        return sumInside
        
    def _createChildren(self):
        rawSegDataStat = RawDataStat(self._region, self._track, TrackFormatReq(interval=True, dense=False))
        rawNumDataStat = RawDataStat(self._region, self._track2, TrackFormatReq(dense=True, val='number', interval=False))
        self._addChild(rawSegDataStat)
        self._addChild(rawNumDataStat)
