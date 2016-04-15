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

from gold.util.CustomExceptions import IncompatibleTracksError
from gold.formatconversion.AllFormatConverters import getFormatConverters
from gold.track.TrackFormat import TrackFormatReq, NeutralTrackFormatReq

class SampleTrackWithConverters:
    IS_MEMOIZABLE = False
    trackNo = 0
    
    def __init__(self, trackView, ignoreTrackFormat = False):
        self._tv = trackView
        self.trackName = ['dummy' + str(SampleTrackWithConverters.trackNo)]
        self._ignoreTrackFormat = ignoreTrackFormat
        SampleTrackWithConverters.trackNo += 1
        self.formatConverters = None
        self._trackFormatReq = NeutralTrackFormatReq()

    def getTrackView(self, region):
        if self.formatConverters is None:
            self.formatConverters = getFormatConverters(self._tv.trackFormat, self._trackFormatReq)
        
        if self.formatConverters == []:
            raise IncompatibleTracksError('Track with format: '\
                                          + str(self._tv.trackFormat) +
                                          ('(' + self._tv.trackFormat._val + ')' if self._tv.trackFormat._val else '') + \
                                          ' does not satisfy ' + str(self._trackFormatReq))
        
        if not self.formatConverters[0].canHandle(self._tv.trackFormat, self._trackFormatReq):
            raise IncompatibleTracksError(getClassName(self.formatConverters[0]) +\
                                          ' does not support conversion from ' + str(self._tv.trackFormat) + \
                                          ' to ' + str(self._trackFormatReq))
        return self.formatConverters[0].convert(self._tv[region.start - self._tv.genomeAnchor.start : \
                                                         region.end - self._tv.genomeAnchor.start])

    def addFormatReq(self, requestedTrackFormat):
        prevFormatReq = self._trackFormatReq
        self._trackFormatReq = TrackFormatReq.merge(self._trackFormatReq, requestedTrackFormat)
        if self._trackFormatReq is None:
            raise IncompatibleTracksError(str(prevFormatReq ) + \
                                          ' is incompatible with additional ' + str(requestedTrackFormat))
        
    
    #def addFormatReq(self, requestedTrackFormat):
        #if not self._ignoreTrackFormat and requestedTrackFormat != None and not requestedTrackFormat.isCompatibleWith(self._tv.trackFormat):
            #raise IncompatibleTracksError(str(requestedTrackFormat) + ' not compatible with ' + str(self._tv.trackFormat))
