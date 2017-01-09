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
from gold.statistic.CountStat import CountStat
from gold.statistic.RawDataStat import RawDataStatUnsplittable

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestCountStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = CountStat
    
    def test_compute(self):
        self._assertCompute(90, SampleTV_Num( anchor=[10,100] ))
        self._assertCompute(20, SampleTV( segments=[[10,20], [80,90]], anchor=[10,100] ))
        self._assertCompute(3,  SampleTV( starts=[2,15,60], anchor=[10,100] ))
        self._assertCompute(90, SampleTV( ends=[15,90], anchor=[10,100] ))
        self._assertCompute(0, SampleTV( segments=[], anchor=[10,100] ))
        
    def test_createChildren(self):
        self._assertCreateChildren([RawDataStatUnsplittable], SampleTV_Num( anchor=[0,100] ))

class TestCountStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = CountStat

    def test_compute(self):
        self._assertCompute(111, SampleTV_Num( anchor=[10,121] ))
        self._assertCompute(41,  SampleTV( segments=[[10,20], [80,111]], anchor=[10,121] ))
        self._assertCompute(3,   SampleTV( starts=[2,15,110], anchor=[10,121] ))
        self._assertCompute(111, SampleTV( ends=[15,111], anchor=[10,121] ))
        self._assertCompute(0, SampleTV( segments=[], anchor=[10,121] ))
        
if __name__ == "__main__":
    unittest.main()