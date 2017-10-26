import numpy as np

from gold.track.trackstructure.random.OverlapDetector import IntervalTreeOverlapDetector
from gold.track.trackstructure.random.RandomizedTrackDataStorage import RandomizedTrackDataStorage
from gold.track.trackstructure.random.TrackBinIndexer import TrackBinPair, SimpleTrackBinIndexer
from gold.util.CustomExceptions import AbstractClassError


class InvalidPositionException(Exception):
    pass


class TrackDataStorageRandAlgorithm(object):
    def getReadFromDiskTrackColumns(self):
        raise AbstractClassError()

    def getInitTrackColumns(self):
        raise AbstractClassError()

    def needsMask(self):
        raise AbstractClassError()

    def getTrackBinIndexer(self):
        raise AbstractClassError()

    def randomize(self, trackDataStorage, trackBinIndexer):
        raise AbstractClassError()


class ShuffleElementsBetweenTracksAndBinsRandAlgorithm(TrackDataStorageRandAlgorithm):
    MISSING_EL = -1
    NEW_TRACK_BIN_INDEX_KEY = RandomizedTrackDataStorage.NEW_TRACK_BIN_INDEX_KEY

    def __init__(self, allowOverlaps, excludedSegmentsStorage=None, maxSampleCount=25, overlapDetectorCls=IntervalTreeOverlapDetector):
        self._allowOverlaps = allowOverlaps
        self._excludedSegmentsStorage = excludedSegmentsStorage
        # self._trackIdToExcludedRegions = defaultdict(dict)
        self._maxSampleCount = maxSampleCount
        # self._excludedRegions = None
        self._overlapDetectorCls = overlapDetectorCls
        self._trackBinIndexer = None
        self._newTrackBinIndexToOverlapDetectorDict = {}

    def getReadFromDiskTrackColumns(self):
        return ['lengths']

    def getGeneratedTrackColumns(self):
        return ['starts']

    def needsMask(self):
        return True

    def initTrackBinIndexer(self, origTs, binSource):
        self._trackBinIndexer = SimpleTrackBinIndexer(origTs, binSource)

    def getTrackBinIndexer(self):
        assert self._trackBinIndexer is not None
        return self._trackBinIndexer

    def randomize(self, trackDataStorage):
        trackProbabilities = self._getTrackProbabilites(len(self._trackBinIndexer.allTracks()))
        binProbabilities = self._getBinProbabilites(self._trackBinIndexer.allBins())

        trackDataStorage.shuffle()

        for trackBinIndex in self._trackBinIndexer.allTrackBinIndexes():
            trackDataStorageView = trackDataStorage.getView(trackBinIndex)

            lengthsArray = trackDataStorageView.getArray('lengths')
            startsArray, newTrackBinIndexArray = \
                self._generateRandomArrays(lengthsArray, trackProbabilities, binProbabilities)

            trackDataStorageView.updateArray('starts', startsArray)
            trackDataStorageView.updateArray(self.NEW_TRACK_BIN_INDEX_KEY, newTrackBinIndexArray)

        maskArray = generateMaskArray(trackDataStorage.getArray('starts'), self.MISSING_EL)
        trackDataStorage.setMaskColumn(maskArray)

        trackDataStorage.sort(['starts', self.NEW_TRACK_BIN_INDEX_KEY])

        from gold.application.LogSetup import logMessage, logging
        logMessage("Discarded %i elements out of %i possible." % (trackDataStorage.mask.sum(), len(trackDataStorage)),
                   level=logging.WARN)

    def _getTrackProbabilites(self, numTracks):
        return [1.0 / numTracks] * numTracks

    def _getBinProbabilites(self, allBins):
        binsLen = sum([(x.end - x.start) for x in allBins])
        return [float(x.end - x.start) / binsLen for x in allBins]

    def _generateRandomArrays(self, lengthsArray, trackProbabilities, binProbabilities):
        startsArray = np.zeros(len(lengthsArray), dtype='int32')
        newTrackBinIndexArray = np.zeros(len(lengthsArray), dtype='int32')

        # Update probabilities of track and bin after each element is added, in order to, as closely as possible, have the same probabilty of filling each base pair. Discuss
        #
        # Another algorithm might be to first bucket the segments into bins according to the continuously updated probabilities
        # (free bps in region/free bps in all bins)
        # Need to handle the situation if a bin is too small to keep the segment, the correct thing is perhaps to remove those bins
        # from the probability calculation in that iteration.
        # Then you shuffle the segments in each bin and distribute the free bps as gaps according to some distribution
        # When using exclusion track, one could simply handle redefine the bins accordingly. In this way IntervalTrees should not
        # be needed. Also, the probability of a bps being filled should be even (except perhaps start/end of bins).

        for i, segLen in enumerate(lengthsArray):
            for sampleCount in xrange(self._maxSampleCount):
                newTrackBinPair = TrackBinPair(self._trackBinIndexer.selectRandomTrack(trackProbabilities),
                                            self._trackBinIndexer.selectRandomBin(binProbabilities))
                newTrackBinIndex = self._trackBinIndexer.getTrackBinIndexForTrackBinPair(newTrackBinPair)
                overlapDetector = self._getOverlapDetectorForTrackBinIndex(newTrackBinIndex)

                try:
                    newStartPos = self._selectRandomValidStartPosition(overlapDetector, segLen, newTrackBinPair.bin)
                    if not self._allowOverlaps:
                        overlapDetector.addSegment(newStartPos, newStartPos + segLen)
                    break
                except InvalidPositionException:
                    newStartPos = self.MISSING_EL

            startsArray[i] = newStartPos
            newTrackBinIndexArray[i] = newTrackBinIndex if newStartPos != self.MISSING_EL else self.MISSING_EL

        return startsArray, newTrackBinIndexArray

    def _getOverlapDetectorForTrackBinIndex(self, newTrackBinIndex):
        if newTrackBinIndex not in self._newTrackBinIndexToOverlapDetectorDict:
            self._newTrackBinIndexToOverlapDetectorDict[newTrackBinIndex] = self._overlapDetectorCls(
                self._excludedSegmentsStorage.getExcludedSegmentsIter(newTrackBinIndex.bin))

        overlapDetector = self._newTrackBinIndexToOverlapDetectorDict[newTrackBinIndex]
        return overlapDetector

    def _selectRandomValidStartPosition(self, overlapDetector, segLen, targetGenomeRegion):
        '''
        Randomly select a start position.
        For it to be valid, it must not overlap any of the excluded regions.
        If no valid position is found after maxSampleCount attempts, None is returned
        :param segLen: The length of the track element
        :param targetGenomeRegion: The genome region to sample
        :param excludedRegions: IntervalTree object containing all intervals that must be avoided
        :param maxSampleCount: Nr of times the sampling is done if no valid position is selected.
        :return:
        '''

        if targetGenomeRegion.end - targetGenomeRegion.start < segLen:
            raise InvalidPositionException('Segment is larger than bin')

        from random import randint
        candidateStartPos = randint(targetGenomeRegion.start, targetGenomeRegion.end - segLen)
        if overlapDetector.overlaps(candidateStartPos, candidateStartPos + segLen):
            raise InvalidPositionException('New segment overlaps with existing segment')

        return candidateStartPos


def generateMaskArray(numpyArray, maskVal):
    return numpyArray == maskVal