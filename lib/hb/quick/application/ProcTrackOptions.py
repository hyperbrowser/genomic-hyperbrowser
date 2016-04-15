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
from gold.util.CommonFunctions import createDirPath
from gold.description.TrackInfo import TrackInfo
from gold.track.BoundingRegionShelve import isBoundingRegionFileName
from quick.util.GenomeInfo import GenomeInfo

class ProcTrackOptions:
    @staticmethod
    def _getDirContents(genome, trackName):
        dirPath = createDirPath(trackName, genome)
#        print '<br>',"PATH: ", dirPath,'<br>'
        return os.listdir(dirPath) if os.path.exists(dirPath) else []

    @staticmethod
    def getSubtypes(genome, trackName, fullAccess=False):
        dirPath = createDirPath(trackName, genome)
        subtypes = [fn for fn in ProcTrackOptions._getDirContents(genome, trackName) \
                    if not (fn[0] in ['.','_'] or os.path.isfile(dirPath + os.sep + fn) \
                    or GenomeInfo.isValidChr(genome, fn))]

        #fixme, just temporarily:, these dirs should start with _
        subtypes= [x for x in subtypes if not x in ['external','ucsc'] ]

        if not fullAccess and not ProcTrackOptions._isLiteratureTrack(genome, trackName):
            subtypes = [x for x in subtypes if not TrackInfo(genome, trackName+[x]).private]

        return sorted(subtypes, key=str.lower)

    @staticmethod
    def _isLiteratureTrack(genome, trackName):
        return ':'.join(trackName).startswith( ':'.join(GenomeInfo.getPropertyTrackName(genome, 'literature')) )

    @staticmethod
    def _hasPreprocessedFiles(genome, trackName):
        for fn in ProcTrackOptions._getDirContents(genome, trackName):
            if GenomeInfo.isValidChr(genome, fn) or isBoundingRegionFileName(fn):
                return True

    @staticmethod
    def isValidTrack(genome, trackName, fullAccess=False):
        if not TrackInfo(genome, trackName).isValid(fullAccess):
            return False

        if ProcTrackOptions._hasPreprocessedFiles(genome, trackName):
            return True
        
        return  False
        #       len([fn for fn in ProcTrackOptions._getDirContents(genome, trackName) \
        #            if GenomeInfo.isValidChr(genome, fn) ]) > 0
