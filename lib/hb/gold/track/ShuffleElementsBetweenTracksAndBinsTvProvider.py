from collections import OrderedDict, defaultdict, namedtuple

import numpy as np

from gold.statistic.RawDataStat import RawDataStat
from gold.track.NumpyDataFrame import NumpyDataFrame
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
        self._newTrackBinIndexToOverlapDetectorDict = {}

    def getReadFromDiskTrackColumns(self):
        return ['lengths']

    def getGeneratedTrackColumns(self):
        return ['starts']

    def needsMask(self):
        return True

    def randomize(self, trackDataStorage):
        trackDataStorage.shuffle()
        for trackBinIndex in trackDataStorage.allTrackBinIndexes():
            trackBinTuple = trackDataStorage.getTrackAndBinForTrackBinIndex(trackBinIndex)
            trackDataStorageView = trackDataStorage.getView(trackBinTuple.track, trackBinTuple.bin)

            startsArray = self._generateRandomStartsArray(trackDataStorageView.getTrackColumnData('lengths'),
                                                          region)
            trackDataStorageView.setTrackColumnData('starts', startsArray)

            maskArray = generateMaskArray(startsArray, self.MISSING_EL)
            trackDataStorageView.setMaskColumn(maskArray)

            trackDataStorageView.sort('starts')

        return trackDataStorage

    def _generateStartsArray(self, lengthsArray, targetGenomeRegion):
        startsArray = np.zeros(len(lengthsArray), dtype='int32')
        overlapDetector = self._overlapDetectorCls(
            self._excludedSegmentsStorage.getExcludedSegmentsIter(targetGenomeRegion))

        for i, segLen in enumerate(lengthsArray):
            # Find random track and bin. Find overlapdetector for new tracktrackBinIndex, or create it if is not there (or use defaultdict)
            # Update probabilities of track and bin after each element is added, in order to, as closely as possible, have the same probabilty of filling each base pair. Discuss
            #
            # Another algorithm might be to first bucket the segments into bins according to the contuniously updated probabilities (free bps in region/free bps in track)
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


TrackBinTuple = namedtuple('TrackBinTuple', ('track', 'bin'))


class RandomizedTrackDataStorage(object):
    # For the joint consecutive index defined from the double for loop over all tracks and bins
    ORIG_TRACK_BIN_INDEX_KEY = 'origTrackBinIndex'
    LENGTH_KEY = 'lengths'

    def __init__(self, tracks, bins, generatedTrackColumns, readFromDiskTrackColumns, needsMask):
        self._tracks = tracks
        self._bins = bins
        self._generatedTrackColumns = generatedTrackColumns
        self._readFromDiskTrackColumns = readFromDiskTrackColumns
        self._needsMask = needsMask

        self.dataFrame = NumpyDataFrame()
        self._origTrackBinIndexToTrackAndBinDict = {}

        assert len(self._tracks) > 0
        assert len(self._bins) > 0

        listOfColToArrayDicts = []

        origTrackBinIndex = 0
        for track in self._tracks:
            for curBin in self._bins():
                trackView = track.getTrackView(curBin)
                colToArrayDict = {}
                for col in readFromDiskTrackColumns:
                    if col == self.LENGTH_KEY:
                        colToArrayDict[col] = trackView.endsAsNumpyArray() - trackView.startsAsNumpyArray()
                    else:
                        colToArrayDict[col] = trackView.getNumpyArrayFromPrefix(col)
                for col in generatedTrackColumns:
                    if col == self.LENGTH_KEY:
                        numpyArray = trackView.startsAsNumpyArray()
                    else:
                        numpyArray = trackView.getNumpyArrayFromPrefix(col)
                    colToArrayDict[col] = np.zeros(len(numpyArray), dtype=numpyArray.dtype)
                listOfColToArrayDicts.append(colToArrayDict)

                self._origTrackBinIndexToTrackAndBinDict[origTrackBinIndex] = TrackBinTuple(track=track, bin=curBin)
                origTrackBinIndex += 1

        for col in readFromDiskTrackColumns + generatedTrackColumns:
            allColArrays = [colToArrayDict[col] for colToArrayDict in listOfColToArrayDicts]
            fullColArray = np.concatenate(allColArrays)

            if not self.dataFrame.hasArray(self.ORIG_TRACK_BIN_INDEX_KEY):
                origTrackBinIndexArrays = [np.ones(len(colArray), dtype='int32') for colArray in allColArrays]
                fullOrigTrackBinIndexArray = np.concatenate([array * i for i, array in enumerate(origTrackBinIndexArrays)])
                self.dataFrame.addArray(self.ORIG_TRACK_BIN_INDEX_KEY, fullOrigTrackBinIndexArray)

            self.dataFrame.addArray(col, fullColArray)

        if needsMask:
            self.dataFrame.mask = np.zeros(len(self.dataFrame), dtype=bool)

    def getTrackAndBinForTrackBinIndex(self, trackBinIndex):
        return self._origTrackBinIndexToTrackAndBinDict[trackBinIndex]

    def shuffle(self):
        np.random.shuffle(self.dataFrame)

# Newer
class ShuffleElementsBetweenTracksAndBinsPool(object):
    UNKNOWN_GENOME = 'unknown'  # used for unique ID generation

    def __init__(self, origTs, binSource, allowOverlaps=False, excludedTs=None, maxSampleCount=25):
        self._trackElementLists = defaultdict(lambda: defaultdict(list))
        self._origTs = origTs
        self._binSource = binSource
        self._allowOverlaps = allowOverlaps
        self._excludedTs = excludedTs
        self._trackIdToExcludedRegions = defaultdict(dict)
        self._binList = list(binSource)
        self._trackIdList = [sts.track.getUniqueKey(
            self._binSource.genome if self._binSource.genome else self.UNKNOWN_GENOME) \
            for sts in self._origTs.getLeafNodes()]
        self._isSorted = False
        self._maxSampleCount = maxSampleCount
        self._binProbabilities = self._getBinProbabilites()
        self._populatePool()

    @staticmethod
    def _getAllTrackElementsFromTS(ts, binSource):
        allTrackElements = []
        for region in binSource:
            for sts in ts.getLeafNodes():
                tv = sts.track.getTrackView(region)
                allTrackElements += [AutonomousTrackElement(trackEl=te) for te in tv]  # list(tv)

        return allTrackElements

    def _addTrackElement(self, trackElement, newStartPos, newEndPos, binId, trackId):
        '''
        Add an autonomous track element with a new start and end position while keeping all the rest of the values,
        to the appropriate list
        :param trackElement:
        :param newStartPos:
        :param newEndPos:
        :param binId:
        :param trackId:
        :return:
        '''
        autonomousTrackElement = AutonomousTrackElement(trackEl=trackElement)
        autonomousTrackElement._start = newStartPos
        autonomousTrackElement._end = newEndPos
        self._trackElementLists[trackId][binId].append(autonomousTrackElement)

    @staticmethod
    def _selectRandomValidStartPosition(segLen, targetGenomeRegion, excludedRegions):
        '''
        Randomly select a start position.
        For it to be valid, it must not overlap any of the excluded regions.
        :param segLen: The length of the track element
        :param targetGenomeRegion: The genome region to sample
        :param excludedRegions: IntervalTree object containing all intervals that must be avoided
        :return: valid start position for target genome region or None
        '''

        if targetGenomeRegion.end - targetGenomeRegion.start < segLen:
            return None
        from random import randint
        candidateStartPos = randint(targetGenomeRegion.start, targetGenomeRegion.end - segLen)
        if excludedRegions.find(candidateStartPos, candidateStartPos + segLen):
            return None
        else:
            return candidateStartPos

    def _generateExcludedRegions(self, excludedTs, binSource):

        '''
        excludedTs: the single track TS that holds the exclusion track
        binSource: a GenomeRegion iterator
        The exclusion track is saved in a dict of IntervalTree objects, one for each region.'''

        excludedRegions = {}  # region -> IntervalTree
        for region in binSource:
            excludedRegions[region] = self._generateExcludedRegion(excludedTs, region)
        return excludedRegions

    def _generateExcludedRegion(self, excludedTs, region):
        excludedRegion = IntervalTree()
        if excludedTs is None:
            return excludedRegion
        # for now we only support a single exclusion track
        assert isinstance(excludedTs, SingleTrackTS), "Only Single track TS supported for exclusion track."
        excludedTV = RawDataStat(region, excludedTs.track, NeutralTrackFormatReq()).getResult()
        for x in zip(excludedTV.startsAsNumpyArray(), excludedTV.endsAsNumpyArray()):
            excludedRegion.insert(*x)
        return excludedRegion

    def _populatePool(self):

        discardedElements = list()
        allTrackElements = self._getAllTrackElementsFromTS(self._origTs, self._binSource)
        from random import shuffle
        shuffle(allTrackElements)
        for trackElement in allTrackElements:
            cnt = 0
            startPos = None
            while startPos is None and cnt < self._maxSampleCount:
                trackId = self._selectRandomTrackId()
                binId = self._selectRandomBin()
                segLen = len(trackElement)
                if binId not in self._trackIdToExcludedRegions[trackId]:
                    self._trackIdToExcludedRegions[trackId][binId] = self._generateExcludedRegion(self._excludedTs,
                                                                                                  binId)
                excludedRegions = self._trackIdToExcludedRegions[trackId][binId]
                startPos = self._selectRandomValidStartPosition(segLen, binId, excludedRegions)
                cnt += 1
            if startPos:
                self._addElementAndUpdateExcludedRegions(startPos, segLen, trackElement, trackId, binId,
                                                         excludedRegions)
            else:
                discardedElements.append(trackElement)

        logMessage("Discarded %i elements out of %i possible." % (len(discardedElements), len(allTrackElements)),
                   level=logging.WARN)

        # print "Discarded %i elements out of %i possible." % (len(discardedElements), len(allTrackElements))

    def _addElementAndUpdateExcludedRegions(self, startPos, segLen, trackElement, trackId, binId, excludedRegions):
        endPos = startPos + segLen  # -1
        if not self._allowOverlaps:
            self._addElementHandleBxPythonZeroDivisionException(startPos, endPos, excludedRegions, 10)
            assert len(excludedRegions.find(startPos, endPos)) == 1, "Overlapping segments!"  # sanity check
        self._addTrackElement(trackElement, startPos, endPos, binId, trackId)

    def _addElementHandleBxPythonZeroDivisionException(self, startPos, endPos, excludedRegions, nrTries=10):
        """DivisionByZero error is caused by a bug in the bx-python library.
        It happens rarely, so we just execute the add command again up to nrTries times
        when it does. If it pops up more than 10 times, we assume something else is wrong and raise."""
        cnt = 0
        while True:
            cnt += 1
            try:
                excludedRegions.add(startPos, endPos)
            except Exception as e:
                logMessage("Try nr %i. %s" % (cnt, str(e)), level=logging.WARN)
                if cnt > nrTries:
                    raise e
                continue
            else:
                break

    def _selectRandomTrackId(self):
        from random import randint
        return self._trackIdList[randint(0, len(self._trackIdList) - 1)]

    def _selectRandomBin(self):
        import numpy as np
        selectedBinId = np.random.choice(range(0, len(self._binList)), p=self._binProbabilities)
        return self._binList[selectedBinId]

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

    def _getBinProbabilites(self):
        binsLen = sum([(x.end - x.start) for x in self._binList])
        return [float(x.end - x.start) / binsLen for x in self._binList]
