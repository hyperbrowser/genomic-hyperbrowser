from gold.track.trackstructure.random.RandomizedTrackDataStorage import RandomizedTrackDataStorage
from gold.track.trackstructure.random.TrackBinIndexer import TrackBinPair


class RandomizeBetweenTracksAndBinsPool(object):
    def __init__(self, randAlgorithm, origTs, binSource):
        self._randAlgorithm = randAlgorithm
        self._randAlgorithm.initTrackBinIndexer(origTs, binSource)
        self._trackDataStorage = \
            RandomizedTrackDataStorage(self._randAlgorithm.getTrackBinIndexer(),
                                       self._randAlgorithm.getReadFromDiskTrackColumns(),
                                       self._randAlgorithm.getInitTrackColumns(),
                                       self._randAlgorithm.needsMask())

    def randomize(self):
        self._randAlgorithm.randomize(self._trackDataStorage)

    def getTrackView(self, region, origTrack):
        trackBinIndexer = self._randAlgorithm.getTrackBinIndexer()
        origTrackBinIndex = \
            trackBinIndexer.getTrackBinIndexForTrackBinPair(TrackBinPair(origTrack, region))
        return self._trackDataStorage.getTrackView(origTrackBinIndex)
