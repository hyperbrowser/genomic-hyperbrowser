from abc import ABCMeta, abstractmethod

from gold.formatconversion.FormatConverter import TrivialFormatConverter
from gold.statistic.RawDataStat import RawDataStat
from gold.track.Track import Track
from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.util.CustomExceptions import NotSupportedError
from quick.util.CommonFunctions import prettyPrintTrackName


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
        self.formatConverters = [TrivialFormatConverter]  # To allow construction of uniqueID
        self._trackId = None  # To allow construction of uniqueID

        self._init(origTrack, randIndex, **kwArgs)

    def _init(self, origTrack, randIndex, **kwArgs):
        pass

    def getTrackView(self, region):
        if self._minimal and not self.WORKS_WITH_MINIMAL:
            return self._origTrack.getTrackView(region)

        randTV = self._getRandTrackView(region)

        assert self._trackFormatReq.isCompatibleWith(randTV.trackFormat), \
            'Incompatible track-format: ' + str(self._trackFormatReq) + \
            ' VS ' + str(randTV.trackFormat)

        return randTV

    @abstractmethod
    def _getRandTrackView(self, region):
        pass


class OrigTrackWrapper(Track):
    IS_MEMOIZABLE = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, origTrack, trackRandomizer):
        self._origTrack = origTrack
        self._trackRandomizer = trackRandomizer

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

    def __eq__(self, other):
        if isinstance(other, OrigTrackWrapper):
            return self._origTrack == other._origTrack
        else:
            return self._origTrack == other

    def __ne__(self, other):
        return not self == other
