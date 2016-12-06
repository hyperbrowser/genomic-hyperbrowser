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
from gold.statistic.AbstractHistStat import AbstractHistStatUnsplittable
from gold.statistic.MultiDiscreteMarkFlattenerStat import MultiDiscreteMarkFlattenerStat

class FlattenedDiscreteMarksHistStat(MagicStatFactory):
    pass

#class FlattenedDiscreteMarksHistStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False

class FlattenedDiscreteMarksHistStatUnsplittable(AbstractHistStatUnsplittable):
    def __init__(self, region, track, track2=None, numDiscreteVals=None, reducedNumDiscreteVals=None, \
                 marksStat='MarksListStat', controlTrackNameList=None, **kwArgs):

        self._numDiscreteVals = numDiscreteVals
        self._reducedNumDiscreteVals = reducedNumDiscreteVals
        self._marksStat = marksStat

        assert controlTrackNameList is not None
        self._controlTrackNameList = controlTrackNameList
        
        numControlTracks = len([x.split('^') for x in controlTrackNameList.split('^^')] \
            if isinstance(controlTrackNameList, basestring) else controlTrackNameList)
        assert numControlTracks > 0

        self._numHistBins = int(reducedNumDiscreteVals)**numControlTracks

        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, \
                           reducedNumDiscreteVals=reducedNumDiscreteVals, marksStat=marksStat, \
                           controlTrackNameList=controlTrackNameList, **kwArgs)

    def _createChildren(self):
        self._addChild( MultiDiscreteMarkFlattenerStat(self._region, self._track,\
                                                       numDiscreteVals=self._numDiscreteVals, reducedNumDiscreteVals=self._reducedNumDiscreteVals,\
                                                       marksStat=self._marksStat, controlTrackNameList=self._controlTrackNameList) )
