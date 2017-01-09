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
from gold.util.CommonFunctions import parseDirPath
from gold.util.CommonFunctions import createDirPath
from quick.application.ProcTrackOptions import ProcTrackOptions
from quick.util.GenomeInfo import GenomeInfo

class ProcTrackNameSource(object):
    def __init__(self, genome, fullAccess=False, avoidLiterature=True, includeParentTrack=True):
        self._genome = genome
        self._fullAccess = fullAccess
        self._avoidLiterature = avoidLiterature
        self._includeParentTrack = includeParentTrack
    
    def __iter__(self):
        return self.yielder([])
    
    def yielder(self, curTn, level=0):
        if self._avoidLiterature and curTn == GenomeInfo.getPropertyTrackName(self._genome, 'literature'):
            return
        
        for subtype in ProcTrackOptions.getSubtypes(self._genome, curTn, self._fullAccess):
            #if self._avoidLiterature and subtype == 'Literature':
            
            if subtype[0] in ['.','_']:
                continue

            newTn = curTn + [subtype]

            doBreak = False
            for subTn in self.yielder(newTn, level=level+1):
                yield subTn

        if self._includeParentTrack or level > 0:
            if ProcTrackOptions.isValidTrack(self._genome, curTn, self._fullAccess):
                yield curTn
