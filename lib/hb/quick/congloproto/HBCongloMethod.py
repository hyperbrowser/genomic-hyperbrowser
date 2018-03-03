import sys
import os

from collections import OrderedDict, namedtuple

from config.Config import HB_SOURCE_DATA_BASE_DIR
from conglomerate.core.types import SingleResultValue
from conglomerate.methods.interface import ColocMeasureOverlap
from conglomerate.methods.method import ManyVsManyMethod
from conglomerate.tools.job import Job
from gold.application.HBAPI import doAnalysis
from gold.gsuite import GSuiteParser
from gold.track.Track import Track
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import GlobalBinSource
from quick.statistic.StatFacades import TpRawOverlapStat


AnalysisObject = namedtuple('AnalysisObject', ['analysisSpec', 'binSource', 'tracks', 'genome'])


class HyperBrowser(ManyVsManyMethod):
    REF_TRACK_GSUITE_DIR = os.path.join(HB_SOURCE_DATA_BASE_DIR, 'conglomerate')

    def __init__(self):
        self._parsedResults = None
        self._genome = None
        self._queryTrackFiles = None
        self._refTrackFiles = None
        self._allowOverlaps = False
        self._colocStatistic = "ObservedVsExpectedStat"
        self._colocStatResultKey = 'SingleValExtractorStat'
        # self._randomizationAssumption = 'PermutedSegsAndIntersegsTrack_'
        self.preserveClumping(True)
        self._analyses = OrderedDict()
        self._results = None
        self._params = "Conglo Params not supported in HyperBrowser"
        self._trackTitleMappings = {}
        self._compatibilityState = True

    def _getToolName(self):
        return 'hb_conglo'

    def _getTool(self):
        raise NotImplementedError('Not supported by HB')

    def checkForAbsentMandatoryParameters(self):
        pass

    def setResultFilesDict(self, resultFilesDict):
        self._results = resultFilesDict
        self._ranSuccessfully = True

    def getResultFilesDict(self):
        return self._results

    def _setDefaultParamValues(self):
        pass

    def setGenomeName(self, genomeName):
        self._genome = genomeName.split('(')[-1].split(')')[0]
        self._binSource = GlobalBinSource(self._genome)

    def setChromLenFileName(self, chromLenFileName):
        pass

    def _setQueryTrackFileNames(self, trackFileList):
        # self._queryTracks = [self._getTrackFromFilename(trackFn) for trackFn in trackFnList]
        # self._queryTracks = [ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(self._genome, ['galaxy', 'bed', trackFn, 'dummy']) for trackFn in trackFnList]
        # trackFnList = []
        # for trackFile in trackFileList:
        #     self._addTrackTitleMapping(trackFile.path, trackFile.title)
        #     trackFnList.append(trackFile.path)
        # self._queryTracks = trackFnList
        self._queryTrackFiles = trackFileList

    def _setReferenceTrackFileNames(self, trackFileList):
        # trackFnList = []
        # for trackFile in trackFileList:
        #     if trackFile in ['prebuilt', 'LOLACore_170206']:
        #         refGsuiteFn = os.path.join(self.REF_TRACK_GSUITE_DIR, 'LOLACore_170206',
        #                                    'hg19', 'codex.gsuite')
        #         refGsuite = GSuiteParser.parse(refGsuiteFn)
        #         for track in refGsuite.allTracks():
        #             self._addTrackTitleMapping('/'.join(track.trackName), track.title)
        #             trackFnList.append(track.trackName)
        #     else:
        #         self._addTrackTitleMapping(trackFile.path, trackFile.title)
        #         trackFnList.append(trackFile.path)
        #
        # self._refTracks = trackFnList
        self._refTrackFiles = trackFileList
        # self._refTracks = [ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(self._genome, ['galaxy', 'bed', trackFn, 'dummy']) for trackFn in trackFnList]
        # self._refTracks = [self._getTrackFromFilename(trackFn) for trackFn in trackFnList]
        # self._refTracks = [Track(ExternalTrackManager.constructGalaxyTnFromSuitedFn(trackFn),
        #                          splitext(basename(trackFn))) for trackFn in trackFnList]

    def setAllowOverlaps(self, allowOverlaps):
        self._allowOverlaps = allowOverlaps

    def _parseResultFiles(self):
        pass

    def getPValue(self):
        pvals = OrderedDict()
        for trackTuple, result in self._results.iteritems():
            pval = result.getGlobalResult().get('P-value')
            if pval is None:
                pvals[trackTuple] = SingleResultValue(None, 'N/A')
            else:
                pvals[trackTuple] = \
                    SingleResultValue(self._getNumericFromStr(pval),
                                      self._getFormattedVal(self._getNumericFromStr(pval)))
        return self.getRemappedResultDict(pvals)

    def getTestStatistic(self):
        testStats = OrderedDict()
        for trackTuple, result in self._results.iteritems():
            testStat = float(self.getTestStatVal(result))
            svr = SingleResultValue(testStat, '<span title="' + \
                                    self.getTestStatDescr() \
                                    + '">' + self._getFormattedVal(testStat) + '</span>')
            testStats[trackTuple] = svr
        return self.getRemappedResultDict(testStats)

    def getTestStatVal(self, result):
        globalRes = result.getGlobalResult()
        print globalRes
        for key in [self._colocStatResultKey, 'TSMC_' + self._colocStatistic]:
            if key in globalRes:
                testStatVal = globalRes[key]
                break
        return testStatVal

    @classmethod
    def getTestStatDescr(cls):
        return 'Forbes coefficient: ratio of observed to expected overlap'

    def getFullResults(self, galaxyFn=None):
        from os import linesep
        fullResult = OrderedDict()

        if galaxyFn:
            resultPage = self._generateResultPage(galaxyFn)
            for trackTuple, result in self._results.iteritems():
                fullResult[trackTuple] = resultPage
        else:
            for trackTuple, result in self._results.iteritems():
                fullResult[trackTuple] = str(self.getTestStatVal(result)) + \
                             "\t" + str(result.getGlobalResult()['P-value']) + " <br>" + linesep
        return self.getRemappedResultDict(fullResult)

    def _generateResultPage(self, galaxyFn):
        from gold.result.ResultsViewer import ResultsViewerCollection

        resColl = ResultsViewerCollection(self._results.values(), galaxyFn,
                                          presCollectionType='standardnoplots')
        resultPage = GalaxyInterface.getHtmlBeginForRuns(galaxyFn)
        resultPage += GalaxyInterface.getHtmlForToggles(withRunDescription=True)
        resultPage += str(resColl)
        resultPage += GalaxyInterface.getHtmlEndForRuns()

        return resultPage

    def preserveClumping(self, preserve):
        if preserve:
            self._randomizationAssumption = \
                'PermutedSegsAndIntersegsTrack_:' \
                'Preserve segments (T2), segment lengths and inter-segment gaps (T1); ' \
                'randomize positions (T1) (MC)'
        else:
            self._randomizationAssumption = \
                'PermutedSegsAndSampledIntersegsTrack_:' \
                'Preserve segments (T2) and segment lengths (T1); randomize positions (T1) (MC)'

    def setRestrictedAnalysisUniverse(self, restrictedAnalysisUniverse):
        if restrictedAnalysisUniverse is not None:
            self.setNotCompatible()

    def setColocMeasure(self, colocMeasure):
        if isinstance(colocMeasure, ColocMeasureOverlap):
            self._colocStatistic = "TpRawOverlapStat"
        else:
            self.setNotCompatible()

    def setHeterogeneityPreservation(self, preservationScheme, fn=None):
        pass

    def setRuntimeMode(self, mode):
        if mode =='quick':
            self._runtimeMode = 'Quick and rough indication'
        elif mode == 'medium':
            self._runtimeMode = 'Moderate resolution of global p-value'
        elif mode == 'accurate':
            self._runtimeMode = 'Fixed 10 000 samples (slow)'
        else:
            raise Exception("Invalid mode")

    def _getAnalysisSpec(self):
        from gold.description.AnalysisList import REPLACE_TEMPLATES
        from gold.description.AnalysisDefHandler import AnalysisDefHandler

        analysisDefString = REPLACE_TEMPLATES[
                                '$MCFDR$'] + ' -> RandomizationManagerStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', self._runtimeMode)
        analysisSpec.addParameter('assumptions', self._randomizationAssumption)
        analysisSpec.addParameter('rawStatistic', self._colocStatistic)
        analysisSpec.addParameter('tail', 'more')
        analysisSpec.addParameter('H0:_', 'The segments of track 1 are located independently '
                                          'of the segments of track 2 with respect to overlap')
        analysisSpec.addParameter('H1_more:_', 'The segments of track 1 tend to overlap the '
                                               'segments of track 2')
        analysisSpec.addParameter('H1_less:_', 'The segments of track 1 tend to avoid overlapping '
                                               'the segments of track 2')
        analysisSpec.addParameter('H1_different:_', 'The locations of the segments of track 1 '
                                                    'are dependent on the locations of the '
                                                    'segments of track 2 with respect to overlap')
        return analysisSpec

    def _getAnalysisSpecNoPval(self):
        from gold.description.AnalysisDefHandler import AnalysisDefHandler
        analysisSpec = AnalysisDefHandler('-> GenericResultsCombinerStat')
        analysisSpec.addParameter('rawStatistics',
                                  '^'.join([self._colocStatistic, 'TpRawOverlapStat',
                                            'CountStat', 'CountElementStat']))
        return analysisSpec

    # def _getTrackFromFilename(self, filePath):
    #     import os
    #     import shutil
    #     from gold.util.CommonFunctions import convertTNstrToTNListFormat
    #     relFilePath = os.path.relpath(filePath)
    #     trackName = ':'.join(os.path.normpath(relFilePath).split(os.sep))
    #     # trackName = _convertTrackName(trackName)
    #     convertedTrackName = convertTNstrToTNListFormat(trackName, doUnquoting=True)
    #
    #     from gold.util.CommonFunctions import createOrigPath, ensurePathExists
    #     origFn = createOrigPath(self._genome, convertedTrackName, os.path.basename(filePath))
    #     if os.path.exists(origFn):
    #         shutil.rmtree(os.path.dirname(origFn))
    #     ensurePathExists(origFn)
    #     shutil.copy(filePath, origFn)
    #     os.chmod(origFn, 0664)
    #
    #     from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
    #     PreProcessAllTracksJob(self._genome, convertedTrackName).process()
    #     return Track(convertedTrackName, trackTitle=trackName.split(":")[-1])

    def createJobs(self, jobOutputDir):
        if self._refTrackFiles == ['prebuilt', 'LOLACore_170206']:
            refTracks = self._readGsuiteAndRegisterTracks('LOLACore_170206', 'codex.gsuite')
            refTrackPaths = [self._getPathVersionOfTrackName(rTrack) for rTrack in refTracks]
            analysisSpec = self._getAnalysisSpecNoPval()
        else:
            refTracks = [self._registerTrackFileAndProcess(refTrack)
                         for refTrack in self._refTrackFiles]
            refTrackPaths = [refTrack.path for refTrack in self._refTrackFiles]
            analysisSpec = self._getAnalysisSpec()

        for queryTrackFile in self._queryTrackFiles:
            qTrack = self._registerTrackFileAndProcess(queryTrackFile)
            for i, rTrack in enumerate(refTracks):
                self._analyses[(queryTrackFile.path, refTrackPaths[i])] = \
                    AnalysisObject(analysisSpec, self._binSource,
                                   [qTrack, rTrack], self._genome)
        return [HBJob(self._analyses)]

    def _registerTrackFileAndProcess(self, trackFile):
        self._addTrackTitleMapping(trackFile.path, trackFile.title)
        return self._processTrack(trackFile.path)

    def _readGsuiteAndRegisterTracks(self, trackIndex, trackCollection):
        refTracks = []

        refGsuiteFn = os.path.join(self.REF_TRACK_GSUITE_DIR, trackIndex,
                                   self._genome, trackCollection)
        refGsuite = GSuiteParser.parse(refGsuiteFn)
        for gsuiteTrack in refGsuite.allTracks():
            self._addTrackTitleMapping(self._getPathVersionOfTrackName(gsuiteTrack), gsuiteTrack.title)
            refTracks.append(Track(gsuiteTrack.trackName))

        return refTracks

    @staticmethod
    def _getPathVersionOfTrackName(track):
        return '/'.join(track.trackName)

    def _processTrack(self, trackFn):
        from os.path import splitext, basename
        storedStdOut = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        track = Track(ExternalTrackManager.getPreProcessedTrackFromGalaxyTN
                      (self._genome, ['galaxy', 'bed', trackFn, basename(trackFn)],
                       printErrors=False, printProgress=False),
                      splitext(basename(trackFn)))
        sys.stdout = storedStdOut
        return track

    @staticmethod
    def addRunDescriptionToResult(analysisObj, result):
        runDescription = GalaxyInterface.getRunDescription(
            analysisObj.tracks[0].trackName, analysisObj.tracks[1].trackName,
            analysisObj.analysisSpec.getDef(),
            analysisObj.genome + ':*', '*', analysisObj.genome,
            showBatchLine=False)
        runDescBox = GalaxyInterface.getRunDescriptionBox(runDescription)
        result.setRunDescription(runDescBox)


class HBJob(Job):
    def __init__(self, analyses):
        self._analyses = analyses

    def run(self):
        results = OrderedDict()
        for key, analysisObj in self._analyses.iteritems():
            result = doAnalysis(analysisObj.analysisSpec, analysisObj.binSource, analysisObj.tracks)
            HyperBrowser.addRunDescriptionToResult(analysisObj, result)
            results[key] = result
        return results
