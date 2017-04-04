from gold.track.RandomizedTrack import RandomizedTrack


class TsBasedRandomizedTrack(RandomizedTrack):
    def __init__(self, origTrack, randTvProvider, randIndex, **kwArgs):
        self._origTrack = origTrack
        self._randTvProvider = randTvProvider
        self._randIndex = randIndex
        #self._trackSomeUniqueID = trackSomeUniqueID#TODO: correct naming, Name, Title, ID, the Track object itself ??
        #TODO should the __init__ of the superclass be called?

        super(TsBasedRandomizedTrack, self).__init__(origTrack, randIndex, **kwArgs)

    def getTrackView(self, region):
        return self._randTvProvider.getTrackView(region, self._origTrack, self._randIndex)

    #TODO: Add other overridden methods..


