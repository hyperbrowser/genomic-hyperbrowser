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
from gold.track.Track import Track
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import IncompatibleTracksError
from gold.util.CommonFunctions import createDirPath
import os.path
from copy import copy
from gold.statistic.GeneralOneTcTrackStat import GeneralOneTcTrackStatUnsplittable

class GeneralTrack2TcStat(MagicStatFactory):
    pass

#class GeneralTrack2TcStatSplittable(StatisticDictSumResSplittable):
    #pass
            
class GeneralTrack2TcStatUnsplittable(GeneralOneTcTrackStatUnsplittable):        
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'rawStatistic' in kwArgs:
            del kwArgs['rawStatistic']
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        #self._track.formatConverters = 'Dummy' #to avoid check of tracks not being used..
        #self._track2.formatConverters = 'Dummy' #to avoid check of tracks not being used..
        #self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(dense=False, val='tc') ) )
        self._addChild( self._rawStatistic(self._region, self._track, self._track2, **kwArgs) ) #This will actually compute, without any use for it. 
        self._indexOfFirstSubCatChild = len(self._children)

        for subtype2 in ['0','1']:
            #for subtype2 in ['0','1']:
            tn2 = self._track2.trackName + [subtype2]
            if not os.path.exists(createDirPath(tn2, self.getGenome())):
                #logMessage('DID NOT EXIST.. '+createOrigPath(self.getGenome(),tn1))
                raise IncompatibleTracksError
            #else:
            #    logMessage('DID EXIST')
            track2 = Track( tn2)
            track2.formatConverters = self._track2.formatConverters
            #track2 = Track( self._track2.trackName + [subtype2])
            #track2.formatConverters = self._track2.formatConverters
            self._addChild(self._rawStatistic(self._region, self._track, track2, **kwArgs) )
            #logMessage('Came all down..')
        
