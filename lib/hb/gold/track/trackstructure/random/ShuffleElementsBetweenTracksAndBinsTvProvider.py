from collections import defaultdict

from gold.statistic.RawDataStat import RawDataStat
from gold.track.Track import Track
from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.track.TrackStructure import SingleTrackTS
from gold.track.TrackView import AutonomousTrackElement, TrackView
from gold.track.TsBasedRandomTrackViewProvider import BetweenTracksRandomTvProvider, TsBasedRandomTrackViewProvider
from gold.track.trackstructure.random.RandomizeBetweenTracksAndBinsPool import RandomizeBetweenTracksAndBinsPool
from quick.application.SignatureDevianceLogging import takes
from test.gold.track.common.SampleTrack import SampleTrack


class ShuffleElementsBetweenTracksAndBinsTvProvider(BetweenTracksRandomTvProvider):
    _NEEDS_ORIG_TRACK_SOURCE = True
    _NEEDS_BIN_SOURCE = True
    _SUPPORTS_LOCAL_ANALYSIS = False

    def __init__(self, randAlgorithm):
        self._randAlgorithm = randAlgorithm
        self._curRandIndex = -1
        self._pool = None
        super(ShuffleElementsBetweenTracksAndBinsTvProvider, self).__init__()

    def supportsTrackFormat(self, origTrackFormat):
        return self._randAlgorithm.supportsTrackFormat(origTrackFormat)

    def supportsOverlapMode(self, allowOverlaps):
        return self._randAlgorithm.supportsOverlapMode(allowOverlaps)

    @takes('ShuffleElementsBetweenTracksAndBinsTvProvider', 'GenomeRegion', (Track, SampleTrack), int)
    def _getTrackView(self, region, origTrack, randIndex):
        self._assertConsecutiveRandIndex(randIndex)

        if self._isFirstIteration():
            self._pool = RandomizeBetweenTracksAndBinsPool(self._randAlgorithm, self._origTs,
                                                           self._binSource)

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


# # Newer
# class ShuffleElementsBetweenTracksAndBinsPool(object):
#     UNKNOWN_GENOME = 'unknown'  # used for unique ID generation
#
#     def __init__(self, origTs, binSource, allowOverlaps=False, excludedTs=None, maxSampleCount=25):
#         self._trackElementLists = defaultdict(lambda: defaultdict(list))
#         self._origTs = origTs
#         self._binSource = binSource
#         self._allowOverlaps = allowOverlaps
#         self._excludedTs = excludedTs
#         self._trackIdToExcludedRegions = defaultdict(dict)
#         self._binList = list(binSource)
#         self._trackIdList = [sts.track.getUniqueKey(
#             self._binSource.genome if self._binSource.genome else self.UNKNOWN_GENOME) \
#             for sts in self._origTs.getLeafNodes()]
#         self._isSorted = False
#         self._maxSampleCount = maxSampleCount
#         self._binProbabilities = self._getBinProbabilites()
#         self._populatePool()
#
#     @staticmethod
#     def _getAllTrackElementsFromTS(ts, binSource):
#         allTrackElements = []
#         for region in binSource:
#             for sts in ts.getLeafNodes():
#                 tv = sts.track.getTrackView(region)
#                 allTrackElements += [AutonomousTrackElement(trackEl=te) for te in tv]  # list(tv)
#
#         return allTrackElements
#
#     def _addTrackElement(self, trackElement, newStartPos, newEndPos, binId, trackId):
#         '''
#         Add an autonomous track element with a new start and end position while keeping all the rest of the values,
#         to the appropriate list
#         :param trackElement:
#         :param newStartPos:
#         :param newEndPos:
#         :param binId:
#         :param trackId:
#         :return:
#         '''
#         autonomousTrackElement = AutonomousTrackElement(trackEl=trackElement)
#         autonomousTrackElement._start = newStartPos
#         autonomousTrackElement._end = newEndPos
#         self._trackElementLists[trackId][binId].append(autonomousTrackElement)
#
#     @staticmethod
#     def _selectRandomValidStartPosition(segLen, targetGenomeRegion, excludedRegions):
#         '''
#         Randomly select a start position.
#         For it to be valid, it must not overlap any of the excluded regions.
#         :param segLen: The length of the track element
#         :param targetGenomeRegion: The genome region to sample
#         :param excludedRegions: IntervalTree object containing all intervals that must be avoided
#         :return: valid start position for target genome region or None
#         '''
#
#         if targetGenomeRegion.end - targetGenomeRegion.start < segLen:
#             return None
#         from random import randint
#         candidateStartPos = randint(targetGenomeRegion.start, targetGenomeRegion.end - segLen)
#         if excludedRegions.find(candidateStartPos, candidateStartPos + segLen):
#             return None
#         else:
#             return candidateStartPos
#
#     def _generateExcludedRegions(self, excludedTs, binSource):
#
#         '''
#         excludedTs: the single track TS that holds the exclusion track
#         binSource: a GenomeRegion iterator
#         The exclusion track is saved in a dict of IntervalTree objects, one for each region.'''
#
#         excludedRegions = {}  # region -> IntervalTree
#         for region in binSource:
#             excludedRegions[region] = self._generateExcludedRegion(excludedTs, region)
#         return excludedRegions
#
#     def _generateExcludedRegion(self, excludedTs, region):
#         excludedRegion = IntervalTree()
#         if excludedTs is None:
#             return excludedRegion
#         # for now we only support a single exclusion track
#         assert isinstance(excludedTs, SingleTrackTS), "Only Single track TS supported for exclusion track."
#         excludedTV = RawDataStat(region, excludedTs.track, NeutralTrackFormatReq()).getResult()
#         for x in zip(excludedTV.startsAsNumpyArray(), excludedTV.endsAsNumpyArray()):
#             excludedRegion.insert(*x)
#         return excludedRegion
#
#     def _populatePool(self):
#
#         discardedElements = list()
#         allTrackElements = self._getAllTrackElementsFromTS(self._origTs, self._binSource)
#         from random import shuffle
#         shuffle(allTrackElements)
#         for trackElement in allTrackElements:
#             cnt = 0
#             startPos = None
#             while startPos is None and cnt < self._maxSampleCount:
#                 trackId = self._selectRandomTrackId()
#                 binId = self._selectRandomBin()
#                 segLen = len(trackElement)
#                 if binId not in self._trackIdToExcludedRegions[trackId]:
#                     self._trackIdToExcludedRegions[trackId][binId] = self._generateExcludedRegion(self._excludedTs,
#                                                                                                   binId)
#                 excludedRegions = self._trackIdToExcludedRegions[trackId][binId]
#                 startPos = self._selectRandomValidStartPosition(segLen, binId, excludedRegions)
#                 cnt += 1
#             if startPos:
#                 self._addElementAndUpdateExcludedRegions(startPos, segLen, trackElement, trackId, binId,
#                                                          excludedRegions)
#             else:
#                 discardedElements.append(trackElement)
#
#         logMessage("Discarded %i elements out of %i possible." % (len(discardedElements), len(allTrackElements)),
#                    level=logging.WARN)
#
#         # print "Discarded %i elements out of %i possible." % (len(discardedElements), len(allTrackElements))
#
#     def _addElementAndUpdateExcludedRegions(self, startPos, segLen, trackElement, trackId, binId, excludedRegions):
#         endPos = startPos + segLen  # -1
#         if not self._allowOverlaps:
#             self._addElementHandleBxPythonZeroDivisionException(startPos, endPos, excludedRegions, 10)
#             assert len(excludedRegions.find(startPos, endPos)) == 1, "Overlapping segments!"  # sanity check
#         self._addTrackElement(trackElement, startPos, endPos, binId, trackId)
#
#     def _addElementHandleBxPythonZeroDivisionException(self, startPos, endPos, excludedRegions, nrTries=10):
#         """DivisionByZero error is caused by a bug in the bx-python library.
#         It happens rarely, so we just execute the add command again up to nrTries times
#         when it does. If it pops up more than 10 times, we assume something else is wrong and raise."""
#         cnt = 0
#         while True:
#             cnt += 1
#             try:
#                 excludedRegions.add(startPos, endPos)
#             except Exception as e:
#                 logMessage("Try nr %i. %s" % (cnt, str(e)), level=logging.WARN)
#                 if cnt > nrTries:
#                     raise e
#                 continue
#             else:
#                 break
#
#     def _selectRandomTrackId(self):
#         from random import randint
#         return self._trackIdList[randint(0, len(self._trackIdList) - 1)]
#
#     def _selectRandomBin(self):
#         import numpy as np
#         selectedBinId = np.random.choice(range(0, len(self._binList)), p=self._binProbabilities)
#         return self._binList[selectedBinId]
#
#     def getTrackView(self, region, origTrack):
#
#         if not self._isSorted:
#             self._sortTrackElementLists()
#         trackId = origTrack.getUniqueKey(self._binSource.genome if self._binSource.genome else self.UNKNOWN_GENOME)
#         trackElements = self._trackElementLists[trackId][region]
#         import numpy as np
#         origTV = origTrack.getTrackView(, region,
#         return TrackView(genomeAnchor=origTV.genomeAnchor,
#                          startList=np.array([x.start() for x in trackElements]),
#                          endList=np.array([x.end() for x in trackElements]),
#                          valList=np.array([x.val() for x in trackElements]),
#                          strandList=np.array([x.strand() for x in trackElements]),
#                          idList=np.array([x.id() for x in trackElements]),
#                          edgesList=None,
#                          weightsList=None,
#                          borderHandling=origTV.borderHandling,
#                          allowOverlaps=self._allowOverlaps)
#
#     def _sortTrackElementLists(self):
#         import operator
#         for trackId in self._trackElementLists:
#             for binId in self._trackElementLists[trackId]:
#                 self._trackElementLists[trackId][binId].sort(key=operator.attrgetter('start', 'end'))
#
#         self._isSorted = True
#
#     def _getBinProbabilites(self):
#         binsLen = sum([(x.end - x.start) for x in self._binList])
#         return [float(x.end - x.start) / binsLen for x in self._binList]
