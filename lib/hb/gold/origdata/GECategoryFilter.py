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

class GECategoryFilter(GEFilter):
    def __init__(self, geSource, filterList, strict=True):
        GEFilter.__init__(self, geSource)
        self._filterSet = set(filterList)
        self._strict = strict
    
    def next(self):
        nextEl = self._geIter.next()
        while (self._strict and not nextEl.val in self._filterSet) or \
            (not self._strict and not any(x in nextEl.val for x in self._filterSet)):
            nextEl = self._geIter.next()
        return nextEl
    