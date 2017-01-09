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
# DD

from numpy import zeros

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import MultipleTrackStatistic
from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.BinSizeStat import BinSizeStat


class SumTrackPointsStat(MagicStatFactory):
    pass

# class SumTrackPointsStatSplittable(StatisticSplittable):
#     def _combineResults(self):
#         self._result = RawVisualizationResultType(self._childResults)
#         
    
class SumTrackPointsStatUnsplittable(MultipleTrackStatistic):
    IS_MEMOIZABLE = False
        
    def _compute(self):
        # print 'bin:::' + str(self._binSizeStat.getResult()) + '<br />'
        if self._binSizeStat.getResult() > 1:
            result = zeros(self._binSizeStat.getResult())
            
            # print 'result:::' + str(result)
            for track in self._children[:-1]:
                # print 'track:::' + str(track)
                result += track.getResult().getBinaryBpLevelArray()

            # print result
            exit()

    def _createChildren(self):
        for track in self._tracks:
            self._addChild( RawDataStat(self._region, track, TrackFormatReq(dense=False), **self._kwArgs) )
        self._binSizeStat = self._addChild(BinSizeStat(self._region, self._tracks[0]))
