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
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class GenerateGsuiteFileWithHotSpotRegions(GeneralGuiTool, UserBinMixin, GenomeMixin):
    @classmethod
    def getToolName(cls):
        return "Generate gSuite file with HotSpot regions"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select track collection GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [('Number of top hotspots', 'param')
                ] + cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxParam(cls, prevChoices):

        # if prevChoices.gSuite:
        #     from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        #     gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
        #     tracks = list(gSuite.allTracks())
        #     fullCategory = AnalysisManager.combineMainAndSubCategories('Descriptive statistics', 'Distributions')
        #     if len(tracks) >0:
        #         analysis = GenerateGsuiteFileWithHotSpotRegions.resolveAnalysisFromName(gSuite.genome, fullCategory, \
        #                                                         tracks[0].trackName, 'Hot spot regions')
        #
        #         if analysis and analysis.getOptionsAsKeys():
        #             return analysis.getOptionsAsKeys().values()[1]
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
                ttNew = str(tt)

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
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'

        return None

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