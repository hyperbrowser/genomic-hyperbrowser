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

from gold.origdata.GEFilter import GEFilter

class GERegionBoundaryFilter(GEFilter):
    def __init__(self, geSource, regionBoundaryIter):
        GEFilter.__init__(self, geSource)
        self._boundaryRegions = {}
        for region in regionBoundaryIter:
            if not region.chr in self._boundaryRegions:
                self._boundaryRegions[region.chr] = []
            self._boundaryRegions[region.chr].append(region)
    
    def next(self):
        nextEl = self._geIter.next() 
        while nextEl.chr not in self._boundaryRegions or \
            not True in [r.contains(nextEl) for r in self._boundaryRegions[nextEl.chr]]:
            nextEl = self._geIter.next()
        return nextEl
