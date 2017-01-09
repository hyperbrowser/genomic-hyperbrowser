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
from gold.extra.nmers.NmerAsIntSlidingWindow import NmerAsIntSlidingWindow

class TestNmerAsIntSlidingWindow(unittest.TestCase):
    def setUp(self):
        pass
    
    def testIter(self):
        self.assertEqual([], list(NmerAsIntSlidingWindow(2,'')) )
        self.assertEqual([], list(NmerAsIntSlidingWindow(2,'n')) )
        self.assertEqual([], list(NmerAsIntSlidingWindow(2,'a')) )
        self.assertEqual([1,6,11,12,None,None,4], list(NmerAsIntSlidingWindow(2,'acGtaNca')) )
        self.assertEqual([6,27], list(NmerAsIntSlidingWindow(3,'acGt')) )
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    unittest.main()