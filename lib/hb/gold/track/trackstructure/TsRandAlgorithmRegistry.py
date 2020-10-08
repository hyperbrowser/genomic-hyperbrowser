import inspect

from collections import namedtuple, OrderedDict

from gold.track.RandTrackBasedTrackViewProvider import \
    (PermutedSegsAndIntersegsTrackViewProvider,
     PermutedSegsAndSampledIntersegsTrackViewProvider)
from gold.track.ShuffleElementsBetweenTracksTvProvider import \
    (SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider,
     CoveragePreservedShuffleElementsBetweenTracksTvProvider,
     ShuffleElementsBetweenTracksTvProvider)
from gold.track.trackstructure.random.ShuffleElementsBetweenTracksAndBinsTvProvider import \
    ShuffleElementsBetweenTracksAndBinsTvProvider
from gold.track.trackstructure.random.TrackDataStorageRandAlgorithm import \
    CollisionDetectionTracksAndBinsRandAlgorithm
from third_party.typecheck import takes


WITHIN_TRACKS_CATEGORY = u'Within tracks'

BETWEEN_TRACKS_CATEGORY = u'Between tracks'

SHUFFLE_BETWEEN_TRACKS_AND_BINS_STR = u'Shuffle between tracks and bins, ' \
                                      u'possibly avoiding segments from a specified track'

SHUFFLE_BETWEEN_TRACKS_PRESERVE_COVERAGE_STR = u'Shuffle between tracks, ' \
                                               u'preserve base pair coverage per track'

SHUFFLE_BETWEEN_TRACKS_PRESERVE_COUNT_STR = u'Shuffle between tracks, ' \
                                            u'preserve number of segments per track'

SHUFFLE_BETWEEN_TRACKS_STR = u'Shuffle between tracks'

PERMUTED_SEGS_AND_INTERSEGS_STR = u'Permute segments and inter-segment regions ' \
                                  u'(size of inter-segment regions remains constant)'

PERMUTED_SEGS_AND_SAMPLED_INTERSEGS_STR = u'Permute segments and sampled inter-segment regions ' \
                                          u'(size of inter-segment regions is random)'

RandAlgorithmSpec = namedtuple('RandAlgorithmSpec', ('trackViewProviderCls', 'randAlgorithmCls'))


EXCLUDED_TS_ARG = 'excludedTS'

BIN_SOURCE_ARG = 'binSource'


# IMPORTANT: if extra algorithms are added to this dict, add them after the existing algorithms!
_RAND_ALGORITHM_DICT_WITHIN_TRACKS = OrderedDict([
    (PERMUTED_SEGS_AND_INTERSEGS_STR,
     RandAlgorithmSpec(PermutedSegsAndIntersegsTrackViewProvider, None)),
    (PERMUTED_SEGS_AND_SAMPLED_INTERSEGS_STR,
     RandAlgorithmSpec(PermutedSegsAndSampledIntersegsTrackViewProvider, None))
])


# IMPORTANT: if extra algorithms are added to this dict, add them after the existing algorithms!
_RAND_ALGORITHM_DICT_BETWEEN_TRACKS = OrderedDict([
    (SHUFFLE_BETWEEN_TRACKS_STR,
     RandAlgorithmSpec(ShuffleElementsBetweenTracksTvProvider, None)),
    (SHUFFLE_BETWEEN_TRACKS_PRESERVE_COUNT_STR,
     RandAlgorithmSpec(SegmentNumberPreservedShuffleElementsBetweenTracksTvProvider, None)),
    (SHUFFLE_BETWEEN_TRACKS_PRESERVE_COVERAGE_STR,
     RandAlgorithmSpec(CoveragePreservedShuffleElementsBetweenTracksTvProvider, None)),
    (SHUFFLE_BETWEEN_TRACKS_AND_BINS_STR,
     RandAlgorithmSpec(ShuffleElementsBetweenTracksAndBinsTvProvider,
                       CollisionDetectionTracksAndBinsRandAlgorithm))
])


_RAND_ALGORITHM_REGISTRY = OrderedDict([
    (WITHIN_TRACKS_CATEGORY, _RAND_ALGORITHM_DICT_WITHIN_TRACKS),
    (BETWEEN_TRACKS_CATEGORY, _RAND_ALGORITHM_DICT_BETWEEN_TRACKS)
])


def getCategories():
    return _RAND_ALGORITHM_REGISTRY.keys()


@takes(basestring)
def getAlgorithmList(category):
    return _RAND_ALGORITHM_REGISTRY[category].keys()


@takes(basestring)
def getTvProviderClsFromName(tvProviderClsName):
    for category in getCategories():
        for algSpec in _RAND_ALGORITHM_REGISTRY[category].values():
            if tvProviderClsName == algSpec.trackViewProviderCls.__name__:
                return algSpec.trackViewProviderCls
    else:
        raise KeyError('TrackViewProvider class named "{}" not found.'.format(tvProviderClsName))

@takes(basestring, basestring)
def getRequiredArgsForAlgorithm(category, algorithm):
    argSpec = _getArgSpecForAlgorithmInit(category, algorithm)
    if argSpec:
        return argSpec.args[1:-len(argSpec.defaults)]
    else:
        return []


@takes(basestring, basestring)
def getKwArgsForAlgorithm(category, algorithm):
    argSpec = _getArgSpecForAlgorithmInit(category, algorithm)
    if argSpec:
        numKwArgs = len(argSpec.defaults)
        return OrderedDict(zip(argSpec.args[-numKwArgs:], argSpec.defaults))
    else:
        return OrderedDict()


def _getArgSpecForAlgorithmInit(category, algorithm):
    randAlgSpec = _RAND_ALGORITHM_REGISTRY[category][algorithm]
    randAlgCls = randAlgSpec.randAlgorithmCls

    if randAlgCls:
        argSpec = inspect.getargspec(randAlgCls.__init__)
        return argSpec


@takes(basestring, basestring)
def createTrackViewProvider(category, algorithm, *args, **kwArgs):
    randAlgSpec = _RAND_ALGORITHM_REGISTRY[category][algorithm]
    if randAlgSpec.randAlgorithmCls:
        return randAlgSpec.trackViewProviderCls(
            randAlgorithm=randAlgSpec.randAlgorithmCls(*args, **kwArgs)
        )
    else:
        return randAlgSpec.trackViewProviderCls()


def createDefaultTrackViewProvider():
    return PermutedSegsAndIntersegsTrackViewProvider()
