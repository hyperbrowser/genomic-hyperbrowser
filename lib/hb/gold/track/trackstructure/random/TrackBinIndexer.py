from collections import namedtuple

from gold.util.CustomExceptions import AbstractClassError


class TrackBinIndexer(object):
    def __init__(self, origTs, binSource):
        raise AbstractClassError()

    def allTrackBinIndexes(self):
        raise AbstractClassError()

    # def allBins(self):
    #     raise AbstractClassError()
    #
    # def allTracks(self):
    #     raise AbstractClassError()

    def getTrackBinIndexForTrackBinPair(self, TrackBinPair):
        raise AbstractClassError()

    def getTrackBinPairForTrackBinIndex(self, trackBinIndex):
        raise AbstractClassError()


class SimpleTrackBinIndexer(TrackBinIndexer):
    def __init__(self, origTs, binSource):
        self._tracks = [leafNode.track for leafNode in origTs.getLeafNodes()]
        self._bins = list(binSource)

        assert len(self._tracks) > 0
        assert len(self._bins) > 0

        self._origTrackBinPairToTrackBinIndexDict = {}

        trackBinIndex = 0
        for track in self._tracks:
            for curBin in self._bins:
                self._origTrackBinPairToTrackBinIndexDict[TrackBinPair(track, curBin)] = trackBinIndex
                trackBinIndex += 1

    def _getTrackAndBinIndexFromTrackBinIndex(self, trackBinIndex):
        trackIndex = trackBinIndex / len(self._tracks)
        binIndex = trackBinIndex % len(self._bins)
        return trackIndex, binIndex

    def allTrackBinIndexes(self):
        for i in xrange(len(self._tracks)*len(self._bins)):
            yield i

    # def allBins(self):
    #     raise AbstractClassError()
    #
    # def allTracks(self):
    #     raise AbstractClassError()

    def getTrackBinIndexForTrackBinPair(self, trackBinPair):
        return self._origTrackBinPairToTrackBinIndexDict[trackBinPair]

    def getTrackBinPairForTrackBinIndex(self, trackBinIndex):
        trackIndex, binIndex = self._getTrackAndBinIndexFromTrackBinIndex(trackBinIndex)
        return TrackBinPair(self._tracks[trackIndex], self._bins[binIndex])

    def selectRandomTrack(self, trackProbabilities):
        import numpy as np
        assert len(self._tracks) == len(trackProbabilities)
        selectedTrackIndex = np.random.choice(range(0, len(self._tracks)), p=trackProbabilities)
        return self._tracks[selectedTrackIndex]

    def selectRandomBin(self, binProbabilities):
        import numpy as np
        assert len(self._bins) == len(binProbabilities)
        selectedBinIndex = np.random.choice(range(0, len(self._bins)), p=binProbabilities)
        return self._bins[selectedBinIndex]


class TrackBinPair(object):
    def __init__(self, track, bin):
        self.track = track
        self.bin = bin

    def __hash__(self):
        return hash(self.track.getUniqueKey(self.bin.genome), self.bin)

    def getTrackView(self):
        return self.track.getTrackView(self.bin)
