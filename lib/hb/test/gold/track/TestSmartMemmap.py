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
import os
import sys
from numpy import array, memmap

from gold.track.SmartMemmap import SmartMemmap
from test.util.FileUtils import removeFile
from test.util.Asserts import AssertList

import gold.track.SmartMemmap
gold.track.SmartMemmap.MEMMAP_BIN_SIZE = 100

class TestSmartMemmap(unittest.TestCase):
    def setUp(self):
        self.stderr = sys.stderr
        sys.stderr = open('/dev/null', 'w')

        self._fn = os.tmpnam()
        self._m = memmap(self._fn, dtype='int32', mode='w+', shape=190)
        self._m[0:190] = array(range(190))
        self._m.flush()
        
        self._sm = SmartMemmap(self._fn, elementDim=None, dtype='int32', dtypeDim=1, mode='r')
        
    def tearDown(self):
        sys.stderr = sys.stderr

        removeFile(self._fn)
        
    def testSlice(self):
        m = self._m
        sm = self._sm
        
        AssertList(m[0:0], sm[0:0], self.assertEqual)
        AssertList(m[0:100], sm[0:100], self.assertEqual)
        AssertList(m[10:20], sm[10:20], self.assertEqual)
        AssertList(m[90:110], sm[90:110], self.assertEqual)
        AssertList(m[110:120], sm[110:120], self.assertEqual)
        
    def testIndex(self):
        m = self._m
        sm = self._sm
        
        self.assertEqual(m[0], sm[0])
        self.assertEqual(m[11], sm[11])
        self.assertEqual(m[99], sm[99])
        self.assertEqual(m[111], sm[111])
        self.assertEqual(m[189], sm[189])
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestSmartMemmap().debug()
    unittest.main()