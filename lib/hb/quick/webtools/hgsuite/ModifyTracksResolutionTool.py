from gold.description.AnalysisDefHandler import AnalysisSpec
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.SingleTSStat import SingleTSStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from gold.statistic.CountStat import CountStat

class ModifyTracksResolutionTool(GeneralGuiTool, GenomeMixin):
    @classmethod
    def getToolName(cls):
        return "Modify resolution of tracks"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [('Select resolution', 'resolution')]


    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxResolution(cls, prevChoices):
        return ['1k', '10k', '100k', '1m', '10m']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        resolution = choices.resolution.encode('utf-8')

        #chamge resolution of tracks
        analysisSpec = AnalysisSpec(SingleTSStat)
        analysisSpec.addParameter('rawStatistic', CountStat.__name__)
        regSpec = '*'
        binSpec = resolution
        analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                         binSpec,
                                                         choices.genome)


        #get local result from statistic

        #rebuild the gsuite

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
