from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.track_operations.utils.TrackHandling import parseBoolean


class TrackOperationsManagerStat(MagicStatFactory):
    pass


class TrackOperationsManagerStatUnsplittable(Statistic):

    def _init(self, rawStatistic=None, postprocessStatistic=None, shouldPostprocessVar=None, **kwArgs):
        assert rawStatistic is not None

        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        if postprocessStatistic is not None:
            self._postprocessStatistic = self.getRawStatisticClass(postprocessStatistic)
        if shouldPostprocessVar is None:
            self._shouldPostProcess = True
        else:
            self._shouldPostProcess = parseBoolean(shouldPostprocessVar)

    def _compute(self):
        return self._children[0].getResult()

    def _createChildren(self):
        track2 = self._track2 if hasattr(self, '_track2') else None
        if self._shouldPostProcess:
            self._addChild(self._postprocessStatistic(self._region, self._track, track2, **self._kwArgs))
        else:
            self._addChild(self._rawStatistic(self._region, self._track, track2, **self._kwArgs))
