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

class HBCongloMethod(ManyVsManyMethod):

    def __init__(self):
        self._parsedResults = None
        self._genome = None
        self._queryTracks = None
        self._refTracks = None
        self._queryTracksProcessed = None
        self._refTracksProcessed = None
        self._allowOverlaps = False
        self._colocStatistic = None
        self._randomizationAssumption = None
        self._analyses = OrderedDict()
        self._results = None


    def _getToolName(self):
        return 'hb_conglo'

    def _getTool(self):
        raise NotImplementedError('Not supported by HB')

    def createJobs(self):
        self._processTracks()
        for queryTrack in self._queryTracksProcessed:
            for refTrack in self._refTracksProcessed:
                self._analyses[(queryTrack.title, refTrack.title)] = AnalysisObject(self._getAnalysisSpec(),
                                                                                    self._binSource,
                                                                                    [queryTrack, refTrack])
        return [HBJob(self._analyses)]


    def setResultFilesDict(self, resultFilesDict):
        self._results = resultFilesDict

    def getResultFilesDict(self):
        raise NotImplementedError('Not supported by HB')

    def _setDefaultParamValues(self):
        pass

    def setGenomeName(self, genomeName):
        self._genome = genomeName.split('(')[-1].split(')')[0]
        self._binSource = GlobalBinSource(genomeName)

    def setChromLenFileName(self, chromLenFileName):
        pass

    def _setQueryTrackFileNames(self, trackFnList):
        # self._queryTracks = [self._getTrackFromFilename(trackFn) for trackFn in trackFnList]
        # self._queryTracks = [ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(self._genome, ['galaxy', 'bed', trackFn, 'dummy']) for trackFn in trackFnList]
        self._queryTracks = trackFnList

    def _setReferenceTrackFileNames(self, trackFnList):
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
        for trackTuple, result in self._results:
            pval = result.getGlobalResult()['Result']['P-value']
            pvals[trackTuple] = pval
        return pvals


    def getTestStatistic(self):
        testStats = OrderedDict()
        for trackTuple, result in self._results:
            pval = result.getGlobalResult()['Result']['TSMC_' + self._colocStatistic]
            testStats[trackTuple] = pval
        return testStats

    def getFullResults(self):
        return self._results

    def preserveClumping(self, preserve):
        if preserve:
            self._randomizationAssumption = 'PermutedSegsAndIntersegsTrack_'
        else:
            self._randomizationAssumption = 'PermutedSegsAndSampledIntersegsTrack_'

    def setRestrictedAnalysisUniverse(self, restrictedAnalysisUniverse):
        pass

    def setColocMeasure(self, colocMeasure):

        if isinstance(colocMeasure, ColocMeasureOverlap):
            self._colocStatistic = TpRawOverlapStat
        else:
            raise AssertionError('Overlap is the only supported measure')

    def setHeterogeneityPreservation(self, preservationScheme, fn=None):
        pass

    def _getAnalysisSpec(self):

        from gold.description.AnalysisList import REPLACE_TEMPLATES
        from gold.description.AnalysisDefHandler import AnalysisDefHandler

        analysisDefString = REPLACE_TEMPLATES[
                                '$MCFDR$'] + ' -> RandomizationManagerStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', 'mediumGlobal')
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

    def _processTracks(self):
        self._queryTracksProcessed = \
            [ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(self._genome,
                                                                   ['galaxy', 'bed', trackFn, 'qdummy'])
             for trackFn in self._queryTracks]

        self._refTracksProcessed = \
            [ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(self._genome,
                                                                   ['galaxy', 'bed', trackFn, 'rdummy'])
             for trackFn in self._refTracks]


class HBJob(Job):

    def __init__(self, analyses):
        self._analyses = analyses

    def run(self):
        results = OrderedDict()
        for analysisObj in self._analyses:
            results[tuple(analysisObj.tracks)] = doAnalysis(analysisObj.analysisSpec, analysisObj.binSource, analysisObj.tracks)
        return results
