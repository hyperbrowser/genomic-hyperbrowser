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

#!/usr/bin/env python
import ast
import sys
import unittest
from test.integration.GalaxyIntegrationTest import GalaxyIntegrationTest
from test.integration.ProfiledIntegrationTest import ProfiledIntegrationTest

class TestStatInternals(GalaxyIntegrationTest):
    def testTrackFormatMerging(self):
        self._assertBatchEqual([[[('Result', [119121])], [('Result', [0])]]],\
           ['TestGenome|chr21:10000001-11000000|500000|segsMany|ZipperStat(statClassList=CountStat)'])
        
        self._assertBatchEqual([[[('Result', [447,447])], [('Result', [0,0])]]],\
           ['TestGenome|chr21:10000001-11000000|500000|segsMany|ZipperStat(statClassList=CountStat^CountPointStat)'])
        
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestStatInternals().run()
    #TestStatInternals().debug()
    if len(sys.argv) == 2:
        TestStatInternals.VERBOSE = ast.literal_eval(sys.argv[1])
        sys.argv = sys.argv[:-1]
    unittest.main()
