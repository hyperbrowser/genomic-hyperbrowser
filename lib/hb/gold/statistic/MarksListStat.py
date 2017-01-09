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

import ast

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import StatisticConcatNumpyArrayResSplittable, Statistic, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class MarksListStat(MagicStatFactory):
    pass

class MarksListStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False
           
class MarksListStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2=None, withOverlaps='no', markType='number', enforcePoints=True, **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps
        self._markType = markType
        if isinstance(enforcePoints, basestring):
            enforcePoints = ast.literal_eval(enforcePoints)
        self._enforcePoints = enforcePoints
        Statistic.__init__(self, region, track, track2, withOverlaps=withOverlaps, markType=markType, enforcePoints=enforcePoints, **kwArgs)
    
    def _compute(self):
        marks = self._children[0].getResult().valsAsNumpyArray()
        assert marks is not None
        #print marks
        #res = [float(x) for x in self._children[0].getResult().valsAsNumpyArray() ]
        return marks
    
    def _createChildren(self):
        interval = False if self._enforcePoints else None
        self._addChild( RawDataStat(self._region, self._track, \
                                    TrackFormatReq(interval=interval, val=self._markType, allowOverlaps=(self._withOverlaps=='yes'))) )
