from gold.track.TrackStructure import SingleTrackTS


class ExcludedSegmentsStorage(object):
    # TODO: Could be improved to use less memory
    def __init__(self, excludedTS, binSource):
        self._excludedTS = excludedTS
        self._binSource = binSource
        self._excludedSegmentsDict = None

    def _initExcludedRegions(self):
        # for now we only support a single exclusion track
        assert isinstance(self._excludedTS, SingleTrackTS), \
            "Only Single track TS supported for exclusion track."
        self._excludedSegmentsDict = dict()

        for region in self._binSource:
            excludedTV = self._excludedTS.track.getTrackView(region)
            assert not excludedTV.allowOverlaps, \
                "Only non-overlapping exclusion track elements make sense"
            self._excludedSegmentsDict[region] = \
                zip(excludedTV.startsAsNumpyArray() + excludedTV.genomeAnchor.start,
                    excludedTV.endsAsNumpyArray() + excludedTV.genomeAnchor.start)

    def getExcludedSegmentsIter(self, region):
        if not self._excludedSegmentsDict:
            self._initExcludedRegions()

        assert region in self._excludedSegmentsDict, "Not a valid region %s" % str(region)
        return self._excludedSegmentsDict[region]
