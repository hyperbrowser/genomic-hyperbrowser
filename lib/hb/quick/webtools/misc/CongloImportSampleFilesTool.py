import os

import shutil

from config.Config import GALAXY_TOOL_DATA_PATH
from proto.HtmlCore import HtmlCore
from quick.util.CommonFunctions import getFileSuffix
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class CongloImportSampleFilesTool(GeneralGuiTool):
    SAMPLE_DATA_PATH = os.path.join(GALAXY_TOOL_DATA_PATH, 'conglomerate', 'sampledata')
    SAMPLE_FILES = sorted(os.listdir(SAMPLE_DATA_PATH))

    @classmethod
    def getToolName(cls):
        return "Import sample files into history"

    @classmethod
    def getInputBoxNames(cls):
        return []

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None
    #
    # @classmethod
    # def getOptionsBoxFirstKey(cls):
    #     return None
    #
    # @classmethod
    # def getOptionsBoxSecondKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']

    @classmethod
    def getExtraHistElements(cls, choices):
        from proto.tools.GeneralGuiTool import HistElement
        return [HistElement(sampleBaseFn,
                            getFileSuffix(sampleBaseFn),
                            cls._createLabel(sampleBaseFn))
                for sampleBaseFn in cls.SAMPLE_FILES]

    @classmethod
    def _createLabel(cls, sampleBaseFn):
        return sampleBaseFn[2:].replace('_', ' ')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        for sampleBaseFn in cls.SAMPLE_FILES:
            historyFn = cls.extraGalaxyFn[sampleBaseFn]
            shutil.copy(os.path.join(cls.SAMPLE_DATA_PATH, sampleBaseFn), historyFn)

        core = HtmlCore()
        core.begin()
        core.header('The following sample data files have been added to your history:')
        core.unorderedList([cls._createLabel(sampleBaseFn) for sampleBaseFn in cls.SAMPLE_FILES])
        core.end()

        print>>open(galaxyFn, 'w'), str(core)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None

    @classmethod
    def isPublic(cls):
        return True

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
    #     return False
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
    # @classmethod
    # def getToolDescription(cls):
    #     return ''
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
        return 'customhtml'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
