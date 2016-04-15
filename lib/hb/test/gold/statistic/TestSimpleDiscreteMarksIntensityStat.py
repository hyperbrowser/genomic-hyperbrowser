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
from gold.statistic.SimpleDiscreteMarksIntensityStat import SimpleDiscreteMarksIntensityStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSimpleDiscreteMarksIntensityStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SimpleDiscreteMarksIntensityStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([0.2,0.2,0.2,0.2], SampleTV_Num( vals=range(10,30), anchor=[0,20] ), SampleTV( starts=[0,5,10,15], anchor=[0,20] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)
        
        self._assertCompute([ 0.875, 0.475, 0.075, 0.075], SampleTV_Num( vals=range(10,26), anchor=[0,16] ), SampleTV( starts=range(0,6), anchor=[0,16] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)

        self._assertCompute([0,0,0,0], SampleTV_Num( vals=range(10,30), anchor=[0,20] ), SampleTV( starts=[], anchor=[0,20] ),\
                            numDiscreteVals=4, assertFunc=self.assertListsOrDicts)
        
    #def test_createChildren(self):
        #self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestSimpleDiscreteMarksIntensityStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = SimpleDiscreteMarksIntensityStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestDiscreteMarksIntensityStatSplittable().debug()
    #TestDiscreteMarksIntensityStatUnsplittable().debug()
    unittest.main()
