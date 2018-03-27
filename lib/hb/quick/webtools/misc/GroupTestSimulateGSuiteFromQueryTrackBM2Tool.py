from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.track.Track import Track
from proto.CommonFunctions import ensurePathExists
from proto.tools.GeneralGuiTool import HistElement
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.gsuite import GuiBasedTsFactory
from quick.statistic.StatTvOutputWriterStat import StatTvOutputWriterStat
from quick.statistic.StatTvOutputWriterWrapperV2Stat import StatTvOutputWriterWrapperV2Stat
from quick.util.debug import DebugUtil
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class GroupTestSimulateGSuiteFromQueryTrackBM2Tool(GeneralGuiTool, UserBinMixin):
    @classmethod
    def getToolName(cls):
        return "Simulate two level GSuite from a base track"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select the base track', 'baseTrack'),
                ('Select the genome build', 'genome'),
                ('Nr. of simulated sub-GSuites', 'nrSubGSuites'),
                ('Nr. of tracks per group', 'nrTracks'),
                ('True positive probability', 'tpProb'),
                ('True negative probability', 'tnProb')] + \
                cls.getInputBoxNamesForUserBinSelection()

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxBaseTrack(cls):
        return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        return '__genome__'

    @classmethod
    def getOptionsBoxNrSubGSuites(cls, prevChoices):
        return '100'

    @classmethod
    def getOptionsBoxNrTracks(cls, prevChoices):
        return '10'
    @classmethod
    def getOptionsBoxTpProb(cls, prevChoices):
        return '0.5'
    @classmethod
    def getOptionsBoxTnProb(cls, prevChoices):
        return '0.99'

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']
    #
    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('Simulated GSuite (BM2)', 'gsuite')]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome = choices.genome
        # trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.baseTrack,
        #                                                                   printProgress=False)
        # baseTrack = Track(trackName)

        baseTrackSTS = GuiBasedTsFactory.getSingleTrackTS(genome, choices.baseTrack, title="base_track")

        nrSubGSuites = int(choices.nrSubGSuites)
        nrTracks = int(choices.nrTracks)
        tpProb = float(choices.tpProb)
        tnProb = float(choices.tnProb)

        analysisBins = GalaxyInterface._getUserBinSource(*UserBinMixin.getRegsAndBinsSpec(choices),
                                                         genome=genome)

        #TODO: implement
        cls._execute(baseTrackSTS, genome, analysisBins, nrSubGSuites, nrTracks, tpProb, tnProb, galaxyFn)

    @classmethod
    def _execute(cls, baseTrackSTS, genome, analysisBins, nrSubGSuites, nrTracks, tpProb, tnProb, galaxyFn):
        import time
        startTime = time.time()
        gsuite = GSuite()
        groupOne = "A"
        groupTwo = "B"
        for i in xrange(nrSubGSuites):
            for j in xrange(nrTracks):
                for trackGroup in [groupOne, groupTwo]:
                    cls._addSimulatedTrackToGSuite(gsuite, str(i), str(j), trackGroup, baseTrackSTS, genome,
                                                   analysisBins, tpProb, tnProb, galaxyFn)
                    m, s = divmod(time.time() - startTime, 60)
                    h, m = divmod(m, 60)
                    print("%d:%02d:%02d" % (h, m, s))

        GSuiteComposer.composeToFile(gsuite, cls.extraGalaxyFn('Simulated GSuite (BM2)'))

    @classmethod
    def _addSimulatedTrackToGSuite(cls, gsuite, subGSuiteLabel, trackIndex, trackGroupLabel, baseTrackSTS, genome,
                                   analysisBins, tpProb, tnProb, galaxyFn):
        trackTitle = "{}--{}-{}-{}".format(baseTrackSTS.metadata["title"], subGSuiteLabel, trackIndex, trackGroupLabel)
        attr = OrderedDict()
        attr['originalTrackName'] = trackTitle
        attr['sub-gsuite-label'] = subGSuiteLabel
        attr['track-index'] = trackIndex
        attr['group-label'] = trackGroupLabel
        attr['tp'] = str(tpProb)
        attr['tn'] = str(tnProb)

        extraFN = "{}-{:f}-{:f}".format(trackTitle, tpProb, tnProb)

        uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                            extraFileName=extraFN,
                                            suffix='bed')
        gSuiteTrack = GSuiteTrack(uri, title=extraFN, genome=genome, attributes=attr)
        trackFN = gSuiteTrack.path
        ensurePathExists(trackFN)

        import urllib
        fn = urllib.quote(trackFN, safe='')

        spec = AnalysisSpec(StatTvOutputWriterWrapperV2Stat)
        spec.addParameter('trackFilePath', fn)
        spec.addParameter('trackGenerationStat', 'NoisyPointTrackGenerationStat')
        spec.addParameter('keepOnesProb', tpProb)
        spec.addParameter('introduceZerosProb', 1 - tnProb)

        doAnalysis(spec, analysisBins, baseTrackSTS)

        gsuite.addTrack(gSuiteTrack)

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.baseTrack:
            return "Please select a base track dataset from your history."

        if not choices.genome or choices.genome == '--- Select ---':
            return "Please select a genome build."

        if choices.baseTrack and choices.genome:
            try:
                ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(choices.genome, choices.baseTrack,
                                                                      printProgress=False)
            except:
                return "Please select a valid base track (BED, GTrack...)."

        try:
            int(choices.nrSubGSuites)
        except:
            return "Nr. of sub-GSuites must be a valid integer."

        try:
            int(choices.nrTracks)
        except:
            return "Nr. of tracks per group must be a valid integer."

        probErr = "The probabilities must be real numbers between 0.0 and 1.0."
        try:
            tpProb = float(choices.tpProb)
            tnProb = float(choices.tnProb)
        except:
            return probErr
        else:
            if tnProb > 1 or tnProb < 0 or tpProb > 1 or tnProb < 0:
                return probErr


    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    @classmethod
    def isPublic(cls):
        return True
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
