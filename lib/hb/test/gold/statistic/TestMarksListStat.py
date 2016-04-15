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
from gold.statistic.MarksListStat import MarksListStat
from gold.track.GenomeRegion import GenomeRegion
from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestMarksListStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = MarksListStat

    def testIncompatibleTracks(self):
        pass
        #self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([1,2,3], SampleTV( starts = [10,30,50], vals = [1,2,3], anchor = [0,100], valDType='int32' ), \
                            assertFunc=self.assertListsOrDicts, markType='number (integer)')
        self._assertCompute([1,2,3], SampleTV_Num( vals = [1,2,3], anchor = [0,3], valDType='int32' ), \
                            assertFunc=self.assertListsOrDicts, markType='number (integer)')
        self._assertCompute([], SampleTV( vals = [], ends=False, numElements = 0, anchor = [0,100], valDType='int32' ), \
                            assertFunc=self.assertListsOrDicts, markType='number (integer)') 
        
    #def test_createChildren(self):  
        #self._assertCreateChildren([RawDataStatUnsplittable]*2, \
        #                            SampleTV( numElements=5 ), SampleTV_Num( anchor = [10,1000]  ))

class TestMarksListStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = MarksListStat
#
    def test_compute(self):
        self._assertCompute([1,2,3], SampleTV( starts = [10,30,150], vals = [1,2,3], anchor = [0,200], valDType='int32' ),\
                            binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)),\
                            assertFunc=self.assertListsOrDicts, markType='number (integer)')
        self._assertCompute([1,2,3], SampleTV_Num( vals = [1,2,3], anchor = [99,102], valDType='int32' ), \
                            binRegs = (GenomeRegion('TestGenome','chr21',99,100), GenomeRegion('TestGenome','chr21',100,102)),\
                            assertFunc=self.assertListsOrDicts, markType='number (integer)')
        #        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    unittest.main()