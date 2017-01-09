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

from gold.statistic.RawOverlapStat import RawOverlapStat, RawOverlapStatUnsplittable
from gold.statistic.Statistic import StatisticDictSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat
from collections import OrderedDict

class PointCountsVsSegsStat(RawOverlapStat):
    pass

class PointCountsVsSegsStatSplittable(StatisticDictSumResSplittable):
    pass

class PointCountsVsSegsStatUnsplittable(RawOverlapStatUnsplittable):
    def _compute(self):
        res = RawOverlapStatUnsplittable._compute(self)
        return OrderedDict([('Both', res['Both']), ('Only1', res['Only1'])])

    def _createChildren(self):
        rawDataStat = RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False))
        self._addChild(rawDataStat)
        rawDataStat2 = RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True))
        self._addChild(rawDataStat2)
        self._binSizeStat = self._addChild( BinSizeStat(self._region, self._track2))
