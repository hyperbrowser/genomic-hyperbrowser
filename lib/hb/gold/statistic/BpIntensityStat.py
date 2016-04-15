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
from gold.statistic.MultiDiscreteMarkFlattenerStat import MultiDiscreteMarkFlattenerStat
from gold.statistic.SimpleBpIntensityStat import SimpleBpIntensityStatUnsplittable
from gold.statistic.DiscreteMarksIntensityStat import DiscreteMarksIntensityStat

class BpIntensityStat(MagicStatFactory):
    pass

#class BpIntensityStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class BpIntensityStatUnsplittable(SimpleBpIntensityStatUnsplittable):    
    IS_MEMOIZABLE = False
    VERBOSE_INTENSITY_CREATION = True

    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, \
                 controlTrackNameList=None, **kwArgs):
            assert controlTrackNameList is not None
            self._numDiscreteVals = numDiscreteVals
            self._reducedNumDiscreteVals = reducedNumDiscreteVals
            self._controlTrackNameList = controlTrackNameList
            Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, \
                               reducedNumDiscreteVals=reducedNumDiscreteVals, controlTrackNameList=controlTrackNameList, **kwArgs)

    def _createChildren(self):
        self._addChild( MultiDiscreteMarkFlattenerStat(self._region, self._track, numDiscreteVals=self._numDiscreteVals, \
                                                       reducedNumDiscreteVals=self._reducedNumDiscreteVals, controlTrackNameList=self._controlTrackNameList) )
        self._addChild( DiscreteMarksIntensityStat(self._region, self._track, numDiscreteVals=self._numDiscreteVals, \
                                                   reducedNumDiscreteVals=self._reducedNumDiscreteVals, controlTrackNameList=self._controlTrackNameList) )