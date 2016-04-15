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
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from gold.util.CommonFunctions import isIter

class RawDataStat(MagicStatFactory):
    def __new__(cls, region, track, trackFormatReq, **kwArgs):
        assert isinstance(trackFormatReq, TrackFormatReq)
        track.addFormatReq(trackFormatReq)
        return MagicStatFactory.__new__(cls, region, track, **kwArgs)
        #return MagicStatFactory.__new__(cls, region, track, trackFormatReq=trackFormatReq, **kwArgs)

class RawDataStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def __init__(self, region, track, **kwArgs):
        if isIter(region):
            raise SplittableStatNotAvailableError()

        #super(self.__class__, self).__init__(region, track, trackFormatReq=trackFormatReq, **kwArgs)
        super(self.__class__, self).__init__(region, track, **kwArgs)
        #self._trackFormatReq = trackFormatReq

    def _compute(self):
        return self._track.getTrackView(self._region)

    def _createChildren(self):
        #if self._trackFormatReq is None:
        #    print 'dense'
        self._children = []
        #self._track.addFormatReq(self._trackFormatReq)

    def _afterComputeCleanup(self):
        if self.hasResult():
            #print 'clean up for reg: ',self._region ,'with trackname: ',self._track.trackName
            del self._result
    
    def _updateInMemoDict(self, statKwUpdateDict):
        pass
