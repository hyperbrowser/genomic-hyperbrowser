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

    
def getStart(ge):
    return ge.start

def getEnd(ge):
    return ge.end

def getVal(ge):
    return ge.val

def getStrand(ge):
    return ge.strand

def getId(ge):
    return ge.id
    
def getEdges(ge):
    return ge.edges
    
def getWeights(ge):
    return ge.weights
    
def getNone(ge):
    return None

def getPointEnd(ge):
    return ge.start + 1

class GetExtra:
    def __init__(self, prefix):
        self._prefix = prefix
        
    def parse(self, ge):
        if self._prefix == 'extra':
            return ge.extra['extra']
        return getattr(ge, self._prefix)

class GetPartitionStart:
    def __init__(self):
        self._prevEnd = 0
        
    def parse(self, ge):
        #print self, ge, ge.end
        tempPrevEnd = self._prevEnd
        self._prevEnd = ge.end
        return tempPrevEnd
        
def writeNoSlice(mmap, index, ge, parseFunc):
    #print index, ge, parseFunc.__name__, parseFunc(ge)
    mmap[index] = parseFunc(ge)

def writeSliceFromFront(mmap, index, ge, parseFunc):
    #print index, ge, ge.edges, ge.weights, parseFunc.__name__
    geLen = sum(1 for x in parseFunc(ge))
    if geLen >= 1:
        mmap[index][:geLen] = parseFunc(ge)
