import ast
from collections import OrderedDict
from functools import partial

from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteComposer import composeToFile
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class FilterCategoricalGSuiteTool(GeneralGuiTool):
    NUM_CATEGORY_FIELDS = 5
    NULL_OPTION = '-- select --'
    ACTION = ['<', '<=', '=', '>=', '>']

    @classmethod
    def getToolName(cls):
        return "Filter according to values in selected column"

    @classmethod
    def getInputBoxNames(cls):
        return ['Select gSuite: '] + \
               ['Select column: ', 'Select action: ', 'Select value: '] * cls.NUM_CATEGORY_FIELDS

    @classmethod
    def getOptionsBox1(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBox2(cls, prevChoices):
        if not prevChoices[0]:
            return

        return cls._getNotStringColumns(prevChoices[0])

    @classmethod
    def getOptionsBox3(cls, prevChoices):
        if not prevChoices[1]:
            return

        if prevChoices[1] == cls.NULL_OPTION:
            return

        return cls.ACTION

    @classmethod
    def getOptionsBox4(cls, prevChoices):
        if not prevChoices[1]:
            return

        if prevChoices[1] == cls.NULL_OPTION:
            return

        return ''

    @classmethod
    def setupCategoryFields(cls):
        for i in xrange(cls.NUM_CATEGORY_FIELDS):
            setattr(cls, 'getOptionsBox%i' % (i * 3 + 5),
                    partial(cls._getColumn, index=i * 3 + 5))
            setattr(cls, 'getOptionsBox%i' % (i * 3 + 5 + 1),
                    partial(cls._getAction, index=i * 3 + 5 + 1))
            setattr(cls, 'getOptionsBox%i' % (i * 3 + 5 + 2),
                    partial(cls._getValue, index=i * 3 + 5 + 2))

    @classmethod
    def _getColumn(cls, prevChoices, index):
        if not prevChoices[0]:
            return

        if prevChoices[1] == cls.NULL_OPTION:
            return

        dd=''
        for i in range(0, int(index/3)):
            dd += str(prevChoices[i*3+5-4])
            if prevChoices[i*3+5-4] == cls.NULL_OPTION:
                return

        return cls._getNotStringColumns(prevChoices[0])


    @classmethod
    def _getAction(cls, prevChoices, index):
        if not prevChoices[0]:
            return

        for i in range(1, index):
            if i - 2 % 3 != 0:
                if prevChoices[i] == cls.NULL_OPTION:
                    return

        return cls.ACTION

    @classmethod
    def _getValue(cls, prevChoices, index):
        if not prevChoices[0]:
            return

        for i in range(1, index):
            if i - 3 % 3 != 0:
                if prevChoices[i] == cls.NULL_OPTION:
                    return

        return ''

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
    def execute(cls, choices, galaxyFn=None, username=''):

        gSuite = getGSuiteFromGalaxyTN(choices[0])
        filterQuestionsDict = cls._parseQuestions(choices)
        trackDict = cls._parseGsuiteByQuestion(choices, gSuite, filterQuestionsDict)

        filterResult = cls._filterResults(filterQuestionsDict, trackDict)
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

                    countResults += cls._filterValues(valTrack, f, valUser)

            if countResults == 0:
                filterResult.append(trackName)

        return filterResult

    @classmethod
    def _selectRowsFromGSuiteByTitle(cls, gSuite, titleList):
        reducedTrackList = [gSuite.getTrackFromTitle(title) for title in titleList]
        reducedGSuite = GSuite(trackList=reducedTrackList)
        return reducedGSuite


    @classmethod
    def _filterValues(cls, valTrack, action, valUser):

        valAction = eval(str(valTrack) + action + str(valUser))

        if valAction == False:
            return 1
        else:
            return 0


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
    def _parseQuestions(cls, choices):

        filterQuestionsDict = OrderedDict()
        for i in xrange(1, cls.NUM_CATEGORY_FIELDS * 3):
            if (i - 1) % 3 == 0:
                if choices[i] != cls.NULL_OPTION and choices[i] != '':
                    option = choices[i].encode('utf-8')
                    if not option in filterQuestionsDict.keys():
                        filterQuestionsDict[option] = {}
                    filterQuestionsDict[option][choices[i + 1].encode('utf-8')] = float(choices[i + 2])

        return filterQuestionsDict

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices[0]:
            return 'Select gSuite'

        if choices[0]:

            if len(cls._getNotStringColumns(choices[0])) == 1:
                return 'The gSuite does not contain any numbered column'
            else:
                if choices[1] == cls.NULL_OPTION:
                    return 'Select at least one column'
                else:
                    if choices[3] == '':
                        return 'Define value'

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