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
import numpy
from gold.statistic.BinScaledFunctionAvgStat import BinScaledFunctionAvgStat
from gold.track.GenomeRegion import GenomeRegion

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestBinScaledFunctionAvgStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = BinScaledFunctionAvgStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute(None, \
            SampleTV_Num( vals=xrange(1), anchor=[0,1] ), numSubBins=4)

        self._assertCompute([0,1.5,3,4.5], \
            SampleTV_Num( vals=xrange(6), anchor=[0,6] ), numSubBins=4,\
            assertFunc=self.assertListsOrDicts)

        self._assertCompute([4.5, 14.5, 24.5, 34.5], \
            SampleTV_Num( vals=xrange(40), anchor=[0,40] ), numSubBins=4, assertFunc=self.assertListsOrDicts)

    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
class TestBinScaledFunctionAvgStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = BinScaledFunctionAvgStat

    def test_compute(self):
        self._assertCompute({ 'Result': {'sdOfMean': [0,0,0,0], 'mean': [0,1,2,3]} }, \
            SampleTV_Num( vals=xrange(4), anchor=[0,4] ), numSubBins=4, binRegs = \
            (GenomeRegion('TestGenome','chr21',0,4), GenomeRegion('TestGenome','chr21',4,4)), assertFunc=self.assertListsOrDicts)

        self._assertCompute({ 'Result': {'sdOfMean': [32.70368863, 27.40038777, 22.09708691, 16.79378605], \
                                         'mean': [(12+104.5)/2.0, (37+114.5)/2.0, (62+124.5)/2.0, (87+134.5)/2.0 ]} }, \
            SampleTV_Num( vals=xrange(140), anchor=[0,140] ), numSubBins=4, binRegs = \
            (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,140)), \
            assertFunc=self.assertListsOrDicts)
        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestBinScaledFunctionAvgStatSplittable().debug()
    #TestBinScaledFunctionAvgStatUnsplittable().debug()
    unittest.main()