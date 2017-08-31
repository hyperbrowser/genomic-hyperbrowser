from collections import OrderedDict, defaultdict

from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.track.TrackStructure import SingleTrackTS, TrackStructureV2
from gold.track.TrackView import AutonomousTrackElement, TrackView
from gold.track.TsBasedRandomTrackViewProvider import BetweenTrackRandomTvProvider, TsBasedRandomTrackViewProvider

from bx.intervals.intersection import IntervalTree

class ShuffleElementsBetweenTracksAndBinsTvProvider(BetweenTrackRandomTvProvider):

    UNKNOWN_GENOME = 'unknown' #used for unique ID generation

    def __init__(self, origTs, excludedTs, binSource, allowOverlaps):
        TsBasedRandomTrackViewProvider.__init__(self, origTs, allowOverlaps)
        self._poolDict = OrderedDict() #rand_index -> trackId -> binId -> list of TrackElements
        self._excludedTs = excludedTs
        self._binSource = binSource


    def getTrackView(self, region, origTrack, randIndex):
        if randIndex not in self._poolDict:
            self._poolDict[randIndex] = ShuffleElementsBetweenTracksAndBinsPool(self._origTs, self._binSource, self._allowOverlaps, self._excludedTs)

        return self._poolDict[randIndex].getTrackView(region, origTrack)


        # @takes('ShuffleElementsBetweenTracksAndBinsTvProvider', TrackStructureV2, BinSource)
        # def _getAllSegmentLengthsFromTS(self, ts, binSource):
        #
        #     '''Return of a list of all segment length in all tracks in the track structure ts'''
        #
        #     segLengths = []
        #     for sts in ts.getLeafNodes():
        #         res = SegmentLengthsStat(binSource, sts.track).getResult()['Result'] #TODO: with overlaps?
        #         segLengths += list(res)
        #
        #     return segLengths




class ShuffleElementsBetweenTracksAndBinsPool(object):

    def __init__(self, origTs, binSource, allowOverlaps=False, excludedTs=None):
        self._trackElementLists = defaultdict(lambda: defaultdict(list))
        self._origTs = origTs
        self._binSource = binSource
        self._allowOverlaps = allowOverlaps
        self._excludedTs = excludedTs
        self._trackIdToExcludedRegions = defaultdict(dict)
        self._binList = list(binSource)
        self._binDict = dict([(hash(x), x) for x in binSource])
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
        to the pool
        :param trackElement:
        :param newStartPos:
        :param newEndPos:
        :param binId:
        :param trackId:
        :return:
        '''
        # if trackId not in self._poolDict:
        #     self._trackElementLists[trackId] = {}
        # if binId not in self._poolDict[trackId]:
        #     self._trackElementLists[trackId][binId] = []

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
        from random import randint
        candidateStartPos = randint(targetGenomeRegion.start, targetGenomeRegion.end-segLen)
        candidateEndPos = candidateStartPos + segLen #-1?
        cnt = 0
        # while excludedRegions.overlaps(candidateStartPos, candidateEndPos) and cnt < maxSampleCount:
        while excludedRegions.find(candidateStartPos, candidateEndPos) and cnt < maxSampleCount:
            candidateStartPos = randint(targetGenomeRegion.start, targetGenomeRegion.end)
            candidateEndPos = candidateStartPos + segLen  # -1?
            cnt += 1
        # if excludedRegions.overlaps(candidateStartPos, candidateEndPos):
        if excludedRegions.find(candidateStartPos, candidateEndPos):
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
        excludedTrack = excludedTs.track
        excludedTV = RawDataStat(region, excludedTrack, NeutralTrackFormatReq()).getResult()
        for x in zip(excludedTV.startsAsNumpyArray(), excludedTV.endsAsNumpyArray()):
            excludedRegion.insert(*x)
            # excludedRegions[region] = IntervalTree.from_tuples(
            #     zip(excludedTV.startsAsNumpyArray(), excludedTV.endsAsNumpyArray()))

        return excludedRegion

    def _populatePool(self):

        # segmentLengthsList = self._getAllSegmentLengthsFromTS(self._origTs, self._binSource)
        allTrackElements = self._getAllTrackElementsFromTS(self._origTs, self._binSource)

        from random import shuffle
        # shuffle(segmentLengthsList)
        shuffle(allTrackElements)

        # binList = list(self._binSource)
        # binCount = len(binList)
        # segmentCount = len(segmentLengthsList)

        trackIdToRandomTrackArraysDict = dict()

        discardedElements = list()
        getStartEndFromInterval = lambda x: (x.start, x.end)
        for trackElement in allTrackElements:
            trackId = self._selectRandomTrackId()
            binId = self._selectRandomBin()

            segLen = len(trackElement)
            if binId not in self._trackIdToExcludedRegions[trackId]:
                # self._trackIdToExcludedRegions[trackId][binId] = self._excludedRegions[binId].copy()
                self._trackIdToExcludedRegions[trackId][binId] = self._generateExcludedRegion(self._excludedTs, binId)
            excludedRegions = self._trackIdToExcludedRegions[trackId][binId]
            # gRegion = self._binDict[binId]
            startPos = self._selectRandomValidStartPosition(segLen, binId, excludedRegions)
            if startPos:
                endPos = startPos + segLen #-1
                if not self._allowOverlaps:
                    excludedRegions.add(startPos, endPos)

                    # excludedRegions.addi(startPos, endPos)
                self._addTrackElement(trackElement, startPos, endPos, binId, trackId)
                assert len(excludedRegions.find(startPos, endPos)) == 1, "Overlapping segments!"
            else:
                discardedElements.append(trackElement)

        print "Discarded %i elements" % len(discardedElements)
    #     for trackId, val in self._trackIdToExcludedRegions.iteritems():
    #         print "Track: %s" % str(trackId)
    #         for binId, iTree in val.iteritems():
    #             print "Bin ID: %s" % str(binId)
    #             iTree.traverse(self.printIntervalNode)
    #
    # def printIntervalNode(self, x):
    #     print "(%s, %s)" % (x.start, x.end)

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
        starts = np.array([x.start() for x in trackElements])
        ends = np.array([x.end() for x in trackElements])
        vals = np.array([x.val() for x in trackElements])
        strands = np.array([x.strand() for x in trackElements])
        ids = np.array([x.id() for x in trackElements])
        edges = None #np.array([]) #doesn't make sense for between tracks randomization
        weights = None #np.array([]) #same

        origTV = origTrack.getTrackView(region)
        return TrackView(genomeAnchor=origTV.genomeAnchor,
                         startList=starts,
                         endList=ends,
                         valList=vals,
                         strandList=strands,
                         idList=ids,
                         edgesList=edges,
                         weightsList=weights,
                         borderHandling=origTV.borderHandling,
                         allowOverlaps=self._allowOverlaps)

    def _sortTrackElementLists(self):
        import operator
        for trackId in self._trackElementLists:
            for binId in self._trackElementLists[trackId]:
                self._trackElementLists[trackId][binId].sort(key=operator.attrgetter('start', 'end'))

        self._isSorted = True

