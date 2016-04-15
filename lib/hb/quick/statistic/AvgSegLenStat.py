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
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
#from gold.statistic.CountSegmentStat import CountSegmentStat
#from quick.statistic.CountNumSegmentsStat import CountNumSegmentsStat
from gold.statistic.SegmentLengthsStat import SegmentLengthsStat

class AvgSegLenStat(MagicStatFactory):
    pass
            
class AvgSegLenStatUnsplittable(Statistic):    
    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'])
        self._withOverlaps = withOverlaps
        
    def _compute(self):
        #return 1.0 * self._children[0].getResult() / self._children[1].getResult()
        return self._children[0].getResult()['Result'].mean()
        
    def _createChildren(self):
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True)) )
        #self._addChild( CountSegmentStat(self._region, self._track) )
        #self._addChild( CountNumSegmentsStat(self._region, self._track) )
        self._addChild( SegmentLengthsStat(self._region, self._track, withOverlaps=self._withOverlaps) )
