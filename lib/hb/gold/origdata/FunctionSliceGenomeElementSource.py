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

from copy import copy
from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GenomeElement import GenomeElement

class FunctionSliceGenomeElementSource(GenomeElementSource):
    _hasOrigFile = False
    _isSliceSource = True
    
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)
        
    def __init__(self, genome, trackName, region, valSlice, valDataType='float64'):
        GenomeElementSource.__init__(self, None, genome=genome, trackName=trackName)
        self._returnedOneElement = False
        self._valSlice = valSlice
        self._region = region
        self._valDataType = valDataType

    def __iter__(self):
        return copy(self)
        
    def next(self):
        if self._returnedOneElement:
            raise StopIteration
            
        self._returnedOneElement = True
        return GenomeElement(genome=self._genome, chr=self._region.chr, val=self._valSlice)
    
    def getNumElements(self):
        return 1
        
    def getPrefixList(self):
        return ['val']
    
    def getValDataType(self):
        return self._valDataType