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
from gold.statistic.AbstractHistStat import AbstractHistStatUnsplittable

class DiscreteMarksHistStat(MagicStatFactory):
    pass

#class DiscreteMarksHistStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            

class DiscreteMarksHistStatUnsplittable(AbstractHistStatUnsplittable):    
    def __init__(self, region, track, track2=None, numDiscreteVals=None, marksStat='MarksListStat', **kwArgs):
        self._numDiscreteVals = numDiscreteVals
        self._marksStat = marksStat

        self._numHistBins = int(self._numDiscreteVals)

        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, marksStat=marksStat, **kwArgs)
    
    def _createChildren(self):
        self._addChild( DiscreteMarksStat(self._region, self._track, (self._track2 if hasattr(self,'_track2') else None),\
                                          numDiscreteVals=self._numDiscreteVals, marksStat=self._marksStat) )

