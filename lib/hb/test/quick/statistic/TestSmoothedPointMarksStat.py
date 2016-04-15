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
from quick.statistic.SmoothedPointMarksStat import SmoothedPointMarksStat
from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestSmoothedPointMarksStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = SmoothedPointMarksStat

    def testIncompatibleTracks(self):
        pass
        #self._assertIncompatibleTracks(SampleTV( 1 ))

    def test_compute(self):
        self._assertCompute([1.119203,1.891642,2.989013], SampleTV( starts = [10,30,60], vals = [1,2,3], anchor = [0,100], valDType='int32'),\
                                     markReq='number' ,windowSize=3, windowBpSize=5000, sdOfGaussian=10,guaranteeBpCoverByWindow='False',assertFunc=self.assertListsOrDicts)
        #self._assertCompute([1.119203,1.891642,2.989013,1.119203,1.891642,2.989013], SampleTV( starts = [10,30,60,110,130,160], vals = [1,2,3,1,2,3], anchor = [0,200], valDType='int32'),\
        #                             markReq='number' ,windowSize=3, windowBpSize=5000, sdOfGaussian=10,guaranteeBpCoverByWindow='False',assertFunc=self.assertListsOrDicts)
        self._assertCompute([], SampleTV( starts=[], anchor = [0,100], valDType='int32'),\
                                     markReq='number' ) 
        
    #def test_createChildren(self):  
        #self._assertCreateChildren([RawDataStatUnsplittable]*2, \
        #                            SampleTV( numElements=5 ), SampleTV_Num( anchor = [10,1000]  ))

#class TestMarksSortedBySegmentOverlapStatStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = MarksSortedBySegmentOverlapStatStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestMarksSortedBySegmentOverlapStatStatSplittable().debug()
    #TestMarksSortedBySegmentOverlapStatStatUnsplittable().debug()
    unittest.main()