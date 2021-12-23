from gold.statistic.Statistic import Statistic
from numpy import concatenate, zeros, bincount

class AbstractHistStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    DTYPE='int32'

    def _compute(self):
        discreteMarks = self._children[0].getResult()
        if len(discreteMarks) == 0:
            return zeros(self._numHistBins, dtype=self.DTYPE)
        hist = bincount(discreteMarks.astype(self.DTYPE))
        if len(hist) != self._numHistBins:
            zeros(self._numHistBins-len(hist), dtype=self.DTYPE)
            hist = concatenate([hist, zeros(self._numHistBins-len(hist), dtype=self.DTYPE)])
        return hist
