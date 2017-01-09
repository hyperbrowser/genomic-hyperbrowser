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

import os
#from numpy import memmap
from gold.util.CommonFunctions import createDirPath
from gold.track.CommonMemmapFunctions import parseMemmapFileFn
from gold.track.SmartMemmap import SmartMemmap
from gold.track.BoundingRegionShelve import BoundingRegionShelve, isBoundingRegionFileName

class TrackData(dict):
    def __init__(self, other=None):
        if other is not None:
            dict.__init__(self, other)
        else:
            dict.__init__(self)
        
        self.boundingRegionShelve = None

class TrackSource:
    def __init__(self):
        self._chrInUse = None
        self._fileDict = {}
    
    def getTrackData(self, trackName, genome, chr, allowOverlaps, forceChrFolders=False):
        trackData = TrackData()
        
        brShelve = BoundingRegionShelve(genome, trackName, allowOverlaps)        
        if not forceChrFolders and brShelve.fileExists():
            chr = None
        
        dir = createDirPath(trackName, genome, chr, allowOverlaps)

        for fn in os.listdir(dir):
            fullFn = dir + os.sep + fn
            
            if fn[0] == '.' or os.path.isdir(fullFn):
                continue
                
            if isBoundingRegionFileName(fn):
                if fullFn not in self._fileDict:
                    self._fileDict[fullFn] = brShelve
                trackData.boundingRegionShelve = self._fileDict[fullFn]
                continue
            
            prefix, elementDim, dtypeDim, dtype = parseMemmapFileFn(fn)
            
            assert prefix not in trackData
            trackData[prefix] = self._getFile(chr, dir, fullFn, elementDim, dtype, dtypeDim)
        
        return trackData
    
    def _getFile(self, chr, dir, fullFn, elementDim, dtype, dtypeDim):
        if chr is not None and chr != self._chrInUse:
            self._fileDict = {}
            self._chrInUse = chr
            
        if fullFn not in self._fileDict:
            self._fileDict[fullFn] = SmartMemmap(fullFn, elementDim=elementDim, dtype=dtype, dtypeDim=dtypeDim, mode='r')
        
        return self._fileDict[fullFn]        
