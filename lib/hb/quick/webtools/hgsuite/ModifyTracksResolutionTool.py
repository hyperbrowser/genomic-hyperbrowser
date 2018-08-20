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
from quick.webtools.hgsuite.Legend import Legend
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from gold.statistic.CountStat import CountStat
from gold.statistic.CountPointStat import CountPointStat
from quick.statistic.SingleTSStat import SingleTSStat
from gold.track.TrackStructure import SingleTrackTS

class ModifyTracksResolutionTool(GeneralGuiTool, GenomeMixin):
    @classmethod
    def getToolName(cls):
        return "Modify resolution of hGSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select hGSuite', 'gsuite')] + \
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

            attrDict = OrderedDict()
            for attrName in gSuite.attributes:
                attrDict[attrName] = track.getAttribute(attrName)

            sts = SingleTrackTS(PlainTrack(tn), OrderedDict(title=tt, genome=str(genome)))
            res = doAnalysis(analysisSpec, analysisBins, sts)

            wr = open(outFn, 'w')
            for bin, val in res.iteritems():
                v = val['Result'].getResult()
                if int(v) > 0:
                    wr.write(('\t').join([str(bin.chr), str(bin.start), str(bin.end), str(v)]) + '\n')
            wr.close()

            gs = GSuiteTrack(uri, title=ttNew, genome=gSuite.genome, attributes=attrDict)

            outputGSuite.addTrack(gs)

        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)



    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gsuite:
            return 'Please select hGSuite'

        if choices.gsuite:
            gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
            if gsuite.numTracks() == 0:
                return 'Please select a hGSuite file with at least one track'

            if not gsuite.isPreprocessed():
                return 'Selected hGSuite file is not preprocess. Please preprocess ' \
                       'the hGSuite file before continuing the analysis.'

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
    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'The tool allow to expand the resolution of hGSuite.'

        stepsToRunTool = ['Select hGSuite',
                          'Select resolution (1k, 10k, 100k, 1m, 10m)'
                          ]

        example = {'Example': ['', ["""
        ##file format: primary					
        ##track type: unknown					
        ##genome: mm10					
        ###uri	title	mutation	genotype	dir_level_1	dir_level_2
        galaxy:/path/track1.bed;bed	track1.bed	CA	eta	C	A
        galaxy:/path/track2.bed;bed	track2.bed	GT	eta	G	T
        galaxy:/path/track3.bed;bed	track5.bed	CG	iota	C	G
        galaxy:/path/track4.bed;bed	track6.bed	GC	iota	G	C
        galaxy:/path/track5.bed;bed	track3.bed	CA	iota	C	A
        galaxy:/path/track6.bed;bed	track4.bed	GT	iota	G	T
                        """
                    ],
               [
                   ['Select hGSuite', 'gsuite'],
                   ['Select resolution', '100k']

               ],
               [
                   """
        ##location: local
        ##file format: primary
        ##track type: unknown
        ##genome: mm10
        ###uri	title	mutation	genotype	dir_level_1	dir_level_2
        galaxy:/path/track1.bed--100k;bed	track1.bed--100k	CA	eta	C	A
        galaxy:/path/track2.bed--100k;bed	track2.bed--100k	GT	eta	G	T
        galaxy:/path/track5.bed--100k;bed	track5.bed--100k	CG	iota	C	G
        galaxy:/path/track6.bed--100k;bed	track6.bed--100k	GC	iota	G	C
        galaxy:/path/track3.bed--100k;bed	track3.bed--100k	CA	iota	C	A
        galaxy:/path/track4.bed--100k;bed	track4.bed--100k	GT	iota	G	T
                   
                   """
               ]
               ]
   }

        toolResult = 'The output of this tool is a primary hGsuite with extra columns.'

        notice = "If you want to use hGSuite for the futher analysis then remeber to preprocess it using tool: Preprocess a GSuite for analysis"

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example,
                                          notice=notice
                                          )
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
