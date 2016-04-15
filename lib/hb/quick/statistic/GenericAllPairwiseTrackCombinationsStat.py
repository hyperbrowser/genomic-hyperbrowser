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
from gold.statistic.Statistic import MultipleRawDataStatistic
#from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class GenericAllPairwiseTrackCombinationsStat(MagicStatFactory):
    pass

#class ThreeWayProportionalBpOverlapStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericAllPairwiseTrackCombinationsStatUnsplittable(MultipleRawDataStatistic):        
    def _compute(self):
        #rawResults = [child.getResult() for child in self._children]        
        #for res in rawResults:
        
        #return dict([ (resKey, self._childDict[resKey].getResult()) for resKey in self._childDict])
        fullResult = {}        
        for resKey in self._childDict:
            res = self._childDict[resKey].getResult()
            if isinstance(res, dict):
                for subResKey in res:                    
                    fullResult[ '_'.join([resKey,subResKey]) ] = res[subResKey]
            else:
                fullResult[ resKey ] = res
        
        return fullResult
    
    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
        
    def _createChildren(self):
        rawStat = self.getRawStatisticClass( self._kwArgs['rawStatistic'] )
        self._childDict = {}
        
        t = self._tracks
        for i in range(len(t)):
            for j in range(i+1,len(t)):
                from gold.util.CommonFunctions import prettyPrintTrackName                
                resKey = ' vs '.join([prettyPrintTrackName(track.trackName, shortVersion=True) for track in [t[i],t[j]] ])
                self._childDict[resKey] = self._addChild( rawStat(self._region, t[i], t[j], self._getTrackFormatReq() ) )