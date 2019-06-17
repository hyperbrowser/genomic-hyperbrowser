import unittest
import numpy
from gold.origdata.GenomeElement import GenomeElement
from quick.util.CommonFunctions import smartRecursiveAssertList, isListType

def AssertList(list1, list2, assertFunc=None):
    if not (len(list1) == len(list2)):
        print 'Lengths: ', len(list1), '!=', len(list2)
        print [x for x in list1], '!=', [x for x in list2]
        assert(False)
    for x,y in zip(list1, list2):
        assertFunc(x, y)

class TestCaseWithImprovedAsserts(unittest.TestCase):
    def assertEqual(self, a, b):
        if not self._assertIsNan(a, b):
            unittest.TestCase.assertEqual(self, a, b)

    def assertAlmostEqual(self, a, b):
        if not self._assertIsNan(a, b):
            unittest.TestCase.assertAlmostEqual(self, a, b, places=5)
    
    def assertAlmostEquals(self, a, b):
        if not self._assertIsNan(a, b):
            unittest.TestCase.assertAlmostEquals(self, a, b, places=5)
    
    def _assertIsNan(self, a, b):
        try:
            if not any(isListType(x) for x in [a,b]):
                if numpy.isnan(a):
                    self.assertTrue(b is not None and numpy.isnan(b))
                    return True
        except (TypeError, NotImplementedError):
            pass
        return False
        
    def assertListsOrDicts(self, a, b):
        try:
            smartRecursiveAssertList(a, b, self.assertEqual, self.assertAlmostEqual)
        except Exception, e:
            print 'Error in recursive assert of %s == %s' % (a, b)
            raise

    def assertGenomeElements(self, a, b):
        self.assertListsOrDicts(a.val, b.val)
        self.assertListsOrDicts(a.edges, b.edges)
        self.assertListsOrDicts(a.weights, b.weights)
        self.assertListsOrDicts(a.start, b.start)
        self.assertListsOrDicts(a.end, b.end)
        self.assertListsOrDicts(a.strand, b.strand)
        a.val = b.val = None
        a.edges = b.edges = None
        a.weights = b.weights = None

        # a.end is used in GtrackGenomeElementSource in _checkLastBoundingRegion so it can't set to None
        # here, checking for other fields here as well just to be sure
        if isinstance(a.start, numpy.ndarray):
            a.start = b.start = None
        if isinstance(a.end, numpy.ndarray):
            a.end = b.end = None
        if isinstance(a.strand, numpy.ndarray):
            a.strand = b.strand = None

        if a.extra:
            for e in a.orderedExtraKeys:
                self.assertListsOrDicts(a.extra[e], b.extra[e])
                a.extra.pop(e, None)
                b.extra.pop(e, None)

        return unittest.TestCase.assertEqual(self, a, b)
        
    def assertGenomeElementLists(self, a, b):
        self.assertEqual(sum([1 for el in a]), sum([1 for el in b]))
        
        for i, el in enumerate( b ):
            try:
                self.assertGenomeElements(a[i], el)

            except Exception, e:
                print a[i].toStr() + ' != ' + el.toStr()
                raise
