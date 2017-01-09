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

class GcContentStat(MagicStatFactory):
    pass

#class GcContentStatSplittable(StatisticSumResSplittable):
#    pass
            
class GcContentStatUnsplittable(Statistic):    
    def _compute(self):
        tv = self._children[0].getResult()
        vals = tv.valsAsNumpyArray()
        #return vals == 'c'+ vals == 'C'
        #arr = np.logical_or(np.logical_or(vals == 'c', vals == 'C'), np.logical_or(vals == 'g', vals == 'G'))
    
        resList = [0]*vals.size
        gcVals = {'c':None, 'g':None, 'C':None, 'G':None}
        counter = 0
        for i in vals:
            if gcVals.has_key(i):
                resList[counter] = 1
            counter+=1
            
        res = np.array(resList, dtype='float64')
        return res
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=True, val='char')) )
