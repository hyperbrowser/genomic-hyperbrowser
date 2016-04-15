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

class SampleTrack(object):
    IS_MEMOIZABLE = False
    trackNo = 0
    
    def __init__(self, trackView, ignoreTrackFormat = False):
        self._tv = trackView
        self.trackName = ['dummy' + str(SampleTrack.trackNo)]
        self._ignoreTrackFormat = ignoreTrackFormat
        SampleTrack.trackNo += 1

    def getTrackView(self, region):
        return self._tv[region.start - self._tv.genomeAnchor.start : region.end - self._tv.genomeAnchor.start]
    
    def addFormatReq(self, requestedTrackFormat):
        if not self._ignoreTrackFormat and requestedTrackFormat != None and not requestedTrackFormat.isCompatibleWith(self._tv.trackFormat):
            raise IncompatibleTracksError(str(requestedTrackFormat) + ' not compatible with ' + str(self._tv.trackFormat))
