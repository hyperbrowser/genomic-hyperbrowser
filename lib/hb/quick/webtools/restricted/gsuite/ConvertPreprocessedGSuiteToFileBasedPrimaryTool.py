from gold.gsuite import GSuiteConstants, GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack, FileGSuiteTrack, registerGSuiteTrackClass
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.application.ExternalTrackManager import ExternalTrackManager as ETM


class ConvertPreprocessedGSuiteToFileBasedPrimaryTool(GeneralGuiTool, GenomeMixin):
    GSUITE_MIN_TRACK_COUNT = 1

    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_TRACK_TYPES = []

    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PRIMARY
    GSUITE_OUTPUT_TRACK_TYPE = ''

    GSUITE_DESCRIPTION = ', converted from preprocessed gsuite'

    @classmethod
    def getToolName(cls):
        return "Converts a preprocessed GSuite into a primary GSuite with local file paths (not secure)"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite file from history:', 'gsuite')] + \
               GenomeMixin.getInputBoxNamesForGenomeSelection()

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxGsuite(cls):
        return '__history__', GSuiteConstants.GSUITE_SUFFIX

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']
    #
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     pass

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        inGSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        if choices.genome != inGSuite.genome:
            inGSuite.setGenomeOfAllTracks(choices.genome)

        registerGSuiteTrackClass(FileGSuiteTrack)

        outGSuite = GSuite()

        for track in inGSuite.allTracks():
            origGalaxyTN = ETM.createGalaxyTnFromExternalTn(track.trackName)

            uri = FileGSuiteTrack.generateURI(path=ETM.extractFnFromGalaxyTN(origGalaxyTN),
                                              suffix=ETM.extractFileSuffixFromGalaxyTN(origGalaxyTN))
            newTrack = GSuiteTrack(uri,
                                   title=track.title,
                                   trackType=track.trackType,
                                   genome=track.genome,
                                   attributes=track.attributes)
            outGSuite.addTrack(newTrack)

        GSuiteComposer.composeToFile(outGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('Converts a preprocessed GSuite into a primary GSuite with local file paths')

        core.divider()
        core.paragraph(str(HtmlCore().highlight('NOTE: SHOULD NOT BE MADE PUBLIC FOR SECURITY '
                                                'REASONS.')))

        cls._addGSuiteFileDescription(
            core,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
            outputLocation=cls.GSUITE_OUTPUT_LOCATION,
            outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
            outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
            errorFile=False,
            minTrackCount=cls.GSUITE_MIN_TRACK_COUNT)

        return str(core)
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False

    @classmethod
    def getOutputFormat(cls, choices):
        return 'gsuite'

    @classmethod
    def getOutputName(cls, choices=None):
        from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
        return getGSuiteHistoryOutputName('primary',
                                          description=cls.GSUITE_DESCRIPTION,
                                          datasetInfo=choices.gsuite)
