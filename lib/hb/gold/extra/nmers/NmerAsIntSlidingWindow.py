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

from gold.extra.nmers.NmerTools import NmerTools

class NmerAsIntSlidingWindow:
    def __init__(self, n, bpIter):
        self._n = n
        self._bpIter = bpIter
        
    def __iter__(self):
        bps = 'acgtACGT'
        nmer2int = dict( zip(bps, [NmerTools.nmerAsInt(bp.lower()) for bp in bps]) )
        
        numBps = 0
        validBps = 0
        curNmerAsInt = 0
        for bp in self._bpIter:
            numBps += 1
            if bp in bps:
                validBps += 1
                curNmerAsInt = (curNmerAsInt % 4**(self._n-1)) * 4 + nmer2int[bp]
            else:
                validBps = 0
                curNmerAsInt = 0
            
            if validBps >= self._n:
                yield curNmerAsInt
            elif numBps >= self._n:
                yield None #menas not valid value
            #else we are filling up window from start of sequence..