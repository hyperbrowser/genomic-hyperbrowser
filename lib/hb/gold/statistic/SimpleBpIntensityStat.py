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
from gold.statistic.DiscreteMarksStat import DiscreteMarksStat
from gold.statistic.SimpleDiscreteMarksIntensityStat import SimpleDiscreteMarksIntensityStat
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq

class SimpleBpIntensityStat(MagicStatFactory):
    pass

#class SimpleBpIntensityStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class SimpleBpIntensityStatUnsplittable(Statistic):    
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2, numDiscreteVals=None, **kwArgs):
        self._numDiscreteVals = numDiscreteVals
        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, **kwArgs)

    def _compute(self):
        discreteMarks = self._children[0].getResult()
        discreteMarksIntensities = self._children[1].getResult()
        return discreteMarksIntensities[discreteMarks]
    
    def _createChildren(self):
        self._addChild( DiscreteMarksStat(self._region, self._track, self._track2, numDiscreteVals=self._numDiscreteVals, printIntervals=True) )
        self._addChild( SimpleDiscreteMarksIntensityStat(self._region, self._track, self._track2, numDiscreteVals=self._numDiscreteVals) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, interval=False)) )