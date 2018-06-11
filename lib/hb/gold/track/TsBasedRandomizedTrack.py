from gold.track.RandomizedTrack import RandomizedTrack
from quick.util.CommonFunctions import getClassName


class TsBasedRandomizedTrack(RandomizedTrack):
    def __init__(self, origTrack, randTvProvider, randIndex, **kwArgs):
        self._randTvProvider = randTvProvider
        self._randIndex = randIndex
        super(TsBasedRandomizedTrack, self).__init__(origTrack, randIndex, **kwArgs)

    def _getRandTrackView(self, region):
        randTv = self._randTvProvider.getTrackView(region, self._origTrack, self._randIndex)

        # TODO: Add self._undoTrackViewChanges or similar functionality

        return randTv

    def setRandIndex(self, randIndex):
        self._randIndex = randIndex

    def supportsTrackFormat(self, origTrackFormat):
        return self._randTvProvider.supportsTrackFormat(origTrackFormat)

    def supportsOverlapMode(self, allowOverlaps):
        return self._randTvProvider.supportsOverlapMode(allowOverlaps)

    def getDescription(self):
        return '{} using {}'.format(getClassName(self), getClassName(self._randTvProvider))

