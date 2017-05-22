#For doAnalysis
import collections
import logging
from gold.application.LogSetup import setupDebugModeAndLogging
from gold.application.StatRunner import AnalysisDefJob, StatJob

#For getTrackData
from gold.origdata.GESourceWrapper import GESourceWrapper
from gold.track.Track import Track, PlainTrack
from gold.track.GenomeRegion import GenomeRegion

#Include these in this name space, to allow them to be imported from this API module
from gold.track.TrackStructure import TrackStructureV2
from quick.application.UserBinSource import RegionIter, GlobalBinSource,\
    BinSource
from gold.description.AnalysisDefHandler import AnalysisDefHandler, AnalysisSpec
from gold.gsuite.GSuite import GSuite
from collections import OrderedDict
from quick.application.SignatureDevianceLogging import takes, returns
from gold.result import Results
from gold.application import GSuiteAPI
from gold.application.StatRunnerV2 import StatJobV2
from urllib import quote
from quick.util.CommonFunctions import silenceRWarnings, silenceNumpyWarnings, wrapClass

@takes((AnalysisSpec, AnalysisDefHandler, basestring), collections.Iterable, TrackStructureV2)
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

    # # if isinstance(tracks, TrackStructure):
    # #     pass
    # if len(tracks) > 2:
    #     from gold.util.CommonConstants import MULTIPLE_EXTRA_TRACKS_SEPARATOR
    #     analysisSpec.addParameter(
    #         'extraTracks',
    #         MULTIPLE_EXTRA_TRACKS_SEPARATOR.join(
    #             ['^'.join([quote(part) for part in x.trackName])
    #              for x in tracks[2:]]
    #         )
    #     )
    # job = AnalysisDefJob(analysisSpec.getDefAfterChoices(),
    #                      tracks[0].trackName,
    #                      tracks[1].trackName if len(tracks) > 1 else None,
    #                      analysisBins, galaxyFn=None)
    analysisDef = AnalysisDefHandler(analysisSpec.getDefAfterChoices())
    statClass = analysisDef._statClassList[0]
    validStatClass = wrapClass(statClass, keywords=analysisDef.getChoices(filterByActivation=True) )
    job = StatJob(analysisBins, trackStructure, validStatClass)
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


#@takes(list)
#@returns(list(tuple))
def getTrackCombinations(inputList):
    '''inputList is a list of tracks and/or GSuites. The return value of the method is each product element of the given input elements.'''
    expandedTrackList = [None] * len(inputList)
    for index, trackListElement in enumerate(inputList):
        if isinstance(trackListElement, GSuite):
            expandedTrackList[index] = [Track(gSuiteTrack.trackName) for gSuiteTrack in trackListElement.allTracks()]
        else:
            expandedTrackList[index] = [Track(trackListElement)]

    import itertools
    trackCombinations = itertools.product(expandedTrackList)
    return trackCombinations

#@takes(AnalysisSpec, BinSource, list)
#@returns(dict(tuple, Results))
def doAnalysisSupportingGsuite(analysisSpec, analysisBins, tracks):
    '''For each track combination (a tuple) run the given analysis.
        Return a dictionary of results, where the key is the tuple of tracks involved in the single analysis,
        and the value is the corresponding result'''
    trackCombinations = getTrackCombinations(tracks)
    results = OrderedDict()
    for trackCombination in trackCombinations:
        results[trackCombination] = doAnalysis(analysisSpec, analysisBins, trackCombination)
    return results

# @takes(AnalysisSpec, BinSource, GSuite)
# @returns(dict(tuple, Results))
def doAnalysisGSuitePairwise(analysisSpec, analysisBins, gSuite):
    '''
    For each pair of tracks in a GSuite run the analysis (analysisSpec).
    Returns an OrderedDict where the key is a tuple of track titles, the value is a Results object.
    '''
    results = OrderedDict()
    for trackPair in GSuiteAPI.generateAllTrackPairsInGSuite(gSuite):
        tracks = [Track(t.trackName) for t in trackPair]
        result = doAnalysis(analysisSpec, analysisBins, tracks)
        results[(t.title for t in trackPair)] = result

    return results
