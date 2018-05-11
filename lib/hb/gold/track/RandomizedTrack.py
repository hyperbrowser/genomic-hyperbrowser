import numpy

from abc import abstractmethod, ABCMeta

from gold.track.TrackView import TrackView
from gold.statistic.RawDataStat import RawDataStat
from gold.track.Track import Track
from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.util.CustomExceptions import AbstractClassError, NotSupportedError
from quick.util.CommonFunctions import getClassName, prettyPrintTrackName


class TrackRandomizer(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def supportsTrackFormat(cls, origTrackFormat):
        pass

    @classmethod
    @abstractmethod
    def supportsOverlapMode(cls, allowOverlaps):
        pass

    @classmethod
    def getDescription(cls):
        return cls.__name__


class RandomizedTrack(Track, TrackRandomizer):
    __metaclass__ = ABCMeta

    IS_MEMOIZABLE = False
    WORKS_WITH_MINIMAL = True

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, origTrack, randIndex, **kwArgs):
        self._origTrack = OrigTrackWrapper(origTrack, trackRandomizer=self)
        self.trackName = origTrack.trackName + ['Randomized', str(randIndex)]
        self.trackTitle = origTrack.trackTitle
        self._trackFormatReq = NeutralTrackFormatReq()
        self._cachedTV = None
        self._minimal = ('minimal' in kwArgs and kwArgs['minimal'] == True)

        from gold.formatconversion.FormatConverter import TrivialFormatConverter
        self.formatConverters = [TrivialFormatConverter]  # To allow construction of uniqueID
        self._trackId = None  # To allow construction of uniqueID

    def getTrackView(self, region):
        if self._minimal and not self.WORKS_WITH_MINIMAL:
            return self._origTrack.getTrackView(region)

        randTV = self._getRandTrackView(region)

        assert self._trackFormatReq.isCompatibleWith(randTV.trackFormat), \
            'Incompatible track-format: ' + str(self._trackFormatReq) + \
            ' VS ' + str(randTV.trackFormat)

        return randTV

    def _getRandTrackView(self, region):
        # if self._cachedTV is None:

        origTV = self._origTrack.getTrackView(region)

        starts, ends, vals, strands, ids, edges, weights, extras = \
            self._createRandomizedNumpyArrays(len(origTV.genomeAnchor), origTV.startsAsNumpyArray(), \
                                              origTV.endsAsNumpyArray(), origTV.valsAsNumpyArray(), \
                                              origTV.strandsAsNumpyArray(), origTV.idsAsNumpyArray(), \
                                              origTV.edgesAsNumpyArray(), origTV.weightsAsNumpyArray(), \
                                              origTV.allExtrasAsDictOfNumpyArrays(), region)

        starts, ends, vals, strands, ids, edges, weights, extras = \
            self._undoTrackViewChanges(starts, ends, vals, strands, ids, edges, weights, extras, origTV)

        self._cachedTV = TrackView(origTV.genomeAnchor, starts, ends, vals, strands, ids, edges, weights, \
                                   origTV.borderHandling, origTV.allowOverlaps, extraLists=extras)

        return self._cachedTV

    @classmethod
    def _undoTrackViewChanges(cls, starts, ends, vals, strands, ids, edges, weights, extras, origTV):
        if origTV.trackFormat.isPoints():
            ends = None

        elif origTV.trackFormat.isPartitionOrStepFunction():
            ends = numpy.append([0], ends)
            starts = None

        if starts is not None:
            starts += origTV.genomeAnchor.start

        if ends is not None:
            ends += origTV.genomeAnchor.start

        return starts, ends, vals, strands, ids, edges, weights, extras

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, region):
        raise AbstractClassError


class OrigTrackWrapper(Track):
    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, origTrack, trackRandomizer):
        self._origTrack = origTrack
        self._trackRandomizer = trackRandomizer

        # super(OrigTrackWrapper, self).__init__(origTrack.trackName, trackTitle=origTrack.trackTitle)

    @property
    def trackName(self):
        return self._origTrack.trackName

    @property
    def trackTitle(self):
        return self._origTrack.trackTitle

    @property
    def formatConverters(self):
        return self._origTrack.formatConverters

    def getTrackView(self, region):
        # To make sure that the origTrack is only read once across randomizations
        rawData = RawDataStat(region, self._origTrack, NeutralTrackFormatReq())
        origTv = rawData.getResult()

        if not self._trackRandomizer.supportsTrackFormat(origTv.trackFormat):
            raise NotSupportedError(
                'The original track "{}" has format "{}", '
                'which is not supported by "{}".'.format(
                    prettyPrintTrackName(self.trackName),
                    str(origTv.trackFormat),
                    self._trackRandomizer.getDescription()
                )
            )

        if not self._trackRandomizer.supportsOverlapMode(origTv.allowOverlaps):
            raise NotSupportedError(
                'The original track "{}" has "allowOverlaps={}", '
                'which is not supported by "{}".'.format(
                    prettyPrintTrackName(self.trackName),
                    origTv.allowOverlaps,
                    self._trackRandomizer.getDescription()
                )
            )

        assert origTv.borderHandling == 'crop'

        return origTv

    def addFormatReq(self, requestedTrackFormat):
        self._origTrack.addFormatReq(requestedTrackFormat)

    def setFormatConverter(self, converterClassName):
        self._origTrack.setFormatConverter(converterClassName)

    def getUniqueKey(self, genome):
        return self._origTrack.getUniqueKey(genome)

    def resetTrackSource(self):
        self._origTrack.resetTrackSource()

    def setRandIndex(self, randIndex):
        self._origTrack.setRandIndex()
