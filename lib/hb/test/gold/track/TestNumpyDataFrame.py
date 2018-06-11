import unittest
import numpy as np

from collections import OrderedDict

from gold.track.NumpyDataFrame import NumpyDataFrame
from test.util.Asserts import TestCaseWithImprovedAsserts


class TestNumpyDataFrame(TestCaseWithImprovedAsserts):
    def setUp(self):
        pass

    def testInit(self):
        npDataFrame = NumpyDataFrame()
        self.assertEquals(npDataFrame.asArrayDict(), {})
        self.assertFalse(npDataFrame.hasArray('a'))
        self.assertEquals(npDataFrame.arrayKeys(), [])
        self.assertEquals(len(npDataFrame), 0)

        npDataFrame = NumpyDataFrame(dict(a=range(5)))
        self.assertListsOrDicts(npDataFrame.asArrayDict(),
                                OrderedDict([('a', np.array(range(5)))]))
        self.assertTrue(npDataFrame.hasArray('a'))
        self.assertEquals(npDataFrame.arrayKeys(), ['a'])
        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array(range(5)))
        self.assertEquals(len(npDataFrame), 5)

        self.assertRaises(ValueError, NumpyDataFrame, dict(a=range(5), b=range(4)))
        self.assertRaises(ValueError, NumpyDataFrame, dict(a=1))

    def testArrayAddRemove(self):
        npDataFrame = NumpyDataFrame(dict(a=range(5)))
        npDataFrame.addArray('b', list('abcde'))
        self.assertTrue(npDataFrame.hasArray('b'))
        self.assertEquals(npDataFrame.arrayKeys(), ['a', 'b'])
        self.assertListsOrDicts(npDataFrame.asArrayDict(),
                                OrderedDict([('a', np.array(range(5))),
                                             ('b', np.array(['a', 'b', 'c', 'd', 'e']))]))
        self.assertEquals(len(npDataFrame), 5)

        self.assertRaises(ValueError, npDataFrame.addArray, 'c', range(4))
        self.assertFalse(npDataFrame.hasArray('c'))

        npDataFrame.addArray('aa', [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)])
        self.assertTrue(npDataFrame.hasArray('aa'))
        self.assertEquals(npDataFrame.arrayKeys(), ['a', 'b', 'aa'])
        self.assertListsOrDicts(npDataFrame.getArray('aa'),
                                np.array([(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]))
        self.assertEquals(len(npDataFrame), 5)

        self.assertRaises(KeyError, npDataFrame.removeArray, 'd')
        npDataFrame.removeArray('a')
        self.assertFalse(npDataFrame.hasArray('a'))
        self.assertEquals(npDataFrame.arrayKeys(), ['b', 'aa'])
        self.assertListsOrDicts(npDataFrame.asArrayDict(),
                                OrderedDict([
                                    ('b', np.array(['a', 'b', 'c', 'd', 'e'])),
                                    ('aa', np.array([(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]))
                                ]))
        self.assertEquals(len(npDataFrame), 5)

    @staticmethod
    def _createTestDataFrame():
        npDataFrame = NumpyDataFrame()
        npDataFrame.addArray('floats', [float(_) for _ in range(5)])
        npDataFrame.addArray('strs', 'ab cd efg hi j'.split(' '))
        npDataFrame.addArray('tuples', [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)])
        return npDataFrame

    def testIndexing(self):
        npDataFrame = self._createTestDataFrame()
        
        singleEl = npDataFrame[1]
        self.assertAlmostEqual(singleEl['floats'], 1.0)
        self.assertEquals(singleEl['strs'], 'cd')
        self.assertListsOrDicts(singleEl['tuples'], np.array([3, 4]))

        slicedNpDataFrame = npDataFrame[[1, 3]]
        self.assertNotEquals(id(slicedNpDataFrame), id(npDataFrame))
        self.assertListsOrDicts(slicedNpDataFrame.getArray('floats'), np.array([1.0, 3.0]))
        self.assertListsOrDicts(slicedNpDataFrame.getArray('strs'),
                                np.array(['cd', 'hi'], dtype='S3'))
        self.assertListsOrDicts(slicedNpDataFrame.getArray('tuples'), np.array([(3, 4), (7, 8)]))

        self.assertRaises(IndexError, npDataFrame.__getitem__, 5)
        self.assertRaises(IndexError, npDataFrame.__getitem__, [1, 5])

    def testSlicing(self):
        npDataFrame = self._createTestDataFrame()

        slicedNpDataFrame = npDataFrame[1:4]
        self.assertNotEquals(id(slicedNpDataFrame), id(npDataFrame))
        self.assertListsOrDicts(slicedNpDataFrame.getArray('floats'), np.array([1.0, 2.0, 3.0]))
        self.assertListsOrDicts(slicedNpDataFrame.getArray('strs'), np.array(['cd', 'efg', 'hi']))
        self.assertListsOrDicts(slicedNpDataFrame.getArray('tuples'),
                                np.array([(3, 4), (5, 6), (7, 8)]))

    def testAssignSingleIndex(self):
        npDataFrame = self._createTestDataFrame()

        npDataFrame[1] = npDataFrame[0]
        self.assertListsOrDicts(npDataFrame.getArray('floats'),
                                np.array([0.0, 0.0, 2.0, 3.0, 4.0]))
        self.assertListsOrDicts(npDataFrame.getArray('strs'),
                                np.array(['ab', 'ab', 'efg', 'hi', 'j']))
        self.assertListsOrDicts(npDataFrame.getArray('tuples'),
                                np.array([(1, 2), (1, 2), (5, 6), (7, 8), (9, 10)]))

        self.assertRaises(ValueError, npDataFrame.__setitem__, 1, 'a')

    def testAssignMultipleIndexes(self):
        npDataFrame = self._createTestDataFrame()

        npDataFrame[[1, 3]] = npDataFrame[[0, 2]]
        self.assertListsOrDicts(npDataFrame.getArray('floats'),
                                np.array([0.0, 0.0, 2.0, 2.0, 4.0]))
        self.assertListsOrDicts(npDataFrame.getArray('strs'),
                                np.array(['ab', 'ab', 'efg', 'efg', 'j']))
        self.assertListsOrDicts(npDataFrame.getArray('tuples'),
                                np.array([(1, 2), (1, 2), (5, 6), (5, 6), (9, 10)]))

        self.assertRaises(ValueError, npDataFrame.__setitem__, [1, 3], 'a')

    def testAssignSlice(self):
        npDataFrame = self._createTestDataFrame()

        npDataFrame[1:4] = npDataFrame[[0, 2, 4]]
        self.assertListsOrDicts(npDataFrame.getArray('floats'),
                                np.array([0.0, 0.0, 2.0, 4.0, 4.0]))
        self.assertListsOrDicts(npDataFrame.getArray('strs'),
                                np.array(['ab', 'ab', 'efg', 'j', 'j']))
        self.assertListsOrDicts(npDataFrame.getArray('tuples'),
                                np.array([(1, 2), (1, 2), (5, 6), (9, 10), (9, 10)]))

        self.assertRaises(ValueError, npDataFrame.__setslice__, 1, 3, 'a')

    def testUpdateArray(self):
        npDataFrame = self._createTestDataFrame()

        npDataFrame.updateArray('floats', npDataFrame.getArray('floats')[::-1])
        self.assertListsOrDicts(npDataFrame.getArray('floats'),
                                np.array([4.0, 3.0, 2.0, 1.0, 0.0]))

        npDataFrame.updateArray('strs', npDataFrame.getArray('strs')[::-1])
        self.assertListsOrDicts(npDataFrame.getArray('strs'),
                                np.array(['j', 'hi', 'efg', 'cd', 'ab']))

        npDataFrame.updateArray('tuples', npDataFrame.getArray('tuples')[::-1])
        self.assertListsOrDicts(npDataFrame.getArray('tuples'),
                                np.array([(9, 10), (7, 8), (5, 6), (3, 4), (1, 2)]))

        self.assertRaises(ValueError, npDataFrame.updateArray, 'floats', np.arange(4))

    def testSliceAndUpdateArray(self):
        npDataFrame = self._createTestDataFrame()

        slicedDataFrame = npDataFrame[1:4]
        slicedDataFrame.updateArray('floats', np.array([3.0 ,2.0, 1.0]))
        self.assertListsOrDicts(npDataFrame.getArray('floats'),
                                np.array([0.0, 3.0, 2.0, 1.0, 4.0]))

    def testSort(self):
        npDataFrame = NumpyDataFrame(dict(a=[2,3,2], b=[3,1,1], c=['c', 'b', 'a']))

        npDataFrame.sort(order=['c'])
        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array([2,3,2]))
        self.assertListsOrDicts(npDataFrame.getArray('b'), np.array([1,1,3]))
        self.assertListsOrDicts(npDataFrame.getArray('c'), np.array(['a', 'b', 'c']))

        npDataFrame = NumpyDataFrame(dict(a=[2, 3, 2], b=[3, 1, 1], c=['c', 'b', 'a']))
        npDataFrame.sort(order=['a'])
        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array([2,2,3]))
        self.assertListsOrDicts(npDataFrame.getArray('b'), np.array([3,1,1]))
        self.assertListsOrDicts(npDataFrame.getArray('c'), np.array(['c', 'a', 'b']))

        npDataFrame = NumpyDataFrame(dict(a=[2, 3, 2], b=[3, 1, 1], c=['c', 'b', 'a']))
        npDataFrame.sort(order=['b'])
        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array([3,2,2]))
        self.assertListsOrDicts(npDataFrame.getArray('b'), np.array([1,1,3]))
        self.assertListsOrDicts(npDataFrame.getArray('c'), np.array(['b', 'a', 'c']))

        npDataFrame = NumpyDataFrame(dict(a=[2, 3, 2], b=[3, 1, 1], c=['c', 'b', 'a']))
        npDataFrame.sort(order=['b', 'a'])
        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array([2,3,2]))
        self.assertListsOrDicts(npDataFrame.getArray('b'), np.array([1,1,3]))
        self.assertListsOrDicts(npDataFrame.getArray('c'), np.array(['a', 'b', 'c']))

        self.assertRaises(AssertionError, npDataFrame.sort, order=[])
        self.assertRaises(AssertionError, npDataFrame.sort, order=['a', 'd'])

    def testNumpyMethods(self):
        npDataFrame = self._createTestDataFrame()

        strNpDataFrame = npDataFrame.astype('S3')
        self.assertListsOrDicts(strNpDataFrame.getArray('floats'),
                                np.array(['0.0', '1.0', '2.0', '3.0', '4.0']))
        self.assertListsOrDicts(strNpDataFrame.getArray('strs'),
                                np.array(['ab', 'cd', 'efg', 'hi', 'j']))
        self.assertListsOrDicts(strNpDataFrame.getArray('tuples'),
                                np.array([('1', '2'), ('3', '4'), ('5', '6'),
                                          ('7', '8'), ('9', '10')], dtype='S3'))

        self.assertRaises(TypeError, npDataFrame.sum)
        npDataFrame.removeArray('strs')
        self.assertListsOrDicts(npDataFrame.sum(), OrderedDict([('floats', 10.0),
                                                                ('tuples', 55)]))

        from numpy import random
        random.seed(0)
        from copy import deepcopy
        randomNpDataFrame = deepcopy(npDataFrame)
        random.shuffle(randomNpDataFrame)
        self.assertEquals(len(randomNpDataFrame), len(npDataFrame))
        self.assertFalse(all((randomNpDataFrame == npDataFrame).all().values()))

    def testCopy(self):
        from copy import copy, deepcopy
        npDataFrame = self._createTestDataFrame()
        npDataFrame.mask = [False, True, False, True, True]

        npDataFrameCopy = copy(npDataFrame)
        npDataFrameDeepCopy = deepcopy(npDataFrame)

        self.assertListsOrDicts(npDataFrameCopy.asArrayDict(), npDataFrame.asArrayDict())
        self.assertListsOrDicts(npDataFrameDeepCopy.asArrayDict(), npDataFrame.asArrayDict())

        self.assertTrue(all([id(npDataFrameCopy._arrayDict[key]) == id(npDataFrame._arrayDict[key])
                             for key in npDataFrame.arrayKeys()]))
        self.assertFalse(all([id(npDataFrameDeepCopy._arrayDict[key]) ==
                              id(npDataFrame._arrayDict[key])
                             for key in npDataFrame.arrayKeys()]))

        self.assertTrue(id(npDataFrameCopy.mask) == id(npDataFrame.mask))
        self.assertFalse(id(npDataFrameDeepCopy.mask) is id(npDataFrame.mask))

    def testInitMask(self):
        npDataFrame = NumpyDataFrame(dict(a=range(5)),
                                           mask=[False, False, True, False, True])
        self.assertListsOrDicts(npDataFrame.mask, np.array([False, False, True, False, True]))

        npDataFrame = NumpyDataFrame(dict(a=range(5)), mask=range(5))
        self.assertListsOrDicts(npDataFrame.mask, np.array([False, True, True, True, True]))

        npDataFrame = NumpyDataFrame(dict(a=range(5)))
        self.assertIsNone(npDataFrame.mask)
        npDataFrame.mask = [False, False, True, False, True]
        self.assertListsOrDicts(npDataFrame.mask, np.array([False, False, True, False, True]))

        npDataFrame.mask = np.array([False, False, True, False, True])
        self.assertListsOrDicts(npDataFrame.mask, np.array([False, False, True, False, True]))

        npDataFrame.mask = range(5)
        self.assertListsOrDicts(npDataFrame.mask, np.array([False, True, True, True, True]))

        self.assertRaises(ValueError, npDataFrame.__setattr__, 'mask', range(4))

        npDataFrame.mask = None
        self.assertIsNone(npDataFrame.mask)

    def testMask(self):
        npDataFrame = NumpyDataFrame(dict(a=range(5), b='a b c d e'.split(' ')))
        npDataFrame.mask = [False, False, True, False, True]

        self.assertListsOrDicts(npDataFrame.asArrayDict(),
                                OrderedDict([('a', np.array([0, 1, 3])),
                                             ('b', np.array(['a', 'b', 'd']))]))
        self.assertListsOrDicts(npDataFrame.getArrayNoMask('a'), np.array([0, 1, 2, 3, 4]))
        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array([0, 1, 3]))
        self.assertEquals(len(npDataFrame), 5)

        slicedDataFrame = npDataFrame[1:4]
        self.assertListsOrDicts(slicedDataFrame.mask, np.array([False, True, False]))
        self.assertListsOrDicts(slicedDataFrame.asArrayDict(),
                                OrderedDict([('a', np.array([1, 3])),
                                             ('b', np.array(['b', 'd']))]))
        self.assertListsOrDicts(slicedDataFrame.getArrayNoMask('a'), np.array([1, 2, 3]))
        self.assertListsOrDicts(slicedDataFrame.getArray('a'), np.array([1, 3]))
        self.assertEquals(len(slicedDataFrame), 3)

        npDataFrame.mask[0:2] = True

        self.assertListsOrDicts(npDataFrame.asArrayDict(),
                                OrderedDict([('a', np.array([3])), ('b', np.array(['d']))]))
        self.assertListsOrDicts(npDataFrame.getArrayNoMask('a'), np.array([0, 1, 2, 3, 4]))
        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array([3]))
        self.assertEquals(len(npDataFrame), 5)

    def testMaskSorting(self):
        npDataFrame = NumpyDataFrame(dict(a=range(5), b='e d c b a'.split(' ')))
        npDataFrame.mask = [False, False, True, False, True]
        npDataFrame.sort(['b'])

        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array([3, 1, 0]))

        npDataFrame.mask = [False, False, False, False, False]
        self.assertListsOrDicts(npDataFrame.getArray('a'), np.array([4, 3, 2, 1, 0]))


if __name__ == "__main__":
    unittest.main()
