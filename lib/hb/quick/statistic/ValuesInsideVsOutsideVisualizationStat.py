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
from gold.statistic.ProportionCountStat import ProportionCountStat
from gold.statistic.Statistic import Statistic, StatisticSplittable
from quick.result.model.ResultTypes import GlobalVisualizationResultType
from quick.statistic.MeanInsideOutsideStat import MeanInsideOutsideStat


#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq

class ValuesInsideVsOutsideVisualizationStat(MagicStatFactory):
    pass

class ValuesInsideVsOutsideVisualizationStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = GlobalVisualizationResultType(self._childResults)
        return self._result
            
class ValuesInsideVsOutsideVisualizationStatUnsplittable(Statistic):    
    def _compute(self):
        insideOutsideDict = self._children[0].getResult()
        inside = insideOutsideDict['MeanInsideSegments']
        outside =insideOutsideDict['MeanOutsideSegments']
        coverage = self._children[1].getResult()
        
        return (self._region, inside, outside,coverage)
        #use GlobalVisualizationResult also here..
        
        
    def _createChildren(self):
        #self._track: defines inside vs outside
        #self._track2: provides values        
        self._addChild( MeanInsideOutsideStat(self._region, self._track, self._track2) )
        self._addChild( ProportionCountStat(self._region, self._track) )
