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
from gold.statistic.Statistic import Statistic, StatisticDynamicDictSumResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import IncompatibleTracksError
from collections import OrderedDict
import numpy

class CategoryPointCountNoOverlapsStat(MagicStatFactory):
    pass

class CategoryPointCountNoOverlapsStatSplittable(StatisticDynamicDictSumResSplittable, OnlyGloballySplittable):
    pass
            
class CategoryPointCountNoOverlapsStatUnsplittable(Statistic):
    VERSION = '1.1'
    # Different from FreqPerCatStat in that two overlapping points of the same category are only counted once.
    # Can also be used for segments, but then only counts starting points (ignoring strand)
    def _compute(self):
        rawData = self._children[0].getResult()
        starts = rawData.startsAsNumpyArray()
        catSequence = rawData.valsAsNumpyArray()
        if catSequence is None:
            raise IncompatibleTracksError()
        
        catSet = numpy.unique(catSequence)
        res = OrderedDict()
        for cat in catSet:
            filter = (catSequence==cat)
            res[cat] = len(numpy.unique(starts[filter]))
        return res
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, val='category', allowOverlaps=True)) )
