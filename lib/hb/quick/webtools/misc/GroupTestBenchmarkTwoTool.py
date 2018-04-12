from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisDefHandler, AnalysisSpec
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.track.TrackStructure import TrackStructureV2
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite import GSuiteStatUtils, GuiBasedTsFactory
from quick.statistic.GenericTSChildrenV2Stat import GenericTSChildrenV2Stat
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat
from quick.statistic.WilcoxonUnpairedTestRV2Stat import WilcoxonUnpairedTestRV2Stat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.QueryTrackVsCategoricalGSuiteMixin import QueryTrackVsCategoricalGSuiteMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.webtools.mixin.SimpleProgressOutputMixin import SimpleProgressOutputMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.ts.RandomizedTsWriterTool import RandomizedTsWriterTool


class GroupTestBenchmarkTwoTool(GeneralGuiTool, GenomeMixin, UserBinMixin, QueryTrackVsCategoricalGSuiteMixin, SimpleProgressOutputMixin):

    CAT_LBL_KEY = 'catTwoLbl'

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
        return [('Select query track', 'queryTrack'),
               ('Select a GSuite', 'gsuite')] + \
            cls.getInputBoxNamesForGenomeSelection() + \
            [('Select first level category', 'catOneLbl'),
             ('Select second level category', 'catTwoLbl')] + \
            cls.getInputBoxNamesForQueryTrackVsCatGSuite() + \
            cls.getInputBoxNamesForUserBinSelection()
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
        """
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to
        other methods. These are lists of results, one for each input box
        (in the order specified by getInputBoxOrder()).

        Mandatory for the first key defined in getInputBoxNames(), if any.

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Raw HTML code:          '__rawstr__', 'HTML code'
        - This is mainly intended for read only usage. Even though more
          advanced hacks are possible, it is discouraged.

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) |
                                ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting Galaxy dataset info, as
            described below.

        History check box list: ('__multihistory__', ) |
                                ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with Galaxy dataset ids as key (the number YYYY
            as described below), and the associated Galaxy dataset info as the
            values, given that the history element is ticked off by the user.
            If not, the value is set to None. The Galaxy dataset info structure
            is described below.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'],
                                 ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False),
                                             ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).


        ###
        Note about the "Galaxy dataset info" data structure:
        ###

        "Galaxy dataset info" is a list of strings coding information about a
        Galaxy history element and its associated dataset, typically used to
        provide info on the history element selected by the user as input to a
        ProTo tool.

        Structure:
            ['galaxy', fileFormat, path, name]

        Optionally encoded as a single string, delineated by colon:

            'galaxy:fileFormat:path:name'

        Where:
            'galaxy' used for assertions in the code
            fileFormat (or suffix) contains the file format of the dataset, as
                encoded in the 'format' field of a Galaxy history element.
            path (or file name/fn) is the disk path to the dataset file.
                Typically ends with 'XXX/dataset_YYYY.dat'. XXX and YYYY are
                numbers which are extracted and used as an unique id  of the
                dataset in the form [XXX, YYYY]
            name is the title of the history element

        The different parts can be extracted using the functions
        extractFileSuffixFromDatasetInfo(), extractFnFromDatasetInfo(), and
        extractNameFromDatasetInfo() from the module CommonFunctions.py.
        """
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
        results = doAnalysis(analysisSpec, analysisBins, ts).getGlobalResult()["Result"]
        cls._endProgressOutput()
        cls._printResults(results, choices, galaxyFn)

    @classmethod
    def _getOpertationsCount(cls, analysisBins, choices, ts):
        operationCount = 0
        isWilcoxon = choices.randType == "Wilcoxon"
        for subIndex, subTS in ts.items():
            currTS = subTS if isWilcoxon else subTS['real']
            operationCount += cls._calculateNrOfOperationsForProgresOutput(currTS,
                                                                           analysisBins,
                                                                           choices,
                                                                           isMC=(not isWilcoxon))
        return operationCount

    @classmethod
    def _prepareTrackStructure(cls, querySTS, catTS, randType, randAlg, randInput, analysisBins):

        ts = TrackStructureV2()
        if randType == 'Wilcoxon':
            for cat, subTS in catTS.items():
                ts[cat] = cls._prepareQueryRefTrackStructure(querySTS, subTS)
        else:
            randAlgorithm = RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT[randType][randAlg]
            for cat, subTS in catTS.items():
                randQuerySTS = querySTS
                randCatTS = subTS
                if randInput == TrackStructureV2.QUERY_KEY:
                    randQuerySTS = querySTS.getRandomizedVersion(
                        randAlgorithm,
                        binSource=analysisBins)
                elif randInput == TrackStructureV2.REF_KEY:
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

    @classmethod
    def _printResults(cls, results, choices, galaxyFn):
        from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.divBegin()

        if choices.randType == 'Wilcoxon':
            core.paragraph('The table contains the results from Wilcoxon{}s unpaired rank sum test executed for '
                           'each sub-GSuite, using the similarity measure "<b>{}</b>".'.format(
                            "'", choices.similarityFunc))
            resTableDict = OrderedDict()
            for key, val in results.iteritems():
                resTableDict[key] = [val.getResult()['statistic'], val.getResult()['p.value']]

            columnNames = ["GSuite index", "Wilcoxon statistic", "P-value"]
            addTableWithTabularAndGsuiteImportButtons(core, choices, galaxyFn, 'table', resTableDict, columnNames)
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
