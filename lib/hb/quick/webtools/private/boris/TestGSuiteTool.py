from config.DebugConfig import DebugConfig
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.track.TrackStructure import TrackStructureV2
from gold.track.trackstructure.random.ExcludedSegmentsStorage import ExcludedSegmentsStorage
from gold.track.trackstructure.random.ShuffleElementsBetweenTracksAndBinsTvProvider import ShuffleElementsBetweenTracksAndBinsTvProvider
from gold.track.trackstructure.random.ShuffleElementsBetweenTracksAndBinsTvProvider import \
    ShuffleElementsBetweenTracksAndBinsTvProvider
from gold.track.trackstructure.random.TrackDataStorageRandAlgorithm import \
    ShuffleElementsBetweenTracksAndBinsRandAlgorithm
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.PairedTSStat import PairedTSStat
from quick.statistic.StatFacades import ObservedVsExpectedStat
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
            [('Select excluded regions track', 'excludedRegions'),
            ('Select MCFDR sampling depth', 'mcfdrDepth')] + \
            cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxGsuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxQueryTrack(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxExcludedRegions(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxMcfdrDepth(cls, prevChoices):
        return AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0]


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        # DebugUtil.insertBreakPoint()

        choices_queryTrack = choices.queryTrack
        choices_gsuite = choices.gsuite
        genome = choices.genome
        # queryTrackNameAsList = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.queryTrack,
        #                                                                              printErrors=False,
        #                                                                              printProgress=False)
        # gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)

        import quick.gsuite.GuiBasedTsFactory as factory
        queryTS = factory.getSingleTrackTS(genome, choices_queryTrack)
        refTS = factory.getFlatTracksTS(genome, choices_gsuite)

        excludedTs = None
        if choices.excludedRegions:
            excludedTs = factory.getSingleTrackTS(genome, choices.excludedRegions)

        ts = TrackStructureV2()
        realTS = TrackStructureV2()
        realTS["query"] = queryTS
        realTS["reference"] = refTS
        randQueryTS = queryTS
        excludedSegments = ExcludedSegmentsStorage(excludedTS=excludedTs, binSource=analysisBins)
        randAlg = ShuffleElementsBetweenTracksAndBinsRandAlgorithm(
            False, excludedSegmentsStorage=excludedSegments)
        randTvProvider = ShuffleElementsBetweenTracksAndBinsTvProvider(randAlgorithm=randAlg,
                                                                       origTs=refTS,
                                                                       binSource=analysisBins)
        randRefTS = refTS._getRandomizedVersion(randTvProvider, 0)
        hypothesisKeyList = [sts.metadata["title"] for sts in randRefTS.values()]
        for hypothesisKey in hypothesisKeyList:
            realTS = TrackStructureV2()
            realTS["query"] = queryTS
            realTS["reference"] = refTS[hypothesisKey]
            randTS = TrackStructureV2()
            randTS["query"] = randQueryTS
            randTS["reference"] = randRefTS[hypothesisKey]
            hypothesisTS = TrackStructureV2()
            hypothesisTS["real"] = realTS
            hypothesisTS["rand"] = randTS
            ts[hypothesisKey] = hypothesisTS
        analysisSpec = cls._prepareAnalysisWithHypothesisTests(choices)
        if DebugConfig.USE_PROFILING:
            from gold.util.Profiler import Profiler
            profiler = Profiler()
            resDict = {}
            profiler.run('resDict[0] = doAnalysis(analysisSpec, analysisBins, ts)', globals(), locals())
            res = resDict[0]
            result = res.getGlobalResult()['Result']
            profiler.printStats()
            if DebugConfig.USE_CALLGRAPH and galaxyFn:
                profiler.printLinkToCallGraph(['profile_AnalysisDefJob'], galaxyFn)
        else:
            result = doAnalysis(analysisSpec, analysisBins, ts).getGlobalResult()['Result']
        print "Result", result


        # tvProvider = ShuffleElementsBetweenTracksAndBinsTvProvider(refTS, queryTS, binSource=analysisBins, allowOverlaps=False)
        # for region in analysisBins:
        #     tv = tvProvider.getTrackView(region, refTS.getLeafNodes()[0].track, 0)
        #     print tv
        # tvProvider._populatePool()

    @classmethod
    def _prepareAnalysisWithHypothesisTests(cls, choices):
        mcfdrDepth = choices.mcfdrDepth if choices.mcfdrDepth else \
            AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0][0]
        analysisDefString = REPLACE_TEMPLATES['$MCFDRv5$'] + ' -> ' + ' -> MultipleRandomizationManagerStat'
        analysisSpec = AnalysisDefHandler(analysisDefString)
        analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
        analysisSpec.addParameter('rawStatistic', PairedTSStat.__name__)
        analysisSpec.addParameter('pairedTsRawStatistic', ObservedVsExpectedStat.__name__)
        analysisSpec.addParameter('tail', 'right-tail')
        analysisSpec.addParameter('evaluatorFunc', 'evaluatePvalueAndNullDistribution')
        analysisSpec.addParameter('tvProviderClass', ShuffleElementsBetweenTracksAndBinsTvProvider)
        return analysisSpec

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'