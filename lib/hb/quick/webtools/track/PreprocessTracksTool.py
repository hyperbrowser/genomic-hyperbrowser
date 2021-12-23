import re
import sys

from config.DebugConfig import DebugConfig
from gold.util.CustomExceptions import PreprocessWarning, PreprocessError
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.extra.StandardizeTrackFiles import PlainMover
from quick.util.CommonFunctions import stdout_redirector
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin


class PreprocessTracksTool(GeneralGuiTool, DebugMixin):
    MOVE_TO_PARSING_ERROR_CHOICE = "Move files to parsing error tree"
    DO_NOTHING_CHOICE = "Ignore"

    @classmethod
    def getToolName(cls):
        return "Preprocess tracks"

    @classmethod
    def getInputBoxNames(cls):
        return [('Genome build:', 'genome'),
                ('Standardized track', 'track'),
                ('If any errors: ', 'parsingError')] +\
                cls.getInputBoxNamesForDebug()

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxGenome(cls):
        return '__genome__'

    @classmethod
    def getOptionsBoxTrack(cls, prevChoices):
        return '__track__', 'standardized'

    @classmethod
    def getOptionsBoxParsingError(cls, prevChoices):
        return [cls.MOVE_TO_PARSING_ERROR_CHOICE, cls.DO_NOTHING_CHOICE]

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
        cls._setDebugModeIfSelected(choices, galaxyFn)

        with stdout_redirector(open(galaxyFn, "w", 0)):
            core = HtmlCore()
            core.append(GalaxyInterface.getHtmlBeginForRuns(galaxyFn))
            core.append(GalaxyInterface.getHtmlForToggles(withRunDescription=False))
            core.styleInfoBegin(styleClass='debug')
            core.paragraph(
                'GalaxyInterface.startPreProcessing({}, {}, {})'.format(
                    choices.genome, choices.track, username)
            )
            print core

            if choices.parsingError == cls.MOVE_TO_PARSING_ERROR_CHOICE:
                finished = False
                while not finished:
                    DebugConfig.PASS_ON_PREPROCESS_EXCEPTIONS = True
                    try:
                        GalaxyInterface.startPreProcessing(choices.genome, choices.track, username)
                        finished = True
                    except (PreprocessWarning, PreprocessError) as e:
                        print e
                        match = re.search("trackName=\"([^\"]+)\"", str(e))
                        if match:
                            trackName = match.group(1).split(':')
                            PlainMover().parseFiles(choices.genome, trackName, direction='std_to_error')
            else:  # cls.DO_NOTHING_CHOICE
                GalaxyInterface.startPreProcessing(choices.genome, choices.track, username)

            core = HtmlCore()
            core.styleInfoEnd()
            core.script('done = true;')
            core.end()
            print core

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.genome:
            return "Please select a reference genome"

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
        core = HtmlCore()
        core.paragraph("This is a simple tool for preprocessing track files in the HyperBrowser track repository. "
                       "Please select a track directory from the standarized tracks file tree. ")
        core.divider()
        core.descriptionLine("Recursion",
                             "Directories can be selected at any level. The preprocessor will recursively visit all "
                             "sub-directories of the selected directory")
        core.descriptionLine("Track file merge",
                             "All track files within a directory will be merged together as one track (under the "
                             "assumption that all files are of the same track type).")
        return str(core)

    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None

    @classmethod
    def isDebugMode(cls):
        return True

    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'

    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
