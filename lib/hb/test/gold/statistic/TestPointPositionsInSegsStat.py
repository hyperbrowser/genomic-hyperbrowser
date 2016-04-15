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
from gold.statistic.PointPositionsInSegsStat import PointPositionsInSegsStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestPointPositionsInSegsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = PointPositionsInSegsStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( numElements=5 ), SampleTV( numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( starts=[0,5] ), SampleTV( starts=[0,5] ))
        self._assertIncompatibleTracks(SampleTV( ends=[0,5] ), SampleTV( ends=[0,5] ))
        self._assertIncompatibleTracks(SampleTV_Num( anchor=[5,10] ), SampleTV_Num( anchor=[5,10] ))

    def test_compute(self):
        self._assertCompute([], SampleTV( starts=[] ), SampleTV( segments=[] ), \
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([], SampleTV( starts=[1,2,3] ), SampleTV( segments=[] ), \
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([], SampleTV( starts=[] ), SampleTV( segments=[[10,20]] ), \
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([0.0, 0.1, 0.5, 1.0],
                            SampleTV( starts=[10,11,15,20,25,30,31,41], strands=False),\
                            SampleTV( segments=[[10,21], [26,29], [30,31], [40,42]], strands=False), \
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([1.0, 0.9, 0.0],
                            SampleTV( starts=[10,11,15,20,25,30,31,41], strands=[False,False,True,False,True,False,False,False]),\
                            SampleTV( segments=[[10,21], [26,29], [30,31], [40,42]], strands=[False,True,True,False]), \
                            assertFunc=self.assertListsOrDicts)
        self._assertCompute([0.0, 0.1, 0.5], SampleTV( starts=[10,11,15], strands=False ), SampleTV( ends=[0,10,21,100] ), \
                            assertFunc=self.assertListsOrDicts)
        
    def test_createChildren(self):  
        self._assertCreateChildren([RawDataStatUnsplittable]*2, \
                                    SampleTV( ends=False, numElements=5 ), SampleTV( numElements=5 ))

    def runTest(self):
        self.test_compute()
    
#class TestPointPositionsInSegsStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = PointPositionsInSegsStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestPointPositionsInSegsStatSplittable().debug()
    #TestPointPositionsInSegsStatUnsplittable().debug()
    unittest.main()
