from gold.track.TsBasedRandomTrackViewProvider import BetweenTrackRandomTvProvider, TsBasedRandomTrackViewProvider
from random import shuffle

class ShuffleTracksTvProvider(BetweenTrackRandomTvProvider):

    UNKNOWN_GENOME = 'unknown' #used for unique ID generation

    def __init__(self, origTs, binSource, *args, **kwArgs):
        TsBasedRandomTrackViewProvider.__init__(self, origTs, binSource=binSource, *args, **kwArgs)
        self._randTs = origTs._copyTreeStructure()
        self._sTSList = self._randTs.getLeafNodes()
        self._trackList = [x.track for x in self._sTSList]
        self._trackIdList = [sts.track.getUniqueKey(
            self._binSource.genome if self._binSource.genome else self.UNKNOWN_GENOME) \
            for sts in self._sTSList]
        self._shufflePool = {}

    def getTrackView(self, region, origTrack, randIndex):
        if randIndex not in self._shufflePool:
            self._shuffleTracks(randIndex)
        return self._shufflePool[randIndex][self._getTrackIndexFromTrackUniqueId(origTrack)].getTrackView(region)

    def _getTrackIndexFromTrackUniqueId(self, origTrack):
        uniqueId = origTrack.getUniqueKey(self._binSource.genome if self._binSource.genome else self.UNKNOWN_GENOME)
        trackIndex = self._trackIdList.index(uniqueId)
        return trackIndex

    def _shuffleTracks(self, randIndex):
        shuffledTrackList = list(self._trackList)
        shuffle(shuffledTrackList)
        self._shufflePool[randIndex] = shuffledTrackList

