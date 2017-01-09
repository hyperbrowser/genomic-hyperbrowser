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
from gold.statistic.Statistic import Statistic, StatisticDictSumResSplittable, OnlyGloballySplittable
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.ThreeWayExpectedBpOverlapStat import ThreeWayExpectedBpOverlapStat
from quick.statistic.BinSizeStat import BinSizeStat
from gold.util.CommonFunctions import isIter
class ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat(MagicStatFactory):
    pass

class ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStatSplittable(StatisticDictSumResSplittable, OnlyGloballySplittable):
    pass
    #def _combineResults(self):
    #    self._result = OrderedDict([ (key, smartSum([res[key] for res in self._childResults])) for key in self._childResults[0] ])
    #    print 'here:    '
    #    print OrderedDict([ (key, [res[key] for res in self._childResults]) for key in self._childResults[0] ])
    #    print self._result

class ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStatUnsplittable(Statistic):
    def _compute(self):
        #origRes = ThreeWayExpectedBpOverlapStatUnsplittable._compute(self)
        assert not isIter(self._region)
        #print 'REG: ',self._region
        origRes = self._children[0].getResult()
        binSize = self._children[1].getResult()
        return dict([(key+'_GivenBinPresence', value*binSize) for key,value in origRes.items()])
        
    def _createChildren(self):
        self._addChild( ThreeWayExpectedBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        
    #def _createChildren(self):
    #    self._addChild( ThreeWayProportionalBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )