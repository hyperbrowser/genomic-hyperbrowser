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
from gold.statistic.Statistic import Statistic, StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class BpCoveragePerT2SegStat(MagicStatFactory):
    pass

class BpCoveragePerT2SegStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
            
class BpCoveragePerT2SegStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def _compute(self):
        tv1, tv2 = self._children[0].getResult(), self._children[1].getResult()
        t1BpArray = tv1.getBinaryBpLevelArray()
        return numpy.array([t1BpArray[el.start():el.end()].sum() for el in tv2])
            

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True)) ) #interval=False is supported through the faster PointCountPerSegStat..
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, interval=True)) )
        #fixme: Track 2 should have borderhandling='include', but this is not supported yet. This to support correct splitting'
