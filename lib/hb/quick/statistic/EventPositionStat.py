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
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np

class EventPositionStat(MagicStatFactory):
    pass

#class EventPositionStatSplittable(StatisticSumResSplittable):
#    pass
            
class EventPositionStatUnsplittable(Statistic):
    
    def _compute(self):
        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        tv1Events = np.concatenate((tv1.startsAsNumpyArray(), tv1.endsAsNumpyArray()))
        tv2Events = np.concatenate((tv2.startsAsNumpyArray(), tv2.endsAsNumpyArray()))
        return np.unique(np.concatenate((tv1Events, tv2Events)))
        
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq()) )
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq()) )