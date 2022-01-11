from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq, NeutralTrackFormatReq
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from gold.util.CommonFunctions import isIter

class RawDataStat(MagicStatFactory):
    def __new__(cls, region, track, trackFormatReq, **kwArgs):
        assert isinstance(trackFormatReq, TrackFormatReq)
        return MagicStatFactory.__new__(cls, region, track, trackFormatReq=trackFormatReq, **kwArgs)


class RawDataStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    IS_MINIMAL_MEMOIZABLE = False

    def __init__(self, region, track, trackFormatReq=NeutralTrackFormatReq(), **kwArgs):
        if isIter(region):
            raise SplittableStatNotAvailableError()

        super(self.__class__, self).__init__(region, track, trackFormatReq=trackFormatReq, **kwArgs)
        self._track.addFormatReq(trackFormatReq)

    def _compute(self):
        return self._track.getTrackView(self._region)

    def _createChildren(self):
        self._children = []

    def _afterComputeCleanup(self):
        if self.hasResult():
            del self._result
