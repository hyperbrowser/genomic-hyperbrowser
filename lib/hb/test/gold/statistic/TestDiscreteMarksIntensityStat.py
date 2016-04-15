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
from gold.statistic.DiscreteMarksIntensityStat import DiscreteMarksIntensityStat
import gold.statistic.MultiDiscreteMarkFlattenerStat
from gold.track.Track import PlainTrack
import gold.statistic.DiscreteMarksIntensityStat
from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
from test.gold.track.common.SampleTrack import SampleTrack

def provideTrack(tn):
    valList = tn[0].split(',')
    return SampleTrack(SampleTV_Num( vals=valList, anchor=[0,len(valList)] ))

def encodeTn(intList):
    return ','.join([str(x) for x in intList])

class TestDiscreteMarksIntensityStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = DiscreteMarksIntensityStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV( 1 ))

    def setUp(self):
        gold.statistic.DiscreteMarksIntensityStat.DiscreteMarksIntensityStatUnsplittable.PRIOR_FACTOR = 1/1e9
        gold.statistic.MultiDiscreteMarkFlattenerStat.PlainTrack = provideTrack 

    def tearDown(self):
        gold.statistic.DiscreteMarksIntensityStat.DiscreteMarksIntensityStatUnsplittable.PRIOR_FACTOR = 1.0
        gold.statistic.MultiDiscreteMarkFlattenerStat.PlainTrack = PlainTrack

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute( [0.2]*16, SampleTV(starts=[0,5,10,15], anchor=[0,20]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            controlTrackNameList='^^'.join([encodeTn(range(10,30)), encodeTn(range(10,30))]) )
        #[1,0.5,0,0,0,0,0,0,0,0,0,0,0,0,0,1]
        self._assertCompute( [1, 0.5, 0, 0.5, 0.5, 0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, 0.5, 0.5, 0.5, 1], SampleTV(starts=[0,1,2,7], anchor=[0,8]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            controlTrackNameList='^^'.join([ encodeTn(range(0,8)), encodeTn([0,0,0,0,0,1,2,3]) ]) )

        self._assertCompute( [0.2,0.2,0,0], SampleTV(starts=[0,5], anchor=[0,20]), numDiscreteVals=4, reducedNumDiscreteVals=4, \
            controlTrackNameList=encodeTn(range(10,30)) )

        
    #def test_createChildren(self):
    #    self._assertCreateChildren([4], SampleTV_Num( anchor=5 ))

    def runTest(self):
        pass
    
#class TestDiscreteMarksIntensityStatSplittable(StatUnitTest):
#    CLASS_TO_CREATE = DiscreteMarksIntensityStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestDiscreteMarksIntensityStatSplittable().debug()
    #TestDiscreteMarksIntensityStatUnsplittable().debug()
    unittest.main()