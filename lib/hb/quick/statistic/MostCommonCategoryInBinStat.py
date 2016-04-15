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
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class MostCommonCategoryInBinStat(MagicStatFactory):
    pass

#class MostCommonCategoryStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class MostCommonCategoryInBinStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    
    def _compute(self):
        markDict = {}
        tv = self._children[0].getResult()
        
        for te in tv:
            if markDict.has_key(te.val()):
                markDict[te.val()] +=1
            else:
                markDict[te.val()] = 1
                        
        max = 0
        resultStr =''
        for mark in markDict.keys():
            if markDict[mark] > max:
                resultStr = mark
                max = markDict[mark]
            elif markDict[mark] == max:
                resultStr+=', '+mark
               
        return resultStr
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=False, val='category') ) )
        
