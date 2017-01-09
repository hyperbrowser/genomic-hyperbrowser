# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# Diana
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
import numpy
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticListSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class CountDistanceStat(MagicStatFactory):
    "Count distance among points"
    pass

class CountDistanceStatSplittable(StatisticListSumResSplittable):
    pass

class CountDistanceStatUnsplittable(Statistic):
    
    def _compute(self):    
        rawData = self._children[0].getResult()
        
        if len(rawData.startsAsNumpyArray())==0:
            return []
        if len(rawData.startsAsNumpyArray())==1:
            return [1]
        
        numpyStart = numpy.delete(rawData.startsAsNumpyArray(), 0)
        numpyEnd = numpy.delete(rawData.endsAsNumpyArray(), len(rawData.endsAsNumpyArray())-1)
        resNumpyList = numpyStart - numpyEnd
        valResNumpyListBelowValue = (resNumpyList<int(self._kwArgs['maxNum']))
    
        countResList=[]
        c=0
        prevVal=0
        for i in range(0, len(valResNumpyListBelowValue)):            
            if valResNumpyListBelowValue[i]==False:
                countResList.append(c+1)       
                c=0
            else:
                c+=1
                if i == len(valResNumpyListBelowValue)-1:
                    countResList.append(c+1)
            prevVal=c
        
            
        #return numpy.bincount(countResList)
        return countResList 
        
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, \
                                    TrackFormatReq(dense=False, interval=False), **self._kwArgs) )
 