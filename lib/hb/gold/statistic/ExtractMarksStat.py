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
from gold.statistic.Statistic import StatisticConcatNumpyArrayResSplittable, Statistic, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class ExtractMarksStat(MagicStatFactory):
    pass

class ExtractMarksStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
            
class ExtractMarksStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def _compute(self):
        vals = self._children[0].getResult().valsAsNumpyArray()
        rawData2 = self._children[1].getResult()
        
        if rawData2.trackFormat.isInterval():
            return vals[ rawData2.getBinaryBpLevelArray() ]
        else:
            points = rawData2.startsAsNumpyArray()
            return vals[points]
    
    #def _getCoverageVec(self, rawData):
    #    tempVec = numpy.zeros(len(rawData), dtype='i')
    #    tempVec[ rawData.startsAsNumpyArray() ] = 1
    #    tempVec[ rawData.endsAsNumpyArray() ] = -1
    #    coverageVec = numpy.add.accumulate(tempVec)
    #    return (coverageVec != 0)
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=True, interval=False, val='number')) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False)) ) 
    