from collections import OrderedDict

import itertools

from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class CountDescriptiveStatisticBetweenHGsuiteTool(GeneralGuiTool):

    MAX_NUM_OF_COLS = 15
    MAX_NUM_OF_COLS_IN_GSUITE = 1
    MERGED_SIGN = ' - '
    PHRASE = '-- SELECT --'
    STAT_LIST = ['Count overlap (bps)']
    FIRST_GSUITE = 'First GSuite'
    SECOND_GSUITE = 'Second GSuite'


    @classmethod
    def getToolName(cls):
        return "Count descriptive statistic between hGsuite"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select first gSuite', 'firstGSuite'),
                ('Select column from first gSuite', 'firstGSuiteColumn'),
                ('Select second gSuite', 'secondGSuite'),
                ('Select column from second gSuite', 'secondGSuiteColumn')
                ] + \
               [('Select statistic %s' % (i + 1) + '',
                 'selectedStat%s' % i) for i \
                in range(cls.MAX_NUM_OF_COLS)] + \
               [('Select column from first gSuite %s' % (i + 1) +  ' which you would like to treat as unique',
                 'selectedFirstColumn%s' % i) for i \
                in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               [('Select column from second gSuite %s' % (i + 1) +  ' which you would like to treat as unique',
                 'selectedSecondColumn%s' % i) for i \
                in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)]


    @classmethod
    def getOptionsBoxFirstGSuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxFirstGSuiteColumn(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.firstGSuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.firstGSuite)
            return ['None'] + gSuiteTN.attributes

    @classmethod
    def getOptionsBoxSecondGSuite(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxSecondGSuiteColumn(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.secondGSuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
            return ['None'] + gSuiteTN.attributes

    @classmethod
    def _getOptionsBoxForSelectedStat(cls, prevChoices, index):
        if prevChoices.firstGSuite and prevChoices.secondGSuite:
            selectionList = []
            if not any(cls.PHRASE in getattr(prevChoices, 'selectedStat%s' % i) for i in
                           xrange(index)):
                attrList = [getattr(prevChoices, 'selectedStat%s' % i) for i in xrange(index)]
                selectionList = [cls.PHRASE] + list(set(cls.STAT_LIST) - set(attrList))
            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedStatMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedStat%s' % i,
                partial(cls._getOptionsBoxForSelectedStat, index=i))

    @classmethod
    def _getOptionsBoxForSelectedFirstColumn(cls, prevChoices, index):
        if prevChoices.firstGSuite and prevChoices.secondGSuite:
            selectionList = []

            if not any(cls.PHRASE in getattr(prevChoices, 'selectedFirstColumn%s' % i) for i in
                       xrange(index)):
                gSuiteTNFirst = getGSuiteFromGalaxyTN(prevChoices.firstGSuite)
                selectionList += gSuiteTNFirst.attributes

                attrList = [getattr(prevChoices, 'selectedFirstColumn%s' % i) for i in xrange(index)]
                selectionList = [cls.PHRASE] + list(set(selectionList) - set(attrList))

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedFirstColumnMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedFirstColumn%s' % i,
                    partial(cls._getOptionsBoxForSelectedFirstColumn, index=i))

    @classmethod
    def _getOptionsBoxForSelectedSecondColumn(cls, prevChoices, index):
        if prevChoices.firstGSuite and prevChoices.secondGSuite:
            selectionList = []

            if not any(cls.PHRASE in getattr(prevChoices, 'selectedSecondColumn%s' % i) for i in
                       xrange(index)):
                gSuiteTNSecond = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
                selectionList += gSuiteTNSecond.attributes

                attrList = [getattr(prevChoices, 'selectedSecondColumn%s' % i) for i in xrange(index)]
                selectionList = [cls.PHRASE] + list(set(selectionList) - set(attrList))

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedSecondColumnMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedSecondColumn%s' % i,
                    partial(cls._getOptionsBoxForSelectedSecondColumn, index=i))

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        firstGSuite = getGSuiteFromGalaxyTN(choices.firstGSuite)
        firstGSuiteColumn = choices.firstGSuiteColumn.encode('utf-8')
        secondGSuite = getGSuiteFromGalaxyTN(choices.secondGSuite)
        secondGSuiteColumn = choices.secondGSuiteColumn.encode('utf-8')

        print firstGSuite, '<br>'
        print firstGSuiteColumn, '<br>'
        print secondGSuite, '<br>'
        print secondGSuiteColumn, '<br>'
        print choices

        statList = [a.strip(' ').split(',') for a in cls._getSelectedStat(choices, 'selectedStat%s', cls.MAX_NUM_OF_COLS)]
        firstColumnList = cls._getSelectedStat(choices, 'selectedFirstColumn%s', cls.MAX_NUM_OF_COLS_IN_GSUITE)
        secondColumnList = cls._getSelectedStat(choices, 'selectedSecondColumn%s', cls.MAX_NUM_OF_COLS_IN_GSUITE)


        print statList, '<br>'
        print 'firstColumnList', firstColumnList, '<br>'
        print 'secondColumnList', secondColumnList, '<br>'


        #As many unique columns from: firstColumnList and secondColumnList as many outputGSuites
        firstOutput = cls._getAttributes(firstGSuite, firstColumnList)
        print 'firstOutput', firstOutput, '<br>'
        secondOutput = cls._getAttributes(secondGSuite, secondColumnList)
        print 'secondOutput', secondOutput, '<br>'
        listOfLists = firstOutput + secondOutput
        print cls._getCombinations(listOfLists)





        outputGSuites = OrderedDict()
        for iTrackFromFirst, trackFromFirst in firstGSuite.allTracks():
            pass


    @classmethod
    def _getAttributes(cls, firstGSuite, firstColumnList):
        if len(firstColumnList) > 0:
            firstOutput = []
            for fCol in firstColumnList:
                at = firstGSuite.getAttributeValueList(fCol)
                print at
                firstOutput.append(list(set(at)))
            return firstOutput
        return []

    @classmethod
    def _getCombinations(cls, listOfLists):
        return list(itertools.product(*listOfLists))

    @classmethod
    def _getSelectedStat(cls, choices, division, num):
        cols = []
        for i in range(0, num):
            cols.append(getattr(choices, division % i))
        return cls._getDatafromSelectedStat(cols)

    @classmethod
    def _getDatafromSelectedStat(cls, cols):
        selectedCols = []
        if len(cols) >=1:
            for c in cols:
                c = c.encode('utf-8')
                if c != cls.PHRASE and c != '':
                    selectedCols.append(c)
        return selectedCols

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
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedStatMethods()
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedFirstColumnMethods()
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedSecondColumnMethods()