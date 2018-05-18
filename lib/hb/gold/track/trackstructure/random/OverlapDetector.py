from gold.util.CustomExceptions import AbstractClassError


class OverlapDetector(object):
    def __init__(self, excludedSegments):
        raise AbstractClassError()

    def overlaps(self, start, end):
        raise AbstractClassError()

    def addSegment(self, start, end):
        raise AbstractClassError()


class IntervalTreeOverlapDetector(OverlapDetector):
    def __init__(self, excludedSegments=None):
        from bx.intervals.intersection import IntervalTree
        self._intervalTree = IntervalTree()
        if excludedSegments:
            for start, end in excludedSegments:
                self._intervalTree.add(start, end)

    def overlaps(self, start, end):
        return bool(self._intervalTree.find(start, end))

    def addSegment(self, start, end):
        self._addElementHandleBxPythonZeroDivisionException(start, end)
        # self._intervalTree.add(start, end)

    def _addElementHandleBxPythonZeroDivisionException(self, start, end, nrTries=10):
        """
        DivisionByZero error is caused by a bug in the bx-python library.
        It happens rarely, so we just execute the add command again up to nrTries times
        when it does. If it pops up more than 10 times, we assume something else is wrong and
        raise.
        """
        cnt = 0
        while True:
            cnt += 1
            try:
                self._intervalTree.add(start, end)
            except Exception as e:
                from gold.application.LogSetup import logMessage, logging
                logMessage("Try nr %i. %s" % (cnt, str(e)), level=logging.WARN)
                if cnt > nrTries:
                    raise e
                continue
            else:
                break
