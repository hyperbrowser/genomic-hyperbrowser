
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from quick.track_operations.raw_operations.UniquifyLinks import uniquifyLinks
from quick.track_operations.utils.TrackHandling import createRawResultTrackView
from hb.quick.track_operations.TrackOperationsModule import parseBoolean, createEmptyTrackView


class UniquifyLinksStat(MagicStatFactory):
    pass


class UniquifyLinksStatUnsplittable(Statistic):

    def _init(self, useGlobal=False, identifier=None, **kwargs):
        self._useGlobal = parseBoolean(useGlobal)
        if identifier == 'None':
            self._identifier = None
        else:
            self._identifier = identifier

    def _compute(self):
        tv = self._children[0].getResult()
        if not tv.trackFormat.isLinked():
            return tv

        ids = tv.idsAsNumpyArray()
        edges = tv.edgesAsNumpyArray()

        ret = uniquifyLinks(ids, edges, self._identifier)

        if ret is not None and len(ret) != 0:
            newIds, newEdges, index = ret

            return createRawResultTrackView(index, self._region, tv, True,
                                          newIds=newIds, newEdges=newEdges,
                                          trackFormat=tv.trackFormat)

        else:
            return createEmptyTrackView(tv)

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))
