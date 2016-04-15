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
import numpy
from gold.origdata.GenomeElementSource import GenomeElementSource, BoundingRegionTuple
from gold.track.GenomeRegion import GenomeRegion

class HBFunctionGenomeElementSource(GenomeElementSource):
    _VERSION = '1.2'
    FILE_SUFFIXES = ['hbfunction']
    FILE_FORMAT_NAME = 'HB function'
    _numHeaderLines = 0
    _hasOrigFile = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
    
    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._returnedOneElement = False
        
    def next(self):
        if self._returnedOneElement:
            raise StopIteration
        
        self._genomeElement.chr = 'chr21'
        self._genomeElement.val = 0.0
        self._returnedOneElement = True
        return self._genomeElement
        
    def getValDataType(self):
        return 'float64'

    def getPrefixList(self):
        return ['val']
        
    def getBoundingRegionTuples(self):
        return [BoundingRegionTuple(GenomeRegion(genome='TestGenome', chr='chr21', start=0, end=1), 1)]
