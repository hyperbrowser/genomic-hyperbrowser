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
from gold.statistic.SumStat import SumStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSumStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SumStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( anchor=[10,100], numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( starts=False, anchor=[10,100], numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( ends=False, anchor=[10,100], numElements=5 ))

    def test_compute(self):
        self._assertCompute(2.8, SampleTV_Num( vals=[2.0, 1.5, -0.7] ), assertFunc=self.assertAlmostEqual)
        self._assertCompute(0, SampleTV_Num( vals=[] ), assertFunc=self.assertAlmostEqual)
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable], SampleTV_Num( anchor=[10,100] ))

class TestSumStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = SumStat

    def test_compute(self):
        self._assertCompute(2.8, SampleTV_Num( vals=[2.0, 1.5, -0.7], anchor=[99,102] ), assertFunc=self.assertAlmostEqual)
        
if __name__ == "__main__":
    unittest.main()