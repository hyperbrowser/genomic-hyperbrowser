from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.track.TrackView import TrackView
from gold.track.Track import Track
import numpy as np
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TsBasedRandomTrackViewProvider import BetweenTrackRandomTvProvider
from gold.track.TsBasedRandomTrackViewProvider import COVERAGE
from gold.track.TsBasedRandomTrackViewProvider import NUMBER_OF_SEGMENTS
from gold.track.TsBasedRandomTrackViewProvider import TsBasedRandomTrackViewProvider
from quick.application.SignatureDevianceLogging import takes
from test.gold.track.common.SampleTrack import SampleTrack
from third_party.typecheck import optional, list_of, anything, one_of

# A genome is needed in order to get a unique key from a track,
# but a genome should not be necessary for randomization.
# So the genome will always be set to this string.
GENOME_FOR_UNIQUE_KEY = 'unknown'

class ShuffleElementsBetweenTracksTvProvider(BetweenTrackRandomTvProvider):
    @takes('ShuffleElementsBetweenTracksTvProvider', 'TrackStructureV2', bool)
    def __init__(self, origTs, allowOverlaps):
        self._elementPoolDict = {}
        self._preservationMethod = None
        TsBasedRandomTrackViewProvider.__init__(self, origTs, allowOverlaps)

    @takes('ShuffleElementsBetweenTracksTvProvider', 'GenomeRegion', (Track, SampleTrack), int)
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
    @takes('ShuffleElementsBetweenTracksPool', 'TrackStructureV2', 'GenomeRegion', bool, one_of(None, COVERAGE, NUMBER_OF_SEGMENTS))
    def __init__(self, origTs, region, allowOverlaps, preservationMethod):
        self._region = region
        self._allowOverlaps = allowOverlaps

        self._trackIdToIndexDict = {}
        self.origArrays = {'starts':[], 'ends':[], 'vals':[], 'strands':[], 'ids':[], 'edges':[], 'weights':[]}

        for index, leafNode in enumerate(origTs.getLeafNodes()):
            track = leafNode.track
            trackId = track.getUniqueKey(GENOME_FOR_UNIQUE_KEY)
            self._trackIdToIndexDict[trackId] = index

            tv = track.getTrackView(region)
            self.origArrays['starts'].append(tv.startsAsNumpyArray())
            self.origArrays['ends'].append(tv.endsAsNumpyArray())
            self.origArrays['vals'].append(tv.valsAsNumpyArray())
            self.origArrays['strands'].append(tv.strandsAsNumpyArray())
            self.origArrays['ids'].append(tv.idsAsNumpyArray())
            self.origArrays['edges'].append(tv.edgesAsNumpyArray())
            self.origArrays['weights'].append(tv.weightsAsNumpyArray())

        self._amountTracks = index + 1
        self._probabilities = self._getProbabilities(preservationMethod, self.origArrays['starts'], self.origArrays['ends'])

        for tvParam in self.origArrays.keys():
            try:
                self.origArrays[tvParam] = np.concatenate(self.origArrays[tvParam])
            except ValueError: # this happens when one of the arrays is None
                self.origArrays.pop(tvParam)

        self._randomTrackSets = {'starts': {}, 'ends': {}, 'vals': {}, 'strands': {}, 'ids': {},
                                 'edges': {}, 'weights': {}}

        self._order = self.origArrays['starts'].argsort()

        if allowOverlaps:
            self._selectRandomTrackIndex = self._selectSimpleRandomTrackIndex
        else:
            self._selectRandomTrackIndex = self._selectNonOverlappingRandomTrackIndex

    def _getProbabilities(self, preservationMethod, origStartArrays, origEndArrays):
        allItemsLength = len(np.concatenate(origStartArrays))
        if allItemsLength == 0:
            return [1.0 / float(self._amountTracks) for i in range(0, self._amountTracks)]
        elif preservationMethod == NUMBER_OF_SEGMENTS:
            return [float(len(array)) / float(allItemsLength) for array in origStartArrays]
        elif preservationMethod == COVERAGE:
            coverages = [float(sum(origEndArrays[i] - origStartArrays[i])) for i in range(0, self._amountTracks)]
            return [coverage / sum(coverages) for coverage in coverages]
        else:
            return [1.0 / float(self._amountTracks) for i in range(0, self._amountTracks)]


    @takes('ShuffleElementsBetweenTracksPool', (Track, SampleTrack), int)
    def getOneTrackViewFromPool(self, origTrack, randIndex):
        trackId = origTrack.getUniqueKey(GENOME_FOR_UNIQUE_KEY)
        assert trackId in self._trackIdToIndexDict.keys(), 'given track should be in the original TrackStructure that was used to make this pool'
        trackIndex = self._trackIdToIndexDict[origTrack.getUniqueKey(GENOME_FOR_UNIQUE_KEY)]

        if randIndex not in self._randomTrackSets['starts']:
            self._computeRandomTrackSet(randIndex)

        origTV = RawDataStat(self._region, origTrack, NeutralTrackFormatReq()).getResult()

        for tvParam in self._randomTrackSets:
            try:
                self._randomTrackSets[tvParam][randIndex][trackIndex]
            except KeyError: # if the parameter does not exist, set it to None
                self._randomTrackSets[tvParam][randIndex] = {}
                self._randomTrackSets[tvParam][randIndex][trackIndex] = None

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

        newTrackValues = {}

        for tvParam in self.origArrays.keys():
            newTrackValues[tvParam] = [[] for track in range(0, self._amountTracks)]

        for index in self._order:
            start = self.origArrays['starts'][index]
            end = self.origArrays['ends'][index]
            selectedTrack = self._selectRandomTrackIndex(newEnds=newTrackValues['ends'], newStart=start)

            for tvParam in self.origArrays.keys():
                newTrackValues[tvParam][selectedTrack].append(self.origArrays[tvParam][index])


        for tvParam in self.origArrays.keys():
            self._randomTrackSets[tvParam][randIndex] = [np.array(track) for track in newTrackValues[tvParam]]


    @takes('ShuffleElementsBetweenTracksPool', optional(anything))
    def _selectSimpleRandomTrackIndex(self, **kwArgs):
        return np.random.choice(range(0, self._amountTracks), p=self._probabilities)

    @takes('ShuffleElementsBetweenTracksPool', list_of(list_of(int)), int, optional(anything))
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
