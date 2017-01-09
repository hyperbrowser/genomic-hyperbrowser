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
from gold.statistic.FormatSpecStat import FormatSpecStat
from gold.track.TrackFormat import TrackFormatReq
#from gold.statistic.GeneralTwoTracksIterateValsStat import GeneralTwoTracksIterateValsStatUnsplittable

class GeneralTwoCatTracksStat(MagicStatFactory):
    pass

#class GeneralTwoCatTracksStatUnsplittable(GeneralTwoTracksIterateValsStatUnsplittable):
class GeneralTwoCatTracksStatUnsplittable(Statistic):
    STORE_CHILDREN = True
    
    #def __init__(self, region, track, track2, rawStatistic=None, **kwArgs):
    #    GeneralTwoTracksIterateValsStatUnsplittable.__init__(self, region, track, track2, \
    #                                                         rawStatistic=rawStatistic, \
    #                                                         storeChildren=self.STORE_CHILDREN, \
    #                                                         **kwArgs)
    #    
    def _createChildren(self):
        #GeneralTwoTracksIterateValsStatUnsplittable._createChildren(self)
        self._addChild( FormatSpecStat(self._region, self._track, TrackFormatReq(val='category')) )
        self._addChild( FormatSpecStat(self._region, self._track2, TrackFormatReq(val='category')) )
