from config.DebugConfig import DebugConfig
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec, AnalysisDefHandler
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuiteConstants import TITLE_COL
from gold.track.TrackStructure import TrackStructureV2
from gold.track.trackstructure.TsUtils import getRandomizedVersionOfTs
from gold.track.trackstructure.random.ExcludedSegmentsStorage import ExcludedSegmentsStorage
from gold.track.trackstructure.random.ShuffleElementsBetweenTracksAndBinsTvProvider import \
    ShuffleElementsBetweenTracksAndBinsTvProvider
from gold.track.trackstructure.random.TrackDataStorageRandAlgorithm import \
    CollisionDetectionTracksAndBinsRandAlgorithm
from gold.util.CommonClasses import OrderedDefaultDict
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.MultiplePairedTSStat import MultiplePairedTSStat
from quick.statistic.PairedTSStat import PairedTSStat
from quick.statistic.StatFacades import ObservedVsExpectedStat
from quick.util import McEvaluators
from quick.util.debug import DebugUtil
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.RandAlgorithmMixin import RandAlgorithmMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs


class CategoricalGSuiteVsGSuiteTool(GeneralGuiTool, GenomeMixin, UserBinMixin,
                                    RandAlgorithmMixin, DebugMixin):

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

    GSUITE_FILE_OPTIONS_BOX_KEYS = ['firstGSuite', 'secondGSuite']

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Categorical GSuite analysis"

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
        return [('Select first GSuite', 'firstGSuite'),
                ('Select category for first GSuite', 'firstGSuiteCat'),
                ('Select second GSuite', 'secondGSuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
                [('Select category for second GSuite', 'secondGSuiteCat'),
                 ('Select analysis', 'analysis')] + \
                cls.getInputBoxNamesForRandAlgSelection() + \
                [('Select MCFDR sampling depth', 'mcfdrDepth')] + \
                cls.getInputBoxNamesForUserBinSelection() + \
                cls.getInputBoxNamesForDebug()

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
    def getOptionsBoxFirstGSuite(cls):  # Alt: getOptionsBox1()
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
        return GeneralGuiTool.getHistorySelectionElement('gsuite')


    @classmethod
    def getOptionsBoxFirstGSuiteCat(cls, prevChoices):
        if prevChoices.firstGSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.firstGSuite)
            attributeList = gSuite.attributes
            attributeList = [TITLE_COL] + attributeList
            return attributeList

    @classmethod
    def getOptionsBoxSecondGSuite(cls, prevChoices):  # Alt: getOptionsBox2()
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
    def getOptionsBoxSecondGSuiteCat(cls, prevChoices):
        if prevChoices.secondGSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
            attributeList = gSuite.attributes
            attributeList = [TITLE_COL] + attributeList
            return attributeList

    @classmethod
    def getOptionsBoxAnalysis(cls, prevChoices):
        return ['Forbes', 'Forbes with a p-val']

    @classmethod
    def _showRandAlgorithmChoices(cls, prevChoices):
        return prevChoices.analysis in ['Forbes with a p-val']

    @classmethod
    def getOptionsBoxMcfdrDepth(cls, prevChoices):
        if prevChoices.randType and prevChoices.randType != cls.SELECT_CHOICE_STR:
            return AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0]

    # @classmethod
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
        cls._setDebugModeIfSelected(choices)

        firstGSuiteCat = choices.firstGSuiteCat
        firstGSuiteCat = firstGSuiteCat.encode("utf-8")
        secondGSuiteCat = choices.secondGSuiteCat
        secondGSuiteCat = secondGSuiteCat.encode("utf-8")

        genome = choices.genome
        analysisBins = UserBinMixin.getUserBinSource(choices)

        import quick.gsuite.GuiBasedTsFactory as factory

        firstTs = factory.getFlatTracksTS(genome, choices.firstGSuite)
        secondTs = factory.getFlatTracksTS(genome, choices.secondGSuite)

        core = HtmlCore()
        # core.begin()
        core.divBegin(divId='results-page')
        core.divBegin(divClass='results-section')

        if choices.analysis == "Forbes":
            ts = cls._prepareTs(firstTs, secondTs, firstGSuiteCat, secondGSuiteCat)
            analysisSpec = cls._prepareAnalysis(choices)
            result = doAnalysis(analysisSpec, analysisBins, ts).getGlobalResult()['Result']
            transformedResultsDict = OrderedDefaultDict(list)
            data = []
            for cat, res in result.iteritems():
                transformedResultsDict[cat].append(res.result)
                data.append(res.result)
            addTableWithTabularAndGsuiteImportButtons(
                core, choices, galaxyFn, choices.analysis,
                tableDict=transformedResultsDict,
                columnNames=["Category", "Forbes similarity"]
            )

            cls.drawHist(core, data)

        else:
            ts = cls._prepareRandomizedTs(choices, firstTs, secondTs, analysisBins,  firstGSuiteCat, secondGSuiteCat)
            analysisSpec = cls._prepareAnalysisWithHypothesisTests(choices)
            if DebugConfig.USE_PROFILING:
                from gold.util.Profiler import Profiler
                profiler = Profiler()
                resDict = {}
                profiler.run('resDict[0] = doAnalysis(analysisSpec, analysisBins, ts)', globals(), locals())
                res = resDict[0]
                result = res.getGlobalResult()['Result']
                profiler.printStats()
                if DebugConfig.USE_CALLGRAPH and galaxyFn:
                    profiler.printLinkToCallGraph(['profile_AnalysisDefJob'], galaxyFn)
            else:
                result = doAnalysis(analysisSpec, analysisBins, ts).getGlobalResult()['Result']

            transformedResultsDict = OrderedDefaultDict(list)
            data = []
            data1 = []
            for cat, res in result.iteritems():
                forbes = res.getResult()['TSMC_' + PairedTSStat.__name__]
                pVal = res.getResult()[McEvaluators.PVAL_KEY]
                transformedResultsDict[cat].append(forbes)
                transformedResultsDict[cat].append(pVal)
                data.append(forbes)
                data1.append(pVal)


            # print transformedResultsDict
            addTableWithTabularAndGsuiteImportButtons(
                core, choices, galaxyFn, choices.analysis,
                tableDict=transformedResultsDict,
                columnNames=["Category", "Forbes similarity", "P-value"]
            )

            cls.drawHist(core, data)
            cls.drawHist(core, data1, breaks = True)

        core.divEnd()
        core.divEnd()
        # core.end()
        print core

    @classmethod
    def drawHist(cls, core, data, breaks = False):
        from proto.RSetup import r, robjects

        if breaks == False:
            rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
            data = robjects.FloatVector(data)
            dataFromRPois = r(rCode)(data)
            textTitle = 'Histogram Forbes'
            # print '1', data
        else:
            # print '2', data
            rCode = 'ourHist <- function(vec) {hist(vec, breaks=c(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0), plot=FALSE)}'
            data = robjects.FloatVector(data)
            dataFromRPois = r(rCode)(data)
            textTitle = 'Histogram p-values'

        breaks = list(dataFromRPois.rx2('breaks'))
        counts = list(dataFromRPois.rx2('density'))
        vg = visualizationGraphs()
        res = vg.drawColumnChart(counts,
                                 xAxisRotation=90,
                                 categories=breaks,
                                 showInLegend=False,
                                 titleText=textTitle,
                                 histogram=True,
                                 height=400
                                 )
        core.line(res)

    @classmethod
    def _prepareTs(cls, firstTs, secondTs, firstGSuiteCat, secondGSuiteCat):
        ts = TrackStructureV2()
        for sts1 in firstTs.getLeafNodes():
            #assert 'category' in sts1.metadata, "The GSuites must contain a category column/attribute named 'category'"
            #cat1 = sts1.metadata['category']
            cat1 = sts1.metadata[firstGSuiteCat]
            for sts2 in secondTs.getLeafNodes():
                #assert 'category' in sts2.metadata, "The GSuites must contain a category column/attribute named 'category'"
                # cat2 = sts2.metadata['category']
                cat2 = sts2.metadata[secondGSuiteCat]
                if cat1 == cat2:
                    realTs = TrackStructureV2()
                    realTs["query"] = sts1
                    realTs["reference"] = sts2
                    ts[cat1] = realTs
        return ts

    @classmethod
    def _prepareRandomizedTs(cls, choices, firstTs, secondTs, binSource,  firstGSuiteCat, secondGSuiteCat):
        ts = TrackStructureV2()
        for sts1 in firstTs.getLeafNodes():
            #assert 'category' in sts1.metadata, "The GSuites must contain a category column/attribute named 'category'"
            # cat1 = sts1.metadata['category']
            cat1 = sts1.metadata[firstGSuiteCat]
            for sts2 in secondTs.getLeafNodes():
                # assert 'category' in sts2.metadata, "The GSuites must contain a category column/attribute named 'category'"
                # cat2 = sts2.metadata['category']
                cat2 = sts2.metadata[secondGSuiteCat]
                if cat1 == cat2:
                    assert cat1 not in ts, "Multiple tracks from category %s" % cat1
                    realTs = TrackStructureV2()
                    realTs["query"] = sts1
                    realTs["reference"] = sts2
                    randTs = TrackStructureV2()
                    randTs["query"] = sts1
                    #TODO: handle randomization of sub-trackstructures better
                    randTvProvider = cls.createTrackViewProvider(choices, sts2, binSource,
                                                                 choices.genome)
                    randTs["reference"] = getRandomizedVersionOfTs(sts2, randTvProvider)
                    hypothesisTS = TrackStructureV2()
                    hypothesisTS["real"] = realTs
                    hypothesisTS["rand"] = randTs
                    ts[cat1] = hypothesisTS

        return ts

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
        errorString = cls._checkGSuiteFile(choices.firstGSuite)
        if errorString:
            return errorString

        errorString = cls._checkGSuiteFile(choices.secondGSuite)
        if errorString:
            return errorString

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

        errorString = cls.validateRandAlgorithmSelection(choices)
        if errorString:
            return errorString

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

    @classmethod
    def _prepareAnalysis(cls, choices):
        analysisSpec = AnalysisSpec(MultiplePairedTSStat)
        analysisSpec.addParameter("pairedTsRawStatistic", ObservedVsExpectedStat.__name__)
        return analysisSpec

    @classmethod
    def _prepareAnalysisWithHypothesisTests(cls, choices):
        mcfdrDepth = choices.mcfdrDepth if choices.mcfdrDepth else \
            AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0][0]
        analysisDefString = REPLACE_TEMPLATES['$MCFDRv5$'] + ' -> ' + ' -> MultipleRandomizationManagerStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
        analysisSpec.addParameter('rawStatistic', PairedTSStat.__name__)
        analysisSpec.addParameter('pairedTsRawStatistic', ObservedVsExpectedStat.__name__)
        analysisSpec.addParameter('tail', 'right-tail')
        analysisSpec.addParameter('evaluatorFunc', 'evaluatePvalueAndNullDistribution')
        analysisSpec.addParameter('runLocalAnalysis', 'No')
        return analysisSpec

