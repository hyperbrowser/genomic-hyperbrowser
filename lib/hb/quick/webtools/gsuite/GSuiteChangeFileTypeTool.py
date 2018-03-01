from collections import OrderedDict

from gold.application.DataTypes import getSupportedFileSuffixes
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class GSuiteChangeFileTypeTool(GeneralGuiTool):
    GSUITE_ALLOWED_LOCATIONS = []  # [] is any value is allowed
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PRIMARY]  # [] is any value is allowed
    GSUITE_ALLOWED_TRACK_TYPES = []  # [] is any value is allowed

    SELECT_FILE_TYPE = '--- Select file type ---'

    OUTPUT_DESCRIPTION = ', file type changed'

    @classmethod
    def getToolName(cls):
        return "Change file type of primary tracks in a GSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite', 'gsuite'),
                ('Select file suffixes (from the selected GSuite file) to modify', 'suffixes'),
                ('Select new supported file type', 'fileType')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxGsuite(cls):
        return '__history__', 'gsuite'

    @classmethod
    def getOptionsBoxSuffixes(cls, prevChoices):
        if prevChoices.gsuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            suffixes = set(track.suffix for track in gSuite.allTracks())
            return OrderedDict([(suffix, False) for suffix in sorted(suffixes)])

    @classmethod
    def getOptionsBoxFileType(cls, prevChoices):
        if prevChoices.gsuite:
            return [cls.SELECT_FILE_TYPE] + getSupportedFileSuffixes()

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        outGsuite = GSuite()

        suffixes = set(suffix for suffix, selected in choices.suffixes.iteritems() if selected)
        for track in gSuite.allTracks():
            if track.suffix in suffixes:
                newTrack = GSuiteTrack(
                    track.uriWithoutSuffix + ';' + choices.fileType,
                    title=track.title,
                    fileFormat=track.fileFormat,
                    trackType=track.trackType,
                    genome=track.genome,
                    attributes=track.attributes
                )
                outGsuite.addTrack(newTrack)
            else:
                outGsuite.addTrack(track)

        print>>open(galaxyFn, 'w'), outGsuite

    @classmethod
    def validateAndReturnErrors(cls, choices):
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements(
            gSuite,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES
        )

        if errorString:
            return errorString

        if choices.suffixes and not any(chosen for chosen in choices.suffixes.values()):
            return 'Please select at least one of the file suffixes present in the ' \
                   'selected GSuite.'

        if not choices.fileType or choices.fileType == cls.SELECT_FILE_TYPE:
            return 'Please select a supported file type to change the tracks into.'

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

    @classmethod
    def getToolDescription(cls):
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('In some cases, the suffix of a track is not present, or the incorrect '
                       'to use in order to preprocess a GSuite. This might be obvious from '
                       'error messages for failed tracks after preprocessing. For instance '
                       'a track of type BedGraph might be mistakenly denoted as BED.')

        core.paragraph('This tool changes all tracks in a GSuite of some file type (with any '
                       'of the user-selected suffixes) to a particular file type supported '
                       'by the GSuite preprocessing step.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES)

        cls._addGSuiteFileDescription(core,
                                     alwaysShowRequirements=True)

        return str(core)

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
    def getOutputName(cls, choices):
        return getGSuiteHistoryOutputName('primary', cls.OUTPUT_DESCRIPTION, choices.gsuite)

