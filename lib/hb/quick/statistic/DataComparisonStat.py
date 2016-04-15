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
from gold.statistic.XYPairStat import XYPairStat

class DataComparisonStat(MagicStatFactory):
    pass

#class DataComparisonStatStatSplittable(StatisticSumResSplittable):
#    pass
            
class DataComparisonStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, track1SummarizerName, track2SummarizerName, *args, **kwArgs):
        Statistic.__init__(self, region, track, track2, track1SummarizerName=track1SummarizerName, \
                           track2SummarizerName=track2SummarizerName, allowIdenticalTracks=True, **kwArgs)
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        assert( track1SummarizerName in STAT_CLASS_DICT and track2SummarizerName in STAT_CLASS_DICT)
        
        self._track1Summarizer = STAT_CLASS_DICT[track1SummarizerName]
        self._track2Summarizer = STAT_CLASS_DICT[track2SummarizerName]
        
    def _compute(self):
        res = self._children[0].getResult()
        return res #self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild( XYPairStat(self._region, self._track, self._track2, self._track1Summarizer, self._track2Summarizer) )
