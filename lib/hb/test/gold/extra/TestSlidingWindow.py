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
from gold.extra.SlidingWindow import SlidingWindow
from gold.util.CustomExceptions import NotSupportedError
from test.util.Asserts import AssertList

class TestSlidingWindow(unittest.TestCase):
    def setUp(self):
        pass
    
    def _assertSlide(self, targetWindows, windowSize, source):
        windows = SlidingWindow(source, windowSize)
        self.assertEqual(len(targetWindows), len([el for el in windows]))
        for i, window in enumerate(windows):
            AssertList(targetWindows[i], window, self.assertEqual)
    
    def testSlide(self):
        self._assertSlide([], 3, [])
        self._assertSlide([[0,1],[0,1,2],[1,2,3],[2,3]], 3, range(4))
        self.assertRaises(NotSupportedError, SlidingWindow, [], 4)
    
if __name__ == "__main__":
    unittest.main()