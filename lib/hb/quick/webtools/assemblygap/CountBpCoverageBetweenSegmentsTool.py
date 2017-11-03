from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.statistic.CountSegmentStat import CountSegmentStat
from gold.track.Track import Track, PlainTrack
from gold.track.TrackStructure import SingleTrackTS, FlatTracksTS
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import GlobalBinSource, UserBinSource
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.BpCoveragePerT2SegStat import BpCoveragePerT2SegStat
from quick.statistic.SingleTSStat import SingleTSStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class CountBpCoverageBetweenSegmentsTool(GeneralGuiTool, UserBinMixin, GenomeMixin):

    OPTION1 = 'Count coverage as bp'
    OPTION2 = 'Count coverage as bp/region bp'

    @classmethod
    def getToolName(cls):
        return "Count coverage between segments"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select gsuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               cls.getInputBoxNamesForUserBinSelection() + \
                [('Select file', 'selFile'),
                 ('Select option', 'option'),
                 ('Add summarize statistics', 'sumStat'),
                 ('Download bed file with shared regions', 'sharedRegions')]

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxSelFile(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @classmethod
    def getOptionsBoxOption(cls, prevChoices):
        return [cls.OPTION1,
                cls.OPTION2]

    @classmethod
    def getOptionsBoxSumStat(cls, prevChoices):
        return ['yes', 'no']

    @classmethod
    def getOptionsBoxSharedRegions(cls, prevChoices):
        return ['yes', 'no']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        analysisBins, analysisSpec1, analysisSpec2, genome, option, queryTrack, sumStat, tracksList, tracksNameList, sharedRegions, gSuite = cls.getAllPreprocessedChoices(
            choices)

        bpTrackSize, regions, resultsDict = cls.countAllStat(analysisBins, analysisSpec1,
                                                             analysisSpec2, genome, option,
                                                             queryTrack, tracksList, gSuite)

        cls.addBedFileWithAllSharedRegions(regions, resultsDict, sharedRegions)




        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('resDiv')

        cls.showAllResults(bpTrackSize, choices, galaxyFn, htmlCore, option, regions, resultsDict,
                           sumStat, tracksList, tracksNameList)



        htmlCore.divEnd()
        htmlCore.end()

        print htmlCore

    @classmethod
    def addBedFileWithAllSharedRegions(cls, regions, resultsDict, sharedRegions):
        if sharedRegions == 'yes':
            outputFile = open(
                cls.makeHistElement(galaxyExt='bed', title=str('File with shared regions')), 'w')
            for el in regions:
                sumEl = True
                for singleEl in resultsDict[el]:
                    if singleEl == 0:
                        sumEl = False

                if sumEl == True:
                    c = el.split(':')
                    s = c[1].split('-')[0]
                    e = c[1].split('-')[1]
                    outputFile.write(c[0] + '\t' + s + '\t' + e + '\n')
            outputFile.close()

    @classmethod
    def showAllResults(cls, bpTrackSize, choices, galaxyFn, htmlCore, option, regions, resultsDict,
                       sumStat, tracksList, tracksNameList):

        cls.showResultsPerTrackInGsuite(choices, galaxyFn, htmlCore, regions, resultsDict,
                                        tracksNameList)

        if sumStat == 'yes':

            countSumResultsPerTrack = []
            for j, el in enumerate(regions):
                for i, e in enumerate(resultsDict[el]):
                    if j == 0:
                        countSumResultsPerTrack.append([e])
                    else:
                        countSumResultsPerTrack[i].append(e)

            htmlCore.paragraph('Summarise statiscs per track in gsuite')

            prettyResultsSumPerTrack = OrderedDict()
            prettyResultsSumPerTrack['Number of regions'] = []
            prettyResultsSumPerTrack['Number of regions excluding 0'] = []
            prettyResultsSumPerTrack['Number of regions containing only 0 values'] = []

            for prs in countSumResultsPerTrack:
                prettyResultsSumPerTrack['Number of regions'].append(sum(1 for x in prs))
                prettyResultsSumPerTrack['Number of regions excluding 0'].append(
                    sum(1 for x in prs if x > 0))
                prettyResultsSumPerTrack['Number of regions containing only 0 values'].append(
                    sum(1 for x in prs if x == 0))

            columnNamesSum = ['Statistic'] + tracksNameList
            shortQuestion = 'resultsSummarized'
            addTableWithTabularAndGsuiteImportButtons(
                htmlCore,
                choices,
                galaxyFn,
                shortQuestion,
                tableDict=prettyResultsSumPerTrack,
                columnNames=columnNamesSum
            )

            htmlCore.paragraph('Summarise statiscs per gsuite')

            op = [
                'Number of regions fully covered (all tracks have value in the region)',
                'Number of regions partially covered',
                'Number of regions not covered'
            ]
            regionsNum = len(resultsDict.keys())
            trackNum = len(tracksList)

            resultSumPerGsuiteList = [0 for x in range(0, len(op))]

            for region, it in resultsDict.iteritems():
                ones = sum(1 for x in it if x > 0)
                if ones == trackNum:
                    resultSumPerGsuiteList[0] += 1
                if ones > 0 and ones < trackNum:
                    resultSumPerGsuiteList[1] += 1
                if ones == 0:
                    resultSumPerGsuiteList[2] += 1

            for gNum in range(0, len(resultSumPerGsuiteList)):
                resultSumPerGsuiteList[gNum] = float(resultSumPerGsuiteList[gNum]) / float(
                    regionsNum)

            prettyResultsSumPerGsuite = OrderedDict()
            for oNum in range(0, len(op)):
                prettyResultsSumPerGsuite[op[oNum]] = resultSumPerGsuiteList[oNum]

            columnNamesSum = ['Statistic', 'Value']
            shortQuestion = 'resultsSummarized'
            addTableWithTabularAndGsuiteImportButtons(
                htmlCore,
                choices,
                galaxyFn,
                shortQuestion,
                tableDict=prettyResultsSumPerGsuite,
                columnNames=columnNamesSum
            )

            if option == cls.OPTION1:

                htmlCore.paragraph(
                    'Summarise statiscs per gsuite (avg (sum of bps per track / size of track) )')

                prettyResultsSumDividedByBPPerGsuite = OrderedDict()

                avgOfsumAllCoveredBPDividedBYSizeTracks = 0


                for x in range(0, trackNum):
                    avgOfsumAllCoveredBPDividedBYSizeTracks += float(sum(countSumResultsPerTrack[x]) / (
                    float(bpTrackSize[x])))

                prettyResultsSumDividedByBPPerGsuite[
                    'Average covered value'] = float(avgOfsumAllCoveredBPDividedBYSizeTracks / trackNum)

                columnNamesSum = ['Statistic', 'Value']
                shortQuestion = 'resultsSummarizedForSpecialCase'
                addTableWithTabularAndGsuiteImportButtons(
                    htmlCore,
                    choices,
                    galaxyFn,
                    shortQuestion,
                    tableDict=prettyResultsSumDividedByBPPerGsuite,
                    columnNames=columnNamesSum
                )

    @classmethod
    def showResultsPerTrackInGsuite(cls, choices, galaxyFn, htmlCore, regions, resultsDict,
                                    tracksNameList):
        prettyResults = OrderedDict()
        for el in regions:
            prettyResults[el] = resultsDict[el]
        columnNames = ['Regions'] + tracksNameList
        shortQuestion = 'results'
        addTableWithTabularAndGsuiteImportButtons(
            htmlCore,
            choices,
            galaxyFn,
            shortQuestion,
            tableDict=prettyResults,
            columnNames=columnNames
        )

    @classmethod
    def countAllStat(cls, analysisBins, analysisSpec1, analysisSpec2, genome, option, queryTrack,
                     tracksList, gSuite):
        bpTrackSize = []
        resultsDict = {}
        regions = []


        gtNT = queryTrack[-1]
        queryTrack = Track(queryTrack)

        for i, track in enumerate(gSuite.allTracks()):
            #tracks = [track] + [queryTrack]

            sts = SingleTrackTS(PlainTrack(track.trackName), OrderedDict(title=track.title, genome=str(genome)))
            qt = SingleTrackTS(PlainTrack(gtNT), OrderedDict(title=gtNT, genome=str(genome)))


            results = doAnalysis(analysisSpec1, analysisBins, [sts]+[qt])
            resultsStatPerBin = doAnalysis(analysisSpec2, UserBinSource('*', '*', genome=genome), sts)


            print results.getAllValuesForResDictKey('Result')

            resLocal = results.getAllValuesForResDictKey('Result').result
            bpTrackSize.append(resultsStatPerBin.getGlobalResult()['Result'].result)

            if i == 0:
                regions = []
                for region in results.getAllRegionKeys():
                    regions.append(
                        region.chr + ':' + str(int(region.start)) + '-' + str(region.end))

            for j, it in enumerate(resLocal):
                r = regions[j]
                if not r in resultsDict.keys():
                    resultsDict[r] = []

                if len(it) > 0:
                    if option == cls.OPTION1:
                        resultsDict[r].append(it[0])
                    if option == cls.OPTION2:
                        start = results.getAllRegionKeys()[j].start
                        end = results.getAllRegionKeys()[j].end
                        resultsDict[r].append(float(it[0]) / (float(end) - float(start)))



        return bpTrackSize, regions, resultsDict

    @classmethod
    def getAllPreprocessedChoices(cls, choices):
        gsuite = choices.gsuite
        gSuite = getGSuiteFromGalaxyTN(gsuite)
        option = choices.option
        sumStat = choices.sumStat
        genome = gSuite.genome
        selFile = choices.selFile
        sharedRegions = choices.sharedRegions
        selFileTrack = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome,
                                                                             selFile,
                                                                             printErrors=False,
                                                                             printProgress=False)
        # queryTrack = Track(selFileTrack)
        # analysisSpec1 = AnalysisSpec(BpCoveragePerT2SegStat)
        # analysisSpec2 = AnalysisSpec(CountSegmentStat)

        queryTrack = selFileTrack
        analysisSpec1 = AnalysisSpec(SingleTSStat)
        analysisSpec1.addParameter('rawStatistic', BpCoveragePerT2SegStat.__name__)

        analysisSpec2 = AnalysisSpec(SingleTSStat)
        analysisSpec2.addParameter('rawStatistic', CountSegmentStat.__name__)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=gSuite.genome)


        tracksList = [Track(x.trackName, trackTitle=x.title) for x in gSuite.allTracks()]
        tracksNameList = [x.title for x in gSuite.allTracks()]


        return analysisBins, analysisSpec1, analysisSpec2, genome, option, queryTrack, sumStat, tracksList, tracksNameList, sharedRegions, gSuite

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

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
        return 'customhtml'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
