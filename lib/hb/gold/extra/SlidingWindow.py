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

import math
from gold.util.CustomExceptions import NotSupportedError
from copy import copy
from gold.track.TrackView import TrackViewSlider

class SlidingWindow:
    def __init__(self, source, windowSize):
        if windowSize % 2 == 0:
            raise NotSupportedError
        self._windowSize = windowSize
        self._source = source        
        self._sourceIter = None
        self._sourceEmpty = False
    
    def __iter__(self):
        self = copy(self)
        self._sourceIter = self._source.__iter__()
        self._window = []
        return self
    
    def _next(self):
        if len(self._window) == 0 and self._sourceEmpty:
            raise StopIteration

        if len(self._window) == self._windowSize or self._sourceEmpty:
            self._window.pop(0)
        
        try:
            self._window.append( self._sourceIter.next() )
        except StopIteration:
            self._sourceEmpty = True
            
        return self._window
    
    def next(self):
        while True:
            window = self._next()
            if len(window) >= self._minWindowSize():
                return window
        
    def _minWindowSize(self):
        return math.ceil((self._windowSize + 1) / 2.0)
    
    def __len__(self):
        if self._sourceIter == None:
            self._sourceIter = self._source.__iter__()
        return len(self._source)
    
class TrackViewBasedSlidingWindow:
    def __init__(self, trackView, windowSize):
        if windowSize % 2 == 0:
            raise NotSupportedError
        self._windowSize = windowSize
        self._trackView = trackView
        self._trackViewSlider = TrackViewSlider(trackView)
    
    def __iter__(self):
        flankSize = self._windowSize / 2
        tvLen = len(self._trackView)
        for midPos in xrange(0, tvLen):
            if midPos%1e6==0:
                print '.',
            from config.Config import DebugConfig
            if DebugConfig.VERBOSE and midPos%1e3==0:
                print ',',
                            
            start = max(0, midPos - flankSize)
            end = min(tvLen, midPos + flankSize + 1)
            #yield self._trackView[start:end]
            yield self._trackViewSlider.slideTo(start,end)
            
#class GeSlidingWindowBpSize(SlidingWindow):
    
