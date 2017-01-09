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
from gold.track.TrackFormat import TrackFormatReq
from gold.statistic.RawDataStat import RawDataStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from test.util.Asserts import AssertList

class TestRawDataStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = RawDataStat

    def testIncompatibleTracks(self):
        self._assertIncompatibleTracks(SampleTV( numElements=5 ), TrackFormatReq(dense=True))

    def _assertTVEqual(self, target, other):
        self.assertEqual(target.genomeAnchor, other.genomeAnchor)
        self.assertEqual(target.trackFormat, other.trackFormat)
        AssertList([el.start() for el in target],
                   [el.start() for el in other], self.assertEqual)
        AssertList([el.end() for el in target],
                   [el.end() for el in other], self.assertEqual)
        AssertList([el.val() for el in target],
                   [el.val() for el in other], self.assertAlmostEqual)
        AssertList([el.strand() for el in target],
                   [el.strand() for el in other], self.assertEqual)

    def test_compute(self):
        sampleTV = SampleTV( numElements=5 )
        self._assertCompute(sampleTV,
                            sampleTV, TrackFormatReq(), assertFunc=self._assertTVEqual)

    def test_createChildren(self):
        self._assertCreateChildren([],
                                   SampleTV_Num( anchor=[10,100] ), TrackFormatReq())

    def runTest(self):
        self.test_compute()

if __name__ == "__main__":
    #TestRawDataStatUnsplittable().debug()
    unittest.main()