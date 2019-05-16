from collections import OrderedDict

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteComposer import composeToFile
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from proto.CommonFunctions import ensurePathExists
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.CountDescriptiveStatisticBetweenHGsuiteTool import \
    CountDescriptiveStatisticBetweenHGsuiteTool
from quick.webtools.hgsuite.Legend import Legend


class DivideHgSuiteAccordingToColumnTool(GeneralGuiTool):

    DIVISION_BY_COLUMN = 'by column'
    DIVISION_BY_PHRASE = 'by phrase in column'
    DIVISION_BY_VALUE = 'by value'
    TITLE = 'title'
    NUM_CATEGORY_FIELDS = 5
    PHRASE = '-- select --'
    ACTION = ['<', '<=', '=', '>=', '>']

    DIVISION = [DIVISION_BY_COLUMN, DIVISION_BY_PHRASE, DIVISION_BY_VALUE]


    @classmethod
    def getToolName(cls):
        return "Divide/Filter hGSuite according to metadata"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select hGSuite', 'gSuite'),
                ('Select division', 'division')] + \
                [('Select column %s' % (i+1) + '','selectedColumns%s' % i) for i in range(cls.NUM_CATEGORY_FIELDS)] + \
               [('Select %s' % (i) + '', 'selectedColumnsValues%s' % i) for i in
                range(cls.NUM_CATEGORY_FIELDS)] + \
               [('Select value %s' % (i) + '', 'selectedValues%s' % i) for i in
                range(cls.NUM_CATEGORY_FIELDS)] + \
                [('Select column', 'column'),
                ('Show possible phrases', 'possibleColumns'),
                ('Select phrases (use commma to provide more than one phrase)', 'param'),
                ('Add phrases separately', 'add')
                ]

    @classmethod
    def getOptionsBoxGSuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxDivision(cls, prevChoices):
        return cls.DIVISION

    @classmethod
    def _getOptionsBoxForSelectedColumns(cls, prevChoices, index):

        if prevChoices.gSuite:
            if prevChoices.division.encode('utf-8') == cls.DIVISION_BY_VALUE:
                attr = cls._getNotStringColumns(prevChoices.gSuite)
                selectionList = []
                if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumns%s' % i) for i in
                           xrange(index)):
                    selectionList = attr

                if selectionList:
                    return selectionList

    @classmethod
    def setupSelectedColumnsMethods(cls):
        from functools import partial
        for i in xrange(cls.NUM_CATEGORY_FIELDS):
            setattr(cls, 'getOptionsBoxSelectedColumns%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumns, index=i))

    @classmethod
    def _getOptionsBoxForSelectedColumnsValues(cls, prevChoices, index):
        if prevChoices.gSuite:
            if prevChoices.division.encode('utf-8') == cls.DIVISION_BY_VALUE:
                if len([getattr(prevChoices, 'selectedColumns%s' % i) for i in xrange(index)]) != 0:
                    if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumns%s' % i) for i in
                               xrange(index)):
                        return cls.ACTION

    @classmethod
    def setupSelectedColumnsValuesMethods(cls):
        from functools import partial
        for i in xrange(cls.NUM_CATEGORY_FIELDS):
            setattr(cls, 'getOptionsBoxSelectedColumnsValues%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumnsValues, index=i))

    @classmethod
    def _getOptionsBoxForSelectedValues(cls, prevChoices, index):
        if prevChoices.gSuite:
            if prevChoices.division.encode('utf-8') == cls.DIVISION_BY_VALUE:
                if len([getattr(prevChoices, 'selectedColumns%s' % i) for i in xrange(index)]) != 0:
                    if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumns%s' % i) for i in
                               xrange(index)):
                        return ''

    @classmethod
    def setupSelectedValuesMethods(cls):
        from functools import partial
        for i in xrange(cls.NUM_CATEGORY_FIELDS):
            setattr(cls, 'getOptionsBoxSelectedValues%s' % i,
                    partial(cls._getOptionsBoxForSelectedValues, index=i))

    @classmethod
    def getOptionsBoxColumn(cls, prevChoices):
        if prevChoices.gSuite:
            if prevChoices.division.encode('utf-8') in [cls.DIVISION_BY_PHRASE,
                                                        cls.DIVISION_BY_COLUMN]:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
                if prevChoices.division.encode('utf-8') == cls.DIVISION_BY_COLUMN:
                    return gSuite.attributes
                if prevChoices.division.encode('utf-8') == cls.DIVISION_BY_PHRASE:
                    return [cls.TITLE] + gSuite.attributes

    @classmethod
    def getOptionsBoxPossibleColumns(cls, prevChoices):

        if prevChoices.gSuite:
            if prevChoices.division.encode('utf-8') in [cls.DIVISION_BY_PHRASE, cls.DIVISION_BY_COLUMN]:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)

                tableElements = [['Unique phrases']]
                for a in gSuite.getAttributeValueList(prevChoices.column.encode('utf-8')):
                    if not [a] in tableElements:
                        tableElements.append([a])
                return tableElements

    @classmethod
    def getOptionsBoxParam(cls, prevChoices):
        if prevChoices.gSuite and prevChoices.division == cls.DIVISION_BY_PHRASE:
            return ''

    @classmethod
    def getOptionsBoxAdd(cls, prevChoices):
        if prevChoices.gSuite and prevChoices.param and prevChoices.division == cls.DIVISION_BY_PHRASE:
            par = prevChoices.param.replace(' ', '').split(',')
            #
            # lenPar = 0
            # tf = False
            # for pNum, p in enumerate(par):
            #     if pNum == 0:
            #         lenPar = len(p)
            #     if lenPar == len(p):
            #         tf = True
            #     else:
            #         tf = False
            #
            # if tf == True:
            if len(par) >= 2:
                return ['yes', 'no']


    @classmethod
    def rename(cls, dictionary, oldkey, newkey):
        if newkey != oldkey:
            dictionary[newkey] = dictionary[oldkey]
            del dictionary[oldkey]

    @classmethod
    def _getNotStringColumns(cls, choice):
        gSuite = getGSuiteFromGalaxyTN(choice)
        attributeList = gSuite.attributes

        attributeFilteredList = []
        for i, iTrack in enumerate(gSuite.allTracks()):
            if i == 0:
                for aN, a in enumerate(attributeList):
                    attr = iTrack.getAttribute(a.encode('utf-8'))
                    try:
                        float(attr)
                        if not a in attributeFilteredList:
                            attributeFilteredList.append(a)
                    except:
                        pass

        return [cls.PHRASE] + attributeFilteredList

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        column = choices.column.encode('utf-8')

        trackList = {}
        if choices.division == cls.DIVISION_BY_COLUMN:
            for i, iTrack in enumerate(gSuite.allTracks()):
                attr = iTrack.getAttribute(column)
                if not attr in trackList.keys():
                    trackList[attr] = []
                trackList[attr].append(i)

            if None in trackList.keys():
                cls.rename(trackList, None, 'Remaining')
            cls.buildNewGsuites(gSuite, trackList)

        if choices.division == cls.DIVISION_BY_PHRASE:
            par = choices.param.replace(' ', '').split(',')


            if choices.add in ['yes', 'no']:
                add = choices.add
            else:
                add = 'no'

            if add == 'no':
                trackList[('-'.join([p.encode('utf-8') for p in par]))] = []
            else:
                for p in par:
                    trackList[p.encode('utf-8')] = []

            for i, iTrack in enumerate(gSuite.allTracks()):
                if column == cls.TITLE:
                    t = iTrack.title
                else:
                    try:
                        t = iTrack.getAttribute(column)
                    except:
                        t = '.'

                for p in par:
                    if t != None:
                        if p in t:
                            if add == 'no':
                                trackList[('-'.join(par))].append(i)
                            else:
                                trackList[p].append(i)

            cls.buildNewGsuites(gSuite, trackList)

        if choices.division == cls.DIVISION_BY_VALUE:
            selectedColumns = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                         'selectedColumns%s',
                                                                                         cls.NUM_CATEGORY_FIELDS)
            selectedColumnsValues = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(
                choices,
                'selectedColumnsValues%s',
                cls.NUM_CATEGORY_FIELDS)
            selectedValues = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(
                choices,
                'selectedValues%s',
                cls.NUM_CATEGORY_FIELDS)

            filterQuestionsDict = cls._parseQuestions(selectedColumns, selectedColumnsValues, selectedValues, gSuite)
            trackDict = cls._parseGsuiteByQuestion(gSuite, filterQuestionsDict)
            filterResult = cls._filterResults(filterQuestionsDict, trackDict)
            cls._selectRowsFromGSuiteByTitle(gSuite, filterResult)


        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.paragraph('Divided hGSuite is in the history.')
        htmlCore.end()

        print htmlCore

    @classmethod
    def _selectRowsFromGSuiteByTitle(cls, gSuite, titleList):

        outputGSuite = GSuite()
        url = cls.makeHistElement(galaxyExt='gsuite', title=str('GSuite'))
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

        GSuiteComposer.composeToFile(outputGSuite, url)

    @classmethod
    def _parseGsuiteByQuestion(cls, gSuite, filterQuestionsDict):

        trackDict = OrderedDict()
        for i, iTrack in enumerate(gSuite.allTracks()):
            trackTitle = str(iTrack.title)
            if not trackTitle in trackDict.keys():
                trackDict[trackTitle] = {}
                for fq in filterQuestionsDict.keys():
                    trackDict[trackTitle][fq] = iTrack.getAttribute(fq)

        return trackDict

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
    def _filterValues(cls, valTrack, action, valUser):

        if str(valTrack) == None or str(valTrack) == '.':
            return 1
        else:
            valAction = eval(str(valTrack) + action + str(valUser))

        if valAction == False:
            return 1
        else:
            return 0

    @classmethod
    def _parseQuestions(cls, selectedColumns, selectedColumnsValues, selectedValues, gSuite):

        filterQuestionsDict = OrderedDict()
        for sc, selCol in enumerate(selectedColumns):
            if selCol != cls.PHRASE:
                option = selCol.encode('utf-8')
                if not option in filterQuestionsDict.keys():
                    filterQuestionsDict[option] = {}
                selVal = selectedValues[sc]
                if '%' in selVal:
                    numPercentage = float(selVal.replace('%', ''))
                    allValues = []
                    for v in gSuite.getAttributeValueList(option):
                        if v != None and v != 'null':
                            allValues.append(float(v))
                    allValues = sorted(allValues, reverse=False)
                    howManyFromPercentage = int(numPercentage / 100 * len(allValues))
                    filterQuestionsDict[option][selectedColumnsValues[sc].encode('utf-8')] = float(
                        allValues[howManyFromPercentage])

                else:
                    filterQuestionsDict[option][selectedColumnsValues[sc].encode('utf-8')] = float(
                        selectedValues[sc])

        return filterQuestionsDict

    @classmethod
    def buildNewGsuites(cls, gSuite, trackList):
        for tl in trackList.keys():

            outputGSuite = GSuite()
            url = cls.makeHistElement(galaxyExt='gsuite', title=str(tl.replace('_','')))

            for t in trackList[tl]:
                track = gSuite.getTrackFromIndex(t)
                attributes = OrderedDict()
                for key in gSuite.attributes:
                    try:
                        attributes[key] = track.attributes[key]
                    except:
                        attributes[key] = '.'
                gs = GSuiteTrack(track.uri, title=track.title, genome=gSuite.genome,
                                 attributes=attributes)

                outputGSuite.addTrack(gs)

            GSuiteComposer.composeToFile(outputGSuite, url)

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gSuite:
            return 'Please select hGSuite'

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

        toolDescription = 'This tool divide hGSuite in the two possible ways. <br>' \
                          'The first one is division according to selected column, ' \
                          'the second one is division according to selected phrases.'

        stepsToRunTool = ['Select hGSuite',
                          'Select division',
                          'Select column',
                          'Select phrases (use colon to provide more than one phrase)',
                          'Add phrases separately'
                          ]

        toolResult = 'The output of this tool is one or many hGsuites.'

        notice = 'The name of the output hGSuite is the same as phrases in the selecetd column.'

        example = OrderedDict()
        example['Example 1 - Division by column'] = ['',
            ["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title     T-cells B-cells
    hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	.
    hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	X
    hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.
    hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	.
    hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.
    """],
                   [['Select division', 'by column'], ['Select column', 't-cells']],
                   [["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title     T-cells B-cells
    hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	.
    hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	.
        """],
["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title     T-cells B-cells
    hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	X
    hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.
    hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.
        """],
                    ]
                   ]

        example['Example 2 - Division by phrase'] = ['',["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title    t-cells  t-cells-b-cells  b-cells
    hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	t-cells	      .
    hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	b-cells	      X
    hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.	      .
    hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	t-cells	      .
    hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.	      .
            """],
        [['Select division', 'by phrase'],
         ['Select column', 't-cells-b-cells'],
         ['Select phrases (use colon to provide more than one phrase)', 't-cells,b-cells'],
         ['Add phrases separately', 'no']],
                        [["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title    t-cells  t-cells-b-cells  b-cells
    hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	t-cells	      .
    hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	b-cells	      X
    hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	t-cells	      .
        """],
                                 ]
                                ]

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example,
                                          notice=notice)
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
    def getInputBoxOrder(cls):

        selectedColumns = ['selectedColumns%s' % i for i in range(cls.NUM_CATEGORY_FIELDS)]
        selectedColumnsValues = ['selectedColumnsValues%s' % i for i in range(cls.NUM_CATEGORY_FIELDS)]
        selectedValues = ['selectedValues%s' % i for i in range(cls.NUM_CATEGORY_FIELDS)]
        optionFlatList = [item for sublist in zip(selectedColumns, selectedColumnsValues, selectedValues) for item in sublist]

        return ['gSuite'] + \
               ['division'] + \
                optionFlatList +\
               ['column', 'possibleColumns', 'param', 'add']

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
DivideHgSuiteAccordingToColumnTool.setupSelectedColumnsMethods()
DivideHgSuiteAccordingToColumnTool.setupSelectedColumnsValuesMethods()
DivideHgSuiteAccordingToColumnTool.setupSelectedValuesMethods()