from gold.track.GenomeRegion import GenomeRegion
from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.track.TrackView import TrackView
from gold.track.Track import Track
from gold.util.CustomExceptions import AbstractClassError
import numpy as np
import random as rn
from gold.statistic.RawDataStat import RawDataStat
from quick.application.SignatureDevianceLogging import takes
from third_party.typecheck import optional, list_of, anything, one_of

NUMBER_OF_SEGMENTS = 'Number of segments'
COVERAGE = 'Base pair coverage'


class TsBasedRandomTrackViewProvider(object):
    @takes('TsBasedRandomTrackViewProvider', 'TrackStructureV2', bool)
    def __init__(self, origTs, allowOverlaps):
        self._origTs = origTs
        self._allowOverlaps = allowOverlaps

    @takes('TsBasedRandomTrackViewProvider', GenomeRegion, Track, int)
    def getTrackView(self, region, origTrack, randIndex):
        raise AbstractClassError

class BetweenTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    pass

class WithinTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    pass


class ShuffleElementsBetweenTracksTvProvider(BetweenTrackRandomTvProvider):
    @takes('ShuffleElementsBetweenTracksTvProvider', 'TrackStructureV2', bool)
    def __init__(self, origTs, allowOverlaps):
        self._elementPoolDict = {}
        self._preservationMethod = None
        BetweenTrackRandomTvProvider.__init__(self, origTs, allowOverlaps)

    @takes('ShuffleElementsBetweenTracksTvProvider', 'GenomeRegion', Track, int)
    def getTrackView(self, region, origTrack, randIndex):
        if region not in self._elementPoolDict:
            self._populatePool(region)
        return self._elementPoolDict[region].getOneTrackViewFromPool(origTrack, randIndex)

    @takes('ShuffleElementsBetweenTracksTvProvider', 'GenomeRegion')
    def _populatePool(self, region):
        self._elementPoolDict[region] = ShuffleElementsBetweenTracksPool(self._origTs, region, self._allowOverlaps, self._preservationMethod)

class SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider(ShuffleElementsBetweenTracksTvProvider):
    @takes('SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider', 'TrackStructureV2', bool)
    def __init__(self, origTs, allowOverlaps):
        ShuffleElementsBetweenTracksTvProvider.__init__(self, origTs, allowOverlaps)
        self._preservationMethod = NUMBER_OF_SEGMENTS

class CoveragePreservedShuffleElementsBetweenTracksTvProvider(ShuffleElementsBetweenTracksTvProvider):
    @takes('CoveragePreservedShuffleElementsBetweenTracksTvProvider', 'TrackStructureV2', bool)
    def __init__(self, origTs, allowOverlaps):
        ShuffleElementsBetweenTracksTvProvider.__init__(self, origTs, allowOverlaps)
        self._preservationMethod = COVERAGE


class ShuffleElementsBetweenTracksPool(object):
    @takes('ShuffleElementsBetweenTracksPool', 'TrackStructureV2', GenomeRegion, bool, one_of(str, None))
    def __init__(self, origTs, region, allowOverlaps, preservationMethod):
        self._region = region
        self._allowOverlaps = allowOverlaps
        self._randomTrackSets = {} # _randomTrackSets[randIndex] gives a double list; [[track0starts, track1starts, ..., trackNstarts],[track0ends, track1ends, ..., trackNends]
        self._trackIdToIndexDict = {}

        origStartArrays = []
        origEndArrays = []

        for index, leafNode in enumerate(origTs.getLeafNodes()):
            track = leafNode.track
            trackId = track.getUniqueKey('unknown')
            self._trackIdToIndexDict[trackId] = index

            tv = track.getTrackView(region)
            origStartArrays.append(tv.startsAsNumpyArray())
            origEndArrays.append(tv.endsAsNumpyArray())

        self._allStarts = np.concatenate(origStartArrays)
        self._allEnds = np.concatenate(origEndArrays)
        self._order = self._allStarts.argsort()
        self._amountTracks = len(origStartArrays)

        if len(self._allStarts) == 0:
            self._probabilities = [0 for i in range(0, self._amountTracks)]
        elif preservationMethod == NUMBER_OF_SEGMENTS:
            self._probabilities = [float(len(array)) / float(len(self._allStarts)) for array in origStartArrays]
        elif preservationMethod == COVERAGE:
            coverages = [float(sum(origEndArrays[i] - origStartArrays[i])) for i in range(0, self._amountTracks)]
            self._probabilities = [coverage/sum(coverages) for coverage in coverages]
        else:
            self._probabilities = [1.0 / float(self._amountTracks) for i in range(0, self._amountTracks)]


        if allowOverlaps:
            self._selectRandomTrackIndex = self._selectSimpleRandomTrackIndex
        else:
            self._selectRandomTrackIndex = self._selectNonOverlappingRandomTrackIndex


    # TODO: dangerous; trackId must always be based on unknown. to make it easier to make this consistent, the original track is passed all the way here instead of passing the trackId directly
    @takes('ShuffleElementsBetweenTracksPool', Track, int)
    def getOneTrackViewFromPool(self, origTrack, randIndex):
        trackId = origTrack.getUniqueKey('unknown')
        assert trackId in self._trackIdToIndexDict.keys(), 'given track should be in the original TrackStructure that was used to make this pool'
        trackIndex = self._trackIdToIndexDict[origTrack.getUniqueKey('unknown')]

        if randIndex not in self._randomTrackSets:
            self._computeRandomTrackSet(randIndex)

        newStarts = self._randomTrackSets[randIndex][0][trackIndex]
        newEnds = self._randomTrackSets[randIndex][1][trackIndex]

        rawData = RawDataStat(self._region, origTrack, NeutralTrackFormatReq())
        origTV = rawData.getResult()

        return TrackView(genomeAnchor=origTV.genomeAnchor, startList=newStarts, endList=newEnds,
                         valList=[0 for i in range(0, len(newStarts))],
                         strandList=[-1 for i in range(0, len(newStarts))],
                         idList=None, edgesList=None, weightsList=None, borderHandling=origTV.borderHandling, allowOverlaps=self._allowOverlaps)
                         #extraLists=origTV._extraLists, #TODO also 'translate' this extralist? (length needs to be the same)

    @takes('ShuffleElementsBetweenTracksPool', int)
    def _computeRandomTrackSet(self, randIndex):
        rn.seed(randIndex)

        newStarts = [[] for track in range(0, self._amountTracks)]
        newEnds = [[] for track in range(0, self._amountTracks)]

        for index in self._order:
            start = self._allStarts[index]
            end = self._allEnds[index]
            selectedTrack = self._selectRandomTrackIndex(newEnds=newEnds, newStart=start)
            newStarts[selectedTrack].append(start)
            newEnds[selectedTrack].append(end)

        self._randomTrackSets[randIndex] = [[np.array(track) for track in newStarts], [np.array(track) for track in newEnds]]

    @takes('ShuffleElementsBetweenTracksPool', optional(anything))
    def _selectSimpleRandomTrackIndex(self, **kwArgs):
        return np.random.choice(range(0, self._amountTracks), p=self._probabilities)

    @takes('ShuffleElementsBetweenTracksPool', list_of(list_of(int)), list_of(list_of(int)), optional(anything))
    def _selectNonOverlappingRandomTrackIndex(self, newEnds, newStart, **kwArgs):
        selectedTrack = self._selectSimpleRandomTrackIndex()

        if not self._allowOverlaps:
            try:
                while newEnds[selectedTrack][-1] > newStart:
                    selectedTrack = self._selectSimpleRandomTrackIndex()
            except IndexError:
                # there is nothing in the newEnds list yet, place the current track
                pass

        return selectedTrack


