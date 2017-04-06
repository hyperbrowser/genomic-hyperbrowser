from gold.track.TrackFormat import NeutralTrackFormatReq
from gold.track.TrackView import TrackView
from gold.util.CustomExceptions import AbstractClassError
import numpy as np
import random as rn
from gold.statistic.RawDataStat import RawDataStat


class TsBasedRandomTrackViewProvider(object):
    def __init__(self, origTs, allowOverlaps=False, **kwargs):
        self._origTs = origTs
        self._elementPoolDict = {}
        self._allowOverlaps = allowOverlaps

    def getTrackView(self, region, origTrack, randIndex):
        raise AbstractClassError

class BetweenTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    pass

class WithinTrackRandomTvProvider(TsBasedRandomTrackViewProvider):
    pass


class ShuffleElementsBetweenTracksTvProvider(BetweenTrackRandomTvProvider):
    def getTrackView(self, region, origTrack, randIndex):
        if region not in self._elementPoolDict:
            self._populatePool(region)
        return self._elementPoolDict[region].getOneTrackViewFromPool(origTrack, randIndex)

    def _populatePool(self, region):
        self._elementPoolDict[region] = ShuffleElementsBetweenTracksPool(self._origTs, region, allowOverlaps=self._allowOverlaps)


class ShuffleElementsBetweenTracksPool(object):
    def __init__(self, origTs, region, allowOverlaps=False):
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
            self._maxTrackIndex = index

        self._allStarts = np.concatenate(origStartArrays)
        self._allEnds = np.concatenate(origEndArrays)
        self._order = self._allStarts.argsort()

        if allowOverlaps:
            self._selectRandomTrackIndex = self._selectSimpleRandomTrackIndex
        else:
            self._selectRandomTrackIndex = self._selectNonOverlappingRandomTrackIndex


    # TODO: dangerous; trackId must always be based on unknown. to make it easier to make this consistent, the original track is passed all the way here instead of passing the trackId directly
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

        #TODO: now this just returns a trackview with basically everything copied from the original, is that ok? should some other stuff also change?
        return TrackView(genomeAnchor=origTV.genomeAnchor, startList=newStarts, endList=newEnds,
                         valList=[0 for i in range(0, len(newStarts))],
                         strandList=[-1 for i in range(0, len(newStarts))],
                         idList=None, edgesList=None, weightsList=None, borderHandling=origTV.borderHandling, allowOverlaps=self._allowOverlaps)
                         #extraLists=origTV._extraLists, #TODO also 'translate' this extralist? (length needs to be the same)

    def _computeRandomTrackSet(self, randIndex):
        rn.seed(randIndex)

        newStarts = [[] for track in range(0, self._maxTrackIndex + 1)]
        newEnds = [[] for track in range(0, self._maxTrackIndex + 1)]

        for index in self._order:
            start = self._allStarts[index]
            end = self._allEnds[index]
            selectedTrack = self._selectRandomTrackIndex(newEnds=newEnds, newStart=start)
            newStarts[selectedTrack].append(start)
            newEnds[selectedTrack].append(end)

        self._randomTrackSets[randIndex] = [[np.array(track) for track in newStarts], [np.array(track) for track in newEnds]]

    def _selectSimpleRandomTrackIndex(self, **kwArgs):
        return rn.randint(0, self._maxTrackIndex)

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







