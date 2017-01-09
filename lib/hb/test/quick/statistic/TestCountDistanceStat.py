# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# Diana
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
from quick.statistic.CountDistanceStat import CountDistanceStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCountDistanceStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CountDistanceStat
    
    def test_compute(self):
        self._assertCompute([1],  SampleTV( starts=[15], anchor=[10,100]), maxNum=1500)
        self._assertCompute([3],  SampleTV( starts=[1,15,60], anchor=[10,100]), maxNum=1500)
        self._assertCompute([3, 1, 2, 1, 2],  SampleTV( starts=[5,8,11,20, 29, 32, 45, 58, 60], anchor=[0,90]), maxNum=5)
        self._assertCompute([], SampleTV( starts=[], anchor=[10,100] ))
        

class TestCountDistanceStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = CountDistanceStat

    def test_compute(self):
        self._assertCompute([2, 1],  SampleTV( starts=[11,15,160], anchor=[10,200]), maxNum=1500)
      
if __name__ == "__main__":
    unittest.main()