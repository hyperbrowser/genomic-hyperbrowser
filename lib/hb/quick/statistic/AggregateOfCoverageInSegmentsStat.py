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
#from gold.statistic.
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import NotSupportedError
from gold.application.LogSetup import logLackOfSupport

class AggregateOfCoverageInSegmentsStat(MagicStatFactory):
    pass

class AggregateOfCoverageInSegmentsStatSplittable(StatisticSumResSplittable):
    pass
            
class AggregateOfCoverageInSegmentsStatUnsplittable(Statistic):
    def _init(self, method='sum_of_sum', **kwArgs):
        self._method = method
        if method == 'mean_of_mean':
            errorMsg = 'AggregateOfCoverageInSegmentsStat does not support "mean_of_mean".'
            logLackOfSupport(errorMsg)
            raise NotSupportedError(errorMsg)
    
    def _compute(self):
        refTv = self._children[0].getResult()
        segsTv = self._children[1].getResult()
        numData = refTv.getCoverageBpLevelArray()
            
        aggregateInside = numData.dtype.type(0)
        
        for i,el in enumerate(segsTv):
            slicedData = numData[el.start():el.end()]
            #if self._method == 'individual_coverage_per_seg':
            #if self._method == 'sum_of_prop_coverages':
            #    aggregateInside += slicedData.sum(dtype='float64') / len(slicedData)
            if self._method == 'sum_of_sum':
                aggregateInside += slicedData.sum(dtype='float64')
            elif self._method in ['sum_of_mean', 'mean_of_mean']:
                aggregateInside += slicedData.mean(dtype='float64')
                
        if self._method == 'mean_of_mean' and segsTv.getNumElements() > 0:
            aggregateInside /= 1.0 * (i+1)
        
        return aggregateInside
    
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=False, dense=False, interval=True)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(allowOverlaps=False, dense=False, interval=True)) )
        
        

