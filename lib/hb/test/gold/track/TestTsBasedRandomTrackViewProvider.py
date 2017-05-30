# test if the amount of elements in the output track is still the same
import numpy as np
import unittest

from gold.track.GenomeRegion import GenomeRegion
from gold.track.TrackStructure import TrackStructureV2, SingleTrackTS
from gold.track.TrackView import TrackView
from gold.track.RandomizedSegsTvProvider import PermutedSegsAndIntersegsTrackViewProvider, PermutedSegsAndSampledIntersegsTrackViewProvider
from gold.track.ShuffleElementsBetweenTracksTvProvider import ShuffleElementsBetweenTracksTvProvider, \
    CoveragePreservedShuffleElementsBetweenTracksTvProvider, SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider, ShuffleElementsBetweenTracksPool
from gold.util.CustomExceptions import NotSupportedError
from test.gold.track.common.SampleTrack import SampleTrack
from test.gold.track.common.SampleTrackView import SampleTV
from mock import MagicMock
from gold.track.TsBasedRandomTrackViewProvider import NUMBER_OF_SEGMENTS, COVERAGE



class TestTsBasedRandomTrackViewProvider(unittest.TestCase):
    def setUp(self):
        '''Create a fake trackstructure containing tracks with different kinds of segments and one empty track.'''
        genomeAnchor = [0, 101]
        self.region = GenomeRegion('TestGenome', 'chr21', genomeAnchor[0], genomeAnchor[1])

        self.ts = TrackStructureV2()
        allSegmentSets = [[[10, 20]], [[25, 50], [55, 70]], [[5, 15], [20, 30], [75, 80]], [[0, 30], [60, 65], [85, 100]]]

        for i, segmentSet in enumerate(allSegmentSets):
            track = SampleTrack(SampleTV(segments=segmentSet, anchor=genomeAnchor))
            track.getUniqueKey = MagicMock(return_value=i)
            self.ts[str(i)] = SingleTrackTS(track, {})

        track = SampleTrack(SampleTV(segments=[], anchor=genomeAnchor))
        track.getUniqueKey = MagicMock(return_value=i+1)
        self.ts['emptyTrack'] = SingleTrackTS(track, {})

    def testRandomizedTsKeys(self):
        '''The keys after randomization should still be the same (there is a randomized track for every original track)'''
        for tvProviderClass in [ShuffleElementsBetweenTracksTvProvider,
                                SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider,
                                CoveragePreservedShuffleElementsBetweenTracksTvProvider,
                                PermutedSegsAndIntersegsTrackViewProvider,
                                PermutedSegsAndSampledIntersegsTrackViewProvider]:
            self.assertEqual(self.ts.keys(), self.ts.getRandomizedVersion(tvProviderClass, False, 1).keys())

    def testOverlapsNotAllowed(self):
        '''For these within-track randomizers randomization with overlaps is not supported.'''
        with self.assertRaises(NotSupportedError):
            PermutedSegsAndIntersegsTrackViewProvider(self.ts, True)
            PermutedSegsAndSampledIntersegsTrackViewProvider(self.ts, True)

    def testBetweenTrackRandomizationSegmentSizes(self):
        '''Test between track randomization with different parameters, the total segment set should be identical'''
        for betweenTrackTvProviderClass in [ShuffleElementsBetweenTracksTvProvider,
                                            SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider,
                                            CoveragePreservedShuffleElementsBetweenTracksTvProvider]:
            for allowOverlaps in (True, False):
                for randIndex in range(1, 3):
                    tvProvider = betweenTrackTvProviderClass(self.ts, allowOverlaps)
                    self._assertSameSegmentsAfterRandomization(tvProvider, randIndex)

    def testWithinTrackRandomizationSegmentSizes(self):
        '''Test within track randomization with different parameters, the total segment set should be identical'''
        for withinTrackTvProviderClass in [ShuffleElementsBetweenTracksTvProvider,
                                            SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider,
                                            CoveragePreservedShuffleElementsBetweenTracksTvProvider]:
            for randIndex in range(1, 3):
                tvProvider = withinTrackTvProviderClass(self.ts, False)
                self._assertSameSegmentsAfterRandomization(tvProvider, randIndex)

    def _assertSameSegmentsAfterRandomization(self, tvProvider, randIndex):
        '''Assert that the total set of segments before and after randomization is the same'''
        origSizes = []
        randSizes = []

        for singleTs in self.ts.values():
            origTv = singleTs.track.getTrackView(self.region)
            randTv = tvProvider.getTrackView(self.region, singleTs.track, randIndex)
            origSizes += list(origTv.endsAsNumpyArray() - origTv.startsAsNumpyArray())
            randSizes += list(randTv.endsAsNumpyArray() - randTv.startsAsNumpyArray())

        self.assertEqual(len(origSizes), len(randSizes))
        self.assertEqual(sorted(origSizes), sorted(randSizes))


class TestShuffleElementsBetweenTracksPool(unittest.TestCase):
    def setUp(self):
        '''Create a fake trackstructure containing empty tracks,
        this is only used to ensure the randomization pool knows there should be 3 input tracks.'''
        genomeAnchor = [0, 101]
        self.amountTracks = 3
        self.region = GenomeRegion('TestGenome', 'chr21', genomeAnchor[0], genomeAnchor[1])

        self.ts = TrackStructureV2()

        for i, segmentSet in enumerate([[]] * self.amountTracks):
            track = SampleTrack(SampleTV(segments=segmentSet, anchor=genomeAnchor))
            track.getUniqueKey = MagicMock(return_value=i)
            self.ts[str(i)] = SingleTrackTS(track, {})

        self.shufflePool = ShuffleElementsBetweenTracksPool(self.ts, self.region, False, None)


    def testGetProbabilities(self):
        '''Ensure the correct probabilities are returned in the different circumstances.'''
        self.assertEqual(self.shufflePool._getProbabilities(None, np.array([[], [], []]), np.array([[], [], []])), [1.0/3, 1.0/3, 1.0/3])
        self.assertEqual(self.shufflePool._getProbabilities(COVERAGE, np.array([[], [], []]), np.array([[], [], []])), [1.0/3, 1.0/3, 1.0/3])
        self.assertEqual(self.shufflePool._getProbabilities(NUMBER_OF_SEGMENTS, np.array([[], [], []]), np.array([[], [], []])), [1.0/3, 1.0/3, 1.0/3])
        self.assertEqual(self.shufflePool._getProbabilities(None, np.array([[1], [2], [3]]), np.array([[4], [5], [6]])), [1.0/3, 1.0/3, 1.0/3])
        self.assertEqual(self.shufflePool._getProbabilities(COVERAGE, np.array([[1], [2], [3]]), np.array([[7], [5], [6]])), [0.5, 0.25, 0.25])
        self.assertEqual(self.shufflePool._getProbabilities(NUMBER_OF_SEGMENTS, np.array([[1], [2, 3], [4]]), np.array([[4], [5, 6], [7]])), [0.25, 0.5, 0.25])

    def testGetOneTrackViewFromPool(self):
        '''Test if a valid trackview is returned by the pool'''
        self.assertIsInstance(self.shufflePool.getOneTrackViewFromPool(self.ts['1'].track, 1), TrackView)

    def testComputeRandomTrackSet(self):
        '''Test to see that there are no randomized tracksets when the pool is initiated,
        and random track sets are added after the pool has been called with a new randIndex'''
        self.assertEqual(self.shufflePool._randomTrackSets['starts'].keys(), [])
        randIndexes = [1, 2, 3]
        for randIndex in randIndexes:
            self.shufflePool.getOneTrackViewFromPool(self.ts['1'].track, randIndex)
            # Assert that there is a starts and ends array for every track
            self.assertEqual(len(self.shufflePool._randomTrackSets['starts'][randIndex]), self.amountTracks)
            self.assertEqual(len(self.shufflePool._randomTrackSets['ends'][randIndex]), self.amountTracks)
        self.assertEqual(self.shufflePool._randomTrackSets['starts'].keys(), randIndexes)

    def testSelectNonOverlappingRandomTrackIndex(self):
        for i in range(0, 100):
            self.assertEqual(self.shufflePool._selectNonOverlappingRandomTrackIndex([[10], [100], [100]], 20), 0)

