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
from gold.statistic.Statistic import *
from gold.track.Track import Track
from gold.util.CustomExceptions import NoneResultError

class MyStatistic(Statistic):
        def __init__(self, region, track, divideByZero = False, *args):
            super(MyStatistic, self).__init__(region, track, *args)
            self._computeCalled = False
            self._divideByZero = divideByZero
        
        def _compute(self):
            self._computeCalled = True
            if self._divideByZero:
                return 5/0
            else:
                return 5
            
        def _createChildren(self):
            self._addChild(MyStatisticChild(self._region, self._track, self._divideByZero))
            self._addChild(MyStatisticSplittable([self._region]*2, self._track, self._divideByZero))

class MyStatisticChild(MyStatistic):
        def _createChildren(self):
            self._addChild(MyStatisticChildChild(self._region, self._track))

class MyStatisticChildChild(MyStatistic):
        def _createChildren(self):
            pass

class MyStatisticSplittable(MyStatistic, StatisticSumResSplittable):
        def __init__(self, *args):
            super(MyStatisticSplittable, self).__init__(*args)
 
        def _getChildObject(self, bin):
            return MyStatisticChildChild(bin, self._track, self._divideByZero)

class TestStatistic(unittest.TestCase):
    def setUp(self):
        self.statParent = MyStatistic(GenomeRegion('TestGenome','chr21',0,1), Track(['dummy']))
        
    def testCreateChildren(self):
        self.statParent.createChildren()
        self.assertEqual(2, len(self.statParent._children))
        self.assertEqual(1, len(self.statParent._children[0]._children))
        self.assertEqual(0, len(self.statParent._children[0]._children[0]._children))
        self.assertEqual(False, self.statParent._children[1].hasChildren())
        self.assertEqual(False, self.statParent.hasResult())
        
    def testCompute(self):
        self.statParent.compute()
        self.assertEqual(True, self.statParent._computeCalled)
        self.assertEqual(True, self.statParent._children[0]._computeCalled)
        self.assertEqual(True, self.statParent._children[0]._children[0]._computeCalled)
        self.assertEqual(False, self.statParent._children[1]._computeCalled)

        self.assertEqual(True, self.statParent.hasResult())
        self.assertEqual(5, self.statParent.getResult())
        
        self.assertEqual(2, len(self.statParent._children[1]._childResults))
        self.assertEqual([5,5], self.statParent._children[1]._childResults)
        self.assertEqual(10, self.statParent._children[1].getResult())
    
    def testComputeDivideByZero(self):
        self.statParentDivByZero = MyStatistic(GenomeRegion('TestGenome','chr1',0,1), \
                                               Track(['dummy']), True)
        self.statParentDivByZero.compute()

        self.assertEqual(True, self.statParentDivByZero.hasResult())
        self.assertRaises(NoneResultError, self.statParentDivByZero.getResult)
        
        self.assertEqual(2, len(self.statParentDivByZero._children[1]._childResults))
        self.assertEqual([None, None], self.statParentDivByZero._children[1]._childResults)
        self.assertRaises(NoneResultError, self.statParentDivByZero._children[1].getResult)

if __name__ == "__main__":
    unittest.main()
