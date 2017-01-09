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
from gold.statistic.SimilarSegmentStat import SimilarSegmentStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSimilarSegmentStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SimilarSegmentStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute(0, SampleTV( segments=[] ), \
                               SampleTV( segments=[] ), \
                               maxRelDifference=0.5, maxAbsDifference=5, tail='different')
        self._assertCompute(0, SampleTV( segments=[] ), \
                               SampleTV( segments=[[2,5]] ), \
                               maxRelDifference=0.5, maxAbsDifference=5, tail='different')
        self._assertCompute(0, SampleTV( segments=[[10,30]] ), \
                               SampleTV( segments=[] ), \
                               maxRelDifference=0.5, maxAbsDifference=5, tail='different')
        self._assertCompute(1, SampleTV( segments=[[10,30], [60,80], [90,95]] ), \
                               SampleTV( segments=[[2,5], [9,11], [12,28], [29,35], [40,50], [55,76], [89,91]] ), \
                               maxRelDifference=0.5, maxAbsDifference=5, tail='different')
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        self.test_compute()
    
#class TestSimilarSegmentStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = SimilarSegmentStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestSimilarSegmentStatSplittable().debug()
    #TestSimilarSegmentStatUnsplittable().debug()
    unittest.main()