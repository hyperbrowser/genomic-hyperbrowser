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

from gold.origdata.GESourceWrapper import GESourceWrapper
from copy import copy

class GenomeElementSorter(GESourceWrapper):
    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._geIter = None
        self._sortedElements = None
        
    def __iter__(self):
        if True in [attrs in self._geSource.getPrefixList() for attrs in ['start', 'end']]:
            if self._sortedElements is None:
                #self._sortedElements = [deepcopy(el) for el in self._geSource]
                self._sortedElements = [el.getCopy() for el in self._geSource]
                self._sortedElements.sort(key=lambda el: [el.genome, el.chr, el.start, el.end])
                
            self._geIter = self._sortedElements.__iter__()
            return copy(self)
        else:
            return self._geSource.__iter__()        
    
    def next(self):
        el = self._geIter.next()
        return el
        
    def __len__(self):
        if self._sortedElements is None:
            return sum(1 for el in self)
        else:
            return len(self._sortedElements)