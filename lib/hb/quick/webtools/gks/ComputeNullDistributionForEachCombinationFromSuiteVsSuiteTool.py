from proto.tools.hyperbrowser.GeneralGuiTool import GeneralGuiTool
from gold.util.Profiler import Profiler
from config.DebugConfig import DebugConfig
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite import GuiBasedTsFactory
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat

from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.GeneralGuiTool import GeneralGuiToolMixin
from gold.track.TrackStructure import TrackStructureV2
from gold.application.HBAPI import doAnalysis, doAnalysisWithProfiling
from gold.description.AnalysisDefHandler import AnalysisSpec, AnalysisDefHandler
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class ComputeNullDistributionForEachCombinationFromSuiteVsSuiteTool(GeneralGuiTool, DebugMixin, GenomeMixin, UserBinMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gsuite1','gsuite2']
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Sandboxing"

    @classmethod
    def getInputBoxNames(cls):
        """
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase and start with a non-capital letter
              (e.g. "firstKey")

        Optional method. Default return value if method is not defined: []
        """
        return [('Select GSuite 1', 'gsuite1'),
                 ('Select GSuite 2', 'gsuite2')
                ] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()

    @classmethod
    def getOptionsBoxGsuite1(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxGsuite2(cls, prevChoices):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        cls._setDebugModeIfSelected(choices)
        #from time import time
        #startTime = time()
        analysisBins = GalaxyInterface._getUserBinSource(*UserBinMixin.getRegsAndBinsSpec(choices),
                                                         genome=choices.genome)
        queryTS = GuiBasedTsFactory.getFlatTracksTS(choices.genome, choices.gsuite1)
        refTS = GuiBasedTsFactory.getFlatTracksTS(choices.genome, choices.gsuite2)
        ts = TrackStructureV2([("query", queryTS), ("reference", refTS)])

        analysisSpec = AnalysisSpec(SummarizedInteractionWithOtherTracksV2Stat)
        analysisSpec.addParameter('numResamplings','5')
        analysisSpec.addParameter('rawStatistic', 'LogSumDistStat')
        analysisSpec.addParameter('pairwiseStatistic', 'RandomizationManagerStat')
        analysisSpec.addParameter('summaryFunc','raw')
        analysisSpec.addParameter('tails', 'left-tail')
        analysisSpec.addParameter('includeFullNullDistribution','yes')
        analysisSpec.addParameter('assumptions','PermutedSegsAndIntersegsTrack_')

        if DebugConfig.USE_PROFILING:
            resObj = doAnalysisWithProfiling(analysisSpec, analysisBins, ts, galaxyFn)
        else:
            resObj = doAnalysis(analysisSpec, analysisBins, ts)
        tsRes = resObj.getGlobalResult()['Result']

#        print 'Elapsed time: ', (time()-startTime)/3600.0, ' hours'


        for key in tsRes:
            print key, '\t', tsRes[key]._result['fullNullDistribution']

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None, which enables
        the execute button.

        Optional method. Default return value if method is not defined: None
        """
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     """
    #     Specifies a list of classes for subtools of the main tool. These
    #     subtools will be selectable from a selection box at the top of the
    #     page. The input boxes will change according to which subtool is
    #     selected.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     """
    #     Specifies whether the tool is accessible to all users. If False, the
    #     tool is only accessible to a restricted set of users as well as admin
    #     users, as defined in the galaxy.ini file.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     """
    #     Specifies whether the tool should redirect to an URL when the Execute
    #     button is clicked.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     """
    #     This method is called to return an URL if the isRedirectTool method
    #     returns True.
    #
    #     Mandatory method if isRedirectTool() returns True.
    #     """
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     """
    #     Specifies if a History item should be created when the Execute button
    #     is clicked.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     """
    #     Specifies if this tool could be run from batch using the batch. The
    #     batch run line can be fetched from the info box at the bottom of the
    #     tool.
    #
    #     Optional method. Default return value if method is not defined:
    #         same as isHistoryTool()
    #     """
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     """
    #     Specifies whether changing the content of textboxes causes the page
    #     to reload. Returning False stops the need for reloading the tool
    #     after each input, resulting in less lags for the user.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     """
    #     Specifies a list of input boxes which resets the subsequent stored
    #     choices previously made. The input boxes are specified by index
    #     (starting with 1) or by key.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     """
    #     Specifies a help text in HTML that is displayed below the tool.
    #
    #     Optional method. Default return value if method is not defined: ''
    #     """
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     """
    #     Specifies an id used by StaticFile.py to reference an illustration
    #     file on disk. The id is a list of optional directory names followed
    #     by a filename. The base directory is STATIC_PATH as defined by
    #     Config.py. The full path is created from the base directory
    #     followed by the id.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     """
    #     Specifies an URL to an example page that describes the tool, for
    #     instance a Galaxy page.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    @classmethod
    def isDebugMode(cls):
        return True
    #     """
    #     Specifies whether the debug mode is turned on. Debug mode is
    #     currently mostly used within the Genomic HyperBrowser and will make
    #     little difference in a plain Galaxy ProTo installation.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
    #     """
    #     The title (name) of the main output history element.
    #
    #     Optional method. Default return value if method is not defined:
    #     the name of the tool.
    #     """

