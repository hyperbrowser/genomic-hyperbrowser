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
