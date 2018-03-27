from gold.track.Track import Track
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
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
                ('Nr. of simulated sub-GSuites', 'nrSubGsuites'),
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
    def getOptionsBoxGenome(cls):
        return '__genome__'

    @classmethod
    def getOptionsBoxNrSubGsuites(cls, prevChoices):
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
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome = choices.genome
        trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.baseTrack,
                                                                          printProgress=False)
        baseTrack = Track(trackName)
        nrSubGSuites = int(choices.nrSubGSuites)
        nrTracks = int(choices.nrTracks)
        tpProb = float(choices.tpProb)
        tnProb = float(choices.tnProb)

        analysisBins = GalaxyInterface._getUserBinSource(*UserBinMixin.getRegsAndBinsSpec(choices),
                                                         genome=genome)

        #TODO: implement
        cls._execute(baseTrack, analysisBins, nrSubGSuites, nrTracks, tpProb, tnProb, galaxyFn)

    @classmethod
    def _execute(cls, baseTrack, analysisBins, nrSubGSuites, nrTracks, tpProb, tnProb, galaxyFn):
        pass

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
    # @classmethod
    # def isPublic(cls):
    #     return False
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
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
