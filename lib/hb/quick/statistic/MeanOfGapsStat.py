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
#from quick.statistic.BinSizeStat import BinSizeStat
#from quick.statistic.SegmentDistancesStat import SegmentDistancesStat
from quick.statistic.PointGapsStat import PointGapsStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class MeanOfGapsStat(MagicStatFactory):
    pass

#class MeanOfGapsStatSplittable(StatisticSumResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class MeanOfGapsStatUnsplittable(Statistic):
    #IS_MEMOIZABLE = False

    #def _init(self, bpWindow='100', **kwArgs):
    #    self._bpWindow = int(bpWindow)
    
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)    
    def _compute(self):
        gaps = self._children[0].getResult()['Result']
        return gaps.mean()
        #if len(points)==0:
        #    return 1.0
        #else:
                    
    def _createChildren(self):
        self._addChild(PointGapsStat(self._region, self._track) )
        self._addChild(FormatSpecStat(self._region, self._track, TrackFormatReq(dense=False, interval=False) ) )
        #self._addChild( BinSizeStat(self._region, self._track) )