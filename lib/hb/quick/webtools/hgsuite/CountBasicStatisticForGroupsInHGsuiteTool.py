from collections import OrderedDict

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack
from proto.tools.GeneralGuiTool import HistElement
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.CountDescriptiveStatisticBetweenHGsuiteTool import \
    CountDescriptiveStatisticBetweenHGsuiteTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class CountBasicStatisticForGroupsInHGsuiteTool(GeneralGuiTool, GenomeMixin, DebugMixin):
    MAX_NUM_OF_COLS_IN_GSUITE = 10
    MAX_NUM_OF_COLS = 10
    PHRASE = '-- SELECT --'

    NUMTRACK = 'Number of tracks'
    NUMELEMENTS = 'Number of elements in track'
    STAT_LIST = {
        NUMTRACK: 'NumberOfTracks',
        #NUMELEMENTS: 'NumElements'
    }

    @classmethod
    def getToolName(cls):
        return "Overview of groups in hGSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select gSuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
               [('Select statistic %s' % (i + 1) + '',
                 'selectedStat%s' % i) for i \
                in range(cls.MAX_NUM_OF_COLS)] + \
               [('Select column %s' % (
                   i + 1) + ' according to which you would like to group results',
                 'selectedColumn%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)]

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def _getOptionsBoxForSelectedStat(cls, prevChoices, index):
        if prevChoices.gsuite:
            selectionList = []
            if not any(cls.PHRASE in getattr(prevChoices, 'selectedStat%s' % i) for i in
                       xrange(index)):
                attrList = [getattr(prevChoices, 'selectedStat%s' % i) for i in xrange(index)]
                selectionList = [cls.PHRASE] + list(set(cls.STAT_LIST.keys()) - set(attrList))
            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedStatMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedStat%s' % i,
                    partial(cls._getOptionsBoxForSelectedStat, index=i))

    @classmethod
    def _getOptionsBoxForSelectedColumn(cls, prevChoices, index):
        if prevChoices.gsuite:
            selectionList = []

            if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumn%s' % i) for i in
                       xrange(index)):
                gSuiteTNFirst = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                selectionList += gSuiteTNFirst.attributes

                attrList = [getattr(prevChoices, 'selectedColumn%s' % i) for i in
                            xrange(index)]
                selectionList = [cls.PHRASE] + list(
                    set(selectionList) - set(attrList))

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedColumnMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedColumn%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumn, index=i))



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        attrNameList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                  'selectedColumn%s',
                                                                                  cls.MAX_NUM_OF_COLS_IN_GSUITE)

        statList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                   'selectedStat%s',
                                                                                   cls.MAX_NUM_OF_COLS)

        resDict = {}
        for stat in statList:
            resDict[stat] = OrderedDict()

        #count overview
        for iTrack in gSuite.allTracks():
            for stat in statList:
                tupleList = []
                for attrName in attrNameList:
                    tupleList.append(iTrack.getAttribute(attrName))
                tupleList = tuple(tupleList)
                if not tupleList in resDict[stat].keys():
                    resDict[stat][tupleList] = 0

                if stat == cls.NUMTRACK:
                    resDict[stat][tupleList] += 1

        ########################################################################
        ###################### SUMMARIZE RESULTS ###############################
        ########################################################################


        #Overview table

        #build results
        outGSuite = GSuite()
        for i, iTrack in enumerate(gSuite.allTracks()):
            trackTitle = iTrack.title
            trackPath = iTrack.uri

            attr = OrderedDict()
            for a in gSuite.attributes:
                attr[str(a)] = str(iTrack.getAttribute(a))

            tupleList = []
            for attrName in attrNameList:
                tupleList.append(iTrack.getAttribute(attrName))
            tupleList = tuple(tupleList)
            for s in resDict.keys():
                attr[str(s)] = str(resDict[s][tupleList])

            trackType = iTrack.trackType

            cls._buildTrack(outGSuite, trackTitle, gSuite.genome, trackPath, attr, trackType)
        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['overview gSuite'])

    @classmethod
    def _buildTrack(cls, outGSuite, trackTitle, genome, trackPath, attr, trackType):

        uri = trackPath

        gs = GSuiteTrack(uri,
                         title=''.join(trackTitle),
                         genome=genome,
                         attributes=attr,
                         trackType=trackType)

        outGSuite.addTrack(gs)

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('overview gSuite', 'gsuite')]

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
CountBasicStatisticForGroupsInHGsuiteTool.setupSelectedColumnMethods()
CountBasicStatisticForGroupsInHGsuiteTool.setupSelectedStatMethods()
