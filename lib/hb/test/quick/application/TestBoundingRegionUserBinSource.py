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
from test.util.Asserts import TestCaseWithImprovedAsserts
from gold.track.GenomeRegion import GenomeRegion
from quick.application.BoundingRegionUserBinSource import BoundingRegionUserBinSource

class TestBoundingRegionUserBinSource(TestCaseWithImprovedAsserts):
    def setUp(self):
        pass
    
    def _assertIntersect(self, assertRegs, chr, regs1, regs2):
        genomeRegs1 = [GenomeRegion('TestGenome', chr, start, end) for start, end in regs1]
        genomeRegs2 = [GenomeRegion('TestGenome', chr, start, end) for start, end in regs2]
        genomeAssertRegs = [GenomeRegion('TestGenome', chr, start, end) for start, end in assertRegs]
        
        resultRegs = BoundingRegionUserBinSource.getAllIntersectingRegions\
            ('TestGenome', chr, genomeRegs1, genomeRegs2)
        
        #print [str(x) for x in resultRegs]
        self.assertListsOrDicts(genomeAssertRegs, resultRegs)
    
    def testGetAllIntersectingRegions(self):
        self._assertIntersect([], 'chr21', [], [])
        self._assertIntersect([], 'chr21', [], [[3,8]])
        self._assertIntersect([], 'chr21', [[0,6]], [])
        self._assertIntersect([[3,6]], 'chr21', [[0,6]], [[3,8]])
        self._assertIntersect([[3,6],[6,7]], 'chr21', [[2,6],[6,7]], [[3,8]])
        self._assertIntersect([[5,6],[7,8],[9,10]], 'chr21', [[5,10]], [[0,6],[7,8],[9,10]])
        self._assertIntersect([[0,10]], 'chr21', [[0,10]], [[0,10]])
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestBoundingRegionUserBinSource().debug()
    unittest.main()