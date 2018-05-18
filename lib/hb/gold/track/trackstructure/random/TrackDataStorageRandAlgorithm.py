from abc import ABCMeta, abstractmethod
from copy import deepcopy

import numpy as np
import random

from gold.track.RandomizedTrack import TrackRandomizer
from gold.track.trackstructure.random.Constants import LENGTH_KEY, START_KEY, NEW_TRACK_BIN_INDEX_KEY
from gold.track.trackstructure.random.ExcludedSegmentsStorage import ExcludedSegmentsStorage
from gold.track.trackstructure.random.OverlapDetector import IntervalTreeOverlapDetector
from gold.track.trackstructure.random.TrackBinIndexer import TrackBinPair, SimpleTrackBinIndexer


class InvalidPositionException(Exception):
    pass


class TrackDataStorageRandAlgorithm(TrackRandomizer):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getReadFromDiskTrackColumns(self):
        pass

    @abstractmethod
    def getInitTrackColumns(self):
        pass

    @abstractmethod
    def needsMask(self):
        pass

    @abstractmethod
    def getTrackBinIndexer(self):
        pass

    @abstractmethod
    def randomize(self, trackDataStorage, trackBinIndexer):
        pass


class CollisionDetectionTracksAndBinsRandAlgorithm(TrackDataStorageRandAlgorithm):
    MISSING_EL = -1

    def __init__(self, excludedTS, binSource, maxSampleCount=25,
                 overlapDetectorCls=IntervalTreeOverlapDetector):
        self._maxSampleCount = maxSampleCount
        self._trackBinIndexer = None
        self._excludedSegmentsStorage = \
            ExcludedSegmentsStorage(excludedTS, binSource) if excludedTS else None
        self._overlapDetectorCls = overlapDetectorCls

    def _getOverlapDetectorForTrackBinPair(self, newTrackBinPair):
        if self._excludedSegmentsStorage:
            exclSegs = self._excludedSegmentsStorage.getExcludedSegmentsIter(newTrackBinPair.bin)
        else:
            exclSegs = None
        return self._overlapDetectorCls(exclSegs)

    @classmethod
    def supportsTrackFormat(cls, origTrackFormat):
        # TODO: Fix support for all track formats
        return origTrackFormat.isInterval()

    @classmethod
    def supportsOverlapMode(cls, allowOverlaps):
        return True

    def getReadFromDiskTrackColumns(self):
        return [LENGTH_KEY]

    def getInitTrackColumns(self):
        return [START_KEY]

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

        trackDataStorage.setMask(None)
        trackDataStorage.shuffle()

        # for trackBinIndex in self._trackBinIndexer.allTrackBinIndexes():
        #     trackDataStorageView = trackDataStorage.getView(trackBinIndex)

        lengthsArray = trackDataStorage.getArray(LENGTH_KEY)
        allowOverlaps = trackDataStorage.allowOverlaps
        newStartsArray, newTrackBinIndexArray = \
            self._generateRandomArrays(lengthsArray, trackProbabilities,
                                       binProbabilities, allowOverlaps)

        trackDataStorage.updateArray(START_KEY, newStartsArray)
        trackDataStorage.updateArray(NEW_TRACK_BIN_INDEX_KEY, newTrackBinIndexArray)

        maskArray = generateMaskArray(trackDataStorage.getArray(NEW_TRACK_BIN_INDEX_KEY), self.MISSING_EL)
        trackDataStorage.setMask(maskArray)

        # trackDataStorage.sort([RandomizedTrackDataStorage.START_KEY, self.NEW_TRACK_BIN_INDEX_KEY])

        numDiscarded = trackDataStorage.getMask().sum()

        if numDiscarded:
            from gold.application.LogSetup import logMessage, logging
            logMessage("Discarded %i elements out of %i possible." %
                       (trackDataStorage.getMask().sum(), len(trackDataStorage)),
                       level=logging.WARN)

    def _getTrackProbabilites(self, numTracks):
        return [1.0 / numTracks] * numTracks

    def _getBinProbabilites(self, allBins):
        binsLen = sum([(x.end - x.start) for x in allBins])
        return [float(x.end - x.start) / binsLen for x in allBins]

    def _generateRandomArrays(self, lengthsArray, trackProbabilities,
                              binProbabilities, allowOverlaps):
        newStartsArray = np.zeros(len(lengthsArray), dtype='int32')
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

        trackBinPairToOverlapDetectorDict = {}

        for i, segLen in enumerate(lengthsArray):
            for sampleCount in xrange(self._maxSampleCount):
                newTrackBinPair = TrackBinPair(self._trackBinIndexer.selectRandomTrack(trackProbabilities),
                                               self._trackBinIndexer.selectRandomBin(binProbabilities))
                if newTrackBinPair not in trackBinPairToOverlapDetectorDict:
                    overlapDetector = self._getOverlapDetectorForTrackBinPair(newTrackBinPair)
                    trackBinPairToOverlapDetectorDict[newTrackBinPair] = overlapDetector
                else:
                    overlapDetector = trackBinPairToOverlapDetectorDict[newTrackBinPair]

                try:
                    newStartPos = self._selectRandomValidStartPosition(overlapDetector, segLen,
                                                                       newTrackBinPair.bin)

                    if not allowOverlaps:
                        overlapDetector.addSegment(newStartPos, newStartPos + segLen)
                    newStartsArray[i] = newStartPos

                    newTrackBinIndex = \
                        self._trackBinIndexer.getTrackBinIndexForTrackBinPair(newTrackBinPair)
                    newTrackBinIndexArray[i] = newTrackBinIndex

                    break
                except InvalidPositionException:
                    pass
            else:
                newStartsArray[i] = self.MISSING_EL
                newTrackBinIndexArray[i] = self.MISSING_EL

        return newStartsArray, newTrackBinIndexArray

    def _selectRandomValidStartPosition(self, overlapDetector, segLen, targetGenomeRegion):
        '''
        Randomly select a start position.
        For it to be valid, it must not overlap any of the excluded regions.
        If no valid position is found after maxSampleCount attempts, None is returned
        :param overlapDetector OverlapDetector object, containing intervals that must be avoided
        :param segLen: The length of the track element
        :param targetGenomeRegion: The target genome region in which to create the sample
        :return: New start position
        '''

        if targetGenomeRegion.end - targetGenomeRegion.start < segLen:
            raise InvalidPositionException('Segment is larger than bin')

        candidateStartPos = random.randint(targetGenomeRegion.start, targetGenomeRegion.end - segLen)
        if overlapDetector.overlaps(candidateStartPos, candidateStartPos + segLen):
            raise InvalidPositionException('New segment overlaps with existing segment')

        return candidateStartPos


def generateMaskArray(numpyArray, maskVal):
    return numpyArray == maskVal
