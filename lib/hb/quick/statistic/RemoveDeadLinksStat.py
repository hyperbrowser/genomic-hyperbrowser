from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from quick.track_operations.raw_operations.RemoveDeadLinks import removeDeadLinks
from quick.track_operations.utils.TrackHandling import parseBoolean, \
    createEmptyTrackView, createRawResultTrackView


class RemoveDeadLinksStat(MagicStatFactory):
    pass


class RemoveDeadLinksStatUnsplittable(Statistic):

    def _init(self, useGlobal=False, newId=None, rawStatistic=None, **kwargs):
        self._useGlobal = parseBoolean(useGlobal)
        if newId == 'None':
            self._newId = None
        else:
            self._newId = newId
        self._rawStatistic = None
        if rawStatistic is not None:
            self._rawStatistic = self.getRawStatisticClass(rawStatistic)

    def _compute(self):
        tv = self._children[0].getResult()
        if not tv.trackFormat.isLinked():
            return tv
        # if self._useGlobal:
        #     self._globalIds = np.concatenate(([v.idsAsNumpyArray() for v in tv.values()]))

        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()
        weights = tv.weightsAsNumpyArray()

        self._globalIds = None
        ret = removeDeadLinks(ids=ids, edges=edges, weights=weights,
                              globalIds=self._globalIds, newId=self._newId)

        if ret is not None and len(ret) != 0:
            ids, edges, weights, index = ret

            return createRawResultTrackView(index, self._region, tv, True, newIds=ids,
                                          newEdges=edges, newWeights=weights, trackFormat=tv.trackFormat)

        else:
            return createEmptyTrackView(tv)

    def _createChildren(self):
        track2 = self._track2 if hasattr(self, '_track2') else None
        if self._rawStatistic:
            self._addChild(self._rawStatistic(self._region, self._track, track2, **self._kwArgs))
        else:
            self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))

    # def _setGlobalIds(self, track):
    #     """
    #     Improvements: test for uniqueness?
    #     Takes time.. Better to assume that the user knows this and have
    #     used ids that are unique.
    #     :param track: Input track of the operation
    #     :return:
    #     """
    #     trackViews = track.trackViews
    #     self._globalIds = np.concatenate(([x.idsAsNumpyArray() for x in
    #                                        trackViews.values()]))
