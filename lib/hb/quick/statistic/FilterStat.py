from collections import OrderedDict

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq, TrackFormat
from quick.track_operations.utils.TrackHandling import createRawResultTrackView
from hb.quick.track_operations.TrackOperationsModule import parseBoolean


class FilterStat(MagicStatFactory):
    pass


class FilterStatUnsplittable(Statistic):

    def _init(self, removeStrands=False, removeValues=False, removeLinks=False,
            removeWeights=False, removeExtras=False, **kwargs):
        self._removeStrands = parseBoolean(removeStrands)
        self._removeValues = parseBoolean(removeValues)
        self._removeLinks = parseBoolean(removeLinks)
        self._removeWeights = parseBoolean(removeWeights)
        self._removeExtras = parseBoolean(removeExtras)

    def _compute(self):
        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        if self._removeStrands:
            strands = None
        else:
            strands = tv.strandsAsNumpyArray()

        if self._removeValues:
            vals = None
        else:
            vals = tv.valsAsNumpyArray()

        if self._removeLinks:
            # As edges needs its, we need to remove them,
            # and as weights needs edges, we need to remove them as well.
            ids = None
            edges = None
            weights = None
        else:
            ids = tv.idsAsNumpyArray()
            edges = tv.edgesAsNumpyArray()

            if self._removeWeights:
                weights = None
            else:
                weights = tv.weightsAsNumpyArray()

        if self._removeExtras:
            extras = None
        else:
            extras = tv.allExtrasAsDictOfNumpyArrays()


        resultTrackFormat = self._getResultTrackFormat(tv)

        return createRawResultTrackView(None, self._region, None, False,
                                  newStarts=starts, newEnds=ends,
                                  newValues=vals, newStrands=strands,
                                  newIds=ids, newEdges=edges,
                                  newWeights=weights, newExtras=extras,
                                  trackFormat=resultTrackFormat)


    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))

    def _getResultTrackFormat(self, tv1):
        """
        Creates the correct TrackFormatReq according to the input track
        :return:
        """

        tr = tv1.trackFormat
        # Gaps and lengths are not changed
        dense = tr.isDense()
        interval = tr.isInterval()

        valued = tr.isValued()
        linked = tr.isLinked()
        weighted = tr.isWeighted()
        stranded = tr.hasStrand()

        extra = tr.hasExtra()

        if not dense and not interval:
            # Points
            starts = []
            ends = None
        elif not dense and interval:
            # Segments
            starts = []
            ends = []
        elif dense and interval:
            # partition
            starts = None
            ends = []
        else:
            # function
            starts = []
            ends = []

        if stranded:
            if self._removeStrands:
                strands = None
            else:
                strands = []
        else:
            strands = []

        if valued:
            if self._removeValues:
                values = None
            else:
                values = []
        else:
            values = None

        if linked:
            if self._removeLinks:
                ids = None
                edges = None
                weights = None

            else:
                ids = []
                edges = []
                if weighted and self._removeWeights:
                    weights = None
                elif weighted:
                    # Same as with the value name
                    weights = []
                else:
                    weights = None
        else:
            ids = None
            edges = None
            weights = None

        if extra:
            if self._removeExtras:
                extras = None
            else:
                extras = OrderedDict()
        else:
            extras = None

        return TrackFormat(startList=starts, endList=ends, strandList=strands,  valList=values,
                           idList=ids, edgesList=edges, weightsList=weights, extraLists=extras)

