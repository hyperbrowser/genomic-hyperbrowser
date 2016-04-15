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
from gold.statistic.XYPairStat import XYPairStat
from gold.statistic.CountStat import CountStat, CountStatSplittable, CountStatUnsplittable
from gold.statistic.SumStat import SumStat, SumStatSplittable, SumStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from test.util.Asserts import AssertList

class TestXYPairStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = XYPairStat
    
    def _assertList(self, target, other):
        AssertList(target, other, self.assertEqual)
    
    def test_compute(self):
        self._assertCompute([3, 10.0],\
                             SampleTV( segments=[[0,1],[2,4]], anchor=[10,15] ),\
                             SampleTV_Num( vals=[1.0, 1.5, 2.0, 2.5, 3.0], anchor=[10,15] ),\
                             CountStat, SumStat, assertFunc=self._assertList)
        
    def test_createChildren(self):
        self._assertCreateChildren([CountStatUnsplittable, SumStatUnsplittable],\
                                    SampleTV( anchor=[10,100], numElements=5 ),\
                                    SampleTV_Num( anchor=[10,100] ), CountStat, SumStat)
        self._assertCreateChildren([CountStatSplittable, SumStatSplittable],\
                                    SampleTV( anchor=[10,121], numElements=5 ),\
                                    SampleTV_Num( anchor=[10,121] ), CountStat, SumStat)
    
if __name__ == "__main__":
    unittest.main()