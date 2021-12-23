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
        for curBin in self._bins:
            for track in self._tracks:
                self._origTrackBinPairToTrackBinIndexDict[TrackBinPair(track, curBin)] = trackBinIndex
                trackBinIndex += 1

    def _getTrackAndBinIndexFromTrackBinIndex(self, trackBinIndex):
        trackIndex = trackBinIndex % len(self._tracks)
        binIndex = trackBinIndex / len(self._tracks)
        return trackIndex, binIndex

    def allTrackBinIndexes(self):
        for i in xrange(len(self._tracks)*len(self._bins)):
            yield i

    def allBins(self):
        return self._bins

    def allTracks(self):
        return self._tracks

    def getTrackBinIndexForTrackBinPair(self, trackBinPair):
        try:
            return self._origTrackBinPairToTrackBinIndexDict[trackBinPair]
        except KeyError:
            raise

    def getTrackBinPairForTrackBinIndex(self, trackBinIndex):
        trackIndex, binIndex = self._getTrackAndBinIndexFromTrackBinIndex(trackBinIndex)
        return TrackBinPair(self._tracks[trackIndex], self._bins[binIndex])

    def selectRandomTrack(self, trackProbabilities):
        import numpy as np
        assert len(self._tracks) == len(trackProbabilities)
        # TODO: Should be refactored to provide all the choices at once using the param 'size'
        selectedTrackIndex = np.random.choice(np.arange(0, len(self._tracks)), p=trackProbabilities)
        return self._tracks[selectedTrackIndex]

    def selectRandomBin(self, binProbabilities):
        import numpy as np
        assert len(self._bins) == len(binProbabilities)
        # TODO: Should be refactored to provide all the choices at once using the param 'size'
        selectedBinIndex = np.random.choice(np.arange(0, len(self._bins)), p=binProbabilities)
        return self._bins[selectedBinIndex]


class TrackBinPair(object):
    def __init__(self, track, bin):
        self.track = track
        self.bin = bin

    def __hash__(self):
        return hash((self.track.getUniqueKey(self.bin.genome), self.bin))

    def __eq__(self, other):
        return self.track == other.track and self.bin == other.bin

    def __ne__(self, other):
        return not self == other

    def getTrackView(self):
        return self.track.getTrackView(self.bin)
