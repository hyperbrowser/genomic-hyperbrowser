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
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class PercentageChangeStat(MagicStatFactory):
    "Counts bps covered by track. If specified with intra-track overlaps, it will for each bp count the number of times the bp is covered by a track element."
    pass

class PercentageChangeStatSplittable(StatisticSumResSplittable):
    pass
            
class PercentageChangeStatUnsplittable(Statistic):    
    def _compute(self):
        
        companyTrack = self._children[0].getResult()
        companyStart = companyTrack.startsAsNumpyArray()
        companyVals = companyTrack.valsAsNumpyArray()
        
        calendarTrack = self._children[1].getResult()
        calStart = calendarTrack.startsAsNumpyArray()
        calEnd = calendarTrack.endsAsNumpyArray()
        
        index = 0
        result = 1.0
        companyIndex = len(companyTrack)
        try:
            for i in range(len(calStart)):
                rangeList = range(calStart[i], calEnd[i])
                if len(rangeList)==0:
                    continue
                valList = []
                while index < len(companyStart):
                    if companyStart[index] in rangeList:
                        valList.append(companyVals[index])
                    elif companyStart[index]>rangeList[-1]:
                        break
                    index+=1
                
                if len(valList)>1:
                    change = 1.0 + (valList[-1] - valList[0])/valList[0]
                    result *= change
        except:
            pass
        
        return (result*100.0) -100.0
    
        
        
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(interval=True, allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
