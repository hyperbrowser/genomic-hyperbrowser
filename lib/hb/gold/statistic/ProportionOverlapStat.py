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
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class ProportionOverlapStat(MagicStatFactory):
    pass

class ProportionOverlapStatUnsplittable(Statistic):
    def _compute(self):
        res = self._children[0].getResult()

        n = sum( res[key] for key in ['Neither','Only1','Only2','Both'] )

        res['NeitherProp'] = res['Neither']*1.0/n
        res['Only1Prop'] = res['Only1']*1.0/n
        res['Only2Prop'] = res['Only2']*1.0/n
        res['BothProp'] = res['Both']*1.0/n
        
        return res

    def _createChildren(self):
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, interval=True)) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )

        

