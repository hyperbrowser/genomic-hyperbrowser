from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.description.AnalysisDefHandler import AnalysisSpec
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.GenomeInfo import GenomeInfo
from quick.application.UserBinSource import UserBinSource
from gold.application.HBAPI import doAnalysis
from gold.track.Track import Track, PlainTrack
from quick.webtools.hgsuite.Legend import Legend

class PlotMutationFrequencyAlongChromosomeTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Plot frequency of mutation along chromosome"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select way of plotting', 'showResults'),
                ('Select track collection GSuite', 'gSuite1'),
                ('Select statistic', 'statistic1'),
                ('Select track collection GSuite', 'gSuite2'),
                ('Select statistic', 'statistic2'),
                ('Show on plot % the highest values', 'visParam'),
                #('Select bin size (default: 1000000)', 'bps')
                ('User bin source(default: 1000000)', 'binSourceParam')
                ]

    @staticmethod
    def getOptionsBoxShowResults():
        return ['Show results for one Gsuite', 'Show results for two Gsuite']

    @staticmethod
    def getOptionsBoxGSuite1(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStatistic1(prevChoices):
        return ['Count Point', 'Count Segment']

    @staticmethod
    def getOptionsBoxGSuite2(prevChoices):
        if prevChoices.showResults == 'Show results for two Gsuite':
            return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxStatistic2(prevChoices):
        if prevChoices.showResults == 'Show results for two Gsuite':
            return ['Count Point', 'Count Segment', 'Count Proportion']

    @staticmethod
    def getOptionsBoxVisParam(prevChoices):
        if prevChoices.showResults != 'Show results for two Gsuite':
            return ['0', '10', '15', '20', '30', '40', '50']

    @staticmethod
    def getOptionsBoxBinSourceParam(prevChoices):
        return '1000000'

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        from gold.statistic.CountPointStat import CountPointStat
        from gold.statistic.CountSegmentStat import CountSegmentStat
        from quick.statistic.ProportionCountPerBinAvgStat import ProportionCountPerBinAvgStat

        if choices.statistic1 == 'Count Point':
            analysisSpec1 = AnalysisSpec(CountPointStat)
        elif choices.statistic1 == 'Count Segment':
            analysisSpec1 = AnalysisSpec(CountSegmentStat)
        elif choices.statistic1 == 'Count Proportion':
            analysisSpec1 = AnalysisSpec(ProportionCountPerBinAvgStat)

        # use gSuite from option
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        tracks = list(gSuite1.allTracks())

        if choices.binSourceParam:
            binSourceParam = choices.binSourceParam
        else:
            binSourceParam = '1M'

        import quick.webtools.restricted.visualization.visualizationPlots as vp
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('plotDiv')
        htmlCore.line(vp.addJSlibs())
        htmlCore.line(vp.addJSlibsExport())
        htmlCore.line(vp.axaddJSlibsOverMouseAxisisPopup())

        plotNumber = 0

        from operator import itemgetter

        if choices.showResults == 'Show results for one Gsuite':

            for chr in GenomeInfo.getChrList(gSuite1.genome):
                categories = []
                seriesName = []
                seriesType = []
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite1.genome)
                # results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx = 0
                visRes = []
                plotBandsMax = 0
                for track in tracks:
                    visResTrack = []
                    dataY = []
                    results = doAnalysis(analysisSpec1, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        # print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack = [elDataY[2] for elDataY in dataY]
                    if inx == 0:
                        categories = [str(elDataY[0]) + "-" + str(elDataY[1]) for elDataY in dataY]

                    if max(dataY, key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax = max(dataY, key=itemgetter(2))[2]

                    seriesName.append(track.trackName[-1].replace("'", ''))
                    seriesType.append('line')
                    visRes.append(visResTrack)
                    inx += 1

                htmlCore.line(vp.drawChartMulti([visRes],
                                                plotNumber=plotNumber,
                                                seriesType=[seriesType],
                                                legend=False,
                                                minWidth=300,
                                                height=700,
                                                lineWidth=1,
                                                titleText='Visualization for frequency of mutation along the ' + str(
                                                    chr),
                                                yAxisTitle=['Value'],
                                                seriesName=seriesName,
                                                enabled=True,
                                                categories=categories,
                                                interaction=False,
                                                plotBandsY=[
                                                    int(plotBandsMax - float(choices.visParam) / 100 * plotBandsMax),
                                                    plotBandsMax, '#FDFD96',
                                                    str(choices.visParam) + '% the highest values']
                                                ))
                plotNumber += 1

        if choices.showResults == 'Show results for two Gsuite':

            title1 = choices.gSuite1
            title2 = choices.gSuite2

            import urllib2
            title1 = urllib2.unquote(title1.split('/')[-1])
            title2 = urllib2.unquote(title2.split('/')[-1])

            if choices.statistic2 == 'Count Point':
                analysisSpec2 = AnalysisSpec(CountPointStat)
            elif choices.statistic2 == 'Count Segment':
                analysisSpec2 = AnalysisSpec(CountSegmentStat)
            elif choices.statistic2 == 'Count Proportion':
                analysisSpec2 = AnalysisSpec(ProportionCountPerBinAvgStat)

            # use gSuite from option
            gSuite2 = getGSuiteFromGalaxyTN(choices.gSuite2)

            tracks2 = list(gSuite2.allTracks())

            # visResgSuiteY1=[]
            # visResgSuiteY2=[]

            for chr in GenomeInfo.getChrList(gSuite1.genome):
                categories = []
                seriesName1 = []
                seriesType1 = []
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite1.genome)
                # results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx = 0
                visRes1 = []
                plotBandsMax = 0

                for track in tracks:
                    visResTrack = []
                    dataY = []
                    results = doAnalysis(analysisSpec1, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        # print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack = [elDataY[2] for elDataY in dataY]
                    if inx == 0:
                        categories = [str(elDataY[0]) + "-" + str(elDataY[1]) for elDataY in dataY]

                    if max(dataY, key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax = max(dataY, key=itemgetter(2))[2]

                    seriesName1.append(track.trackName[-1].replace("'", ''))
                    seriesType1.append('line')
                    visRes1.append(visResTrack)
                    inx += 1

                # visResgSuiteY1.append(visRes)

                seriesName2 = []
                seriesType2 = []
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite2.genome)
                # results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx = 0
                visRes2 = []
                plotBandsMax = 0
                for track in tracks2:
                    visResTrack = []
                    dataY = []
                    results = doAnalysis(analysisSpec2, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        # print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack = [elDataY[2] for elDataY in dataY]
                    # if inx ==0:
                    #    categories2=[str(elDataY[0])+"-"+str(elDataY[1]) for elDataY in dataY]

                    if max(dataY, key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax = max(dataY, key=itemgetter(2))[2]

                    seriesName2.append(track.trackName[-1].replace("'", ''))
                    seriesType2.append('line')
                    visRes2.append(visResTrack)
                    inx += 1

                htmlCore.line(vp.drawMultiYAxis(
                    dataY1=visRes1,
                    dataY2=visRes2,
                    categories=categories,
                    titleText='Visualization for the ' + str(chr),
                    minWidth=300,
                    height=700,
                    title1=title1,
                    title2=title2,
                    seriesType1=seriesType1,
                    seriesName1=seriesName1,
                    seriesType2=seriesType2,
                    seriesName2=seriesName2,
                    plotNumber=plotNumber
                ))

                '''
                print title1
                print title2
                print "categories=" + str(categories)
                print "dataY1=" + str(visRes1)
                print "dataY2=" + str(visRes2)
                print "seriesName1=" + str(seriesName1)
                print "seriesName2=" + str(seriesName2)
                print "seriesType1=" + str(seriesType1)
                print "seriesType2=" + str(seriesType2)
                '''

                plotNumber += 1

        htmlCore.divEnd()
        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')
        print htmlCore

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite1)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        if gSuite1.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite1.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite1.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite1.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

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

    # @classmethod
    # def getOptionsBoxFirstKey(cls):  # Alt: getOptionsBox1()
    #     """
    #     Defines the type and contents of the input box. User selections are
    #     returned to the tools in the prevChoices and choices attributes to
    #     other methods. These are lists of results, one for each input box
    #     (in the order specified by getInputBoxOrder()).
    #
    #     Mandatory for the first key defined in getInputBoxNames(), if any.
    #
    #     The input box is defined according to the following syntax:
    #
    #     Selection box:          ['choice1','choice2']
    #     - Returns: string
    #
    #     Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
    #     - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
    #     - The contents is the default value shown inside the text area
    #     - Returns: string
    #
    #     Raw HTML code:          '__rawstr__', 'HTML code'
    #     - This is mainly intended for read only usage. Even though more
    #       advanced hacks are possible, it is discouraged.
    #
    #     Password field:         '__password__'
    #     - Returns: string
    #
    #     Genome selection box:   '__genome__'
    #     - Returns: string
    #
    #     Track selection box:    '__track__'
    #     - Requires genome selection box.
    #     - Returns: colon-separated string denoting track name
    #
    #     History selection box:  ('__history__',) |
    #                             ('__history__', 'bed', 'wig')
    #     - Only history items of specified types are shown.
    #     - Returns: colon-separated string denoting Galaxy dataset info, as
    #         described below.
    #
    #     History check box list: ('__multihistory__', ) |
    #                             ('__multihistory__', 'bed', 'wig')
    #     - Only history items of specified types are shown.
    #     - Returns: OrderedDict with Galaxy dataset ids as key (the number YYYY
    #         as described below), and the associated Galaxy dataset info as the
    #         values, given that the history element is ticked off by the user.
    #         If not, the value is set to None. The Galaxy dataset info structure
    #         is described below.
    #
    #     Hidden field:           ('__hidden__', 'Hidden value')
    #     - Returns: string
    #
    #     Table:                  [['header1','header2'], ['cell1_1','cell1_2'],
    #                              ['cell2_1','cell2_2']]
    #     - Returns: None
    #
    #     Check box list:         OrderedDict([('key1', True), ('key2', False),
    #                                          ('key3', False)])
    #     - Returns: OrderedDict from key to selection status (bool).
    #
    #
    #     ###
    #     Note about the "Galaxy dataset info" data structure:
    #     ###
    #
    #     "Galaxy dataset info" is a list of strings coding information about a
    #     Galaxy history element and its associated dataset, typically used to
    #     provide info on the history element selected by the user as input to a
    #     ProTo tool.
    #
    #     Structure:
    #         ['galaxy', fileFormat, path, name]
    #
    #     Optionally encoded as a single string, delineated by colon:
    #
    #         'galaxy:fileFormat:path:name'
    #
    #     Where:
    #         'galaxy' used for assertions in the code
    #         fileFormat (or suffix) contains the file format of the dataset, as
    #             encoded in the 'format' field of a Galaxy history element.
    #         path (or file name/fn) is the disk path to the dataset file.
    #             Typically ends with 'XXX/dataset_YYYY.dat'. XXX and YYYY are
    #             numbers which are extracted and used as an unique id  of the
    #             dataset in the form [XXX, YYYY]
    #         name is the title of the history element
    #
    #     The different parts can be extracted using the functions
    #     extractFileSuffixFromDatasetInfo(), extractFnFromDatasetInfo(), and
    #     extractNameFromDatasetInfo() from the module CommonFunctions.py.
    #     """
    #     return ['testChoice1', 'testChoice2', '...']

    # @classmethod
    # def getOptionsBoxSecondKey(cls, prevChoices):  # Alt: getOptionsBox2()
    #     """
    #     See getOptionsBoxFirstKey().
    #
    #     prevChoices is a namedtuple of selections made by the user in the
    #     previous input boxes (that is, a namedtuple containing only one element
    #     in this case). The elements can accessed either by index, e.g.
    #     prevChoices[0] for the result of input box 1, or by key, e.g.
    #     prevChoices.key (case 2).
    #
    #     Mandatory for the subsequent keys (after the first key) defined in
    #     getInputBoxNames(), if any.
    #     """
    #     return ''

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

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #     """
    #     Is called when execute-button is pushed by web-user. Should print
    #     output as HTML to standard out, which will be directed to a results
    #     page in Galaxy history. If getOutputFormat is anything else than
    #     'html', the output should be written to the file with path galaxyFn.
    #     If needed, StaticFile can be used to get a path where additional
    #     files can be put (cls, e.g. generated image files). choices is a list
    #     of selections made by web-user in each options box.
    #
    #     Mandatory unless isRedirectTool() returns True.
    #     """
    #     print 'Executing...'

    # @classmethod
    # def validateAndReturnErrors(cls, choices):
    #     """
    #     Should validate the selected input parameters. If the parameters are
    #     not valid, an error text explaining the problem should be returned.
    #     The GUI then shows this text to the user (if not empty) and greys
    #     out the execute button (even if the text is empty). If all
    #     parameters are valid, the method should return None, which enables
    #     the execute button.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

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
        # """
        # Specifies whether the tool is accessible to all users. If False, the
        # tool is only accessible to a restricted set of users as well as admin
        # users, as defined in the galaxy.ini file.
        #
        # Optional method. Default return value if method is not defined: False
        # """
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
    @classmethod
    def getToolDescription(cls):
        """
        Specifies a help text in HTML that is displayed below the tool.

        Optional method. Default return value if method is not defined: ''
        """

        l = Legend()

        toolDescription = 'Generates a plot summarizing the number of mutations along each chromosome.A second GSuite can also be inputted and visualized, where the first GSuite is shown on the bottom end of the plot while the second is shown at the top of the plot.Count points or count segments can be utilized as a statistic, where count point will show each individual point (recommended for bed files containing SNPs) and count segment will show track segments, therefore this should be used to illustrate lengths of genomic areas of interest. For example, the dispersion of intronic or exonic areas of the chromosomes.Note that GSuits (or hGSuites) submitted should be preprocessed. Increasing the bin will lower the amount of detailed information in the plot but make its  execution faster while reducing it will do the opposite. Bins below 10000 are not recommended. Doing so may result in files too big to be opened.'

        stepsToRunTool = ['Select if you want to plot one or two Gsuites',
                          'Select Gsuite',
                          'Select statistic (count point / count segment)',
                          'Select the number of highest values you want to see on the plot ',
                          'Define the bin size (default is 1000000)'
                          ]
        toolResult = 'The results are presented in a interactive chart (png, pdf).'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          )
        return ''

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
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     """
    #     The format of the history element with the output of the tool. Note
    #     that if 'html' is returned, any print statements in the execute()
    #     method is printed to the output dataset. For text-based output
    #     (e.g. bed) the output dataset only contains text written to the
    #     galaxyFn file, while all print statements are redirected to the info
    #     field of the history item box.
    #
    #     Note that for 'html' output, standard HTML header and footer code is
    #     added to the output dataset. If one wants to write the complete HTML
    #     page, use the restricted output format 'customhtml' instead.
    #
    #     Optional method. Default return value if method is not defined:
    #     'html'
    #     """
    #     return 'html'
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
