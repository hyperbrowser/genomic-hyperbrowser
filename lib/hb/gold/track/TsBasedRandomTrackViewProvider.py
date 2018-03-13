from gold.origdata.GESourceWrapper import GESourceWrapper
from gold.track.Track import Track
from gold.util.CustomExceptions import AbstractClassError
from quick.application.SignatureDevianceLogging import takes
from quick.application.UserBinSource import BinSource
from test.gold.track.common.SampleTrack import SampleTrack
from third_party.typecheck import one_of

NUMBER_OF_SEGMENTS = 'Number of segments'
COVERAGE = 'Base pair coverage'

class TsBasedRandomTrackViewProvider(object):
    # @takes('TsBasedRandomTrackViewProvider', 'TrackStructureV2', one_of(None, GESourceWrapper, BinSource), one_of(None, 'TrackStructureV2'), bool)
    def __init__(self, origTs, binSource=None, excludedTs=None,  allowOverlaps=False):
        # TODO: Remove binSource and excludedTs here and where the init is called
        self._origTs = origTs
        self._allowOverlaps = allowOverlaps
        self._excludedTs = excludedTs
        self._binSource = binSource


    @takes('TsBasedRandomTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def getTrackView(self, region, origTrack, randIndex):
        raise AbstractClassError

class BetweenTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    def __init__(self, *args, **kwArgs):
        raise AbstractClassError

class WithinTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    def __init__(self, *args, **kwArgs):
        raise AbstractClassError

