from collections import OrderedDict

from galaxy.tools.parser import factory
from gold.application.HBAPI import doAnalysis
from gold.statistic.CountElementStat import CountElementStat
from gold.statistic.CountStat import CountStat
from gold.track.TrackStructure import SingleTrackTS, TrackStructureV2
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.track.Track import PlainTrack
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.result.model.GSuitePerTrackResultModel import GSuitePerTrackResultModel
from quick.result.model.ResultUtils import getTrackTitleToResultDictFromPairedTrackStructureResult
from quick.statistic.AvgSegLenStat import AvgSegLenStat
from quick.statistic.SingleTSStat import SingleTSStat
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import \
    SummarizedInteractionWithOtherTracksV2Stat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.CountDescriptiveStatisticBetweenHGsuiteTool import \
    CountDescriptiveStatisticBetweenHGsuiteTool
from quick.webtools.hgsuite.CountDescriptiveStatisticForHGSuiteTool import \
    CountDescriptiveStatisticForHGSuiteTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class MixModelsTool(GeneralGuiTool, GenomeMixin, DebugMixin, UserBinMixin):
    MAX_NUM_OF_COLS_IN_GSUITE = 10
    MAX_NUM_OF_COLS = 10
    PHRASE = '-- SELECT --'

    @classmethod
    def getToolName(cls):
        return "Statistics between groups (mix models)"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select track', 'track'),
                ('Select hGSuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
               [('Select group %s' % (
                   i + 1) + '',
                 'selectedColumn%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxTrack(cls):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @classmethod
    def getOptionsBoxGsuite(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def _getOptionsBoxForSelectedColumn(cls, prevChoices, index):
        if prevChoices.gsuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            dimensions = gSuite.getCustomHeader('levels')
            selectionList = []
            if str(dimensions) == 'None':
                if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumn%s' % i) for i in
                           xrange(index)):
                    gSuiteTNFirst = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                    selectionList += gSuiteTNFirst.attributes

                    attrList = [getattr(prevChoices, 'selectedColumn%s' % i) for i in
                                xrange(index)]
                    selectionList = [cls.PHRASE] + list(
                        set(selectionList) - set(attrList))
            else:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                dimensions = gSuite.getCustomHeader('levels')
                dimensions = dimensions.split(',')
                attrList = [getattr(prevChoices, 'selectedColumn%s' % i) for i in
                            xrange(index)]
                selectionList = [item for item in dimensions if item not in attrList]
                cls.MAX_NUM_OF_COLS = len(dimensions)

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
        track = choices.track
        track = ExternalTrackManager.extractFnFromGalaxyTN(track.split(':'))
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        genome = choices.genome
        attrNameList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                       'selectedColumn%s',
                                                                                       cls.MAX_NUM_OF_COLS_IN_GSUITE)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, choices.genome)
        analysisSpec = AnalysisSpec(SingleTSStat)
        analysisSpec.addParameter('rawStatistic', CountStat.__name__)

        analysisSpec2 = AnalysisSpec(SingleTSStat)
        analysisSpec2.addParameter('rawStatistic', CountElementStat.__name__)

        import quick.gsuite.GuiBasedTsFactory as factory
        queryTS = factory.getSingleTrackTS(genome, choices.track)
        refTS = factory.getFlatTracksTS(genome, choices.gsuite)
        ts = TrackStructureV2([("query", queryTS), ("reference", refTS)])
        analysisSpec3 = AnalysisSpec(SummarizedInteractionWithOtherTracksV2Stat)
        analysisSpec3.addParameter('pairwiseStatistic','ObservedVsExpectedStat')
        analysisSpec3.addParameter('reverse', 'No')
        analysisSpec3.addParameter("summaryFunc", 'raw')
        tsRes = doAnalysis(analysisSpec3, analysisBins, ts).getGlobalResult()['Result']
        resultsObsVsExpected = getTrackTitleToResultDictFromPairedTrackStructureResult(tsRes)

        results = []
        trackTitles = []
        for i, track in enumerate(gSuite.allTracks()):
            tt = track.title
            trackTitles.append(tt)

            sts = SingleTrackTS(PlainTrack(track.trackName), OrderedDict(title=tt, genome=str(genome)))
            res = doAnalysis(analysisSpec, analysisBins, sts)
            avgSegLenPerTrack = res.getGlobalResult()['Result'].getResult()

            res2 = doAnalysis(analysisSpec2, analysisBins, sts)
            countElementsPerTrack = res2.getGlobalResult()['Result'].getResult()

            obsVsExpectedValue = resultsObsVsExpected[tt]
            results.append([tt, avgSegLenPerTrack, countElementsPerTrack, obsVsExpectedValue])

        for el in results:
            print el, '<br>'


    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gsuite:
            return 'Select gSuite'

        if not choices.track:
            return 'Select track'

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
MixModelsTool.setupSelectedColumnMethods()