from gold.util.CustomExceptions import AbstractClassError


class OverlapDetector(object):
    def __init__(self, excludedSegments):
        raise AbstractClassError()

    def overlaps(self, start, end):
        raise AbstractClassError()

    def addSegment(self, start, end):
        raise AbstractClassError()


class IntervalTreeOverlapDetector(OverlapDetector):
    def __init__(self, excludedSegments):
        from bx.intervals.intersection import IntervalTree
        self._intervalTree = IntervalTree()
        for start, end in excludedSegments:
            self._intervalTree.add(start, end)

    def overlaps(self, start, end):
        return bool(self._intervalTree.find(start, end))

    def addSegment(self, start, end):
        self._intervalTree.add(start, end)