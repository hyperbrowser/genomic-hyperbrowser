from abc import ABCMeta, abstractmethod, abstractproperty
from collections import Iterable

from gold.track.RandomizedTrack import TrackRandomizer
from gold.track.Track import Track
from gold.track.trackstructure.TsVisitors import TsWrapOrigTracksVisitor
from quick.application.SignatureDevianceLogging import takes
from gold.track.TrackStructure import TrackStructureV2
from quick.util.CommonFunctions import getClassName
from test.gold.track.common.SampleTrack import SampleTrack

NUMBER_OF_SEGMENTS = 'Number of segments'
COVERAGE = 'Base pair coverage'


class TsBasedRandomTrackViewProvider(TrackRandomizer):
    __metaclass__ = ABCMeta

    @abstractproperty
    def _NEEDS_ORIG_TRACK_SOURCE(self):
        pass

    @abstractproperty
    def _NEEDS_BIN_SOURCE(self):
        pass

    @abstractproperty
    def _SUPPORTS_LOCAL_ANALYSIS(self):
        pass

    def __init__(self):
        self._origTs = None
        self._binSource = None

    @takes('TsBasedRandomTrackViewProvider', 'TrackStructureV2')
    def setOrigTrackStructure(self, origTs):
        visitor = TsWrapOrigTracksVisitor()
        self._origTs = visitor.visitAllNodesAndReturnModifiedCopyOfTS(origTs, trackRandomizer=self)

    @takes('TsBasedRandomTrackViewProvider', Iterable)
    def setBinSource(self, binSource):
        self._binSource = binSource

    def supportsLocalAnalysis(self):
        return self._SUPPORTS_LOCAL_ANALYSIS

    @takes('TsBasedRandomTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def getTrackView(self, region, origTrack, randIndex):
        if not self._origTs and self._NEEDS_ORIG_TRACK_SOURCE:
            raise RuntimeError(getClassName(self) + ': '
                               'The original track structure needs to be provided to the '
                               'setOrigTrackStructure() method before the invocation of '
                               'getTrackView().')
        if not self._binSource and self._NEEDS_BIN_SOURCE:
            raise RuntimeError(getClassName(self) + ': '
                               'A binSource iterator returning GenomeRegions needs to be '
                               'provided to the setBinSource() method before the invocation of '
                               'getTrackView().')

        return self._getTrackView(region, origTrack, randIndex)

    @abstractmethod
    @takes('TsBasedRandomTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def _getTrackView(self, region, origTrack, randIndex):
        pass


class BetweenTracksRandomTvProvider(TsBasedRandomTrackViewProvider):
    pass


class WithinTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    pass

