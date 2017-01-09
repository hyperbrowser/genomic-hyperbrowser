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
from gold.statistic.ExtractMarksStat import ExtractMarksStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestExtractMarksStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = ExtractMarksStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([13, 15, 17], SampleTV_Num( vals=range(10, 20), anchor=[0,10], valDType='float32' ), \
                            SampleTV( starts=[3,5,7], anchor=[0,10] ), assertFunc=self.assertListsOrDicts)
        self._assertCompute([13, 14, 15, 17], SampleTV_Num( vals=range(10, 20), anchor=[0,10], valDType='float32' ), \
                            SampleTV( starts=[3,7], ends=[6,8], anchor=[0,10] ), assertFunc=self.assertListsOrDicts)
        self._assertCompute([], SampleTV_Num( vals=range(10, 20), anchor=[0,10], valDType='float32' ), \
                            SampleTV( starts=[], anchor=[0,10] ), assertFunc=self.assertListsOrDicts)
    
    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestExtractMarksStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = ExtractMarksStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestExtractMarksStatSplittable().debug()
    #TestExtractMarksStatUnsplittable().debug()
    unittest.main()