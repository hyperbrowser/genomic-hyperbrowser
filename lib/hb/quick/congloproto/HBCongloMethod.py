from collections import OrderedDict, namedtuple

from conglomerate.methods.interface import ColocMeasureOverlap
from conglomerate.methods.method import ManyVsManyMethod
from conglomerate.tools.job import Job
from gold.application.HBAPI import doAnalysis
from gold.track.Track import Track
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.UserBinSource import GlobalBinSource
from quick.statistic.StatFacades import TpRawOverlapStat


AnalysisObject = namedtuple('AnalysisObject', ['analysisSpec', 'binSource', 'tracks'])

class HyperBrowser(ManyVsManyMethod):

    def __init__(self):
        self._parsedResults = None
        self._genome = None
        self._queryTracks = None
        self._refTracks = None
        self._allowOverlaps = False
        self._colocStatistic = "TpRawOverlapStat"
        self._randomizationAssumption = 'PermutedSegsAndIntersegsTrack_'
        self._analyses = OrderedDict()
        self._results = None
        self._params = "Conglo Params not supported in HyperBrowser"
        self._trackTitleMappings = {}


    def _getToolName(self):
        return 'hb_conglo'

    def _getTool(self):
        raise NotImplementedError('Not supported by HB')

    def checkForAbsentMandatoryParameters(self):
        pass

    def createJobs(self):
        for queryTrack in self._queryTracks:
            qTrack = self._processTrack(queryTrack)
            for refTrack in self._refTracks:
                rTrack = self._processTrack(refTrack)
                self._analyses[(queryTrack, refTrack)] = AnalysisObject(self._getAnalysisSpec(),
                                                                                    self._binSource,
                                                                                    [qTrack, rTrack])
        return [HBJob(self._analyses)]


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
        trackFnList = []
        for trackFile in trackFileList:
            self._addTrackTitleMapping(trackFile.path, trackFile.title)
            trackFnList.append(trackFile.path)
        self._queryTracks = trackFnList

    def _setReferenceTrackFileNames(self, trackFileList):
        trackFnList = []
        for trackFile in trackFileList:
            self._addTrackTitleMapping(trackFile.path, trackFile.title)
            trackFnList.append(trackFile.path)

        self._refTracks = trackFnList
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
            pval = result.getGlobalResult()['P-value']
            pvals[trackTuple] = '<%.4f' % pval
        return self.getRemappedResultDict(pvals)


    def getTestStatistic(self):
        testStats = OrderedDict()
        for trackTuple, result in self._results.iteritems():
            testStat = float(result.getGlobalResult()['TSMC_' + self._colocStatistic]) / result.getGlobalResult()['MeanOfNullDistr']
            testStats[trackTuple] = '<span title="ratio of observed/expected">' + ('%.2f' % testStat) + '</span>'
        return self.getRemappedResultDict(testStats)

    def getFullResults(self):
        from os import linesep
        fullResult = OrderedDict()
        for trackTuple, result in self._results.iteritems():
            fullResult[trackTuple] = str(result.getGlobalResult()['TSMC_' + self._colocStatistic]) + \
                          "\t" + str(result.getGlobalResult()['P-value']) + " <br>" + linesep
        return self.getRemappedResultDict(fullResult)

    def preserveClumping(self, preserve):
        if preserve:
            self._randomizationAssumption = 'PermutedSegsAndIntersegsTrack_'
        else:
            self._randomizationAssumption = 'PermutedSegsAndSampledIntersegsTrack_'

    def setRestrictedAnalysisUniverse(self, restrictedAnalysisUniverse):
        assert restrictedAnalysisUniverse is None, restrictedAnalysisUniverse


    def setColocMeasure(self, colocMeasure):

        if isinstance(colocMeasure, ColocMeasureOverlap):
            self._colocStatistic = "TpRawOverlapStat"
        else:
            raise AssertionError('Overlap is the only supported measure')

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
            raise

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
        return analysisSpec

    def _getTrackFromFilename(self, filePath):
        import os
        import shutil
        from gold.util.CommonFunctions import convertTNstrToTNListFormat
        relFilePath = os.path.relpath(filePath)
        trackName = ':'.join(os.path.normpath(relFilePath).split(os.sep))
        # trackName = _convertTrackName(trackName)
        convertedTrackName = convertTNstrToTNListFormat(trackName, doUnquoting=True)

        from gold.util.CommonFunctions import createOrigPath, ensurePathExists
        origFn = createOrigPath(self._genome, convertedTrackName, os.path.basename(filePath))
        if os.path.exists(origFn):
            shutil.rmtree(os.path.dirname(origFn))
        ensurePathExists(origFn)
        shutil.copy(filePath, origFn)
        os.chmod(origFn, 0664)

        from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob
        PreProcessAllTracksJob(self._genome, convertedTrackName).process()
        return Track(convertedTrackName, trackTitle=trackName.split(":")[-1])

    def _processTrack(self, trackFn):
        from os.path import splitext, basename
        return Track(ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(self._genome,
                                                                    ['galaxy', 'bed', trackFn, 'dummy'],
								    printErrors=False, printProgress=False),
                                                                    splitext(basename(trackFn)))


class HBJob(Job):

    def __init__(self, analyses):
        self._analyses = analyses

    def run(self):
        results = OrderedDict()
        for key, analysisObj in self._analyses.iteritems():
            results[key] = doAnalysis(analysisObj.analysisSpec, analysisObj.binSource, analysisObj.tracks)
        return results
