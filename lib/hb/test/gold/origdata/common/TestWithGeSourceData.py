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

import unittest
import os
from subprocess import call

from gold.util.CommonFunctions import createOrigPath, createDirPath
from quick.util.CommonFunctions import ensurePathExists

class TestWithGeSourceData(unittest.TestCase):
    def _removeDir(self, procDir, trackName):
        #print procDir, trackName
        self.assertTrue(procDir.endswith(os.sep + trackName[-1]))
        if os.path.exists(procDir):
            call('rm -R ' + procDir, shell=True)
            
    def _removeAllTrackData(self, trackName):
        self._removeDir(createDirPath(trackName, self.GENOME, allowOverlaps=False), trackName)
        self._removeDir(createDirPath(trackName, self.GENOME, allowOverlaps=True), trackName)
        self._removeDir(createOrigPath(self.GENOME, trackName), trackName)
        
    def _commonSetup(self):
        from test.gold.origdata.TestGenomeElementSource import TestGenomeElementSource
        testGESource = TestGenomeElementSource()
        testGESource.setUp()
        origDir = createOrigPath(self.GENOME, self.TRACK_NAME_PREFIX)
        self._removeDir(origDir, self.TRACK_NAME_PREFIX)
        return testGESource
    
    def _writeTestFile(self, case):
        fn = createOrigPath(self.GENOME, self.TRACK_NAME_PREFIX + case.trackName, 'testfile' + case.suffix)
        ensurePathExists(fn)
        testfile = open(fn, 'w')
        testfile.write('\n'.join(case.headerLines + case.lines))
        testfile.close()
        return fn
