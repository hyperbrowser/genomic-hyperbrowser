from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisDefHandler, AnalysisSpec
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.track.TrackStructure import TrackStructureV2
from proto.tools.GeneralGuiTool import HistElement
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite import GSuiteStatUtils, GuiBasedTsFactory
from quick.statistic.DiffOfSummarizedRanksPerTsCatV2Stat import DiffOfSummarizedRanksPerTsCatV2Stat
from quick.statistic.GenericTSChildrenV2Stat import GenericTSChildrenV2Stat
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat
from quick.statistic.TtestUnpairedTestStat import TtestUnpairedTestStat
from quick.statistic.WilcoxonUnpairedTestRV2Stat import WilcoxonUnpairedTestRV2Stat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.QueryTrackVsCategoricalGSuiteMixin import QueryTrackVsCategoricalGSuiteMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.webtools.mixin.SimpleProgressOutputMixin import SimpleProgressOutputMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.ts.RandomizedTsWriterTool import RandomizedTsWriterTool


class GroupTestBenchmarkTwoTool(GeneralGuiTool, GenomeMixin, UserBinMixin, QueryTrackVsCategoricalGSuiteMixin, SimpleProgressOutputMixin, DebugMixin):

    CAT_LBL_KEY = 'catTwoLbl'
    INFO_HIST_ELEMENT = 'BM2 info'
    REF_GSUITE_INPUT_LBL = 'Select a GSuite of case-control tracks simulated from the reference'

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Group difference test - Benchmark two"

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
        return [('Select reference track', 'queryTrack'),
               (cls.REF_GSUITE_INPUT_LBL, 'gsuite')] + \
            cls.getInputBoxNamesForGenomeSelection() + \
            [('Select GSuite column with sub-GSuite labels', 'catOneLbl'),
             ('Select GSuite column with group labels', 'catTwoLbl')] + \
            cls.getInputBoxNamesForQueryTrackVsCatGSuite() + \
            cls.getInputBoxNamesForUserBinSelection() \
               + \
            cls.getInputBoxNamesForDebug()
             # ('Select primary group category value', 'categoryVal'),
             # ('Select track to track similarity/distance measure', 'similarityFunc'),
             # ('Select summary function for track similarity to rest of suite', 'summaryFunc'),
             # ('Select summary function per group', 'catSummaryFunc'),
             # ('Type of randomization', 'randType'),
             # ('Select MCFDR sampling depth', 'mcfdrDepth'),
             # ('Select alternative for the wilcoxon test', 'wilcoxonTail'),
             # ('Randomization algorithm', 'randAlg')] + \

    # @classmethod
    # def getInputBoxOrder(cls):
    #     """
    #     Specifies the order in which the input boxes should be displayed,
    #     as a list. The input boxes are specified by index (starting with 1)
    #     or by key. If None, the order of the input boxes is in the order
    #     specified by getInputBoxNames().
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     """
    #     Creates a visual separation of groups of consecutive option boxes
    #     from the rest (fieldset). Each such group has an associated label
    #     (string), which is shown to the user. To define groups of option
    #     boxes, return a list of BoxGroup namedtuples with the label, the key
    #     (or index) of the first and last options boxes (inclusive).
    #
    #     Example:
    #        from quick.webtool.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey',
    #                         last='secondKey')]
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    @classmethod
    def getOptionsBoxQueryTrack(cls):  # Alt: getOptionsBox1()
        return GeneralGuiTool.getHistorySelectionElement()



    @staticmethod
    def getOptionsBoxGsuite(prevChoices):
        return  GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxCatOneLbl(prevChoices):
        if prevChoices.gsuite:
            from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
            gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return gsuite.attributes

    @staticmethod
    def getOptionsBoxCatTwoLbl(prevChoices):
        if prevChoices.gsuite and prevChoices.catOneLbl:
            from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
            gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return [x for x in gsuite.attributes if x != prevChoices.catOneLbl]

    @classmethod
    def getExtraHistElements(cls, choices):
        """
        Defines extra history elements to be created when clicking execute.
        This is defined by a list of HistElement objects, as in the
        following example:

           from proto.GeneralGuiTool import HistElement
           return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]

        It is good practice to use class constants for longer strings.

        In the execute() method, one typically needs to fetch the path to
        the dataset referred to by the extra history element. To fetch the
        path, use the dict cls.extraGalaxyFn with the defined history title
        as key, e.g. "cls.extraGalaxyFn[cls.HISTORY_TITLE]".

        Optional method. Default return value if method is not defined: None
        """
        return [HistElement(cls.INFO_HIST_ELEMENT, "txt")]

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

        # cls._setDebugModeIfSelected(choices)

        analysisBins = GalaxyInterface._getUserBinSource(*UserBinMixin.getRegsAndBinsSpec(choices),
                                                         genome=choices.genome)
        querySTS = GuiBasedTsFactory.getSingleTrackTS(choices.genome, choices.queryTrack)
        refTS = GuiBasedTsFactory.getFlatTracksTS(choices.genome, choices.gsuite)
        catTS = refTS.getSplittedByCategoryTS(choices.catOneLbl)
        for key, val in catTS.items():
            catTS[key] = val.getSplittedByCategoryTS(choices.catTwoLbl)

        ts = cls._prepareTrackStructure(querySTS, catTS, choices.randType, choices.randAlg, choices.randInput, analysisBins)
        operationCount = cls._getOpertationsCount(analysisBins, choices, ts)
        analysisSpec = cls._prepareAnalysis(choices, operationCount)
        cls._startProgressOutput()
        from config.DebugConfig import DebugConfig
        if DebugConfig.USE_PROFILING:
            from gold.util.Profiler import Profiler
            profiler = Profiler()
            resDict = {}
            profiler.run('resDict[0] = doAnalysis(analysisSpec, analysisBins, ts)', globals(), locals())
            res = resDict[0]
            results = res.getGlobalResult()['Result']
            profiler.printStats()
            if DebugConfig.USE_CALLGRAPH and galaxyFn:
                profiler.printLinkToCallGraph(['profile_AnalysisDefJob'], galaxyFn)
        else:
            results = doAnalysis(analysisSpec, analysisBins, ts).getGlobalResult()
            results = results["Result"]

        cls._endProgressOutput(hidden=(not DebugConfig.USE_PROFILING))
        cls._printResults(results, choices, galaxyFn)

        cls._writeInfoBMLocal(choices, results, cls.extraGalaxyFn[cls.INFO_HIST_ELEMENT])

    @classmethod
    def _writeInfoBMLocal(cls, choices, results, fn):
        cls._writeInfo(2, choices, results, fn)

    @classmethod
    def _getOpertationsCount(cls, analysisBins, choices, ts):
        operationCount = 0
        isWilcoxon = choices.randType == "Wilcoxon"
        isTtest = choices.randType == "T-test"
        for subIndex, subTS in ts.items():
            currTS = subTS if isWilcoxon or isTtest else subTS['real']
            operationCount += cls._calculateNrOfOperationsForProgresOutput(currTS,
                                                                           analysisBins,
                                                                           choices,
                                                                           isMC=(not isWilcoxon and not isTtest))
        return operationCount

    @classmethod
    def _prepareTrackStructure(cls, querySTS, catTS, randType, randAlg, randInput, analysisBins):

        ts = TrackStructureV2()
        if randType == 'Wilcoxon' or randType == "T-test":
            for cat, subTS in catTS.items():
                ts[cat] = cls._prepareQueryRefTrackStructure(querySTS, subTS)
        else:
            randAlgorithm = RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT[randType][randAlg]
            for cat, subTS in catTS.items():
                randQuerySTS = querySTS
                randCatTS = subTS
                #if randInput == TrackStructureV2.QUERY_KEY:
                if randInput == 'reference':
                    randQuerySTS = querySTS.getRandomizedVersion(
                        randAlgorithm,
                        binSource=analysisBins)
                #elif randInput == TrackStructureV2.REF_KEY:
                elif randInput == 'case-control':
                    randCatTS = subTS.getRandomizedVersion(
                        randAlgorithm,
                        binSource=analysisBins)
                else:
                    raise ValueError("Randomization input must be one of {}".format(str(cls.RANDOMIZABLE_INPUTS)))
                realTS = cls._prepareQueryRefTrackStructure(querySTS, subTS)
                randTS = cls._prepareQueryRefTrackStructure(randQuerySTS, randCatTS)
                hypothesisTS = TrackStructureV2()
                hypothesisTS["real"] = realTS
                hypothesisTS["rand"] = randTS
                ts[cat] = hypothesisTS
        return ts

    @classmethod
    def _prepareQueryRefTrackStructure(cls, queryTS, refTS):
        return TrackStructureV2(dict([("query", queryTS), ("reference", refTS)]))

    @classmethod
    def _prepareAnalysis(cls, choices, opCount):
        if choices.randType == 'Wilcoxon':

            analysisSpec = AnalysisSpec(GenericTSChildrenV2Stat)
            analysisSpec.addParameter('genericTSChildrenRawStatistic', WilcoxonUnpairedTestRV2Stat.__name__)
            analysisSpec.addParameter('primaryCatVal', choices.categoryVal)
            analysisSpec.addParameter('alternative', choices.tail)
        elif choices.randType == 'T-test':
            analysisSpec = AnalysisSpec(GenericTSChildrenV2Stat)
            analysisSpec.addParameter('genericTSChildrenRawStatistic', TtestUnpairedTestStat.__name__)
            analysisSpec.addParameter('primaryCatVal', choices.categoryVal)
            analysisSpec.addParameter('alternative', choices.tail)
        else:
            mcfdrDepth = choices.mcfdrDepth if choices.mcfdrDepth else \
                AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0][0]
            analysisDefString = REPLACE_TEMPLATES['$MCFDRv5$'] + ' -> ' + ' -> MultipleRandomizationManagerStat'
            analysisSpec = AnalysisDefHandler(analysisDefString)
            analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
            if choices.catSummaryFunc == cls.DIFF_RANK_SUM_CAT_SUMMARY_FUNC_LBL:
                analysisSpec.addParameter('rawStatistic', DiffOfSummarizedRanksPerTsCatV2Stat.__name__)
            else:
                analysisSpec.addParameter('rawStatistic', SummarizedInteractionPerTsCatV2Stat.__name__)
                analysisSpec.addParameter('summaryFunc',
                                          GSuiteStatUtils.SUMMARY_FUNCTIONS_MAPPER[choices.summaryFunc])
                analysisSpec.addParameter('catSummaryFunc', str(choices.catSummaryFunc))
            analysisSpec.addParameter('tail', choices.tail)
            analysisSpec.addParameter('evaluatorFunc', 'evaluatePvalueAndNullDistribution')
        analysisSpec.addParameter('progressPoints', opCount)
        analysisSpec.addParameter('segregateNodeKey', 'reference')

        analysisSpec.addParameter('pairwiseStatistic',
                                  GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[
                                      choices.similarityFunc])
        analysisSpec.addParameter('selectedCategory', choices.categoryVal)
        analysisSpec.addParameter('runLocalAnalysis', "No")

        return analysisSpec

    @classmethod
    def _printResults(cls, results, choices, galaxyFn):
        from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.divBegin()

        if choices.randType == 'Wilcoxon' or choices.randType == "T-test":
            core.paragraph('The table contains the results from %s unpaired rank sum test executed for '
                           'each sub-GSuite, using the similarity measure "<b>{}</b>".'.format(
                            choices.randType, choices.similarityFunc))
            resTableDict = OrderedDict()
            for key, val in results.iteritems():
                resTableDict[key] = [val.getResult()['statistic'], val.getResult()['p.value']]

            columnNames = ["GSuite index", "%s statistic" % choices.randType, "P-value"]
            addTableWithTabularAndGsuiteImportButtons(core, choices, galaxyFn, 'table', resTableDict, columnNames)

            nameList = [choices.randType, 'qqplot.png']
            pvals = [x[1] for x in resTableDict.values()]

            cls._addQQPlot(core, pvals, nameList, galaxyFn)
            # core.tableFromDictionary(resTableDict, columnNames=columnNames)
        else:
            cls._multipleMCResultsToHtmlCore(core, choices, results, galaxyFn)

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
    @classmethod
    def isDebugMode(cls):
        """
        Specifies whether the debug mode is turned on. Debug mode is
        currently mostly used within the Genomic HyperBrowser and will make
        little difference in a plain Galaxy ProTo installation.

        Optional method. Default return value if method is not defined: False
        """
        return True
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
        return 'html'
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
