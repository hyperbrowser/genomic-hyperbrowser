from abc import ABCMeta, abstractproperty

from gold.track.PermutedSegsAndIntersegsTrack import PermutedSegsAndIntersegsTrack
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack
from gold.track.Track import Track
from gold.track.TsBasedRandomTrackViewProvider import WithinTrackRandomTvProvider
from quick.application.SignatureDevianceLogging import takes
from test.gold.track.common.SampleTrack import SampleTrack


class RandTrackBasedTrackViewProvider(WithinTrackRandomTvProvider):
    __metaclass__ = ABCMeta

    _NEEDS_ORIG_TRACK_SOURCE = False
    _NEEDS_BIN_SOURCE = False
    _SUPPORTS_LOCAL_ANALYSIS = False

    @abstractproperty
    def _RAND_TRACK_CLS(self):
        pass

    @takes('RandTrackBasedTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def _getTrackView(self, region, origTrack, randIndex):
        return self._RAND_TRACK_CLS(origTrack, randIndex).getTrackView(region)

    @classmethod
    def supportsTrackFormat(cls, origTrackFormat):
        return cls._RAND_TRACK_CLS.supportsTrackFormat(origTrackFormat)

    @classmethod
    def supportsOverlapMode(cls, allowOverlaps):
        return cls._RAND_TRACK_CLS.supportsOverlapMode(allowOverlaps)


class PermutedSegsAndIntersegsTrackViewProvider(RandTrackBasedTrackViewProvider):
    _RAND_TRACK_CLS = PermutedSegsAndIntersegsTrack


class PermutedSegsAndSampledIntersegsTrackViewProvider(RandTrackBasedTrackViewProvider):
    _RAND_TRACK_CLS = PermutedSegsAndSampledIntersegsTrack
