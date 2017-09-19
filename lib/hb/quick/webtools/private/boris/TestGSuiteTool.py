from gold.statistic.RawDataStat import RawDataStat
from gold.track.ShuffleElementsBetweenTracksAndBinsTvProvider import ShuffleElementsBetweenTracksAndBinsTvProvider
from gold.track.Track import Track
from gold.track.TrackFormat import NeutralTrackFormatReq
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.debug import DebugUtil
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class TestGSuiteTool(GeneralGuiTool, UserBinMixin, GenomeMixin):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Test tool"

    @classmethod
    def getInputBoxNames(cls):
        return [
            ('Select GSuite', 'gsuite'),
            ('Avoidance track', 'queryTrack')] + \
            cls.getInputBoxNamesForGenomeSelection() + \
            cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxQueryTrack(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        DebugUtil.insertBreakPoint()

        choices_queryTrack = choices.queryTrack
        choices_gsuite = choices.gsuite
        genome = choices.genome
        queryTrackNameAsList = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.queryTrack,
                                                                                     printErrors=False,
                                                                                     printProgress=False)
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)
        queryTrack = Track(queryTrackNameAsList)

        import quick.gsuite.GuiBasedTsFactory as factory
        queryTS = factory.getSingleTrackTS(genome, choices_queryTrack)
        refTS = factory.getFlatTracksTS(genome, choices_gsuite)

        tvProvider = ShuffleElementsBetweenTracksAndBinsTvProvider(refTS, queryTS, binSource=analysisBins, allowOverlaps=False)
        for region in analysisBins:
            tv = tvProvider.getTrackView(region, refTS.getLeafNodes()[0].track, 0)
            print tv
        # tvProvider._populatePool()



        @staticmethod
        def getOutputFormat(choices=None):
            return 'customhtml'