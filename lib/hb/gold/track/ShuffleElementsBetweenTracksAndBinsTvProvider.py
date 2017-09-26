from collections import OrderedDict, defaultdict

from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.track.TrackStructure import SingleTrackTS
from gold.track.TrackView import AutonomousTrackElement, TrackView
from gold.track.TsBasedRandomTrackViewProvider import BetweenTrackRandomTvProvider, TsBasedRandomTrackViewProvider

from bx.intervals.intersection import IntervalTree

class ShuffleElementsBetweenTracksAndBinsTvProvider(BetweenTrackRandomTvProvider):

    def __init__(self, origTs, excludedTs, binSource, allowOverlaps):
        TsBasedRandomTrackViewProvider.__init__(self, origTs, allowOverlaps)
        self._poolDict = OrderedDict() #rand_index -> trackId -> binId -> list of TrackElements
        self._excludedTs = excludedTs
        self._binSource = binSource


    def getTrackView(self, region, origTrack, randIndex):
        if randIndex not in self._poolDict:
            #remove all previous samples, we assume they are not needed
            self._poolDict = OrderedDict()
            self._poolDict[randIndex] = ShuffleElementsBetweenTracksAndBinsPool(self._origTs, self._binSource, self._allowOverlaps, self._excludedTs)
        return self._poolDict[randIndex].getTrackView(region, origTrack)


class ShuffleElementsBetweenTracksAndBinsPool(object):

    UNKNOWN_GENOME = 'unknown' #used for unique ID generation

    def __init__(self, origTs, binSource, allowOverlaps=False, excludedTs=None):
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
        self._populatePool()


    @staticmethod
    def _getAllTrackElementsFromTS(ts, binSource):
        allTrackElements = []
        for region in binSource:
            for sts in ts.getLeafNodes():
                tv = sts.track.getTrackView(region)
                allTrackElements += [AutonomousTrackElement(trackEl=te) for te in tv]#list(tv)

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
    def _selectRandomValidStartPosition(segLen, targetGenomeRegion, excludedRegions, maxSampleCount=25):
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
            return None
        from random import randint
        candidateStartPos = randint(targetGenomeRegion.start, targetGenomeRegion.end-segLen)
        cnt = 0
        while excludedRegions.find(candidateStartPos, candidateStartPos + segLen) and cnt < maxSampleCount:
            candidateStartPos = randint(targetGenomeRegion.start, targetGenomeRegion.end-segLen)
            cnt += 1
        if cnt==maxSampleCount and excludedRegions.find(candidateStartPos, candidateStartPos + segLen):
            return None
        else:
            return candidateStartPos

    def _generateExcludedRegions(self, excludedTs, binSource):

        '''
        excludedTs: the single track TS that holds the exclusion track
        binSource: a GenomeRegion iterator
        The exclusion track is saved in a dict of IntervalTree objects, one for each region.'''

        excludedRegions = {} #region -> IntervalTree
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

        #print "Discarded %i elements out of %i possible." % (len(discardedElements), len(allTrackElements))

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

