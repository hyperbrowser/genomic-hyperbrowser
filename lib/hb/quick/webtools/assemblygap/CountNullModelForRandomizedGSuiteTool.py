from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool, GeneralGuiToolMixin


class CountNullModelForRandomizedGSuiteTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Count null model for randomized gSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select orginal gSuite', 'orgGsuite'),
                ('Select column from orginal gSuite', 'orgCol'),
                ('Second randomized gSuite', 'randGsuite'),
                ('Second column from randomized gSuite', 'randCol')]


    @classmethod
    def getOptionsBoxOrgGsuite(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxOrgCol(cls, prevChoices):
        if prevChoices.orgGsuite:
            first = getGSuiteFromGalaxyTN(prevChoices.orgGsuite)
            attributeList = ['title'] + first.attributes
            return attributeList
        else:
            return

    @classmethod
    def getOptionsBoxRandGsuite(cls, prevChoices):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxRandCol(cls, prevChoices):
        if prevChoices.randGsuite:
            first = getGSuiteFromGalaxyTN(prevChoices.randGsuite)
            attributeList = ['title'] + first.attributes
            return attributeList
        else:
            return

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        print 'Executing...'

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
