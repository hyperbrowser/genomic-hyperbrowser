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
from gold.statistic.MultitrackCoverageDepthStat import MultitrackCoverageDepthStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestMultitrackCoverageDepthStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MultitrackCoverageDepthStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[10,100] ), \
                                       SampleTV( anchor=[10,100], numElements=10 ))
        self._assertIncompatibleTracks(SampleTV( anchor=[10,100], numElements=10 ), \
                                       SampleTV_Num( anchor=[10,100] ))
        self._assertIncompatibleTracks(SampleTV( starts=False, anchor=[10,100], numElements=10 ), \
                                       SampleTV( starts=False, anchor=[10,100], numElements=10 ))

    def test_compute(self):
        self._assertCompute([7, 7, 7, 1], \
                            SampleTV( segments=[[2,4], [10,14], [18,20]], anchor=[1,22] ), \
                            SampleTV( segments=[[1,3], [9,11], [17,21]], anchor=[1,22] ),\
                            SampleTV( segments=[[1,5], [8,10], [20,22]], anchor=[1,22] ),\
                            assertFunc=self.assertListsOrDicts)
#         self._assertCompute({ 'Both':27, 'Neither':30, 'Only1':33, 'Only2':0 }, \
#                             SampleTV( segments=[[10,20], [20,70]], anchor=[10,100] ), \
#                             SampleTV( segments=[[15,25], [30,47]], anchor=[10,100] ),\
#                             assertFunc=self.assertListsOrDicts)
        self._assertCompute([90, 0, 0, 0], \
                            SampleTV( segments=[], anchor=[10,100] ), \
                            SampleTV( segments=[], anchor=[10,100] ),\
                            SampleTV( segments=[], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([RawDataStatUnsplittable] * 2, \
    #                               SampleTV_Num( anchor=[10,100] ), \
    #                               SampleTV_Num( anchor=[10,100] ))

class TestMultitrackCoverageDepthStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = MultitrackCoverageDepthStat

    def test_compute(self):
        self._assertCompute([7, 7, 7, 1], \
                            SampleTV( segments=[[2,4], [10,14], [18,20]], anchor=[1,22] ), \
                            SampleTV( segments=[[1,3], [9,11], [17,21]], anchor=[1,22] ),\
                            SampleTV( segments=[[1,5], [8,10], [20,22]], anchor=[1,22] ),\
                            assertFunc=self.assertListsOrDicts)
#         self._assertCompute({ 'Both':15, 'Neither':125, 'Only1':35, 'Only2':5 }, \
#                             SampleTV( segments=[[10,20], [130,170]], anchor=[10,190] ), \
#                             SampleTV( segments=[[15,25], [137,147]], anchor=[10,190] ),\
#                             assertFunc=self.assertListsOrDicts)
        self._assertCompute([180, 0, 0, 0], \
                            SampleTV( segments=[], anchor=[10,190] ), \
                            SampleTV( segments=[], anchor=[10,190] ),\
                            SampleTV( segments=[], anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts)
    
if __name__ == "__main__":
    unittest.main()
