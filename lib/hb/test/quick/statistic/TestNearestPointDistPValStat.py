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
from quick.statistic.NearestPointDistPValStat import NearestPointDistPValStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestNearestPointDistPValStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = NearestPointDistPValStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        #self._assertCompute(None, SampleTV( starts=[] ), SampleTV( starts=[1,4,5,6,9] ))
        #self._assertCompute(None, SampleTV( starts=[2,6] ), SampleTV( starts=[] ))
        
        #THIS IS NOT QUALITY CHECKED. TARGETS HAVE BEEN TAKEN FROM OUTPUT..
        self._assertCompute({'P-value': 0.0}, SampleTV( starts=[0,10,50] ), SampleTV( starts=[0,10,50] ))
        self._assertCompute({'P-value': 0.0096525096525096523}, SampleTV( starts=[0,10,50] ), SampleTV( starts=[1,11,49] ))
        self._assertCompute({'P-value': 0.063241106719367585}, SampleTV( starts=[0,10,50] ), SampleTV( starts=[5,30] ))
        self._assertCompute({'P-value': 0.041666666666666671}, SampleTV( starts=[0,10,50] ), SampleTV( starts=[0,5] ))
        self._assertCompute({'P-value': 0.08580858085808582}, SampleTV( starts=[0,10,50] ), SampleTV( starts=[20,40] ))
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestNearestPointDistPValStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = NearestPointDistPValStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        self.test_compute()
    
if __name__ == "__main__":
    #TestNearestPointDistPValStatSplittable().debug()
    #TestNearestPointDistPValStatUnsplittable().debug()
    unittest.main()