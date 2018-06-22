from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.track.Track import PlainTrack
from proto.CommonFunctions import ensurePathExists
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.SingleTSStat import SingleTSStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from gold.statistic.CountStat import CountStat
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.SingleTSStat import SingleTSStat
from gold.track.TrackStructure import SingleTrackTS

class ModifyTracksResolutionTool(GeneralGuiTool, GenomeMixin):
    @classmethod
    def getToolName(cls):
        return "Modify resolution of tracks"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [('Select resolution', 'resolution')]


    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxResolution(cls, prevChoices):
        return ['1k', '10k', '100k', '1m', '10m']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        resolution = choices.resolution.encode('utf-8')

        #chamge resolution of tracks
        analysisSpec = AnalysisSpec(SingleTSStat)
        analysisSpec.addParameter('rawStatistic', CountStat.__name__)
        regSpec = '*'
        binSpec = resolution
        analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                         binSpec,
                                                         choices.genome)

        outputGSuite = GSuite()
        #get local result from statistic
        for i, track in enumerate(gSuite.allTracks()):
            tt = track.title
            tn = track.trackName
            ttNew = str(tt) + '--' + str(resolution)

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=ttNew,
                                                suffix='bed')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            sts = SingleTrackTS(PlainTrack(tn), OrderedDict(title=tt, genome=str(genome)))
            res = doAnalysis(analysisSpec, analysisBins, sts)

            wr = open(outFn, 'w')
            for bin, val in res.iteritems():
                v = val['Result'].getResult()
                if int(v) > 0:
                    wr.write(('\t').join([str(bin.chr), str(bin.start), str(bin.end), str(v)]) + '\n')
            wr.close()

            gs = GSuiteTrack(uri, title=ttNew, genome=gSuite.genome)

            outputGSuite.addTrack(gs)

        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)



    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

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
    @classmethod
    def getOutputFormat(cls, choices):
        return 'gsuite'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
