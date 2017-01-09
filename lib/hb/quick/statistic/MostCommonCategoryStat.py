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

class MostCommonCategoryStat(MagicStatFactory):
    pass

#class MostCommonCategoryStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class MostCommonCategoryStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    
    def _compute(self):
        
        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        finished = False
        #print "length: ",len(list(tv1)), len(list(tv2))
        it = iter(tv1)
        try:
            
            te1 = it.next() # in Python 2.x
        except StopIteration:
            #print 'No data for Track 1'
            return 'No data for Track 1'
        resultStr = ''
        for te2 in tv2:
            markDict = {}
            if te1.start() > te2.end():
                continue
            
            if te2.end()>te1.start() >= te2.start():
                while te1.start() < te2.end():
                    try:
                        if markDict.has_key(te1.val()):
                            markDict[te1.val()] +=1
                        else:
                            markDict[te1.val()] = 1
                        te1 = it.next() # in Python 2.x
                    except StopIteration:
                        finished = True
                        break
                
                
                max = 0
                tempresultStr =''
                for mark in markDict.keys():
                    if markDict[mark] > max:
                        tempresultStr = mark
                        max = markDict[mark]
                    elif markDict[mark] == max:
                        tempresultStr+=', '+mark
                
                resultStr+=' ('+ tempresultStr+') '
                if finished:
                    return resultStr
                
            else:
                while te1.start() < te2.start() :
                    try:
                        te1 = it.next() # in Python 2.x
                    except StopIteration:
                        return resultStr   
        return resultStr
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=False, val='category') ) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(interval=True, val='category', allowOverlaps=True) ) )

