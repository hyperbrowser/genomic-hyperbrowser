# For doAnalysis
import collections
from urllib import quote
from gold.application.StatRunner import StatJob

# For getTrackData
from gold.origdata.GESourceWrapper import GESourceWrapper
from gold.track.Track import Track, PlainTrack
from gold.track.GenomeRegion import GenomeRegion

# Include these in this name space, to allow them to be imported from this API module
from gold.track.TrackStructure import TrackStructureV2
from quick.application.UserBinSource import RegionIter, GlobalBinSource, \
    BinSource
from gold.description.AnalysisDefHandler import AnalysisDefHandler, AnalysisSpec
from gold.gsuite.GSuite import GSuite
from collections import OrderedDict
from quick.application.SignatureDevianceLogging import takes
from gold.result import Results
from gold.application import GSuiteAPI
from quick.deprecated.StatRunner import AnalysisDefJob
from quick.util.CommonFunctions import silenceRWarnings, silenceNumpyWarnings, wrapClass


@takes((AnalysisSpec, AnalysisDefHandler, basestring), collections.Iterable,
       (TrackStructureV2, tuple, list))
def doAnalysis(analysisSpec, analysisBins, trackStructure):
    '''Performs an analysis,
    as specified by analysisSpec object,
    in each bin specified by analysisBins,
    on data sets specified in tracks.

    Typical usage:
    analysisSpec = AnalysisSpec(AvgSegLenStat)
    analysisSpec.addParameter("withOverlaps","no")
    analysisBins = GlobalBinSource('hg18')
    tracks = [ Track(['Genes and gene subsets','Genes','Refseq']) ]
    results = doAnalysis(analysisSpec, analysisBins, tracks)
    '''

    # TODO: handle multiple tracks analysis
    # assert len(tracks) in [1,2] #for now..
    # in an API setting, exceptions should not generally be hidden.
    # Maybe this should be optional.
    # setupDebugModeAndLogging()
    silenceRWarnings()
    silenceNumpyWarnings()

    if isinstance(trackStructure, TrackStructureV2):
        analysisDef = AnalysisDefHandler(analysisSpec.getDefAfterChoices())
        statClass = analysisDef._statClassList[0]
        validStatClass = wrapClass(statClass, keywords=analysisDef.getChoices(filterByActivation=True))
        job = StatJob(analysisBins, trackStructure, validStatClass)
    else:
        tracks = trackStructure
        if len(tracks) > 2:
            from gold.util.CommonConstants import MULTIPLE_EXTRA_TRACKS_SEPARATOR
            analysisSpec.addParameter(
                'extraTracks',
                MULTIPLE_EXTRA_TRACKS_SEPARATOR.join(
                    ['^'.join([quote(part) for part in x.trackName])
                     for x in tracks[2:]]
                )
            )
        job = AnalysisDefJob(analysisSpec.getDefAfterChoices(),
                             tracks[0].trackName,
                             tracks[1].trackName if len(tracks) > 1 else None,
                             analysisBins, galaxyFn=None)

    res = job.run(printProgress=False)  # printProgress should be optional?
    return res


# @sdl.takes(Track, GenomeRegion)
# @sdl.returns(TrackView)
def getTrackData(track, region):
    '''Gets data of specified track in specified region, in the form of a TrackView-object.
    The returned TrackView-object supports iteration of TrackElements (having start-location, end-location, and more)
    as well as having methods for getting vectors of all start-locations, all end-locations, and more.
    Typical usage:
    track = PlainTrack(['Genes and gene subsets','Genes','Refseq'])
    region = GenomeRegion('hg18','chr1',1000,900000)
    trackView = getTrackData(track, region)
    '''
    return track.getTrackView(region)
