from gold.track.Track import Track
from gold.util.CustomExceptions import AbstractClassError
from quick.application.SignatureDevianceLogging import takes
from test.gold.track.common.SampleTrack import SampleTrack

NUMBER_OF_SEGMENTS = 'Number of segments'
COVERAGE = 'Base pair coverage'

class TsBasedRandomTrackViewProvider(object):
    @takes('TsBasedRandomTrackViewProvider', 'TrackStructureV2', bool)
    def __init__(self, origTs, allowOverlaps):
        self._origTs = origTs
        self._allowOverlaps = allowOverlaps

    @takes('TsBasedRandomTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def getTrackView(self, region, origTrack, randIndex):
        raise AbstractClassError

class BetweenTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    def __init__(self, *args, **kwArgs):
        raise AbstractClassError

class WithinTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    def __init__(self, *args, **kwArgs):
        raise AbstractClassError

