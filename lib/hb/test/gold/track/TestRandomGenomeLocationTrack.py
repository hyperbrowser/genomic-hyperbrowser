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

from gold.track.GenomeRegion import GenomeRegion
from gold.track.RandomGenomeLocationTrack import RandomGenomeLocationTrack
from test.gold.track.common.SampleTrack import SampleTrack
from test.gold.track.common.SampleTrackView import SampleTV, SampleTV_Num
import sys
import StringIO

class TestRandomGenomeLocationTrack(unittest.TestCase):
    def setUp(self):
        sys.stdout = StringIO.StringIO()
    
    def _doRandTest(self, origTV):
        origTrack = SampleTrack(origTV)
        queryReg = GenomeRegion('TestGenome','chr21',100,400)
        for randClass in [RandomGenomeLocationTrack]:
            for i in range(10):
                randTrack = randClass(origTrack, queryReg, i)
                randTV = randTrack.getTrackView(queryReg)
                self.assertEqual(len(queryReg), len(randTV))

    def testRandomization(self):
        anchor = [0, 46944323]
        
        self._doRandTest( SampleTV( segments=[], anchor=anchor ) )
    
        self._doRandTest( SampleTV( starts=True, ends=True, vals=False, strands=False, numElements=1000, anchor=anchor ) )
        self._doRandTest( SampleTV( starts=True, ends=True, vals=True, strands=True, numElements=1000, anchor=anchor ) )

        self._doRandTest( SampleTV( starts=True, ends=False, vals=False, strands=False, numElements=1000, anchor=anchor ) )
        self._doRandTest( SampleTV( starts=True, ends=False, vals=True, strands=True, numElements=1000, anchor=anchor ) )

        self._doRandTest( SampleTV( starts=False, ends=True, vals=False, strands=False, numElements=1000, anchor=anchor ) )
        self._doRandTest( SampleTV( starts=False, ends=True, vals=True, strands=True, numElements=1000, anchor=anchor ) )
        
        #self._doRandTest( SampleTV_Num( anchor=anchor ) )
        
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestPermutedSegsAndIntersegsRandomizedTrack().debug()
    unittest.main()