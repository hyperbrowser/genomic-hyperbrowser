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
from quick.statistic.NeighborhoodCorrespondenceDistribution3dStat import NeighborhoodCorrespondenceDistribution3dStat

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestNeighborhoodCorrespondenceDistribution3dStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = NeighborhoodCorrespondenceDistribution3dStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        from gold.application.StatRunner import StatJob
        #from quick.application.UserBinSource import UserBinSource
        from gold.track.GenomeRegion import GenomeRegion
        
        StatJob.USER_BIN_SOURCE = [GenomeRegion('TestGenome', 'chr21', 0, 100), GenomeRegion('TestGenome', 'chr21', 100, 200)]
        self._assertCompute([2.0,None], \
                            SampleTV( starts=[0,10,120,130], ids=['a','b','c','d'], edges=[['d'],['d'],['d'],list('abc')], anchor=[0,200] ), \
                            globalSource='userbins', weightThreshold='0')
        
        self._assertCompute([None,None], \
                            SampleTV( starts=[], ids=[], edges=[], anchor=[0,200] ), \
                            globalSource='userbins', weightThreshold='0')
        
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestXSplittable(StatUnitTest):
#    CLASS_TO_CREATE = NumberOfNodesAndEdges3dStat
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestNumberOfNodesAndEdges3dStatSplittable().debug()
    #TestNumberOfNodesAndEdges3dStatUnsplittable().debug()
    unittest.main()