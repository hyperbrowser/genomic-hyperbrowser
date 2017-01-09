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
from tempfile import NamedTemporaryFile

from gold.origdata.GtrackStandardizer import standardizeGtrackFileAndReturnContents
from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from gold.track.TrackFormat import TrackFormat
from test.gold.origdata.common.TestWithGeSourceData import TestWithGeSourceData
from test.util.Asserts import TestCaseWithImprovedAsserts

class TestGtrackStandardizer(TestWithGeSourceData, TestCaseWithImprovedAsserts):
    GENOME = 'TestGenome'
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']
        
    def setUp(self):
        pass
    
    def testStandardizing(self):
        geSourceTest = self._commonSetup()
        
        for caseName in geSourceTest.cases:
            if not caseName.startswith('gtrack'):
                continue
                
            if 'no_standard' in caseName:
                print 'Test case skipped: ' + caseName
                continue
                
            print caseName
            print
            
            case = geSourceTest.cases[caseName]
            testFn = self._writeTestFile(case)
            print open(testFn).read()
            print
            
            stdContents = standardizeGtrackFileAndReturnContents(testFn, case.genome)
            print stdContents

            self.assertTrue('##track type: linked valued segments' in stdContents)
            self.assertTrue('\t'.join(['###seqid', 'start', 'end', 'value', 'strand', 'id', 'edges']) in stdContents)
            
            geSource = GtrackGenomeElementSource('', case.genome, strToUseInsteadOfFn=stdContents)
            for ge in geSource:
                pass
            
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestGtrackSorter().debug()
    unittest.main()