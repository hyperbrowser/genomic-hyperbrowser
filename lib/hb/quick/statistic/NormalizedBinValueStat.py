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
from quick.application.UserBinSource import MinimalBinSource
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq

class NormalizedBinValueStat(MagicStatFactory):
    pass

#class NormalizedBinValueStatSplittable(StatisticSumResSplittable):
    #pass
            
class NormalizedBinValueStatUnsplittable(Statistic):
    '''Takes as parameter a rawStatistic, which should be a class that returns a single numerical value as getResult.
    NormalizedBinValueStat will then compute these values from all bins, and for each bin normalize these accordint to
    a specified normalizationType, e.g. so that all values per bin are scaled between zero and one.
    The normalized values are then returned by getResult.
    '''
    
    def __init__(self, region, track, track2, rawStatistic=None, normalizationType='zeroToOne', minimal=False, **kwArgs):
        if minimal == True:
            self._globalSource = MinimalBinSource(region.genome)
        else:
            from gold.application.StatRunner import StatJob
            assert StatJob.USER_BIN_SOURCE is not None
            self._globalSource = StatJob.USER_BIN_SOURCE
        
        Statistic.__init__(self, region, track, track2, rawStatistic=rawStatistic, normalizationType=normalizationType, minimal=minimal, **kwArgs)
        
        if type(rawStatistic) is str:
            from gold.statistic.AllStatistics import STAT_CLASS_DICT
            rawStatistic = STAT_CLASS_DICT[rawStatistic]
     
        self._rawStatistic = rawStatistic
        self._normalizationType = normalizationType
        
    def _compute(self):
        raise
        #
        #rawData = self._children[0].getResult()
        #if rawData.trackFormat.reprIsDense():
        #    return len(rawData.valsAsNumpyArray())
        #else:
        #    #return sum(el.end()-el.start() for el in rawData)
        #    return rawData.endsAsNumpyArray().sum() - rawData.startsAsNumpyArray().sum()
        #
    def _createChildren(self):
        raise
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq()) )
