import numpy as np

from gold.track.trackstructure.random.OverlapDetector import IntervalTreeOverlapDetector
from gold.track.trackstructure.random.TrackBinIndexer import TrackBinPair, SimpleTrackBinIndexer
from gold.util.CustomExceptions import AbstractClassError


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

    def __init__(self, excludedSegmentsStorage=None, maxSampleCount=25, overlapDetectorCls=IntervalTreeOverlapDetector):
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
        binProbabilities = self._getBinProbabilites(self._trackBinIndexer.allBins())
        trackDataStorage.shuffle()

        for trackBinIndex in self._trackBinIndexer.allTrackBinIndexes():
            trackDataStorageView = trackDataStorage.getView(trackBinIndex)

            lengthsArray = trackDataStorageView.getArray('lengths')
            startsArray, newTrackBinIndexArray = self._generateRandomArrays(lengthsArray, trackBinIndex, binProbabilities)
            trackDataStorageView.addArray('starts', startsArray)

            maskArray = generateMaskArray(startsArray, self.MISSING_EL)
            trackDataStorageView.setMaskColumn(maskArray)

            trackDataStorageView.sort('starts')

    def _getBinProbabilites(self, allBins):
        binsLen = sum([(x.end - x.start) for x in allBins])
        return [float(x.end - x.start) / binsLen for x in allBins]

    def _generateRandomArrays(self, lengthsArray, trackBinIndex, binProbabilities):
        trackBinPair = self._trackBinIndexer.getTrackBinPairForTrackBinIndex(trackBinIndex)
        startsArray = np.zeros(len(lengthsArray), dtype='int32')
        if trackBinIndex not in self._newTrackBinIndexToOverlapDetectorDict:
            overlapDetector = self._overlapDetectorCls(
                self._excludedSegmentsStorage.getExcludedSegmentsIter(trackBinPair.bin))
            self._newTrackBinIndexToOverlapDetectorDict[trackBinIndex] = overlapDetector

        # TODO: continue here!!!!!
        for i, segLen in enumerate(lengthsArray):
            newTrackBinPair = TrackBinPair(self._selectRandomTrackId(allTrackIds),
                                             self._selectRandomBin(allBins, binProbabilities))
            newTrackBinIndex = trackDataStorage.getTrackBinIndexForTrackBinPair(newTrackBinPair)
            trackDataStorageView.getArray('newTrackBinIndex')[i] = newTrackBinIndex

            # Find random track and bin. Find overlapdetector for new tracktrackBinIndex, or create it if is not there (or use defaultdict)
            # Update probabilities of track and bin after each element is added, in order to, as closely as possible, have the same probabilty of filling each base pair. Discuss
            #
            # Another algorithm might be to first bucket the segments into bins according to the continuously updated probabilities
            # (free bps in region/free bps in all bins)
            # Need to handle the situation if a bin is too small to keep the segment, the correct thing is perhaps to remove those bins
            # from the probability calculation in that iteration.
            # Then you shuffle the segments in each bin and distribute the free bps as gaps according to some distribution
            # When using exclusion track, one could simply handle redefine the bins accordingly. In this way IntervalTrees should not
            # be needed. Also, the probability of a bps being filled should be even (except perhaps start/end of bins).
            startsArray[i] = self._selectRandomValidStartPosition(overlapDetector, segLen, targetGenomeRegion)
        return startsArray

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

        from random import randint

        if targetGenomeRegion.end - targetGenomeRegion.start < segLen:
            return self.MISSING_EL

        for count in xrange(self._maxSampleCount):
            candidateStartPos = randint(targetGenomeRegion.start, targetGenomeRegion.end - segLen)
            if not overlapDetector.overlaps(candidateStartPos, candidateStartPos + segLen):
                return candidateStartPos

        return self.MISSING_EL


def generateMaskArray(numpyArray, maskVal):
    return numpyArray == maskVal