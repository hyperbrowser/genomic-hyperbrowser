from gold.track.PermutedSegsAndIntersegsTrack import PermutedSegsAndIntersegsTrack
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack
from gold.track.Track import Track
from gold.track.TsBasedRandomTrackViewProvider import TsBasedRandomTrackViewProvider, WithinTrackRandomTvProvider
from gold.util.CustomExceptions import  NotSupportedError
from quick.application.SignatureDevianceLogging import takes
from test.gold.track.common.SampleTrack import SampleTrack

class PermutedSegsAndIntersegsTrackViewProvider(WithinTrackRandomTvProvider):
    def __init__(self, origTs, allowOverlaps, *args, **kwargs):
        self._poolDict = {}
        if allowOverlaps == True:
            raise NotSupportedError('Overlaps are not supported in this type of randomization')
        TsBasedRandomTrackViewProvider.__init__(self, origTs, False)

    @takes('PermutedSegsAndIntersegsTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def getTrackView(self, region, origTrack, randIndex):
        if region not in self._poolDict:
            self._poolDict[region] = RandomizedSegsTvProviderPool(region, PermutedSegsAndIntersegsTrack)
        self._poolDict[region].getTrackView(origTrack, randIndex)
        # return PermutedSegsAndIntersegsTrack(origTrack, randIndex).getTrackView(region)

class PermutedSegsAndSampledIntersegsTrackViewProvider(WithinTrackRandomTvProvider):
    def __init__(self, origTs, allowOverlaps, *args, **kwargs):
        self._poolDict = {}
        if allowOverlaps == True:
            raise NotSupportedError('Overlaps are not supported in this type of randomization')
        TsBasedRandomTrackViewProvider.__init__(self, origTs, False)

    @takes('PermutedSegsAndSampledIntersegsTrackViewProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def getTrackView(self, region, origTrack, randIndex):
        if region not in self._poolDict:
            self._poolDict[region] = RandomizedSegsTvProviderPool(region, PermutedSegsAndSampledIntersegsTrack)
        return self._poolDict[region].getTrackView(origTrack, randIndex)
        # return PermutedSegsAndSampledIntersegsTrack(origTrack, randIndex).getTrackView(region)


class RandomizedSegsTvProviderPool(object):

    def __init__(self, region, permutedTrackClass):
        self._region = region
        self._permutedTrackClass = permutedTrackClass
        self._pool = {}

    def getTrackView(self, origTrack, randIndex):
        if (randIndex - 1) in self._pool:
            self._cleanData()
        if randIndex not in self._pool:
            self._pool[randIndex] = {}
        trackId = origTrack.getUniqueKey(self._region)
        if trackId not in self._pool[randIndex]:
            self._pool[randIndex][trackId] = self._permutedTrackClass(origTrack, randIndex).getTrackView(self._region)
        return self._pool[randIndex][trackId]

    def _cleanData(self):
        self._pool = {}