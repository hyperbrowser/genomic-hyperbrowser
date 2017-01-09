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

import unittest
from quick.origdata.GERegionBoundaryFilter import GERegionBoundaryFilter
from quick.application.UserBinSource import GlobalBinSource
from test.gold.origdata.common.Asserts import assertDecorator
from functools import partial

class TestGERegionBoundaryFilter(unittest.TestCase):
    def setUp(self):
        pass    
    
    def _assertFilter(self, filteredList, unfilteredList):
        assertDecorator(partial(GERegionBoundaryFilter, regionBoundaryIter=GlobalBinSource('TestGenome')), \
                                self.assertEqual, filteredList, unfilteredList)
    
    def testFilter(self):
        self._assertFilter([['TestGenome','chr21',2,5],['TestGenome','chrM',3,8]], [['TestGenome','chr21',2,5],['TestGenome','chrM',3,8]])
        self._assertFilter([['TestGenome','chrM',3,8]], [['Test','chr21',2,5],['TestGenome','chrM',3,8]])
        self._assertFilter([['TestGenome','chr21',2,5]], [['TestGenome','chr21',2,5],['TestGenome','chrTest',3,8]])
        self._assertFilter([['TestGenome','chrM',3,8]], [['TestGenome','chr21',-2,5],['TestGenome','chrM',3,8]])
        
if __name__ == "__main__":
    unittest.main()