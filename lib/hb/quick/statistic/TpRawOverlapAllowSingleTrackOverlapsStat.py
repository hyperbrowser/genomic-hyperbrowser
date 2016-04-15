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
from quick.statistic.BpLevelArrayRawDataStat import BpLevelArrayRawDataStat
from gold.track.TrackFormat import TrackFormatReq
#from quick.statistic.BinSizeStat import BinSizeStat

class TpRawOverlapAllowSingleTrackOverlapsStat(MagicStatFactory):
    pass

class TpRawOverlapAllowSingleTrackOverlapsStatSplittable(StatisticSumResSplittable):
    pass

class TpRawOverlapAllowSingleTrackOverlapsStatUnsplittable(Statistic):
    VERSION = '1.0'
    def _init(self, cacheBpLevelArray='no', **kwArgs):
        if cacheBpLevelArray=='yes':
            self._cacheBpLevelArray = True
        elif cacheBpLevelArray=='no':
            self._cacheBpLevelArray = False
        else:
            raise Exception
            
        
    def _compute(self): #Numpy Version..
        if self._cacheBpLevelArray:
            tv1BpLevelCoverage, tv2BpLevelCoverage = self._children[0].getResult(), self._children[1].getResult()
        else:
            tv1BpLevelCoverage, tv2BpLevelCoverage = self._children[0].getResult().getCoverageBpLevelArray(), self._children[1].getResult().getCoverageBpLevelArray()
        
        tp = (tv1BpLevelCoverage*tv2BpLevelCoverage).sum()
        return int( tp )
    
    def _createChildren(self):
        if self._cacheBpLevelArray:
            self._addChild( BpLevelArrayRawDataStat(self._region, self._track) )
            self._addChild( BpLevelArrayRawDataStat(self._region, self._track2) )
        else:
            self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=None)) )
            self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(allowOverlaps=None)) )
    