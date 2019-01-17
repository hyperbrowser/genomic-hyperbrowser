import ast
from collections import OrderedDict
from functools import partial

from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteComposer import composeToFile, composeToString
from gold.gsuite.GSuiteTrack import GSuiteTrack
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.Legend import Legend


class FilterCategoricalGSuiteTool(GeneralGuiTool):

    NUM_CATEGORY_FIELDS = 5
    NULL_OPTION = '-- select --'
    ACTION = ['<', '<=', '=', '>=', '>']
    FILTER_BY_VAl = 'select tracks by value'
    FILTER_BY_DATA = 'select data in column'
    TITLE = 'title'

    @classmethod
    def getToolName(cls):
        return "Filter hGSuite"

    @classmethod
    def getInputBoxNames(cls):
        return ['Select hGSuite'] + \
               ['Select operation'] + \
               ['Select column: ', 'Select: ', 'Select value: '] * cls.NUM_CATEGORY_FIELDS

    @classmethod
    def getOptionsBox1(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBox2(cls, prevChoices):
        if not prevChoices[0]:
            return
        return [cls.FILTER_BY_VAl, cls.FILTER_BY_DATA]

    @classmethod
    def getOptionsBox3(cls, prevChoices):
        if not prevChoices[0]:
            return

        if prevChoices[1] == cls.FILTER_BY_VAl:
            return cls._getNotStringColumns(prevChoices[0])
        if prevChoices[1] == cls.FILTER_BY_DATA:
            return cls._getAllColumns(prevChoices[0], prevChoices, None)


    @classmethod
    def getOptionsBox4(cls, prevChoices):
        if not prevChoices[2]:
            return

        if prevChoices[2] == cls.NULL_OPTION:
            return

        if prevChoices[1] == cls.FILTER_BY_VAl:
            return cls.ACTION
        if prevChoices[1] == cls.FILTER_BY_DATA:
            return cls._getAllUniqueData(prevChoices[0], prevChoices[2])

    @classmethod
    def getOptionsBox5(cls, prevChoices):
        if not prevChoices[2]:
            return

        if prevChoices[2] == cls.NULL_OPTION:
            return

        if prevChoices[1] == cls.FILTER_BY_VAl:
            return ''
        return

    @classmethod
    def setupCategoryFields(cls):
        for i in xrange(cls.NUM_CATEGORY_FIELDS):
            setattr(cls, 'getOptionsBox%i' % (i * 3 + 6),
                    partial(cls._getColumn, index=i * 3 + 6))
            setattr(cls, 'getOptionsBox%i' % (i * 3 + 6 + 1),
                    partial(cls._getAction, index=i * 3 + 6 + 1))
            setattr(cls, 'getOptionsBox%i' % (i * 3 + 6 + 2),
                    partial(cls._getValue, index=i * 3 + 6 + 2))

    @classmethod
    def _getColumn(cls, prevChoices, index):
        if not prevChoices[0]:
            return

        if prevChoices[2] == cls.NULL_OPTION:
            return

        dd=''
        for i in range(0, int(index/3)):
            dd += str(prevChoices[i*3+6-4])
            if prevChoices[i*3+6-4] == cls.NULL_OPTION:
                return

        if prevChoices[1] == cls.FILTER_BY_VAl:
            return cls._getNotStringColumns(prevChoices[0])
        if prevChoices[1] == cls.FILTER_BY_DATA:
            return cls._getAllColumns(prevChoices[0], prevChoices, index)


    @classmethod
    def _getAction(cls, prevChoices, index):
        if not prevChoices[0]:
            return

        for i in range(2, index):
            if i - 3 % 3 != 0:
                if prevChoices[i] == cls.NULL_OPTION:
                    return

        if prevChoices[1] == cls.FILTER_BY_VAl:
            return cls.ACTION
        if prevChoices[1] == cls.FILTER_BY_DATA:
            return cls._getAllUniqueData(prevChoices[0], prevChoices[index-2])

    @classmethod
    def _getValue(cls, prevChoices, index):
        if not prevChoices[0]:
            return

        for i in range(2, index):
            if i - 4 % 3 != 0:
                if prevChoices[i] == cls.NULL_OPTION:
                    return

        if prevChoices[1] == cls.FILTER_BY_VAl:
            return ''
        return

    @classmethod
    def _getNotStringColumns(cls, choice):
        gSuite = getGSuiteFromGalaxyTN(choice)
        attributeList = gSuite.attributes

        attributeFilteredList = []
        for i, iTrack in enumerate(gSuite.allTracks()):
            if i == 0:
                for aN, a in enumerate(attributeList):
                    attr = iTrack.getAttribute(a)
                    try:
                        float(attr)
                        if not a in attributeFilteredList:
                            attributeFilteredList.append(a)
                    except:
                        pass

        return [cls.NULL_OPTION] + attributeFilteredList

    @classmethod
    def _getAllColumns(cls, choice, prevChoices, index):
        gSuite = getGSuiteFromGalaxyTN(choice)
        attributeList = gSuite.attributes

        attributeFilteredList = []
        for i, iTrack in enumerate(gSuite.allTracks()):
            if i == 0:
                previousColumn = []
                if index != None:
                    for i in range(0, index-1):
                        if (i + 1) % 3 == 0:
                            previousColumn.append(prevChoices[i])

                for aN, a in enumerate(attributeList):
                    if not a in attributeFilteredList:
                        attributeFilteredList.append(a)

                attributeFilteredList = list(set(attributeFilteredList) - set(previousColumn))

        return [cls.NULL_OPTION] + [cls.TITLE] + attributeFilteredList

    @classmethod
    def _getAllUniqueData(cls, gsuite, column):
        gSuite = getGSuiteFromGalaxyTN(gsuite)
        d = OrderedDict()
        if column != cls.NULL_OPTION and column!= None:
            if column == cls.TITLE:
                data = gSuite.allTrackTitles()
            else:
                data = []
                for tr in gSuite.allTracks():
                    if tr.getAttribute(column.encode('utf-8')) == None:
                        data.append('.')
                    else:
                        data.append(tr.getAttribute(column))

                #data = list(set(gSuite.getAttributeValueList(column)))
                data = list(set(data))
            if len(data)>0:
                for l in data:
                    d[str(l)] = str(l)

            return d

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gSuite = getGSuiteFromGalaxyTN(choices[0])

        if choices[1] == cls.FILTER_BY_VAl:
            filterQuestionsDict = cls._parseQuestions(choices, gSuite)
            trackDict = cls._parseGsuiteByQuestion(choices, gSuite, filterQuestionsDict)
            filterResult = cls._filterResults(filterQuestionsDict, trackDict)

        if choices[1] == cls.FILTER_BY_DATA:
            filterQuestionsDict = cls._parseQuestionsData(choices)
            filterResult = cls._parseGsuiteByQuestionData(gSuite, filterQuestionsDict)

        filteredGSuite = cls._selectRowsFromGSuiteByTitle(gSuite, filterResult)

        composeToFile(filteredGSuite, galaxyFn)

    @classmethod
    def _filterResults(cls, filterQuestionsDict, trackDict):
        filterResult = []
        for trackName in trackDict.keys():
            countResults = 0
            for fq in filterQuestionsDict.keys():
                for f in filterQuestionsDict[fq].keys():
                    valTrack = trackDict[trackName][fq]
                    valUser = filterQuestionsDict[fq][f]

                    if valTrack == None or valTrack == 'nan':
                        countResults += 1
                    else:
                        countResults += cls._filterValues(valTrack, f, valUser)

            if countResults == 0:
                filterResult.append(trackName)

        return filterResult

    @classmethod
    def _selectRowsFromGSuiteByTitle(cls, gSuite, titleList):

        outputGSuite = GSuite()
        for title in titleList:
            tr = gSuite.getTrackFromTitle(title)
            uri = tr.uri

            attrDict = OrderedDict()
            for a in gSuite.attributes:
                if tr.getAttribute(a) == None:
                    attrDict[a] = '.'
                else:
                    attrDict[a] = tr.getAttribute(a)

            gs = GSuiteTrack(uri, title=title, genome=gSuite.genome,
                             attributes=attrDict)
            outputGSuite.addTrack(gs)

        return outputGSuite

        #
        # reducedTrackList = [gSuite.getTrackFromTitle(title) for title in titleList]
        # reducedGSuite = GSuite(trackList=reducedTrackList)
        # return reducedGSuite


    @classmethod
    def _filterValues(cls, valTrack, action, valUser):

        valAction = eval(str(valTrack) + action + str(valUser))

        if valAction == False:
            return 1
        else:
            return 0

    @classmethod
    def _parseGsuiteByQuestionData(cls, gSuite, filterQuestionsDict):

        trackTitleList = []
        allTracksToNotInclude = []
        for i, iTrack in enumerate(gSuite.allTracks()):
            trackTitle = str(iTrack.title)
            for fq in filterQuestionsDict.keys():
                if iTrack.getAttribute(fq) in filterQuestionsDict[fq]:
                    allTracksToNotInclude.append(trackTitle)
                elif '.' in filterQuestionsDict[fq]:
                    if iTrack.getAttribute(fq) == None:
                        allTracksToNotInclude.append(trackTitle)
                    else:
                        trackTitleList.append(trackTitle)
                else:
                    if not trackTitle in allTracksToNotInclude:
                        trackTitleList.append(trackTitle)

        return list(set(trackTitleList) - set(allTracksToNotInclude))

    @classmethod
    def _parseGsuiteByQuestion(cls, choices, gSuite, filterQuestionsDict):

        trackDict = OrderedDict()
        for i, iTrack in enumerate(gSuite.allTracks()):
            trackTitle = str(iTrack.title)
            if not trackTitle in trackDict.keys():
                trackDict[trackTitle] = {}
                for fq in filterQuestionsDict.keys():
                    trackDict[trackTitle][fq] = iTrack.getAttribute(fq)

        return trackDict

    @classmethod
    def _parseQuestionsData(cls, choices):

        filterQuestionsDict = OrderedDict()
        for i in xrange(2, cls.NUM_CATEGORY_FIELDS * 3 + 1):
            if (i - 2) % 3 == 0:
                if choices[i] != cls.NULL_OPTION and choices[i] != '':
                    option = choices[i].encode('utf-8')
                    filterQuestionsDict[option] = [kCh for kCh, iCh in choices[i + 1].iteritems() if iCh == False]

        return filterQuestionsDict

    @classmethod
    def _parseQuestions(cls, choices, gSuite):

        filterQuestionsDict = OrderedDict()
        for i in xrange(2, cls.NUM_CATEGORY_FIELDS * 3 + 1):
            if (i - 2) % 3 == 0:
                if choices[i] != cls.NULL_OPTION and choices[i] != '':
                    option = choices[i].encode('utf-8')
                    if not option in filterQuestionsDict.keys():
                        filterQuestionsDict[option] = {}
                    if '%' in choices[i + 2]:
                        numPercentage = float(choices[i + 2].replace('%',''))
                        allValues = []
                        for v in gSuite.getAttributeValueList(choices[i]):
                            if v != None and v != 'null':
                                allValues.append(float(v))
                        allValues = sorted(allValues, reverse=False)
                        howManyFromPercentage = int(numPercentage/100 * len(allValues))
                        filterQuestionsDict[option][choices[i + 1].encode('utf-8')] = float(allValues[howManyFromPercentage])

                    else:
                        filterQuestionsDict[option][choices[i + 1].encode('utf-8')] = float(choices[i + 2])
        return filterQuestionsDict

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices[0]:
            return 'Please select hGSuite'

        if choices[0]:
            if choices[1] == cls.FILTER_BY_VAl:
                if len(cls._getNotStringColumns(choices[0])) == 1:
                    return 'The gSuite does not contain any numbered column'
                else:
                    if choices[3] == cls.NULL_OPTION:
                        return 'Please select at least one column'
                    else:
                        if choices[4] == '':
                            return 'Please define value'

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

        l = Legend()

        toolDescription = "This tool filter hGSuite according to track's value."

        stepsToRunTool = ['Select hGSuite',
                          'Select operation',
                          'Select column'
                          ]

        example = {'Example 1 - select tracks by value': ['', ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: hg19
        ###uri          	                                  title     T-cells B-cells   Coverage
        hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	.       100
        hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	X       .
        hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.       1500
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	.       .
        hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.       1200
            """],
           [
               ['Select hGSuite', 'gsuite'],
               ['Select operation', 'select tracks by value'],
               ['Select column', 'coverage'],
               ['Select', '>='],
               ['Select value', '1200']

           ],
           ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: hg19
        ###uri          	                                  title     T-cells B-cells   Coverage
        hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.       1500
        hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.       1200
        """
                            ]
                           ],
        'Example 2 - select data in column': ['', ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: hg19
        ###uri          	                                  title     T-cells B-cells   Coverage
        hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	.       100
        hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	X       .
        hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.       1500
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	.       .
        hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.       1200
           """],
           [
               ['Select hGSuite', 'gsuite'],
               ['Select operation', 'select data in column'],
               ['Select column', 't-cells'],
               ['Select', 'X'],
               ['Select value', '1200'],
               ['Select column', 'coverage'],
               ['Select', '1200, 100']
           ],
           ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: hg19
        ###uri          	                                  title     T-cells B-cells   Coverage
        hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	.       100
        """
            ]
           ]
                   }

        toolResult = 'The output of this tool is filtered hGsuite.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example)


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
        return 'gsuite'
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

FilterCategoricalGSuiteTool.setupCategoryFields()