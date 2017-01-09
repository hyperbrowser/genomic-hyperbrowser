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
from gold.statistic.MinAndMaxStat import MinAndMaxStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from numpy import nan

class TestMinAndMaxStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MinAndMaxStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( anchor=[10,100], numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( starts=False, anchor=[10,100], numElements=5 ))
        self._assertIncompatibleTracks(SampleTV( ends=False, anchor=[10,100], numElements=5 ))

    def test_compute(self):
        self._assertCompute({'min':-0.7, 'max':2.0}, SampleTV_Num( vals=[2.0, 1.5, -0.7] ), \
            assertFunc=self.assertListsOrDicts)
        self._assertCompute({'min':nan, 'max':nan}, SampleTV_Num( vals=[2.0, 1.5, nan] ), \
            assertFunc=self.assertListsOrDicts)
        self._assertCompute(None, SampleTV_Num( vals=[] ), \
            assertFunc=self.assertListsOrDicts)
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable], SampleTV_Num( anchor=[10,100] ))

class TestMinAndMaxStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = MinAndMaxStat

    def test_compute(self):
        self._assertCompute({'min':-0.7, 'max':2.0}, SampleTV_Num( vals=[2.0, 1.5, -0.7], anchor=[99,102] ),  \
            assertFunc=self.assertListsOrDicts)
        
if __name__ == "__main__":
    unittest.main()
