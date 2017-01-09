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
from [[%tabstop1:gold]].statistic.[[%tabstop2:X]]Stat import [[%tabstop2:X]]Stat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class Test[[%tabstop2:X]]StatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = [[%tabstop2:X]]Stat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute([[%tabstop3:result]], SampleTV( [[%tabstop4:data]] ))
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([[[%tabstop5:Y]]Stat], SampleTV( [[%tabstop6:data2]] ))

    def runTest(self):
        pass
    
#class Test[[%tabstop2:X]]StatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = [[%tabstop2:X]]Stat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #Test[[%tabstop2:X]]StatSplittable().debug()
    #Test[[%tabstop2:X]]StatUnsplittable().debug()
    unittest.main()