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
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.ProportionCountStat import ProportionCountStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from collections import OrderedDict

class PropPointCountsVsSegsStat(MagicStatFactory):
    pass

class PropPointCountsVsSegsStatUnsplittable(Statistic):
    def _compute(self):
        overlap = self._rawOverlap.getResult()
        res = OrderedDict([('Both', overlap['Both']), ('Only1', overlap['Only1'])])
        
        totPointCount = sum( res.values() )
        res['BothProp'] = res['Both']*1.0/totPointCount if totPointCount != 0 else None
        res['Only1Prop'] = res['Only1']*1.0/totPointCount if totPointCount != 0 else None
        res['SegCoverage'] = self._segmentCoverProportion.getResult()
        
        return res
        
    def _createChildren(self):
        self._rawOverlap = self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        self._segmentCoverProportion = self._addChild( ProportionCountStat(self._region, self._track2) )
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )
