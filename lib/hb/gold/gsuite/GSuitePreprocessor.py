import os

from gold.gsuite.GSuiteAllTracksVisitor import GSuiteAllTracksVisitor
from gold.gsuite.GSuiteConstants import LOCAL, PRIMARY, UNKNOWN
from gold.gsuite.GSuiteRequirements import GSuiteRequirements
from gold.gsuite.GSuiteTrack import GSuiteTrack, HbGSuiteTrack
from third_party.Visitor import Visitor


class GSuitePreprocessor(GSuiteAllTracksVisitor):
    def __init__(self):
        GSuiteAllTracksVisitor.__init__(self, GSuiteTrackPreprocessor())


class GSuiteTrackPreprocessor(Visitor):
    @staticmethod
    def genericVisit(gSuiteTrack):
        gSuiteReq = GSuiteRequirements(allowedLocations=[LOCAL],
                                       allowedFileFormats=[PRIMARY, UNKNOWN])
        gSuiteReq.check(gSuiteTrack)
        assert gSuiteTrack.genome != UNKNOWN, 'A genome build must be selected for the track: ' + \
                                              gSuiteTrack.title

    def visitGalaxyGSuiteTrack(self, gSuiteTrack):
        if gSuiteTrack.hasExtraFileName():
            baseFileName = os.path.basename(gSuiteTrack.uriWithoutSuffix)
        else:
            baseFileName = gSuiteTrack.title

        doEncodeId = True

        return self._createPreprocessedGsuiteTrack(gSuiteTrack, baseFileName, doEncodeId)

    def _createPreprocessedGsuiteTrack(self, gSuiteTrack, baseFileName, doEncodeId, urlPrefix=None):
        from quick.application.ExternalTrackManager import ExternalTrackManager as ETM
        from gold.description.TrackInfo import TrackInfo

        self.genericVisit(gSuiteTrack)

        galaxyTN = ETM.constructGalaxyTnFromSuitedFn(
            gSuiteTrack.path, fileEnding=gSuiteTrack.suffix, name=baseFileName)
        trackName = ETM.getPreProcessedTrackFromGalaxyTN(
            gSuiteTrack.genome, galaxyTN, printErrors=False, printProgress=False,
            renameExistingTracksIfNeeded=False, doEncodeId=doEncodeId, urlPrefix=urlPrefix)

        trackType = TrackInfo(gSuiteTrack.genome, trackName).trackFormatName.lower()
        hbUri = HbGSuiteTrack.generateURI(trackName=trackName)

        return GSuiteTrack(hbUri, title=gSuiteTrack.title, trackType=trackType,
                           genome=gSuiteTrack.genome, attributes=gSuiteTrack.attributes,
                           comment=gSuiteTrack.comment)

    def visitFileGSuiteTrack(self, gSuiteTrack):
        # Hack to re-preprocess "empty" GSuites due to disk crash, in
        # concert with ConvertPreprocessedGSuiteToFileBasedPrimaryTool

        from proto.config.Config import URL_PREFIX
        from config.Config import ALLOW_GSUITE_FILE_PROTOCOL, EXT_RESULTS_PATH
        from quick.application.ExternalTrackManager import ExternalTrackManager as ETM
        from gold.description.TrackInfo import TrackInfo

        assert ALLOW_GSUITE_FILE_PROTOCOL

        resultsPathDirs = EXT_RESULTS_PATH.rstrip(os.path.sep).split(os.path.sep)
        curInstance = URL_PREFIX.strip('/')
        assert resultsPathDirs[-1] == curInstance
        resultsPathDirsNoInstance = os.path.sep.join(resultsPathDirs[:-1])

        assert gSuiteTrack.path.startswith(resultsPathDirsNoInstance)

        pathSplitted = gSuiteTrack.path.split(os.path.sep)
        instance = pathSplitted[len(resultsPathDirs) - 1]
        doEncodeId = instance == curInstance
        urlPrefix = instance

        baseFileName = gSuiteTrack.title

        return self._createPreprocessedGsuiteTrack(gSuiteTrack, baseFileName,
                                                   doEncodeId, urlPrefix)
