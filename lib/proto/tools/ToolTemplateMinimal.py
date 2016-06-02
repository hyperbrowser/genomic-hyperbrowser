from proto.tools.GeneralGuiTool import GeneralGuiTool


class ToolTemplate(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Tool not yet in use"

    @staticmethod
    def getInputBoxNames():
        return [('First header', 'firstKey'),
                ('Second Header', 'secondKey')]

    # @staticmethod
    # def getInputBoxOrder():
    #     return None
    #
    # @staticmethod
    # def getInputBoxGroups(choices=None):
    #     return None

    @staticmethod
    def getOptionsBoxFirstKey():
        return ['testChoice1', 'testChoice2', '...']

    @staticmethod
    def getOptionsBoxSecondKey(prevChoices):
        return ''

    # @staticmethod
    # def getInfoForOptionsBoxKey(prevChoices):
    #     return None
    #
    # @staticmethod
    # def getDemoSelections():
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return None

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        print 'Executing...'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    # @staticmethod
    # def getSubToolClasses():
    #     return None
    #
    # @staticmethod
    # def isPublic():
    #     return False
    #
    # @staticmethod
    # def isRedirectTool():
    #     return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #     return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDynamic():
    #     return True
    #
    # @staticmethod
    # def getResetBoxes():
    #     return []
    #
    # @staticmethod
    # def getToolDescription():
    #     return ''
    #
    # @staticmethod
    # def getToolIllustration():
    #     return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #     return None
    #
    # @staticmethod
    # def isDebugMode():
    #     return False
    #
    # @staticmethod
    # def getOutputFormat(choices):
    #     return 'html'
