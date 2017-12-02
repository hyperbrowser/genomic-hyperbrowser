from collections import OrderedDict

from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.statistic.CountStat import CountStat
from gold.track.Track import Track, PlainTrack
from proto.CommonFunctions import ensurePathExists
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.tools.GeneralGuiTool import HistElement
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from gold.application.HBAPI import doAnalysis


class GSuiteTracksBasicAnalysisTool(GeneralGuiTool, UserBinMixin, GenomeMixin):
    @classmethod
    def getToolName(cls):
        return "Compute basic analysis for tracks in gSsuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select gsuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               cls.getInputBoxNamesForUserBinSelection() + \
                [
                ('Select column', 'metadata')
                ]

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxMetadata(prevChoices):
        if not prevChoices.gsuite:
            return

        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
        attributeList = gSuite.attributes
        return attributeList


    # Treat the file as categorical, with TF column as category. For each category,
    # count the number of tracks contained. Also, for each category,
    # compute the number of base pair covered by each track in the category and
    # compute the ratio of the highest and lowest number of bp coverage of tracks within that category.
    # This results in two values per category: number of tracks, ratio of highest to lowest bp coverage.
    # This should be represented somehow, perhaps simply in original GSuite file, by having columns for
    # these and putting the same value at each track belonging to the same category..


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        attrName = choices.metadata.encode('utf-8')
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        attrValueDict, data = cls._readAndCountDataInGsuite(attrName, choices, gSuite)
        attrValueDict, tableRes = cls._combaineResults(attrValueDict)

        cls._combainFinalGsuite(attrName, attrValueDict, data, gSuite)


        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line("Report")
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(['Attribute: ' + str(attrName), 'number of tracks', 'ratio bp', 'min bp', 'max bp'], sortable=True, tableId='resultsTable')
        for line in tableRes:
            htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()
        htmlCore.end()

        print htmlCore

    @classmethod
    def _combainFinalGsuite(cls, attrName, attrValueDict, data, gSuite):
        outGSuite = GSuite()
        for i, iTrack in enumerate(gSuite.allTracks()):
            trackTitle = iTrack.title
            trackPath = iTrack.uri
            attrValue = iTrack.getAttribute(attrName)

            attr = OrderedDict()
            for a in gSuite.attributes:
                attr[str(a)] = str(iTrack.getAttribute(a))
            attr['bpCovered'] = str(data[trackTitle]['countStat'])
            attr['trackNumber'] = str(attrValueDict[attrValue]['num'])
            attr['ratio'] = str(attrValueDict[attrValue]['allAttrValCountStat'])

            cls._buildTrack(outGSuite, trackTitle, gSuite.genome, trackPath, attr)
        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['output gSuite'])

    @classmethod
    def _combaineResults(cls, attrValueDict):
        tableRes = []
        for attrValue in attrValueDict.keys():
            l = min(attrValueDict[attrValue]['allAttrValCountStat'])
            h = max(attrValueDict[attrValue]['allAttrValCountStat'])
            attrValueDict[attrValue]['allAttrValCountStat'] = float(l) / float(h)
            tableRes.append([attrValue, attrValueDict[attrValue]['num'],
                             attrValueDict[attrValue]['allAttrValCountStat'], l, h])
        return attrValueDict, tableRes

    @classmethod
    def _readAndCountDataInGsuite(cls, attrName, choices, gSuite):
        analysisSpec = AnalysisSpec(CountStat)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=gSuite.genome)
        data = OrderedDict()
        attrValueDict = {}
        for i, iTrack in enumerate(gSuite.allTracks()):
            trackTitle = str(iTrack.title)
            attrValue = iTrack.getAttribute(attrName)
            results = doAnalysis(analysisSpec, analysisBins, [PlainTrack(iTrack.trackName)])

            # collect information about group
            # count CountStat per track
            if not trackTitle in data.keys():
                data[trackTitle] = {}
                data[trackTitle]['countStat'] = ''
            data[trackTitle]['countStat'] = results.getGlobalResult()['Result']

            # count number of tracks per group
            if not attrValue in attrValueDict.keys():
                attrValueDict[attrValue] = {}
                attrValueDict[attrValue]['num'] = 1
                attrValueDict[attrValue]['allAttrValCountStat'] = []
            else:
                attrValueDict[attrValue]['num'] += 1
            attrValueDict[attrValue]['allAttrValCountStat'].append(
                results.getGlobalResult()['Result'])
        return attrValueDict, data

    @classmethod
    def _buildTrack(cls, outGSuite, trackTitle, genome, trackPath, attr):

        uri = trackPath
        gSuiteTrack = GSuiteTrack(uri)

        gs = GSuiteTrack(uri,
                         title=''.join(trackTitle),
                         genome=genome,
                         attributes=attr)

        outGSuite.addTrack(gs)

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('output gSuite', 'gsuite')]

    @classmethod
    def validateAndReturnErrors(cls, choices):

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
