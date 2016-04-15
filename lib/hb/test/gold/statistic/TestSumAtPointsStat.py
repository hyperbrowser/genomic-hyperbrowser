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
from gold.statistic.SumAtPointsStat import SumAtPointsStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSumAtPointsStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SumAtPointsStat

    def test_compute(self):
        self._assertCompute(0.0, SampleTV( starts=[], anchor=[0,0] ),
                            SampleTV_Num( vals=[], anchor=[0,0] ))
        self._assertCompute(0.0, SampleTV( starts=[], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))
        self._assertCompute(128.0, SampleTV( starts=[3,5,50,70], anchor=[0,100] ),
                            SampleTV_Num( vals=[1.0*x for x in range(100)], anchor=[0,100] ))

    def runTest(self):
        pass
        
if __name__ == "__main__":
    unittest.main()