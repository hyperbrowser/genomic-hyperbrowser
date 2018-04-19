import os

import pytest

from proto.config.Config import SOURCE_CODE_BASE_DIR
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class CongloTestTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Run all pycolocstats tests"

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

    # @classmethod
    # def getOptionsBoxFirstKey(cls):
    #     return ['testChoice1', 'testChoice2', '...']
    #
    # @classmethod
    # def getOptionsBoxSecondKey(cls, prevChoices):
    #     return ''

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
        testsPath = os.path.abspath(os.path.join(SOURCE_CODE_BASE_DIR, 'tests', 'test_method.py'))
        print testsPath
        pytest.main([testsPath])

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
    #
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
