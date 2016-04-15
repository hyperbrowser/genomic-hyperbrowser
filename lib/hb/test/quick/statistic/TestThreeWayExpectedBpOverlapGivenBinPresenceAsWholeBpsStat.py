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
from quick.statistic.ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat import \
    ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat
from gold.track.GenomeRegion import GenomeRegion

from test.gold.statistic.StatUnitTest import StatUnitTest
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num

class TestThreeWayExpectedBpOverlapGivenBinPresenceStatUnsplittable(StatUnitTest):
    CLASS_TO_CREATE = ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStat

    #def testIncompatibleTracks(self):
    #    self._assertIncompatibleTracks(SampleTV(  ))

    def test_compute(self):
        #self._assertCompute(1, SampleTV( 2 ))
        ans = {'&&': 1/90.0, '*&': 0.1*0.2, '&*': 0.1*0.2, '**': 0.1*0.2}
        answer = dict([(k+'_GivenBinPresence',v*90) for k,v in ans.items()])
        self._assertCompute(answer, \
                            SampleTV( segments=[[10,28]], anchor=[10,100] ), \
                            SampleTV( segments=[[27,36]], anchor=[10,100] ),\
                            assertFunc=self.assertListsOrDicts)



        exp = 0.5*(0.1*0.2) + 0.5*(1.0*1.0)
        ans = {'&&': 91/180.0, '*&':exp, '&*': exp, '**': exp}
        answer = dict([(k+'_GivenBinPresence',v*180) for k,v in ans.items()])
        #NB! This test assumes splittable statistic is applied below. This is not done as of now, since ThreeWayExpectedBpOverlapGivenBinPresenceAsWholeBpsStatSplittable inherits OnlyGloballySplittable
        #Must for now remove this inheritance to make test work. Should be changed to allow tests to split globally, but how?
        self._assertCompute(answer, \
                            SampleTV( segments=[[10,28], [90,180]], anchor=[10,190] ), \
                            SampleTV( segments=[[27,36], [90,180]], anchor=[10,190] ),\
                            assertFunc=self.assertListsOrDicts, \
                            binRegs = (GenomeRegion('TestGenome','chr21',10,100), GenomeRegion('TestGenome','chr21',100,190)))
        
    #def test_createChildren(self):
    #    self._assertCreateChildren([], SampleTV_Num( anchor= ))

    def runTest(self):
        pass
    
#class TestXSplittable(StatUnitTest):
#    CLASS_TO_CREATE = X
#
#    def test_compute(self):
#        pass
#        
#    def test_createChildren(self):
#        pass
    
    #def runTest(self):
    #    pass
    
if __name__ == "__main__":
    #TestXSplittable().debug()
    #TestXUnsplittable().debug()
    unittest.main()