from collections import defaultdict, namedtuple

import numpy as np
import unittest

from gold.track.GenomeRegion import GenomeRegion
from gold.track.TrackStructure import TrackStructureV2, SingleTrackTS
from gold.track.TrackView import TrackView
from gold.track.RandTrackBasedTrackViewProvider import \
    PermutedSegsAndIntersegsTrackViewProvider, PermutedSegsAndSampledIntersegsTrackViewProvider
from gold.track.ShuffleElementsBetweenTracksTvProvider import \
    (ShuffleElementsBetweenTracksTvProvider,
     CoveragePreservedShuffleElementsBetweenTracksTvProvider,
     SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider,
     ShuffleElementsBetweenTracksPool)
from gold.track.trackstructure.TsUtils import getRandomizedVersionOfTs, getTsTreeStructureAsStr
from gold.track.trackstructure.random import ArrayInfoStorage
from gold.track.trackstructure.random.ShuffleElementsBetweenTracksAndBinsTvProvider import \
    ShuffleElementsBetweenTracksAndBinsTvProvider
from gold.track.trackstructure.random.TrackDataStorageRandAlgorithm import \
    CollisionDetectionTracksAndBinsRandAlgorithm
from test.gold.track.common.SampleTrack import SampleTrack
from test.gold.track.common.SampleTrackView import SampleTV
from mock import MagicMock, patch
from gold.track.TsBasedRandomTrackViewProvider import NUMBER_OF_SEGMENTS, COVERAGE


# Mocks

class MockSmartMemmap(object):
    def __init__(self, filename, numpyArray):
        self.filename = filename
        self._numpyArray = numpyArray

    def getShape(self):
        return self._numpyArray.shape

    def getDType(self):
        return self._numpyArray.dtype

    shape = property(getShape)
    dtype = property(getDType)


def _getTrackData(self, track, curBin, allowOverlaps):
    assert curBin.genome == 'TestGenome'
    assert curBin.chr == 'chr21'

    from gold.track.TrackSource import TrackData
    trackData = TrackData()
    fullTV = track.getTrackView(GenomeRegion(curBin.genome, curBin.chr, 0, 101))
    trackData['starts'] = MockSmartMemmap('starts.{}.int32'.format(len(fullTV)),
                                          fullTV.startsAsNumpyArray())
    trackData['ends'] = MockSmartMemmap('ends.{}.int32'.format(len(fullTV)),
                                        fullTV.endsAsNumpyArray())
    # TODO: add testing of more arrays when this is implemented

    return trackData


# Helper class

class RepeatedAssertion(object):
    def __init__(self, failuresAllowed, assertionFunc, *args):
        self._failuresAllowed = failuresAllowed
        self._assertionFunc = assertionFunc
        self._args = list(args)

    def __iter__(self):
        failures = 0
        self._args.append(0)  # randIndex
        while True:
            # print 'randIndex:', self._args[-1]
            try:
                self._assertionFunc(*self._args)
            except AssertionError:
                failures += 1
                # print 'Failure {}'.format(failures)
                if failures > self._failuresAllowed:
                    print '{} failures seen, which is more than the allowed {}'.format(
                        failures, self._failuresAllowed)
                    raise
            self._args[-1] += 1
            yield


# Tests

class TestTsBasedRandomTrackViewProvider(unittest.TestCase):
    def setUp(self):
        genomeAnchor = [0, 101]
        self.bins = [GenomeRegion('TestGenome', 'chr21', 0, 50),
                     GenomeRegion('TestGenome', 'chr21', 50, 101)]

        self.ts = defaultdict(TrackStructureV2)
        allSegmentSetNoOverlap = [[[10, 20]],
                                  [[5, 10], [25, 50], [55, 70], [75, 80], [90, 95]],
                                  [[5, 15], [20, 30], [45, 55], [75, 80]],
                                  [[0, 20], [60, 65], [85, 100]]]
        allSegmentSetOverlap = [[[10, 25]],
                                [[5, 10], [20, 50], [55, 70], [75, 80], [90, 95]],
                                [[5, 20], [15, 30], [45, 55], [75, 80]],
                                [[0, 20], [60, 65], [85, 100]]]
        excludedSegments = [[45, 55], [70, 75]]

        for allowOverlaps, allSegmentSet in \
                zip([False, True], [allSegmentSetNoOverlap, allSegmentSetOverlap]):
            for i, segmentSet in enumerate(allSegmentSet):
                track = SampleTrack(SampleTV(segments=segmentSet, anchor=genomeAnchor,
                                             allowOverlaps=allowOverlaps))
                track.getUniqueKey = MagicMock(return_value=i)
                self.ts[allowOverlaps]['dummy' + str(i)] = SingleTrackTS(track, {})

            track = SampleTrack(SampleTV(segments=[], anchor=genomeAnchor,
                                         allowOverlaps=allowOverlaps))
            track.getUniqueKey = MagicMock(return_value=i+1)
            self.ts[allowOverlaps]['emptyTrack'] = SingleTrackTS(track, {})

        exclusionTrack = SampleTrack(SampleTV(segments=excludedSegments, anchor=genomeAnchor, 
                                              allowOverlaps=False))
        self.exclusionTs = SingleTrackTS(exclusionTrack, {})

    def testRandomizedTsKeys(self):
        for tvProviderClass in [
                ShuffleElementsBetweenTracksTvProvider,
                SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider,
                CoveragePreservedShuffleElementsBetweenTracksTvProvider,
                PermutedSegsAndIntersegsTrackViewProvider,
                PermutedSegsAndSampledIntersegsTrackViewProvider]:
            for allowOverlaps in [False, True]:
                ts = self.ts[allowOverlaps]
                self.assertEqual(ts.keys(), getRandomizedVersionOfTs(ts, tvProviderClass(),
                                                                     randIndex=1).keys())

    def testOverlapsNotAllowed(self):
        self.assertFalse(
            PermutedSegsAndIntersegsTrackViewProvider().supportsOverlapMode(True))
        self.assertFalse(
            PermutedSegsAndSampledIntersegsTrackViewProvider().supportsOverlapMode(True))

    @patch.object(ArrayInfoStorage.ArrayInfoStorage, '_getTrackData', _getTrackData)
    @patch.object(ArrayInfoStorage, 'SmartMemmap', MockSmartMemmap)
    def testBetweenTracksAndBinsRandomization(self):
        from functools import partial

        betweenTracksAndBinsTvProviderCls = ShuffleElementsBetweenTracksAndBinsTvProvider

        def getBetweenTracksAndBinsTvProvider(randAlgorithm):
            return betweenTracksAndBinsTvProviderCls(randAlgorithm)

        RandAlgTestSetup = namedtuple('RandAlgTestSetup',
                                      ('randAlg', 'testExclusionTs', 'allowLossOfSegments'))
        randAlgorithms = [
            RandAlgTestSetup(randAlg=CollisionDetectionTracksAndBinsRandAlgorithm(
                                excludedTS=None, binSource=self.bins),
                             testExclusionTs=False, allowLossOfSegments=True),
            RandAlgTestSetup(randAlg=CollisionDetectionTracksAndBinsRandAlgorithm(
                                excludedTS=self.exclusionTs, binSource=self.bins),
                             testExclusionTs=True, allowLossOfSegments=True),
        ]

        for randAlgorithm in randAlgorithms:
            createTvProviderFunc = partial(getBetweenTracksAndBinsTvProvider,
                                           randAlgorithm.randAlg)
            self._assertRandTrackContentsAfterRandomization(
                createTvProviderFunc,
                allowOverlapsList=[False, True],
                testExclusionTs=randAlgorithm.testExclusionTs,
                allowLossOfSegments=randAlgorithm.allowLossOfSegments)

    def testBetweenTrackRandomization(self):
        for betweenTrackTvProviderClass in [
                ShuffleElementsBetweenTracksTvProvider,
                SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider,
                CoveragePreservedShuffleElementsBetweenTracksTvProvider]:
            self._assertRandTrackContentsAfterRandomization(
                betweenTrackTvProviderClass,
                allowOverlapsList=[True],
                testExclusionTs=False,
                allowLossOfSegments=False)

    def testWithinTrackRandomization(self):
        for withinTrackTvProviderClass in [
                PermutedSegsAndIntersegsTrackViewProvider,
                PermutedSegsAndSampledIntersegsTrackViewProvider]:
            self._assertRandTrackContentsAfterRandomization(
                withinTrackTvProviderClass,
                allowOverlapsList=[False],
                testExclusionTs=False,
                allowLossOfSegments=False)

    def _assertRandTrackContentsAfterRandomization(self, tvProviderCallable, allowOverlapsList,
                                                   testExclusionTs, allowLossOfSegments):
        # print repr(tvProviderCallable)
        for allowOverlaps in allowOverlapsList:
            # print 'allowOverlaps:', allowOverlaps
            ts = self.ts[allowOverlaps]
            tvProvider = tvProviderCallable()
            tvProvider.setOrigTrackStructure(ts)
            tvProvider.setBinSource(self.bins)

            # List of particular assertion tests that will be repeated in parallel, increasing
            # randIndex by one for each step. Each test can fail up to a specified number of times
            # until the full test fails.
            assertionList = list()

            # If overlaps are allowed then at least one track in one of five randomizations should
            # show a pair of overlapping segments
            # If overlaps are not allowed, then no overlapping segments should be returned, ever
            failuresAllowed = 4 if allowOverlaps else 0
            assertionList.append(
                RepeatedAssertion(failuresAllowed,
                                  self._assertOverlapsAfterRandomization,
                                  ts, tvProvider, allowOverlaps)
            )

            # If the randomization algorithm allows for the loss of segments, then there will be
            # fewer segments than the original. This should not happen more than in one out of
            # five randomizations using the crowded test data. In real-world scenarios, it will
            # happen more rarely.
            failuresAllowed = 1 if allowLossOfSegments else 0
            assertionList.append(
                RepeatedAssertion(failuresAllowed,
                                  self._assertSameSegmentsAfterRandomization,
                                  ts, tvProvider)
            )

            # In a very rare case the randomized tracks might be exactly equal to the original.
            # If it happens twice out of five randomizations, we assume something is wrong.
            failuresAllowed = 1
            assertionList.append(
                RepeatedAssertion(failuresAllowed,
                                  self._assertNotSameTracksAsOrigAfterRandomization,
                                  ts, tvProvider)
            )

            # If the randomization algorithm allows the specification of exclusion tracks (in an
            # exclusion track structure), the random segments should never overlap with the
            # excluded segments.
            if testExclusionTs:
                failuresAllowed = 0
                assertionList.append(
                    RepeatedAssertion(failuresAllowed,
                                      self._assertNotOverlappingExclusionTrackAfterRandomization,
                                      ts, tvProvider)
                )

            assertionIters = [x.__iter__() for x in assertionList]

            # Parallel execution of all assertion tests, one randIndex at a time, up to five
            # randomizations.
            for randIndex in range(5):
                for iter in assertionIters:
                    iter.next()

    def _assertSameSegmentsAfterRandomization(self, ts, tvProvider, randIndex):
        """Assert that the total set of segments before and after randomization is the same"""
        origSizes = []
        randSizes = []

        # print 'same segments'
        for region in self.bins:
            # print region
            for singleTs in ts.values():
                origTv, randTv = self._getOrigAndRandTv(region, singleTs, tvProvider, randIndex)
                origSizes += list(origTv.endsAsNumpyArray() - origTv.startsAsNumpyArray())
                randSizes += list(randTv.endsAsNumpyArray() - randTv.startsAsNumpyArray())

        self.assertEqual(len(origSizes), len(randSizes))
        self.assertEqual(sorted(origSizes), sorted(randSizes))

    def _assertNotSameTracksAsOrigAfterRandomization(self, ts, tvProvider, randIndex):
        sameTracks = []

        # print 'not same tracks'
        for region in self.bins:
            # print region
            for singleTs in ts.values():
                origTv, randTv = self._getOrigAndRandTv(region, singleTs, tvProvider, randIndex)
                origStarts = origTv.startsAsNumpyArray()
                origEnds = origTv.endsAsNumpyArray()
                randStarts = randTv.startsAsNumpyArray()
                randEnds = randTv.endsAsNumpyArray()

                sameTracks.append(len(origStarts) == len(randStarts) ==
                                  len(origEnds) == len(randEnds) and
                                  np.all(origStarts == randStarts) and
                                  np.all(origEnds == randEnds))

        self.assertFalse(all(sameTracks))

    def _assertOverlapsAfterRandomization(self, ts, tvProvider, allowOverlaps, randIndex):
        # print 'some overlaps' if allowOverlaps else 'no overlaps'
        anyOverlaps = False
        for region in self.bins:
            # print region
            for singleTs in ts.values():
                origTv, randTv = self._getOrigAndRandTv(region, singleTs, tvProvider, randIndex)
                distances = randTv.startsAsNumpyArray()[1:] - randTv.endsAsNumpyArray()[:-1]
                anyOverlaps |= np.any(distances < 0)

        if allowOverlaps:
            self.assertTrue(anyOverlaps)
        else:
            self.assertFalse(anyOverlaps)

    def _assertNotOverlappingExclusionTrackAfterRandomization(self, ts, tvProvider, randIndex):
        # print 'not overlapping exclusion track'
        for region in self.bins:
            # print region
            exclusionTv = self.exclusionTs.track.getTrackView(region)
            for singleTs in ts.values():
                randTv = self._getOrigAndRandTv(region, singleTs, tvProvider, randIndex)[-1]
                for excludedSegment in exclusionTv:
                    randStarts = randTv.startsAsNumpyArray()
                    randEnds = randTv.endsAsNumpyArray()
                    exclStart = excludedSegment.start()
                    exclEnd = excludedSegment.end()
                    # print 'Excluded segment: [{}, {}]'.format(exclStart, exclEnd)
                    anyOverlaps = np.logical_and(randStarts < exclEnd, randEnds > exclStart).any()
                    self.assertFalse(anyOverlaps)

    def _getOrigAndRandTv(self, region, singleTs, tvProvider, randIndex):
        origTv = singleTs.track.getTrackView(region)
        randTv = tvProvider.getTrackView(region, singleTs.track, randIndex)
        # print('Orig start: ', origTv.startsAsNumpyArray())
        # print('Orig end: ', origTv.endsAsNumpyArray())
        # print('Rand start: ', randTv.startsAsNumpyArray())
        # print('Rand end: ', randTv.endsAsNumpyArray())
        return origTv, randTv
            

class TestShuffleElementsBetweenTracksPool(unittest.TestCase):
    def setUp(self):
        """
        Create a fake trackstructure containing empty tracks,
        this is only used to ensure the randomization pool knows there should be 3 input tracks.
        """
        genomeAnchor = [0, 101]
        self.amountTracks = 3
        self.region = GenomeRegion('TestGenome', 'chr21', genomeAnchor[0], genomeAnchor[1])

        self.ts = TrackStructureV2()

        for i, segmentSet in enumerate([[]] * self.amountTracks):
            track = SampleTrack(SampleTV(segments=segmentSet, anchor=genomeAnchor))
            track.getUniqueKey = MagicMock(return_value=i)
            self.ts[str(i)] = SingleTrackTS(track, {})

        self.shufflePool = ShuffleElementsBetweenTracksPool(self.ts, self.region, None)

    def testGetProbabilities(self):
        """
        Ensure the correct probabilities are returned in the different circumstances.
        """
        self.assertEqual(self.shufflePool._getProbabilities(None,
                                                            np.array([[], [], []]),
                                                            np.array([[], [], []])),
                         [1.0/3, 1.0/3, 1.0/3])
        self.assertEqual(self.shufflePool._getProbabilities(COVERAGE,
                                                            np.array([[], [], []]),
                                                            np.array([[], [], []])),
                         [1.0/3, 1.0/3, 1.0/3])
        self.assertEqual(self.shufflePool._getProbabilities(NUMBER_OF_SEGMENTS,
                                                            np.array([[], [], []]),
                                                            np.array([[], [], []])),
                         [1.0/3, 1.0/3, 1.0/3])
        self.assertEqual(self.shufflePool._getProbabilities(None,
                                                            np.array([[1], [2], [3]]),
                                                            np.array([[4], [5], [6]])),
                         [1.0/3, 1.0/3, 1.0/3])
        self.assertEqual(self.shufflePool._getProbabilities(COVERAGE,
                                                            np.array([[1], [2], [3]]),
                                                            np.array([[7], [5], [6]])),
                         [0.5, 0.25, 0.25])
        self.assertEqual(self.shufflePool._getProbabilities(NUMBER_OF_SEGMENTS,
                                                            np.array([[1], [2, 3], [4]]),
                                                            np.array([[4], [5, 6], [7]])),
                         [0.25, 0.5, 0.25])

    def testGetOneTrackViewFromPool(self):
        """Test if a valid trackview is returned by the pool"""
        self.assertIsInstance(self.shufflePool.getOneTrackViewFromPool(self.ts['1'].track, 1),
                              TrackView)

    def testComputeRandomTrackSet(self):
        """Test to see that there are no randomized tracksets when the pool is initiated,
        and random track sets are added after the pool has been called with a new randIndex"""
        self.assertEqual(self.shufflePool._randomTrackSets['starts'].keys(), [])
        randIndexes = [1, 2, 3]
        for randIndex in randIndexes:
            self.shufflePool.getOneTrackViewFromPool(self.ts['1'].track, randIndex)
            # Assert that there is a starts and ends array for every track
            self.assertEqual(len(self.shufflePool._randomTrackSets['starts'][randIndex]),
                             self.amountTracks)
            self.assertEqual(len(self.shufflePool._randomTrackSets['ends'][randIndex]),
                             self.amountTracks)
        self.assertEqual(self.shufflePool._randomTrackSets['starts'].keys(), randIndexes)

    def testSelectNonOverlappingRandomTrackIndex(self):
        for i in range(0, 100):
            self.assertEqual(self.shufflePool._selectNonOverlappingRandomTrackIndex(
                                [[10], [100], [100]], 20),
                             0)

