from conglomerate.methods.method import OneVsManyMethod
from conglomerate.tools.constants import HB_TOOL_NAME
from conglomerate.tools.job import Job
from gold.application import HBAPI


class HBCongloMethod(OneVsManyMethod):

    def __init__(self):
        self._parsedResults = None
        self._genome = None
        self._queryTrack = None
        self._refTracks = None
        self._analysisList = []
        self._allowOverlaps = False

    def _getToolName(self):
        return HB_TOOL_NAME

    def _getTool(self):
        raise NotImplementedError('Not supported by HB')

    def createJobs(self):
        pass

    def setResultFilesDict(self, resultFilesDict):
        raise NotImplementedError('Not supported by HB')

    def getResultFilesDict(self):
        raise NotImplementedError('Not supported by HB')

    def _setDefaultParamValues(self):
        pass

    def setGenomeName(self, genomeName):
        self._genome = genomeName

    def setChromLenFileName(self, chromLenFileName):
        pass

    def _setQueryTrackFileName(self, trackFn):
        self._queryTrack = PlainTrack(ExternalTrackManager.constructGalaxyTnFromSuitedFn(trackFn))

    def _setReferenceTrackFileNames(self, trackFnList):
        self._refTracks = [PlainTrack(ExternalTrackManager.constructGalaxyTnFromSuitedFn(trackFn)) for trackFn in trackFnList]

    def setAllowOverlaps(self, allowOverlaps):
        self._allowOverlaps = allowOverlaps

    def _parseResultFiles(self):
        pass

    def getPValue(self):
        pass

    def getTestStatistic(self):
        pass

    def getFullResults(self):
        pass

    def preserveClumping(self, preserve):
        pass

    def setRestrictedAnalysisUniverse(self, restrictedAnalysisUniverse):
        pass

    def setColocMeasure(self, colocMeasure):
        pass

    def setHeterogeneityPreservation(self, preservationScheme, fn=None):
        pass


class HBJob(Job):
    def run(self):
        pass

    def __init__(self, analysesList, binSource, tracks):
        pass