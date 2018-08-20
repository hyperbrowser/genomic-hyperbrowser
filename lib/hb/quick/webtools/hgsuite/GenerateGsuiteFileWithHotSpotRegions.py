from collections import OrderedDict
import operator
from gold.application.HBAPI import doAnalysis, AnalysisSpec
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisManager import AnalysisManager
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.track.Track import PlainTrack
from proto.CommonFunctions import ensurePathExists
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import UserBinSource
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.HotSpotRegionsStat import HotSpotRegionsStat
from quick.statistic.SingleTSStat import SingleTSStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.track.TrackStructure import SingleTrackTS
from proto.hyperbrowser.HtmlCore import HtmlCore

# This is a template prototyping GUI that comes together with a corresponding
# web page.
from quick.webtools.hgsuite.Legend import Legend
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class GenerateGsuiteFileWithHotSpotRegions(GeneralGuiTool, UserBinMixin, GenomeMixin):
    @classmethod
    def getToolName(cls):
        return "Generate hGSuite with hotspot regions"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select hGSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [('Number of top hotspots', 'param')
                ] + cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxParam(cls, prevChoices):
        return ''

    @staticmethod
    def resolveAnalysisFromName(genome, fullCategory, trackName, analysisName):
        selectedAnalysis = None
        for analysis in AnalysisManager.getValidAnalysesInCategory(fullCategory, genome, trackName,
                                                                   None):
            if analysisName == AnalysisDefHandler.splitAnalysisText(str(analysis))[0]:
                selectedAnalysis = analysis

        return selectedAnalysis

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        # use gSuite from option
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        tracks = list(gSuite.allTracks())

        # create new gSuite object
        outputGSuite = GSuite()
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                         binSpec,
                                                         choices.genome)
        analysisSpec = AnalysisSpec(SingleTSStat)
        analysisSpec.addParameter('rawStatistic', HotSpotRegionsStat.__name__)
        analysisSpec.addParameter("numberOfTopHotSpots", choices.param)

        htmlCore = HtmlCore()
        htmlCore.begin()

        for track in tracks:

            tt = track.title
            tn = track.trackName
            sts = SingleTrackTS(PlainTrack(tn),
                                OrderedDict(title=tt, genome=str(gSuite.genome)))

            result = doAnalysis(analysisSpec, analysisBins, sts)
            resultDict = result.getGlobalResult()['Result'].getResult()

            param = int(choices.param)

            if resultDict:
                ttNew = str(tt) + '--' + str(param)

                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                    extraFileName=ttNew,
                                                    suffix='bed')
                gSuiteTrack = GSuiteTrack(uri)
                outFn = gSuiteTrack.path
                ensurePathExists(outFn)

                resList = resultDict
                resList.sort(key=operator.itemgetter(1), reverse=False)
                elNum = resList[int(choices.param) - 1][1]

                for elN in range(int(choices.param), len(resList)):
                    if resList[elN][1] == elNum:
                        param += 1
                    else:
                        break

                outputFile = open(outFn, 'w')
                elNX = 0
                for x in resList[0:param]:
                    outputFile.write(x[0].replace(':', '\t').replace('-', '\t') + '\n')
                    elNX += 1
                outputFile.close()

                gs = GSuiteTrack(uri, title=ttNew, genome=gSuite.genome,
                                 attributes=track.attributes)
                outputGSuite.addTrack(gs)

            GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @staticmethod
    def validateAndReturnErrors(choices):

        if not choices.gsuite:
            return 'Please select hGSuite'

        if choices.gsuite:
            gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
            if gsuite.numTracks() == 0:
                return 'Please select a hGSuite file with at least one track'

            if not gsuite.isPreprocessed():
                return 'Selected hGSuite file is not preprocess. Please preprocess ' \
                       'the hGSuite file before continuing the analysis.'

    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'The tool allow to generate hGSuite with selected hotspot regions.'

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
           ['Number of top hotspots', '100']

                               ],
                               [
                                   """
        ##location: local
        ##file format: primary
        ##track type: unknown
        ##genome: mm10
        ###uri	title	mutation	genotype	dir_level_1	dir_level_2
        galaxy:/path/track1.bed--100;bed	track1.bed--100	CA	eta	C	A
        galaxy:/path/track2.bed--100;bed	track2.bed--100	GT	eta	G	T
        galaxy:/path/track5.bed--100;bed	track5.bed--100	CG	iota	C	G
        galaxy:/path/track6.bed--100;bed	track6.bed--100	GC	iota	G	C
        galaxy:/path/track3.bed--100;bed	track3.bed--100	CA	iota	C	A
        galaxy:/path/track4.bed--100;bed	track4.bed--100	GT	iota	G	T
            
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

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'