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
from gold.statistic.PointCountPerSegStat import PointCountPerSegStat
from gold.track.GenomeRegion import GenomeRegion

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestPointCountPerSegStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = PointCountPerSegStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        self._assertCompute([0,0,2,1,0], SampleTV( starts=range(2,20,2) ),
                                         SampleTV( segments=[[0,2], [3,4], [6,9], [14,15], [15,16]] ))
        self._assertCompute([0,0,0,0,0], SampleTV( starts=[] ),
                                         SampleTV( segments=[[0,2], [3,4], [6,9], [14,15], [15,16]] ))
        self._assertCompute([], SampleTV( starts=range(2,20,2) ),
                                         SampleTV( segments=[] ))
        self._assertCompute([], SampleTV( starts=[] ),
                                         SampleTV( segments=[] ),)
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    #def runTest(self):
    #    pass
    
class TestPointCountPerSegStatSplittable(StatUnitTest):
    CLASS_TO_CREATE = PointCountPerSegStat

    def test_compute(self):
        #NB! Fails until new borderhandling-rules have been implemented..
        #self._assertCompute([0,0,2,1,0], SampleTV( starts=range(2,120,2), anchor=[0,200] ),\
        #                                 SampleTV( segments=[[0,2], [3,4], [6,9], [99,101], [115,116]], anchor=[0,200] ),\
        #                                 binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)))
        #self._assertCompute([0,0,0,0,0], SampleTV( starts=[], anchor=[0,200] ),\
        #                                 SampleTV( segments=[[0,2], [3,4], [6,9], [99,101], [115,116]], anchor=[0,200] ),\
        #                                 binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)))
        #self._assertCompute([], SampleTV( starts=range(2,20,2), anchor=[0,200] ),\
        #                                 SampleTV( segments=[], anchor=[0,200] ),\
        #                                 binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)))
        #self._assertCompute([], SampleTV( starts=[], anchor=[0,200] ),\
        #                                 SampleTV( segments=[], anchor=[0,200] ),\
        #                                 binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)))
        self._assertCompute(None, \
                            SampleTV( starts=range(2,120,2), anchor=[0,200] ),\
                            SampleTV( segments=[[0,2], [3,4], [6,9], [99,101], [115,116]], anchor=[0,200] ),\
                            binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)))
        self._assertCompute(None, \
                            SampleTV( starts=[], anchor=[0,200] ),\
                            SampleTV( segments=[[0,2], [3,4], [6,9], [99,101], [115,116]], anchor=[0,200] ),\
                            binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)))
        self._assertCompute(None, \
                            SampleTV( starts=range(2,20,2), anchor=[0,200] ),\
                            SampleTV( segments=[], anchor=[0,200] ),\
                            binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)))
        self._assertCompute(None, \
                            SampleTV( starts=[], anchor=[0,200] ),\
                            SampleTV( segments=[], anchor=[0,200] ),\
                            binRegs = (GenomeRegion('TestGenome','chr21',0,100), GenomeRegion('TestGenome','chr21',100,200)))
         
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestPointCountPerSegStatSplittable().debug()
    #TestPointCountPerSegStatUnsplittable().debug()
    unittest.main()
