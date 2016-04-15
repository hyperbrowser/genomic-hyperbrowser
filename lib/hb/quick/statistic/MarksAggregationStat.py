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
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import ShouldNotOccurError
import numpy

class MarksAggregationStat(MagicStatFactory):
    "Returns an aggregate operation performed on all marks in the bin, e.g. sum/max/min/mean of marks"
    pass

class MarksAggregationStatSplittable(StatisticSumResSplittable):    
    pass

class MarksAggregationStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, aggregateOperation=None, **kwArgs):
        self._aggregateOperation = aggregateOperation
        Statistic.__init__(self, region, track, track2, aggregateOperation=aggregateOperation, **kwArgs)
        
    def _compute(self):
        array = self._children[0].getResult().valsAsNumpyArray()
        if len(array)==0:
            return numpy.nan
        assert array.dtype == "float32" or array.dtype == "float64"
        if self._aggregateOperation == 'sum':
            return float(array.sum(dtype="float64")) #accumulator must be 64-bit or rounding errors occur
        elif self._aggregateOperation == 'min':
            return float(array.min())
        elif self._aggregateOperation == 'max':
            res = float(array.max())
            #assert not any([v.isnan() for v in ])
            return res
        else:
            raise ShouldNotOccurError()
    
    def _createChildren(self):        
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number')) )
