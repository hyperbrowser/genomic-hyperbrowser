from gold.track.GenomeRegion import GenomeRegion
from gold.track.PermutedSegsAndIntersegsTrack import PermutedSegsAndIntersegsTrack
from gold.track.PermutedSegsAndSampledIntersegsTrack import PermutedSegsAndSampledIntersegsTrack
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
    def __init__(self, *args, **kwArgs):
        raise AbstractClassError

class WithinTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    def __init__(self, *args, **kwArgs):
        raise AbstractClassError

class PermutedSegsAndIntersegsTrackViewProvider(WithinTrackRandomTvProvider):
    def __init__(self, *args, **kwArgs):
        pass

    @takes('PermutedSegsAndIntersegsTrackViewProvider', GenomeRegion, Track, int)
    def getTrackView(self, region, origTrack, randIndex):
        return PermutedSegsAndIntersegsTrack(origTrack, randIndex).getTrackView(region)

class PermutedSegsAndSampledIntersegsTrackViewProvider(WithinTrackRandomTvProvider):
    def __init__(self, *args, **kwArgs):
        pass

    @takes('PermutedSegsAndSampledIntersegsTrackViewProvider', GenomeRegion, Track, int)
    def getTrackView(self, region, origTrack, randIndex):
        return PermutedSegsAndSampledIntersegsTrack(origTrack, randIndex).getTrackView(region)


class ShuffleElementsBetweenTracksTvProvider(BetweenTrackRandomTvProvider):
    @takes('ShuffleElementsBetweenTracksTvProvider', 'TrackStructureV2', bool)
    def __init__(self, origTs, allowOverlaps):
        self._elementPoolDict = {}
        self._preservationMethod = None
        TsBasedRandomTrackViewProvider.__init__(self, origTs, allowOverlaps)

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


class ShuffleElementsBetweenTracksPoolV2(object):
    # IMPORTANT: READ THIS!!!
    # this is a new version of ShuffleElementsBetweenTracksPool, which takes into account that when providing the new trackviews
    # they should contain more than just starts and ends, but also vals, strands, ids, edges and weights (extralists have not been added yet)
    # this is a more complete implementation, however, it is slower than the original and might not always be necessary (only if using certain statistics)
    # also the code works but looks clumpsy now and should be refactored before this is set to the real 'ShuffleElementsBetweenTracksPool'
    @takes('ShuffleElementsBetweenTracksPool', 'TrackStructureV2', GenomeRegion, bool, one_of(str, None))
    def __init__(self, origTs, region, allowOverlaps, preservationMethod):
        self._region = region
        self._allowOverlaps = allowOverlaps
        self._randomTrackSets = {'starts':{}, 'ends':{}, 'vals':{}, 'strands':{}, 'ids':{}, 'edges':{}, 'weights':{}}
        self._trackIdToIndexDict = {}

        origStartArrays = []
        origEndArrays = []
        origValArrays = []
        origStrandArrays = []
        origIdArrays = []
        origEdgeArrays = []
        origWeightArrays = []

        for index, leafNode in enumerate(origTs.getLeafNodes()):
            track = leafNode.track
            trackId = track.getUniqueKey('unknown')
            self._trackIdToIndexDict[trackId] = index

            tv = track.getTrackView(region)
            origStartArrays.append(tv.startsAsNumpyArray())
            origEndArrays.append(tv.endsAsNumpyArray())
            origValArrays.append(tv.valsAsNumpyArray())
            origStrandArrays.append(tv.strandsAsNumpyArray())
            origIdArrays.append(tv.idsAsNumpyArray())
            origEdgeArrays.append(tv.edgesAsNumpyArray())
            origWeightArrays.append(tv.weightsAsNumpyArray())

        self._allStarts = np.concatenate(origStartArrays)
        self._allEnds = np.concatenate(origEndArrays)
        self._allVals = np.concatenate(origValArrays)
        self._allStrands = np.concatenate(origStrandArrays)
        self._allIds = np.concatenate(origIdArrays)
        self._allEdges = np.concatenate(origEdgeArrays)
        self._allWeights = np.concatenate(origWeightArrays)
        self._order = self._allStarts.argsort()
        self._amountTracks = len(origStartArrays)
        self.self._probabilities = self._getProbabilities(preservationMethod, origStartArrays, origEndArrays)

        if allowOverlaps:
            self._selectRandomTrackIndex = self._selectSimpleRandomTrackIndex
        else:
            self._selectRandomTrackIndex = self._selectNonOverlappingRandomTrackIndex

    def _getProbabilities(self, preservationMethod, origStartArrays, origEndArrays):
        if len(self._allStarts) == 0:
            return [0 for i in range(0, self._amountTracks)]
        elif preservationMethod == NUMBER_OF_SEGMENTS:
            return [float(len(array)) / float(len(self._allStarts)) for array in origStartArrays]
        elif preservationMethod == COVERAGE:
            coverages = [float(sum(origEndArrays[i] - origStartArrays[i])) for i in range(0, self._amountTracks)]
            return [coverage / sum(coverages) for coverage in coverages]
        else:
            return [1.0 / float(self._amountTracks) for i in range(0, self._amountTracks)]


    # TODO: dangerous; trackId must always be based on unknown. to make it easier to make this consistent, the original track is passed all the way here instead of passing the trackId directly
    @takes('ShuffleElementsBetweenTracksPool', Track, int)
    def getOneTrackViewFromPool(self, origTrack, randIndex):
        trackId = origTrack.getUniqueKey('unknown')
        assert trackId in self._trackIdToIndexDict.keys(), 'given track should be in the original TrackStructure that was used to make this pool'
        trackIndex = self._trackIdToIndexDict[origTrack.getUniqueKey('unknown')]

        if randIndex not in self._randomTrackSets['starts']:
            self._computeRandomTrackSet(randIndex)

        origTV = RawDataStat(self._region, origTrack, NeutralTrackFormatReq()).getResult()

        return TrackView(genomeAnchor=origTV.genomeAnchor,
                         startList=self._randomTrackSets['starts'][randIndex][trackIndex],
                         endList=self._randomTrackSets['ends'][randIndex][trackIndex],
                         valList=self._randomTrackSets['vals'][randIndex][trackIndex],
                         strandList=self._randomTrackSets['strands'][randIndex][trackIndex],
                         idList=self._randomTrackSets['ids'][randIndex][trackIndex],
                         edgesList=self._randomTrackSets['edges'][randIndex][trackIndex],
                         weightsList=self._randomTrackSets['weights'][randIndex][trackIndex],
                         borderHandling=origTV.borderHandling,
                         allowOverlaps=self._allowOverlaps)

    @takes('ShuffleElementsBetweenTracksPool', int)
    def _computeRandomTrackSet(self, randIndex):
        rn.seed(randIndex)

        newStarts = [[] for track in range(0, self._amountTracks)]
        newEnds = [[] for track in range(0, self._amountTracks)]
        newVals = [[] for track in range(0, self._amountTracks)]
        newStrands = [[] for track in range(0, self._amountTracks)]
        newIds = [[] for track in range(0, self._amountTracks)]
        newEdges = [[] for track in range(0, self._amountTracks)]
        newWeights = [[] for track in range(0, self._amountTracks)]

        for index in self._order:
            start = self._allStarts[index]
            end = self._allEnds[index]
            selectedTrack = self._selectRandomTrackIndex(newEnds=newEnds, newStart=start)
            newStarts[selectedTrack].append(start)
            newEnds[selectedTrack].append(end)
            newVals[selectedTrack].append(self._allVals[index])
            newStrands[selectedTrack].append(self._allStrands[index])
            newIds[selectedTrack].append(self._allIds[index])
            newEdges[selectedTrack].append(self._allEdges[index])
            newWeights[selectedTrack].append(self._allWeights[index])

        #self._randomTrackSets[randIndex] = [[np.array(track) for track in newStarts], [np.array(track) for track in newEnds]]
        self._randomTrackSets['starts'][randIndex] = [np.array(track) for track in newStarts]
        self._randomTrackSets['ends'][randIndex] = [np.array(track) for track in newEnds]
        self._randomTrackSets['vals'][randIndex] = [np.array(track) for track in newVals]
        self._randomTrackSets['strands'][randIndex] = [np.array(track) for track in newStrands]
        self._randomTrackSets['ids'][randIndex] = [np.array(track) for track in newIds]
        self._randomTrackSets['edges'][randIndex] = [np.array(track) for track in newEdges]
        self._randomTrackSets['weights'][randIndex] = [np.array(track) for track in newWeights]

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


