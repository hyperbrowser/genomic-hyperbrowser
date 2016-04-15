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

import numpy
from copy import copy

from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GtrackComposer import StdGtrackComposer
from gold.origdata.GtrackHeaderExpander import expandHeadersOfGtrackFileAndReturnComposer
from gold.origdata.GESourceWrapper import ElementModifierGESourceWrapper
from gold.util.CustomExceptions import ShouldNotOccurError, InvalidFormatError
from gold.util.CommonConstants import BINARY_MISSING_VAL

class GtrackElementStandardizer(ElementModifierGESourceWrapper):
    def _iter(self):
        self._prevElement = None
        self._id = 0
        
    def _next(self, brt, ge, i):
        if ge.genome is not None:
            if self._genome is None:
                self._genome = ge.genome
            elif self._genome != ge.genome:
                raise InvalidFormatError('GtrackStandardizer does not support GTrack files with more than one genome')
            ge.genome = None
        
        if ge.start is None:
            if i == 0:
                if brt is not None:
                    ge.start = brt.region.start
                else:
                    raise ShouldNotOccurError
            else:
                ge.start = self._prevElement.end
                
        if ge.end is None:
            ge.end = ge.start + 1
            
        if ge.val is None:
            ge.val = numpy.nan
            
        if ge.strand is None:
            ge.strand = BINARY_MISSING_VAL
            
        if ge.id is None:
            ge.id = str(self._id)
            self._id += 1
            
        if ge.edges is None:
            ge.edges = []
        
        self._prevElement = ge
        return ge

    def getBoundingRegionTuples(self):
        return []
        
    def inputIsOneIndexed(self):
        return False
    
    def inputIsEndInclusive(self):
        return False
        
def _commonStandardizeGtrackFile(fn, genome, suffix=None):
    geSource = GenomeElementSource(fn, genome, suffix=suffix, doDenseSortingCheck=False)
    composedFile = StdGtrackComposer( GtrackElementStandardizer(geSource)).returnComposed()
    return expandHeadersOfGtrackFileAndReturnComposer('', genome, strToUseInsteadOfFn=composedFile)
       
def standardizeGtrackFileAndReturnContents(fn, genome=None, suffix=None):
    return _commonStandardizeGtrackFile(fn, genome, suffix=suffix).returnComposed()
    
def standardizeGtrackFileAndWriteToFile(inFn, outFn, genome=None, suffix=None):
    return _commonStandardizeGtrackFile(inFn, genome, suffix=suffix).composeToFile(outFn)
