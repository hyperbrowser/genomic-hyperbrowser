from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
from urllib import quote

from gold.util.CustomExceptions import ShouldNotOccurError
from proto.CommonFunctions import ensurePathExists


class StatTvOutputWriterStat(MagicStatFactory):
    pass


class StatTvOutputWriterStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = self._childResults[0]
        for childResult in self._childResults:
            if childResult != self._result:
                raise ShouldNotOccurError('All output filenames should be the same.')


class StatTvOutputWriterStatUnsplittable(Statistic):
    def _init(self, trackFilePath, trackGenerationStat, **kwArgs):
        import urllib
        self._trackFilePath = urllib.unquote(trackFilePath)
        self._trackGenerationStat = self.getRawStatisticClass(trackGenerationStat)

    def _compute(self):
        ensurePathExists(self._trackFilePath)
        outputFile = open(self._trackFilePath, 'a')

        trackView = self._children[0].getResult()
        starts = trackView.startsAsNumpyArray()
        ends = trackView.endsAsNumpyArray()

        for segmentIndex in range(0, len(starts)):
            outputFile.write('\t'.join([self._region.chr, str(starts[segmentIndex]), str(ends[segmentIndex])]) + '\n')

        outputFile.close()
        return quote(self._trackFilePath)

    def _createChildren(self):
        self._addChild(self._trackGenerationStat(self._region, self._track, **self._kwArgs))