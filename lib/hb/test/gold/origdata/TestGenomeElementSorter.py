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
from gold.origdata.GenomeElementSorter import GenomeElementSorter
from test.gold.origdata.common.Asserts import assertDecorator

class TestGenomeElementSorter(unittest.TestCase):
    def setUp(self):
        pass    
    
    def _assertSort(self, sortedList, unsortedList):
        assertDecorator(GenomeElementSorter, self.assertEqual, sortedList, unsortedList)
    
    def testSort(self):
        self._assertSort([['A','chr2',3,8],['B','chr1',2,5]], [['B','chr1',2,5],['A','chr2',3,8]])
        self._assertSort([['A','chr1',3,8],['A','chr2',2,5]], [['A','chr2',2,5],['A','chr1',3,8]])
        self._assertSort([['A','chr1',2,8],['A','chr1',3,5]], [['A','chr1',3,5],['A','chr1',2,8]])
        self._assertSort([['A','chr1',2,5],['A','chr1',2,8]], [['A','chr1',2,8],['A','chr1',2,5]])
        
        self._assertSort([[None,'chr1',3,8],[None,'chr2',2,5]], [[None,'chr2',2,5],[None,'chr1',3,8]])
        self._assertSort([[None,'chr1',2,8],[None,'chr1',3,5]], [[None,'chr1',3,5],[None,'chr1',2,8]])
        self._assertSort([[None,'chr1',2,5],[None,'chr1',2,8]], [[None,'chr1',2,8],[None,'chr1',2,5]])
        
        self._assertSort([['A','chr2',3,None],['B','chr1',2,None]], [['B','chr1',2,None],['A','chr2',3,None]])
        self._assertSort([['A','chr1',3,None],['A','chr2',2,None]], [['A','chr2',2,None],['A','chr1',3,None]])
        self._assertSort([['A','chr1',2,None],['A','chr1',3,None]], [['A','chr1',3,None],['A','chr1',2,None]])

        self._assertSort([['A','chr2',None,8],['B','chr1',None,5]], [['B','chr1',None,5],['A','chr2',None,8]])
        self._assertSort([['A','chr1',None,8],['A','chr2',None,5]], [['A','chr2',None,5],['A','chr1',None,8]])
        self._assertSort([['A','chr1',None,5],['A','chr1',None,8]], [['A','chr1',None,8],['A','chr1',None,5]])

        self._assertSort([['B','chr2',None,None],['A','chr1',None,None]], [['B','chr2',None,None],['A','chr1',None,None]])
        
if __name__ == "__main__":
    unittest.main()