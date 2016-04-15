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

from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GenomeElement import GenomeElement
from gold.util.CustomExceptions import InvalidFormatError
from gold.util.CommonConstants import BINARY_MISSING_VAL
import numpy

class BedGraphGenomeElementSource(GenomeElementSource):
    _VERSION = '1.5'
    FILE_SUFFIXES = ['bedgraph']
    FILE_FORMAT_NAME = 'bedGraph'

    _numHeaderLines = 0
        
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, fn, *args, **kwArgs):
        GenomeElementSource.__init__(self, fn, *args, **kwArgs)
        
        f = open(fn)
        trackDef = f.readline()
        if trackDef.startswith('track type=bedGraph'):
            numHeaderLines = 1
        else:
            numHeaderLines = 0
            
        headerLine = f.readline()
        while headerLine.startswith('#'):
            numHeaderLines += 1
            headerLine = f.readline()
        
        self._numHeaderLines = numHeaderLines
        
    def _next(self, line):
        cols = line.split('\t')
        
        ge = GenomeElement(self._genome)
        ge.chr = self._checkValidChr(cols[0])
        ge.start = int(cols[1])
        ge.end = int(cols[2])
        self._parseVal(ge, cols[3])
        
        return ge
    
    def _parseVal(self, ge, valStr):
        ge.val = numpy.float(self._handleNan(valStr))

class BedGraphTargetControlGenomeElementSource(BedGraphGenomeElementSource):
    _VERSION = '1.6'
    FILE_SUFFIXES = ['targetcontrol.bedgraph']
    FILE_FORMAT_NAME = 'target/control bedGraph'
    
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
        
    def _parseVal(self, ge, valStr):
        if self._handleNan(valStr) == 'nan':
            ge.val = BINARY_MISSING_VAL
        elif valStr == '0':
            ge.val = False
        elif valStr == '1':
            ge.val = True
        else:
            raise InvalidFormatError('Could not parse value: ' + valStr + ' as target/control.') 
        
    def getValDataType(self):
        return 'int8'
