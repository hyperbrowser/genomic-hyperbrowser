from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic

from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq


class CountFunctionTrackBasedOnTresholdStat(MagicStatFactory):
    pass

class CountFunctionTrackBasedOnTresholdStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def _init(self, treshold=0.1, **kwArgs):
        self.treshold = float(treshold)

    def _compute(self):

        tv = self._children[0].getResult()
        vals = tv.valsAsNumpyArray()

        assert vals is not None

        valsOutput = []
        for vIt, v in enumerate(vals):
            if v > self.treshold:
                valsOutput.append(vIt)

        return valsOutput



    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(val='number', allowOverlaps=self._configuredToAllowOverlaps(strict=False))) )
