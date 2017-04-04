from gold.util.CustomExceptions import AbstractClassError


class TsBasedRandomTrackViewProvider(object):
    def __init__(self, origTs, **kwargs):
        self._origTs = origTs
        self._elementPoolDict = {}

    def getTrackView(self, region, trackTitle, randIndex):
        raise AbstractClassError


class ShuffleElementsBetweenTracksTvProvider(TsBasedRandomTrackViewProvider):
    def getTrackView(self, region, trackSomeUniqueID, randIndex):
        if region not in self._elementPoolDict:
            self._populatePool(region)
        return self._elementPoolDict[region].getOneTrackFromPool(trackSomeUniqueID, randIndex)

    def _populatePool(self, region):
        self._elementPoolDict[region] = ShuffleElementsBetweenTracksPool(self._origTs, region)


class ShuffleElementsBetweenTracksPool(object):
    def __init__(self, origTs, region):
        self._origTs = origTs
        self._region = region
        self._preparedTracks = {} #Double dict, where _preparedTracks[randIndex] gives a dict with trackSomeUniqueIDs as keys

        #TODO: trackSomeUniqueID should maybe just be mapped over to a numbers from 0..T (num tracks in origTS)
        self._trackSomeUniqueIDToIndexDict = {}

    def getOneTrackFromPool(self, trackSomeUniqueID, randIndex):
        trackIndex = self._trackSomeUniqueIDToIndexDict[trackSomeUniqueID]
        if randIndex not in self._preparedTracks:
            self._computePreparedTracks(randIndex)

    def _computePreparedTracks(self, randIndex):
        #TODO: put in Lonnekes algorithm, to take data from origTs and shuffle into self._computePreparedTracks[randIndex][i] for i in 0..numTracks


