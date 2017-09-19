from gold.track.PermutedSegsAndIntersegsTrack import PermutedSegsAndIntersegsTrack
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack
from gold.track.Track import Track
from gold.track.TsBasedRandomTrackViewProvider import TsBasedRandomTrackViewProvider, WithinTrackRandomTvProvider
from gold.util.CustomExceptions import  NotSupportedError
from quick.application.SignatureDevianceLogging import takes
from test.gold.track.common.SampleTrack import SampleTrack

class PermutedSegsAndIntersegsTrackViewProvider(WithinTrackRandomTvProvider):
    def __init__(self, origTs, allowOverlaps):
        if allowOverlaps == True:
            raise NotSupportedError('Overlaps are not supported in this type of randomization')
        TsBasedRandomTrackViewProvider.__init__(self, origTs, False)

    @takes('PermutedSegsAndIntersegsTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def getTrackView(self, region, origTrack, randIndex):
        return PermutedSegsAndIntersegsTrack(origTrack, randIndex).getTrackView(region)

class PermutedSegsAndSampledIntersegsTrackViewProvider(WithinTrackRandomTvProvider):
    def __init__(self, origTs, allowOverlaps):
        if allowOverlaps == True:
            raise NotSupportedError('Overlaps are not supported in this type of randomization')
        TsBasedRandomTrackViewProvider.__init__(self, origTs, False)

    @takes('PermutedSegsAndSampledIntersegsTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def getTrackView(self, region, origTrack, randIndex):
        return PermutedSegsAndSampledIntersegsTrack(origTrack, randIndex).getTrackView(region)

