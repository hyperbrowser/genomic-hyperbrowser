from collections import OrderedDict, defaultdict

import numpy

from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.track.TrackStructure import SingleTrackTS
from gold.track.TrackView import AutonomousTrackElement, TrackView
from gold.track.TsBasedRandomTrackViewProvider import BetweenTrackRandomTvProvider, TsBasedRandomTrackViewProvider

from gold.util.CustomExceptions import AbstractClassError


class ShuffleElementsBetweenTracksAndBinsTvProvider(BetweenTrackRandomTvProvider):
    def __init__(self, randAlgorithm, origTs, binSource, allowOverlaps):
        TsBasedRandomTrackViewProvider.__init__(self, origTs, allowOverlaps)
        # self._poolDict = OrderedDict() #rand_index -> trackId -> binId -> list of TrackElements
        self._randAlgorithm = randAlgorithm
        self._binSource = binSource
        self._curRandIndex = -1
        self._pool = None

    def getTrackView(self, region, origTrack, randIndex):
        self._assertConsecutiveRandIndex(randIndex)

        if self._isFirstIteration():
            self._pool = RandomizeBetweenTracksAndBinsPool(self._randAlgorithm, self._origTs, self._binSource,
                                                           self._allowOverlaps)

        if self._isNewIteration(randIndex):
            self._pool.randomize()
            self._updateCurIndex(randIndex)

        return self._pool.getTrackView(region, origTrack)

    def _assertConsecutiveRandIndex(self, randIndex):
        assert randIndex >= 0
        assert randIndex in [self._curRandIndex, self._curRandIndex + 1]

    def _isFirstIteration(self):
        return self._curRandIndex == -1

    def _isNewIteration(self, randIndex):
        return randIndex == self._curRandIndex + 1

    def _updateCurIndex(self, randIndex):
        self._curRandIndex = randIndex


class ExcludedSegmentsStorage(object):
    # TODO: Could be improved to use less memory
    def __init__(self, excludedTS, binSource):
        self._excludedTS = excludedTS
        self._binSource = binSource
        self._excludedSegmentsDict = None

    def _initExcludedRegions(self):
        # for now we only support a single exclusion track
        assert isinstance(self._excludedTs, SingleTrackTS), "Only Single track TS supported for exclusion track."
        self._excludedSegmentsDict = dict()

        for region in self._binSource:
            excludedTV = self._excludedTs.track.getTrackView(region)
            self._excludedSegmentsDict[region] = zip(excludedTV.startsAsNumpyArray(), excludedTV.endsAsNumpyArray())

    def getExcludedSegmentsIter(self, region):
        if not self._excludedSegmentsDict:
            self._initExcludedRegions()

        assert region in self._excludedSegmentsDict, "Not a valid region %s" % str(region)
        return self._excludedSegmentsDict[region]


def generateMaskArray(numpyArray, maskVal):
    return numpyArray == maskVal


class TrackDataStorageRandAlgorithm(object):
    def getReadFromDiskTrackColumns(self):
        raise AbstractClassError()

    def getInitTrackColumns(self):
        raise AbstractClassError()

    def needsMask(self):
        raise AbstractClassError()

    def randomize(self, trackDataStorage):
        raise AbstractClassError()


class ShuffleElementsBetweenTracksAndBinsRandAlgorithm(TrackDataStorageRandAlgorithm):
    MISSING_EL = -1

    def __init__(self, excludedSegmentsStorage=None, maxSampleCount=25, overlapDetectorCls=IntervalTreeOverlapDetector):
        self._excludedSegmentsStorage = excludedSegmentsStorage
        # self._trackIdToExcludedRegions = defaultdict(dict)
        self._maxSampleCount = maxSampleCount
        # self._excludedRegions = None
        self._overlapDetectorCls = overlapDetectorCls

    def getReadFromDiskTrackColumns(self):
        return ['lengths']

    def getInitTrackColumns(self):
        return ['starts']

    def needsMask(self):
        return True

    def randomize(self, trackDataStorage):
        trackDataStorage.shuffle()
        for track in trackDataStorage.getTracks():
            for region in trackDataStorage.getBins():
                trackDataStorageView = trackDataStorage.getView(track, region)

                startsArray = self._generateRandomStartsArray(trackDataStorageView.getTrackColumnData('lengths'),
                                                              region)
                trackDataStorageView.setTrackColumnData('starts', startsArray)

                maskArray = generateMaskArray(startsArray, self.MISSING_EL)
                trackDataStorageView.setMaskColumn(maskArray)

                trackDataStorageView.sort('starts')

        return trackDataStorage

    def _generateStartsArray(self, lengthsArray, targetGenomeRegion):
        startsArray = numpy.zeros(len(lengthsArray), dtype='int32')
        overlapDetector = self._overlapDetectorCls(
            self._excludedSegmentsStorage.getExcludedSegmentsIter(targetGenomeRegion))

        for i, segLen in enumerate(lengthsArray):
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


class OverlapDetector(object):
    def __init__(self, excludedSegments):
        raise AbstractClassError()

    def overlaps(self, start, end):
        raise AbstractClassError()

    def addSegment(self, start, end):
        raise AbstractClassError()


class IntervalTreeOverlapDetector(OverlapDetector):
    def __init__(self, excludedSegments):
        from bx.intervals.intersection import IntervalTree
        self._intervalTree = IntervalTree()
        for start, end in excludedSegments:
            self._intervalTree.add(start, end)

    def overlaps(self, start, end):
        return bool(self._intervalTree.find(start, end))

    def addSegment(self, start, end):
        self._intervalTree.add(start, end)


class RandomizedTrackDataStorage(object):
    def __init__(self, tracks, bins):
        import xarray

        self._tracks = tracks
        self._bins = bins

        xarray



class RandomizeBetweenTracksAndBinsPool(object):

    UNKNOWN_GENOME = 'unknown' #used for unique ID generation

    def __init__(self, randAlgorithm, origTs, binSource, allowOverlaps):
        # self._trackElementLists = defaultdict(lambda: defaultdict(list))
        self._randAlgorithm = randAlgorithm
        self._origTs = origTs
        self._binSource = binSource
        self._allowOverlaps = allowOverlaps
        # self._trackIdToExcludedRegions = defaultdict(dict)
        # self._binList = list(binSource)
        # self._trackIdList = [sts.track.getUniqueKey(
        #     self._binSource.genome if self._binSource.genome else self.UNKNOWN_GENOME) \
        #     for sts in self._origTs.getLeafNodes()]
        # self._isSorted = False
        # self._populatePool()
        self._trackDataStorage = self._initTrackDataStorage(origTs)

    def _initTrackDataStorage(self, origTs):
        return RandomizedTrackDataStorage()

    def randomize(self):
        self._trackDataStorage = self._randAlgorithm.randomize(self._trackDataStorage)

    def _populatePool(self):
        discardedElements = list()
        allTrackElements = self._getAllTrackElementsFromTS(self._origTs, self._binSource)
        from random import shuffle
        shuffle(allTrackElements)
        for trackElement in allTrackElements:
            trackId = self._selectRandomTrackId()
            binId = self._selectRandomBin()
            segLen = len(trackElement)
            if binId not in self._trackIdToExcludedRegions[trackId]:
                self._trackIdToExcludedRegions[trackId][binId] = self._generateExcludedRegion(self._excludedTs, binId)
            excludedRegions = self._trackIdToExcludedRegions[trackId][binId]
            startPos = self._selectRandomValidStartPosition(segLen, binId, excludedRegions)
            if startPos:
                self._addElementAndUpdateExcludedRegions(startPos, segLen, trackElement, trackId, binId,
                                                         excludedRegions)
            else:
                discardedElements.append(trackElement)

        print "Discarded %i elements" % len(discardedElements)

    def _addElementAndUpdateExcludedRegions(self, startPos, segLen, trackElement, trackId, binId, excludedRegions):
        endPos = startPos + segLen  # -1
        if not self._allowOverlaps:
            excludedRegions.add(startPos, endPos)
            assert len(excludedRegions.find(startPos, endPos)) == 1, "Overlapping segments!"  # sanity check
        self._addTrackElement(trackElement, startPos, endPos, binId, trackId)

    def _selectRandomTrackId(self):
        from random import randint
        return self._trackIdList[randint(0, len(self._trackIdList)-1)]


    def _selectRandomBin(self):
        from random import randint
        return self._binList[randint(0, len(self._binList)-1)]

    def getTrackView(self, region, origTrack):

        if not self._isSorted:
            self._sortTrackElementLists()
        trackId = origTrack.getUniqueKey(self._binSource.genome if self._binSource.genome else self.UNKNOWN_GENOME)
        trackElements = self._trackElementLists[trackId][region]
        import numpy as np
        origTV = origTrack.getTrackView(region)
        return TrackView(genomeAnchor=origTV.genomeAnchor,
                         startList=np.array([x.start() for x in trackElements]),
                         endList=np.array([x.end() for x in trackElements]),
                         valList=np.array([x.val() for x in trackElements]),
                         strandList=np.array([x.strand() for x in trackElements]),
                         idList=np.array([x.id() for x in trackElements]),
                         edgesList=None,
                         weightsList=None,
                         borderHandling=origTV.borderHandling,
                         allowOverlaps=self._allowOverlaps)

    def _sortTrackElementLists(self):
        import operator
        for trackId in self._trackElementLists:
            for binId in self._trackElementLists[trackId]:
                self._trackElementLists[trackId][binId].sort(key=operator.attrgetter('start', 'end'))

        self._isSorted = True
