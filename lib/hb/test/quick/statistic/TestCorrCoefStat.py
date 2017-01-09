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
from quick.statistic.CorrCoefStat import CorrCoefStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCorrCoefStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CorrCoefStat

    #def testIncompatibleTracks(self):
        #self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute(-1.0, SampleTV_Num( vals=[1.0,2.0] ), SampleTV_Num( vals=[2.0,1.0] ))
        self._assertCompute(1.0, SampleTV_Num( vals=[1.0,2.0] ), SampleTV_Num( vals=[2.0,4.0] ))
        self._assertCompute(numpy.nan, SampleTV_Num( vals=[1.0,2.0] ), SampleTV_Num( vals=[2.0,2.0] ))
        
        self._assertCompute(None, SampleTV_Num( vals=[] ), SampleTV_Num( vals=[] ))
        self._assertCompute(numpy.nan, SampleTV_Num( vals=[1.0,numpy.nan] ), SampleTV_Num( vals=[2.0,3.0] ))
        
    #def test_createChildren(self):
        #self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestCorrCoefStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = CorrCoefStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestCorrCoefStatSplittable().debug()
    #TestCorrCoefStatUnsplittable().debug()
    unittest.main()
