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
from gold.statistic.DiscreteMarksStat import DiscreteMarksStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestDiscreteMarksStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = DiscreteMarksStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([0]*5 + [1]*5 + [2]*5 + [3]*5, SampleTV_Num( vals=range(10,30) ), \
            numDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([0]*3 + [1]*2 + [2]*2 + [3]*3, SampleTV_Num( vals=range(10,20) ), \
            numDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([0, 3], SampleTV_Num( vals=range(10,12) ), \
            numDiscreteVals=4, marksStat='MarksListStat', assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([], SampleTV_Num( vals=range(10,12), anchor=[0,2]), SampleTV( starts=[], anchor=[0,2]),\
            numDiscreteVals=4, marksStat='ExtractMarksStat', assertFunc=self.assertListsOrDicts)
        
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestDiscreteMarksStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = DiscreteMarksStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestDiscreteMarksStatSplittable().debug()
    #TestDiscreteMarksStatUnsplittable().debug()
    unittest.main()