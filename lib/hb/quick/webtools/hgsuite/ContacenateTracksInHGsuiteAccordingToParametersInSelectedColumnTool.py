from collections import OrderedDict
from functools import partial

import operator

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from proto.CommonFunctions import ensurePathExists
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.HGsuiteClass import HGsuite
from quick.webtools.hgsuite.Legend import Legend


class ContacenateTracksInHGsuiteAccordingToParametersInSelectedColumnTool(GeneralGuiTool):

    MAX_NUM_OF_COLS=15
    PHRASE = 'select phrase'
    COMBINED_SIGN = '-----'

    @classmethod
    def getToolName(cls):
        return "Concatenate tracks in hGSuite based on metadata"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select hGSuite', 'gSuite'),
                ('Select column, you want to use to combine tracks', 'column'),
                ('Show possible keywords', 'possibleColumns')
        ] + \
                [('Select keyword %s' % (i+1) + ', you want to combain (use colon to combine)', 'selectedColumns%s' % i) for i \
                 in range(cls.MAX_NUM_OF_COLS)] + \
                [('Select column %s' % (i+1) + ' which you would like to treat as unique (datasets will be combain separately to selected groups)', 'excludedColumns%s' % i) for i \
                 in range(cls.MAX_NUM_OF_COLS)]

    @classmethod
    def getOptionsBoxGSuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxColumn(cls, prevChoices):
        if prevChoices.gSuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            return gSuiteTN.attributes

    @classmethod
    def getOptionsBoxPossibleColumns(cls, prevChoices):

        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)

            tableElements = [['Unique phrases']]
            for a in gSuite.getAttributeValueList(prevChoices.column.encode('utf-8')):
                if not [a] in tableElements:
                    tableElements.append([a])
            return tableElements


    @classmethod
    def _getOptionsBoxForSelectedColumns(cls, prevChoices, index):

        if prevChoices.gSuite:

            selectionList=''
            if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumns%s' % i) for i in xrange(index)):
                selectionList = cls.PHRASE

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedColumnsMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedColumns%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumns, index=i))


    @classmethod
    def _getOptionsBoxForExcludedColumns(cls, prevChoices, index):

        if prevChoices.gSuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            attr = gSuiteTN.attributes

            #exclude selected column from attributes
            attr = list(set(attr) - set([prevChoices.column]))
            selectionList=[]
            if index < len(attr):
                if not any('None' in getattr(prevChoices, 'excludedColumns%s' % i) for i in xrange(index)):
                    selectionList = ['None']+attr

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectExcludeColumnsMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxExcludedColumns%s' % i,
                    partial(cls._getOptionsBoxForExcludedColumns, index=i))

    @classmethod
    def _getSelectedPhrases(cls, choices):

        cols = [getattr(choices, 'selectedColumns%s' % i) for i in range(0, cls.MAX_NUM_OF_COLS)]
        selectedCols = []
        for c in cols:
            c = c.encode('utf-8')
            if c != cls.PHRASE and c != '':
                selectedCols.append(c)

        return selectedCols

    @classmethod
    def _getExcludedColumns(cls, choices):

        cols = [getattr(choices, 'excludedColumns%s' % i) for i in range(0, cls.MAX_NUM_OF_COLS)]
        excludedCols = []
        for c in cols:
            if c != 'None' and c!= '':
                c = c.encode('utf-8')
                excludedCols.append(c)

        return excludedCols

    @classmethod
    def _getSelectedPhrases(cls, choices):

        cols = [getattr(choices, 'selectedColumns%s' % i) for i in range(0, cls.MAX_NUM_OF_COLS)]
        selectedCols = []
        for c in cols:
            c = c.encode('utf-8')
            if c != cls.PHRASE and c != '':
                selectedCols.append(c)

        return selectedCols

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        column = choices.column.encode('utf-8')
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        phraseList = [a.strip(' ').split(',') for a in cls._getSelectedPhrases(choices)]

        excludedList = cls._getExcludedColumns(choices)

        whichTracksWillBeCombinedTogether = cls._getDictOfCombinedTracks(gSuite, excludedList, phraseList, column)

        outputGSuite = GSuite()
        for k, data in whichTracksWillBeCombinedTogether.iteritems():
            for id, d in enumerate(data):

                attr = OrderedDict()
                #metadata
                trackData = phraseList[id]
                name = '-'.join(k)

                attr[column] = str('-'.join(trackData))
                for eNum, e in enumerate(excludedList):
                    attr[e] = str(k[eNum])

                pathTracks = []
                for p in d:
                    track = gSuite.getTrackFromIndex(p)
                    pathTracks.append(track.path)

                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                    extraFileName=str(name) + '--' + str('-'.join(trackData)),
                                                    suffix='bed')
                gSuiteTrack = GSuiteTrack(uri)
                outFn = gSuiteTrack.path
                ensurePathExists(outFn)

                with open(outFn, 'wb') as newf:
                    lines = []
                    for filename in pathTracks:
                        with open(filename, 'rb') as hf:
                            #sorting bed file
                            for l in hf.readlines():
                                lStrip = l.strip('\n').split('\t')
                                lStripNew = []
                                for l in lStrip:
                                    try:
                                        l = int(l)
                                    except:
                                        l = l
                                    lStripNew.append(l)
                                lines.append(lStripNew)
                            # newf.write(hf.read())
                    lines.sort(key=operator.itemgetter(0, 1, 2))
                    for l in lines:
                        newf.write(('\t').join([str(ll) for ll in l ])+'\n')



                gs = GSuiteTrack(uri, title=''.join(
                    str(name) + '--' + str('-'.join(trackData))), genome=gSuite.genome,
                                 attributes=attr)

                outputGSuite.addTrack(gs)

            GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def _getDictOfCombinedTracks(cls, gSuite, excludedList, phraseList, column):
        whichTracksWillBeCombinedTogether = {}
        for i, iTrack in enumerate(gSuite.allTracks()):

            excludedColumn = []
            for attrName in excludedList:
                excludedColumn.append(iTrack.getAttribute(attrName))
            excludedColumn = tuple(excludedColumn)

            if not excludedColumn in whichTracksWillBeCombinedTogether.keys():
                whichTracksWillBeCombinedTogether[excludedColumn] = []
                for p in phraseList:
                    whichTracksWillBeCombinedTogether[excludedColumn].append([])

            phrase = iTrack.getAttribute(column)
            # print phraseList, phrase, '<br>'
            j = cls._getPhraseIndex(phraseList, phrase)
            # print 'excludedColumn=', excludedColumn, ' i=', i, ' j=', j, '<br>'
            if j != None:
                whichTracksWillBeCombinedTogether[excludedColumn][j] += [i]
        return  whichTracksWillBeCombinedTogether

    @classmethod
    def _getPhraseIndex(cls, phraseList, phrase):
        for j, p in enumerate(phraseList):
            if phrase in p:
                return j

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gSuite:
            return 'Please select hGSuite.'

        if choices.gSuite:
            gsuite = getGSuiteFromGalaxyTN(choices.gSuite)
            if gsuite.isPreprocessed():
                return 'hGSuite need to primary.'

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

        toolDescription = 'This tool concatenate tracks in hGSuite according to selected phrases in the selected columns..'

        stepsToRunTool = ['Select hGSuite',
                          'Select column, you want to use to combain tracks',
                          'Select phrase 1, you want to combain (use colon to combain) ',
                          'Select column 1 which you would like to treat as unique'
                          ]

        example = {'Example': ['', ["""
        ##location: local
        ##file format: primary
        ##track type: unknown
        ##genome: mm10
        ###uri	title	mutation	genotype
        galaxy:/path/track1.bed	track1	CA	eta
        galaxy:/path/track2.bed	track2	TA	eta
        galaxy:/path/track3.bed	track3	CA	iota
        galaxy:/path/track4.bed	track4	TA	iota
        """],
                               [['Select hGSuite: ', 'gsuite'],
                                ['Select column, you want to use to combain tracks', 'mutation'],
                                ['Select phrase 1, you want to combain (use colon to combain) ', 'CA,TA'],
                                ['Select phrase 2, you want to combain (use colon to combain) ', 'select phrase'],
                                ['Select column 1 which you would like to treat as unique', 'genotype'],
                                ['Select column 2 which you would like to treat as unique', 'None']
                                ],
                               ["""
        ##location: local
        ##file format: primary
        ##track type: unknown
        ##genome: mm10
        ###uri	title	mutation	genotype
        galaxy:/path/track1.bed	track5  title1	CA-TA	eta
        galaxy:/path/track2.bed	track6  title2	CA-TA	iota
        """
                                ]
                               ]}

        toolResult = 'The output of this tool is hGsuite with concatenated tracks according to selected parameters.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example)

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

ContacenateTracksInHGsuiteAccordingToParametersInSelectedColumnTool.setupSelectedColumnsMethods()
ContacenateTracksInHGsuiteAccordingToParametersInSelectedColumnTool.setupSelectExcludeColumnsMethods()