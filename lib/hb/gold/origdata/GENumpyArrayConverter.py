from gold.origdata.GenomeElement import GenomeElement
from gold.origdata.GESourceWrapper import GESourceWrapper
import numpy as np


class GENumpyArrayConverter(GESourceWrapper):

    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._origGE = None
        self._npIter = iter([])
        self._colNames = self._geSource.getPrefixList()
        self._geIter = self._geSource.__iter__()

    def __iter__(self):
        self._origGE = None
        self._npIter = iter([])
        self._geIter = self._geSource.__iter__()
        return self

    def _iter(self):
        pass

    def next(self):
        vals = next(self._npIter, None)
        if not vals:
            self._origGE = self._geIter.next()

            self._npIter = np.nditer([getattr(self._origGE, col) for col in self._colNames])
            vals = next(self._npIter, None)

        ge = GenomeElement(genome=self._origGE.genome, chr=self._origGE.chr)
        # the reshape is here because some Fasta can have only one letter as a value
        if isinstance(vals, np.ndarray) and vals.size == 1:
            vals = vals.reshape((1,))
        for val, col in zip(vals, self._colNames):
            setattr(ge, col, val.item())

        return ge

    def getBoundingRegionTuples(self):
        if self._geSource:
            return self._geIter.getBoundingRegionTuples()
        else:
            return []
