from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec, AnalysisDefHandler
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.gsuite import GSuiteConstants
from gold.track.TrackStructure import TrackStructureV2
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite import GSuiteStatUtils, GuiBasedTsFactory
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat
from quick.statistic.MultitrackSummarizedInteractionWithOtherTracksV2Stat import \
    MultitrackSummarizedInteractionWithOtherTracksV2Stat
from quick.statistic.WilcoxonUnpairedTestRV2Stat import WilcoxonUnpairedTestRV2Stat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.QueryTrackVsCategoricalGSuiteMixin import QueryTrackVsCategoricalGSuiteMixin
from quick.webtools.mixin.SimpleProgressOutputMixin import SimpleProgressOutputMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.webtools.ts.RandomizedTsWriterTool import RandomizedTsWriterTool


class GroupTestBenchmarkOneTool(GeneralGuiTool, UserBinMixin, GenomeMixin, DebugMixin, QueryTrackVsCategoricalGSuiteMixin, SimpleProgressOutputMixin):

    GSUITE_FILE_OPTIONS_BOX_KEYS = ['queryGsuite', 'refGsuite']
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False
    WHAT_GENOME_IS_USED_FOR = 'the analysis'

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    CAT_GSUITE_KEY = 'refGsuite'

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Group difference test - Benchmark One"

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
        return [('Select the query GSuite', 'queryGsuite'),
                ('Select the categorical reference GSuite', 'refGsuite'),
                ('Select category column', 'categoryName'),
                ] + \
               cls.getInputBoxNamesForGenomeSelection() + \
                cls.getInputBoxNamesForQueryTrackVsCatGSuite() + \
               cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()


    @classmethod
    def getOptionsBoxQueryGsuite(cls):  # Alt: getOptionsBox2()
        """
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).

        Mandatory for the subsequent keys (after the first key) defined in
        getInputBoxNames(), if any.
        """
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxRefGsuite(cls, prevChoices):  # Alt: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxCategoryName(prevChoices):
        if prevChoices.refGsuite:
            from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
            gsuite = getGSuiteFromGalaxyTN(prevChoices.refGsuite)
            return gsuite.attributes

    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     """
    #     If not None, defines the string content of an clickable info box
    #     beside the corresponding input box. HTML is allowed.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     """
    #     Defines a set of demo inputs to the option boxes in the
    #     order defined by getOptionBoxNames and getOptionsBoxOrder.
    #     If not None, a Demo button appears in the interface. Clicking the
    #     button fills the option boxed with the defined demo values.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     """
    #     Defines extra history elements to be created when clicking execute.
    #     This is defined by a list of HistElement objects, as in the
    #     following example:
    #
    #        from proto.GeneralGuiTool import HistElement
    #        return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]
    #
    #     It is good practice to use class constants for longer strings.
    #
    #     In the execute() method, one typically needs to fetch the path to
    #     the dataset referred to by the extra history element. To fetch the
    #     path, use the dict cls.extraGalaxyFn with the defined history title
    #     as key, e.g. "cls.extraGalaxyFn[cls.HISTORY_TITLE]".
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        """
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than
        'html', the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional
        files can be put (cls, e.g. generated image files). choices is a list
        of selections made by web-user in each options box.

        Mandatory unless isRedirectTool() returns True.
        """

        from quick.util.debug import DebugUtil
        DebugUtil.insertBreakPoint(5678)

        cls._setDebugModeIfSelected(choices)

        analysisBins = GalaxyInterface._getUserBinSource(*UserBinMixin.getRegsAndBinsSpec(choices),
                                                         genome=choices.genome)
        queryTS = GuiBasedTsFactory.getFlatTracksTS(choices.genome, choices.queryGsuite)
        refTS = GuiBasedTsFactory.getFlatTracksTS(choices.genome, choices.refGsuite)
        catTS = refTS.getSplittedByCategoryTS(choices.categoryName)
        assert choices.categoryVal in catTS

        cls._startProgressOutput()
        ts = cls.prepareTrackStructure(queryTS, catTS, analysisBins, choices)
        operationCount = cls._calculateNrOfOperations(ts, analysisBins, choices)
        analysisSpec = cls.prepareMultiQueryAnalysis(choices, operationCount)
        results = doAnalysis(analysisSpec, analysisBins, ts).getGlobalResult()["Result"]
        cls._endProgressOutput()

        core = HtmlCore()
        core.divBegin()
        resTableDict = OrderedDict()
        if choices.randType == "Wilcoxon":
            for key, val in results.iteritems():
                resTableDict[key] = [val.getResult()['statistic'], val.getResult()['p.value']]
            columnNames = ["Query track", "Wilcoxon score", "P-value"]
            addTableWithTabularAndGsuiteImportButtons(core, choices, galaxyFn, 'table', resTableDict, columnNames)
            # core.tableFromDictionary(resTableDict, columnNames=["Query track", "Wilcoxon score", "P-value"])
        else:
            cls._multipleMCResultsToHtmlCore(core, choices, results, galaxyFn)
            # core.tableFromDictionary(resTableDict, columnNames=["Query track"] + catNames)
        core.divEnd()
        core.end()
        print str(core)

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

    @classmethod
    def prepareTrackStructure(cls, queryTS, catTS, analysisBins, choices):
        if choices.randType == "Wilcoxon":
            return cls._prepareQueryRefTrackStructure(queryTS, catTS)
        else:
            ts = TrackStructureV2()
            randAlgorithm = RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT[choices.randType][choices.randAlg]
            for queryTitle, querySTS in queryTS.items():
                randQuerySTS = querySTS
                randCatTS = catTS
                if choices.randInput == TrackStructureV2.QUERY_KEY:
                    randQuerySTS = querySTS.getRandomizedVersion(
                        randAlgorithm,
                        binSource=analysisBins)
                elif choices.randInput == TrackStructureV2.REF_KEY:
                    randCatTS = catTS.getRandomizedVersion(
                        randAlgorithm,
                        binSource=analysisBins)
                else:
                    raise ValueError("Randomization input must be one of {}".format(str(cls.RANDOMIZABLE_INPUTS)))
                ts[queryTitle] = cls._prepareHypothesisTS(catTS, querySTS, randCatTS, randQuerySTS)
            return ts

    @classmethod
    def _prepareHypothesisTS(cls, refTS, queryTS, randRefTS, randQueryTS):
        realTS = cls._prepareQueryRefTrackStructure(queryTS, refTS)
        randTS = cls._prepareQueryRefTrackStructure(randQueryTS, randRefTS)
        hypothesisTS = TrackStructureV2()
        hypothesisTS["real"] = realTS
        hypothesisTS["rand"] = randTS
        return hypothesisTS

    @classmethod
    def _prepareQueryRefTrackStructure(cls, queryTS, refTS):
        return TrackStructureV2(dict([("query", queryTS), ("reference", refTS)]))

    @classmethod
    def _calculateNrOfOperations(cls, ts, analysisBins, choices):
        if choices.randType == "Wilcoxon":
            return cls._calculateNrOfOperationsForProgresOutput(ts,
                                                                analysisBins,
                                                                choices,
                                                                isMC=False)
        else:
            operationCount = 0
            for subIndex, subTS in ts.items():
                currTS = subTS['real']
                operationCount += cls._calculateNrOfOperationsForProgresOutput(currTS,
                                                                               analysisBins,
                                                                               choices,
                                                                               isMC=True)
            return operationCount

    @classmethod
    def prepareMultiQueryAnalysis(cls, choices, opCount):
        if choices.randType == "Wilcoxon":
            analysisSpec = AnalysisSpec(MultitrackSummarizedInteractionWithOtherTracksV2Stat)
            analysisSpec.addParameter('multitrackRawStatistic', WilcoxonUnpairedTestRV2Stat.__name__)
            analysisSpec.addParameter('alternative', choices.tail)
            analysisSpec.addParameter('multitrackSummaryFunc', 'raw')

            analysisSpec.addParameter('pairwiseStatistic',
                                      GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[
                                          choices.similarityFunc])
            analysisSpec.addParameter('segregateNodeKey', 'reference')
            analysisSpec.addParameter('progressPoints', opCount)
            analysisSpec.addParameter('runLocalAnalysis', "No")
            analysisSpec.addParameter('selectedCategory', choices.categoryVal)
            return analysisSpec
        else:
            mcfdrDepth = choices.mcfdrDepth if choices.mcfdrDepth else \
                AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0][0]
            analysisDefString = REPLACE_TEMPLATES['$MCFDRv5$'] + ' -> ' + ' -> MultipleRandomizationManagerStat'
            analysisSpec = AnalysisDefHandler(analysisDefString)
            analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
            analysisSpec.addParameter('rawStatistic', SummarizedInteractionPerTsCatV2Stat.__name__)
            analysisSpec.addParameter('tail', choices.tail)
            analysisSpec.addParameter('evaluatorFunc', 'evaluatePvalueAndNullDistribution')
            analysisSpec.addParameter('catSummaryFunc', str(choices.catSummaryFunc))
            analysisSpec.addParameter('summaryFunc',
                                      GSuiteStatUtils.SUMMARY_FUNCTIONS_MAPPER[choices.summaryFunc])
            analysisSpec.addParameter('progressPoints', opCount)
            analysisSpec.addParameter('segregateNodeKey', 'reference')

            analysisSpec.addParameter('pairwiseStatistic',
                                      GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[
                                          choices.similarityFunc])
            analysisSpec.addParameter('selectedCategory', choices.categoryVal)
            analysisSpec.addParameter('runLocalAnalysis', "No")

            return analysisSpec

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
    @classmethod
    def isPublic(cls):
        """
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as well as admin
        users, as defined in the galaxy.ini file.

        Optional method. Default return value if method is not defined: False
        """
        return True
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
    # @classmethod
    # def isDebugMode(cls):
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
        """
        The format of the history element with the output of the tool. Note
        that if 'html' is returned, any print statements in the execute()
        method is printed to the output dataset. For text-based output
        (e.g. bed) the output dataset only contains text written to the
        galaxyFn file, while all print statements are redirected to the info
        field of the history item box.

        Note that for 'html' output, standard HTML header and footer code is
        added to the output dataset. If one wants to write the complete HTML
        page, use the restricted output format 'customhtml' instead.

        Optional method. Default return value if method is not defined:
        'html'
        """
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
