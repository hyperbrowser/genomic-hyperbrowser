class TsBasedRandomizedTrack(RandomizedTrack):
    def __init__(self, randTvProvider, randIndex, trackSomeUniqueID,  **kwargs):
        self._randTvProvider = randTvProvider
        self._randIndex = randIndex
        self._trackSomeUniqueID = trackSomeUniqueID#TODO: correct naming, Name, Title, ID, the Track object itself ??

    def getTrackView(self, region):
        return self._randTvProvider.getTrackView(region, self._trackSomeUniqueID, self._randIndex)

    #TODO: Add other overridden methods..


