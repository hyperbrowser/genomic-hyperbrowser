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
from gold.statistic.NearestPointDistsStat import NearestPointDistsStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestNearestPointDistsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = NearestPointDistsStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( numElements=5 ), SampleTV( numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( ends=[0,5] ), SampleTV( ends=[0,5] ))
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[5,10] ), SampleTV_Num( anchor=[5,10] ))

    def test_compute(self):
        self._assertCompute([], SampleTV( starts=[] ), SampleTV( starts=[1,4,5,6,9] ), 'right',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([None,None], SampleTV( starts=[2,6] ), SampleTV( starts=[] ), 'right',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([2,0,None], SampleTV( starts=[2,6,10] ), SampleTV( starts=[1,4,5,6,9] ), 'right',\
                            assertFunc=self.assertListsOrDicts)

        self._assertCompute([], SampleTV( starts=[] ), SampleTV( starts=[1,4,5,6,9] ), 'left',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([None,None], SampleTV( starts=[2,6] ), SampleTV( starts=[] ), 'left',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([None,0,2], SampleTV( starts=[0,6,10] ), SampleTV( starts=[1,4,5,6,8] ), 'left',\
                            assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([], SampleTV( starts=[] ), SampleTV( starts=[1,4,5,6,9] ), 'both',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([None,None], SampleTV( starts=[2,6] ), SampleTV( starts=[] ), 'both',\
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([1,1,0,1,2,3], SampleTV( starts=[0,2,6,7,10,11] ), SampleTV( starts=[1,4,5,6,8] ), 'both',\
                            assertFunc=self.assertListsOrDicts)

        self._assertCompute([100], SampleTV( starts=[110] ), SampleTV( starts=[10] ), 'both',\
                            assertFunc=self.assertListsOrDicts)
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable] * 2, SampleTV( starts=[10,100] ), SampleTV( starts=[10,100] ))

    def runTest(self):
        pass
    
#class TestNearestPointDistStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = NearestPointDistStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestNearestPointDistStatSplittable().debug()
    #TestNearestPointDistStatUnsplittable().debug()
    unittest.main()
