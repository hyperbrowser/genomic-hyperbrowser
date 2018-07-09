import os
import subprocess
from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.statistic.CountElementStat import CountElementStat
from gold.track.TrackStructure import SingleTrackTS
from gold.util.RandomUtil import random
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.statistic.AvgSegLenStat import AvgSegLenStat
from quick.statistic.SingleTSStat import SingleTSStat
from quick.util.CommonFunctions import ensurePathExists
from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool, GeneralGuiToolMixin
from gold.track.Track import Track, PlainTrack
from quick.webtools.assemblygap.Legend import Legend
from quick.webtools.gsuite.GSuiteConvertFromPreprocessedToPrimaryTool import GSuiteConvertFromPreprocessedToPrimaryTool, \
    FileFormatInfo
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin

#class RandomizeTracksInGsuiteTool(GeneralGuiTool, DebugMixin):
class RandomizeTracksInGsuiteTool(GeneralGuiTool, GenomeMixin):
    @classmethod
    def getToolName(cls):
        return "Randomize a collection of genomic tracks (GSuite)"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [
                   ('With exclusion', 'excl'),
                ('Select track of regions to be excluded', 'track'),
                ('Number of randomised samples to be generated for each track', 'varTracks'),
                ('Preserve the average length and the number of elements (per GSuite - [yes]) and (per each track in GSuite - [no])', 'option')]\
               # + \
               # cls.getInputBoxNamesForDebug()


    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxExcl(cls, prevChoices):
        return ['yes', 'no']

    @classmethod
    def getOptionsBoxTrack(cls, prevChoices):
        if prevChoices.excl == 'yes':
            return GeneralGuiToolMixin.getHistorySelectionElement('bed')

    @classmethod
    def getOptionsBoxVarTracks(cls, prevChoices):
        return '1'

    @classmethod
    def getOptionsBoxOption(cls, prevChoices):
        return ['yes', 'no']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        #http://bedtools.readthedocs.io/en/latest/content/tools/shuffle.html

        # cls._setDebugModeIfSelected(choices)
        import gold.gsuite.GSuiteComposer as GSuiteComposer
        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
        from quick.application.UserBinSource import GlobalBinSource
        from quick.extra.TrackExtractor import TrackExtractor

        option = choices.option
        varTracks = int(choices.varTracks)

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        genome = gSuite.genome
        fullGenomeBins = GlobalBinSource(genome)

        outGSuite = GSuite()
        hiddenStorageFn = cls.extraGalaxyFn[
            getGSuiteHistoryOutputName('storage', datasetInfo=choices.gsuite)]

        resFile = GalaxyRunSpecificFile(['genomeSize.bed'], galaxyFn)
        rfPath = resFile.getDiskPath()
        ensurePathExists(rfPath)

        #genome
        rf = open(rfPath, 'w')
        gen = GenomeInfo.getStdChrLengthDict(gSuite.genome)
        for keyG, itG in gen.items():
            rf.write(str(keyG) + '\t' + str(itG) + '\n')
        rf.close()

        allTracksLen = gSuite.numTracks()
        analysisBins = GlobalBinSource(genome)
        analysis1 = AnalysisSpec(SingleTSStat)
        analysis1.addParameter('rawStatistic', AvgSegLenStat.__name__)
        # analysis1 = AnalysisSpec(AvgSegLenStat)
        analysis2 = AnalysisSpec(SingleTSStat)
        analysis2.addParameter('rawStatistic', CountElementStat.__name__)

        analysisDict = OrderedDict()
        avgLength = 0
        avgNumber = 0
        for track in gSuite.allTracks():
            title = track.title

            if not title in analysisDict.keys():
                analysisDict[title] = {}
                analysisDict[title]['length'] = 0
                analysisDict[title]['number'] = 0

            sts = SingleTrackTS(PlainTrack(track.trackName), OrderedDict(title=track.title, genome=str(genome)))

            # resultsAvgSegLen = doAnalysis(analysis1, analysisBins, [PlainTrack(track.trackName)])
            resultsAvgSegLen = doAnalysis(analysis1, analysisBins, sts)
            analysisDict[title]['length'] = resultsAvgSegLen.getGlobalResult()['Result'].getResult()
            avgLength += analysisDict[title]['length']

            # resultsCountElement = doAnalysis(analysis2, analysisBins, [PlainTrack(track.trackName)])
            resultsCountElement = doAnalysis(analysis2, analysisBins, sts)
            analysisDict[title]['number'] = resultsCountElement.getGlobalResult()['Result'].getResult()
            avgNumber += analysisDict[title]['number']

        avgLength = float(avgLength/allTracksLen)
        avgNumber = float(avgNumber / allTracksLen)

        fileNameSet = set()
        r = 0
        for track in gSuite.allTracks():
            for nt in range(0, varTracks):
                variants = '---' + str(nt)
                fileName = cls._getUniqueFileName(fileNameSet, track.trackName, variants)

                orgTitle = track.title
                title = orgTitle.replace(' ','') + variants
                attributes = track.attributes

                fi = FileFormatInfo(fileFormatName='BED', asOriginal=False, allowOverlaps=False,
                               suffix='bed')

                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn,
                                                    extraFileName=fileName,
                                                    suffix=fi.suffix)

                gSuiteTrack = GSuiteTrack(uri,
                                          title=title,
                                          genome=genome,
                                          attributes={'orginalTrack': track.title})

                TrackExtractor.extractOneTrackManyRegsToOneFile(
                    track.trackName, fullGenomeBins,
                    gSuiteTrack.path,
                    fileFormatName=fi.fileFormatName,
                    globalCoords=True,
                    asOriginal=fi.asOriginal,
                    allowOverlaps=fi.allowOverlaps)

                if option == 'yes':
                    l = analysisDict[orgTitle]['length']
                    n = analysisDict[orgTitle]['number']
                else:
                    l = avgLength
                    n = avgNumber


                if choices.excl == 'no':
                    command = """bedtools random -l """ + str(l) + """ -n """ + str(n) + """ -g """ + str(rfPath)
                    # command = """bedtools shuffle -i """ + str(
                    #     gSuiteTrack.path) + """ -g """ + str(rfPath)

                    process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

                    results, errors = process.communicate()

                    wr = open(gSuiteTrack.path, 'w')
                    wr.write(results)
                    wr.close()


                else:

                    command = """bedtools random -l """ + str(l) + """ -n """ + str(
                        n) + """ -g """ + str(rfPath)

                    process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

                    results, errors = process.communicate()

                    wr = open(gSuiteTrack.path, 'w')
                    wr.write(results)
                    wr.close()

                    bedFile = ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':'))
                    command = """bedtools shuffle -i """ + str(
                        gSuiteTrack.path) + """ -g """ + str(
                        rfPath) + """ -excl """ + str(bedFile)

                    process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

                    results, errors = process.communicate()

                    wr = open(gSuiteTrack.path, 'w')
                    wr.write(results)
                    wr.close()



                outGSuite.addTrack(gSuiteTrack)
            r = r+1

        primaryFn = cls.extraGalaxyFn[
            getGSuiteHistoryOutputName('primary', datasetInfo=choices.gsuite)]
        GSuiteComposer.composeToFile(outGSuite, primaryFn)

        print 'Randomized GSuite is in the history'

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gsuite:
            return 'You need to specify GSuite'

        if choices.excl == 'yes' and not choices.track:
            return 'You need to specify track'

        if not choices.varTracks:
            return 'You need to specify number of randomised variants'


        return None

    @staticmethod
    def _getUniqueFileName(fileNameSet, trackName, variants):
        from gold.gsuite.GSuiteFunctions import \
            renameBaseFileNameWithDuplicateIdx

        candFileName = trackName[-1].replace(' ','') + variants
        duplicateIdx = 1

        while candFileName in fileNameSet:
            duplicateIdx += 1
            candFileName = renameBaseFileNameWithDuplicateIdx(candFileName,
                                                              duplicateIdx)
        fileNameSet.add(candFileName)
        return candFileName

    @classmethod
    def _getFileFormatInfo(cls, gSuite, genome, track):

        outputFormatDict = GSuiteConvertFromPreprocessedToPrimaryTool._getOutputFormatDict(gSuite, genome)

        #FileFormatInfo(fileFormatName='BED', asOriginal=False, allowOverlaps=False, suffix='bed')

        return outputFormatDict['BED (any overlaps merged)']


    @classmethod
    def getExtraHistElements(cls, choices):
        from quick.webtools.GeneralGuiTool import HistElement
        histList = []
        histList.append(
            HistElement(getGSuiteHistoryOutputName('primary', datasetInfo=choices.gsuite),
                        GSuiteConstants.GSUITE_SUFFIX))
        histList.append(
            HistElement(getGSuiteHistoryOutputName('storage', datasetInfo=choices.gsuite),
                        GSuiteConstants.GSUITE_SUFFIX, hidden=True))

        return histList

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

        toolDescription = 'This tool shuffles genomic tracks by excluding the randomization in certain regions'

        stepsToRunTool = ['Select GSuite',
                          'With exclusion (yes, no)',
                          'Select track of regions to be excluded',
                          'Number of randomised samples to be generated for each track ',
                          'Preserve the average length and the number of elements (per GSuite - [yes]) and (per each track in GSuite - [no])'
                          ]

        toolResult = 'The output of this tool is a randomized collection of tracks presented as GSuite.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult)
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
    #     return True

    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()




# from collections import OrderedDict
#
# from gold.application.HBAPI import doAnalysis
# from gold.description.AnalysisDefHandler import AnalysisSpec
# from gold.statistic import BpOverlapPValOneTrackFixedStat
# from gold.track.Track import Track
# from gold.util import CommonConstants
# from gold.util.RandomUtil import random
# from proto.hyperbrowser.HtmlCore import HtmlCore
# from quick.gsuite import GSuiteStatUtils
# from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
# from quick.statistic.GSuiteVsGSuiteWrapperStat import GSuiteVsGSuiteWrapperStat
# from quick.webtools.GeneralGuiTool import GeneralGuiTool, GeneralGuiToolMixin
# from quick.webtools.mixin.GenomeMixin import GenomeMixin
# from quick.webtools.mixin.UserBinMixin import UserBinMixin
# from quick.application.GalaxyInterface import GalaxyInterface
# from urllib import quote
#
# from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
#
#
# class CountNullModelForRandomizedGSuiteTool(GeneralGuiTool, UserBinMixin, GenomeMixin):
#     ALLOW_UNKNOWN_GENOME = False
#     OPTION = 'random'
#
#     @classmethod
#     def getToolName(cls):
#         return "Count null model for randomized gSuite"
#
#     @classmethod
#     def getInputBoxNames(cls):
#         return [('Select orginal gSuite', 'orgGsuite'),
#                 ('Select column from orginal gSuite', 'orgCol'),
#                 ('Select additional orginal gSuite', 'addGsuite'),
#                 ('Second randomized gSuite', 'gsuite')] + \
#                cls.getInputBoxNamesForGenomeSelection() + \
#                [('Second column from randomized gSuite', 'randCol'),
#                 ('Select method', 'method')] + \
#                cls.getInputBoxNamesForUserBinSelection()
#
#     @classmethod
#     def getOptionsBoxOrgGsuite(cls):
#         return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')
#
#     @classmethod
#     def getOptionsBoxOrgCol(cls, prevChoices):
#         if prevChoices.orgGsuite:
#             first = getGSuiteFromGalaxyTN(prevChoices.orgGsuite)
#             attributeList = [cls.OPTION] + ['title'] + first.attributes
#             return attributeList
#         else:
#             return
#
#     @classmethod
#     def getOptionsBoxAddGsuite(cls, prevChoices):
#         if prevChoices.orgCol == cls.OPTION:
#             return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')
#
#     @classmethod
#     def getOptionsBoxGsuite(cls, prevChoices):
#         return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')
#
#     # options: random mean that two gsuites does not have any common column
#
#     @classmethod
#     def getOptionsBoxRandCol(cls, prevChoices):
#         if prevChoices.gsuite:
#             first = getGSuiteFromGalaxyTN(prevChoices.gsuite)
#             attributeList = ['title'] + first.attributes
#             return attributeList
#         else:
#             return
#
#     @classmethod
#     def getOptionsBoxMethod(cls, prevChoices):
#         return ['1', '2']
#
#     @classmethod
#     def execute(cls, choices, galaxyFn=None, username=''):
#         orgGsuite = choices.orgGsuite
#         randGsuite = choices.gsuite
#         orgCol = choices.orgCol
#         randCol = choices.randCol
#         method = choices.method
#
#         printing = False
#
#         if orgCol == cls.OPTION:
#             addGsuite = choices.addGsuite
#             additiionalgSuite = getGSuiteFromGalaxyTN(addGsuite)
#             addAttributesList = additiionalgSuite.allTrackTitles()
#
#         orginalgSuite = getGSuiteFromGalaxyTN(orgGsuite)
#         randomGsuite = getGSuiteFromGalaxyTN(randGsuite)
#
#         if randCol == 'title':
#             randAttributesList = randomGsuite.allTrackTitles()
#         else:
#             randAttributesList = randomGsuite.getAttributeValueList(randCol)
#
#         randAttributesListNotDuplicates = list(set(randAttributesList))
#         numRandAttributesList = len(list(set(randAttributesListNotDuplicates)))
#
#         howManyTimesWasEveryTracksRandomize = len(randAttributesList) / numRandAttributesList
#
#         #
#         # print 'randAttributesListNotDuplicates', randAttributesListNotDuplicates, '<br>'
#         # print 'numRandAttributesList', numRandAttributesList, '<br>'
#
#         if orgCol == 'title' or orgCol == cls.OPTION:
#             orgAttributesList = orginalgSuite.allTrackTitles()
#         else:
#             orgAttributesList = orginalgSuite.getAttributeValueList(orgCol)
#
#         orgAttributesListNotDuplicates = list(set(orgAttributesList) - set(randAttributesList))
#         numOrgAttributesListNotDuplicates = len(orgAttributesListNotDuplicates)
#
#         # print 'orgAttributesListNotDuplicates', orgAttributesListNotDuplicates, '<br>'
#         # print 'numOrgAttributesListNotDuplicates', numOrgAttributesListNotDuplicates,'<br>'
#
#
#         # random tracks just for having analysis real to real
#         if orgCol != cls.OPTION:
#             randOrginalTracks = random.sample(xrange(numOrgAttributesListNotDuplicates),
#                                               numRandAttributesList)
#         else:
#             randTracksForTwoOrginalDatasets = random.sample(xrange(len(addAttributesList)),
#                                                             numRandAttributesList)
#             addOrginalTracks = randTracksForTwoOrginalDatasets[0:numRandAttributesList]
#
#             randOrginalTracks = random.sample(xrange(numOrgAttributesListNotDuplicates),
#                                               numRandAttributesList)
#             if printing == True:
#                 print 'addOrginalTracks', addOrginalTracks, len(addOrginalTracks), '<br>'
#
#         if printing == True:
#             print 'randOrginalTracks', randOrginalTracks, '<br>'
#
#         resultsDict = OrderedDict()
#
#         originalTracksVSRandTracks = OrderedDict()
#
#         oTr = 0
#         rTr = 0
#         for oTrack1 in orginalgSuite.allTracks():
#             if oTr in randOrginalTracks:
#
#                 # first analysis
#                 # one random track from gsuite1 - T1
#                 # second random track from gsuite - T2
#
#                 # T1
#                 oTrackName1 = oTrack1.trackName
#                 oTrackTitle1 = oTrackName1[-1]
#
#                 # T2 - random tracks to comapare
#                 if orgCol == cls.OPTION:
#                     oTrack2 = additiionalgSuite.getTrackFromIndex(addOrginalTracks[rTr])
#                     oTrackName2 = oTrack2.trackName
#                     oTrackTitle2 = oTrackName2[-1]
#                 else:
#                     oTrack2 = orginalgSuite.getTrackFromTitle(randAttributesListNotDuplicates[rTr])
#                     oTrackTitle2 = randAttributesListNotDuplicates[rTr]
#
#                     if not oTrackTitle2 in originalTracksVSRandTracks.keys():
#                         originalTracksVSRandTracks[oTrackTitle2] = oTrackTitle1
#
#                 if method == '1':
#                     if not oTrackTitle2 in resultsDict.keys():
#                         resultsDict[oTrackTitle2] = OrderedDict()
#                         resultsDict[oTrackTitle2]['firstRealToSecondRealValue'] = 0
#                         resultsDict[oTrackTitle2]['firstRealToRandomLessCountedValues'] = 0
#                         resultsDict[oTrackTitle2]['firstRealToRandomMoreOrEqualCountedValues'] = 0
#
#                     if printing == True:
#                         print 'oTrackTitle1', oTrackTitle1, '<br>'
#                         print 'oTrackTitle2', oTrackTitle2, '<br>'
#                     analysis1 = cls.countNullModelMethod(choices, oTrack1, oTrack2, orginalgSuite)
#
#                     if printing == True:
#                         print 'analysis1', analysis1, '<br>'
#                         print 'resultsDict', resultsDict, '<br>'
#
#                     for key0, val0 in analysis1.iteritems():
#                         for key1, val1 in val0.iteritems():
#                             resultsDict[oTrackTitle2]['firstRealToSecondRealValue'] = float(val1)
#
#                 if method == '2':
#                     resultsDict[oTrackTitle2] = OrderedDict()
#                     resultsDict[oTrackTitle2]['values'] = []
#
#                 rTr += 1
#             oTr += 1
#
#         if printing == True:
#             print '<br><br><br><br><br>'
#
#             print 'originalTracksVSRandTracks', originalTracksVSRandTracks, '<br>'
#             print 'resultsDict', resultsDict, '<br>'
#
#             print '<br><br><br><br><br>'
#
#         # check random number of tracks
#         numForEveryTracksRandomize = 0
#         for nrRTrack1, rTrack1 in enumerate(randomGsuite.allTracks()):
#             rTrackName1 = rTrack1.trackName
#             attrRtrack1 = randAttributesList[nrRTrack1]
#
#             if printing == True:
#                 print 'attrRtrack1', attrRtrack1, '<br>'
#             if orgCol != cls.OPTION:
#                 oTrack1 = orginalgSuite.getTrackFromTitle(originalTracksVSRandTracks[attrRtrack1])
#                 oTrackName1 = oTrack1.trackName
#                 oTrackTitle1 = oTrackName1[-1]
#             else:
#                 if nrRTrack1 != 0 and nrRTrack1 % (howManyTimesWasEveryTracksRandomize) == 0:
#                     numForEveryTracksRandomize += 1
#
#                 oTrack1 = additiionalgSuite.getTrackFromIndex(
#                     addOrginalTracks[numForEveryTracksRandomize])
#                 oTrackName1 = oTrack1.trackName
#                 oTrackTitle1 = oTrackName1[-1]
#                 attrRtrack1 = oTrackTitle1
#
#                 if printing == True:
#                     print 'attrRtrack1', attrRtrack1, '<br>'
#
#             if printing == True:
#                 print 'oTrackTitle1', oTrackTitle1, '<br>'
#                 print 'rTrackName1', rTrackName1, '<br>'
#
#             analysis1 = cls.countNullModelMethod(choices, oTrack1, rTrack1, orginalgSuite)
#
#             if printing == True:
#                 print 'analysis1', analysis1, '<br>'
#
#             if method == '1':
#                 val = resultsDict[attrRtrack1]['firstRealToSecondRealValue']
#                 for key0, val0 in analysis1.iteritems():
#                     for key1, val1 in val0.iteritems():
#                         if printing == True:
#                             print 'val, val1', val, val1, '<br>'
#                         if float(val1) < val:
#                             resultsDict[attrRtrack1]['firstRealToRandomLessCountedValues'] += 1
#                         else:
#                             resultsDict[attrRtrack1][
#                                 'firstRealToRandomMoreOrEqualCountedValues'] += 1
#             if method == '2':
#                 for key0, val0 in analysis1.iteritems():
#                     for key1, val1 in val0.iteritems():
#                         resultsDict[attrRtrack1]['values'].append(val1)
#
#         if printing == True:
#             print '<br><br><br><br><br>'
#             print 'resultsDict', resultsDict, '<br>'
#             print '<br><br><br><br><br>'
#
#         vg = visualizationGraphs()
#
#         if method == '1':
#
#             pValueList = []
#             for key0, it0 in resultsDict.iteritems():
#                 if printing == True:
#                     print key0, it0, '<br>'
#                     print 'len(randAttributesList)', len(
#                         randAttributesList), 'numRandAttributesList', numRandAttributesList, '<br>'
#                     print 'float(float(len(randAttributesList))/numRandAttributesList)', float(
#                         float(len(randAttributesList)) / numRandAttributesList), '<br>'
#                 pValue = float(it0['firstRealToRandomMoreOrEqualCountedValues']) / float(
#                     float(len(randAttributesList)) / numRandAttributesList)
#                 if printing == True:
#                     print pValue, '<br>'
#                 pValueList.append(pValue)
#
#             # print pValueList
#
#
#             res = vg.drawScatterChart(
#                 pValueList,
#                 seriesName=['p-values'],
#                 label='<b>{series.name}</b>: {point.y}',
#                 height=300,
#                 yAxisTitle='p-values',
#                 marginTop=30
#             )
#         if method == '2':
#
#             pValueList = []
#             for key0, it0 in resultsDict.iteritems():
#                 pValueList += it0['values']
#
#             if printing == True:
#                 print 'pValueList', pValueList, '<br>'
#
#             from proto.RSetup import robjects, r
#             rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
#             dd = robjects.FloatVector(pValueList)
#             simpleHist = r(rCode)(dd)
#
#             breaks = list(simpleHist.rx2('breaks'))
#             counts = list(simpleHist.rx2('counts'))
#
#             res = vg.drawColumnChart(counts,
#                                      xAxisRotation=90,
#                                      categories=breaks,
#                                      showInLegend=False,
#                                      histogram=True,
#                                      height=400
#                                      )
#
#         htmlCore = HtmlCore()
#         htmlCore.begin()
#         htmlCore.line(res)
#         htmlCore.end()
#
#         print 'Results'
#         print htmlCore
#
#     @classmethod
#     def countNullModelMethod(cls, choices, oTrack1, oTrack2, orginalgSuite):
#         regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
#         analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec,
#                                                          genome=orginalgSuite.genome)
#         queryTrackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
#             [quote(oTrack1.title, safe='')])
#         refTrackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
#             [quote(oTrack2.title, safe='')])
#         queryTrackList = [Track(oTrack1.trackName, oTrack1.title)]
#         refTrackList = [Track(oTrack2.trackName, oTrack2.title)]
#         # print queryTrackTitles, '<br>'
#         # print refTrackTitles, '<br>'
#         analysisSpec = AnalysisSpec(GSuiteVsGSuiteWrapperStat)
#         analysisSpec.addParameter('queryTracksNum', str(len(queryTrackList)))
#         analysisSpec.addParameter('refTracksNum', str(len(refTrackList)))
#         analysisSpec.addParameter('queryTrackTitleList', queryTrackTitles)
#         analysisSpec.addParameter('refTrackTitleList', refTrackTitles)
#         stat = GSuiteStatUtils.T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP
#         analysisSpec.addParameter('similarityStatClassName',
#                                   str(GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[stat]))
#         resultsObj = doAnalysis(analysisSpec, analysisBins, queryTrackList + refTrackList)
#         results = resultsObj.getGlobalResult()
#         analysis1 = results['Similarity_score_table']
#         return analysis1
#         return analysis1
#
#     analysis = AnalysisSpec(BpOverlapPValOneTrackFixedStat)
#
#     @classmethod
#     def validateAndReturnErrors(cls, choices):
#         return None
#
#     # @classmethod
#     # def getSubToolClasses(cls):
#     #     return None
#     #
#     # @classmethod
#     # def isPublic(cls):
#     #     return False
#     #
#     # @classmethod
#     # def isRedirectTool(cls):
#     #     return False
#     #
#     # @classmethod
#     # def getRedirectURL(cls, choices):
#     #     return ''
#     #
#     # @classmethod
#     # def isHistoryTool(cls):
#     #     return True
#     #
#     # @classmethod
#     # def isBatchTool(cls):
#     #     return cls.isHistoryTool()
#     #
#     # @classmethod
#     # def isDynamic(cls):
#     #     return True
#     #
#     # @classmethod
#     # def getResetBoxes(cls):
#     #     return []
#     #
#     # @classmethod
#     # def getToolDescription(cls):
#     #     return ''
#     #
#     # @classmethod
#     # def getToolIllustration(cls):
#     #     return None
#     #
#     # @classmethod
#     # def getFullExampleURL(cls):
#     #     return None
#     #
#     # @classmethod
#     # def isDebugMode(cls):
#     #     return False
#     #
#     @classmethod
#     def getOutputFormat(cls, choices):
#         return 'customhtml'
#         #
#         # @classmethod
#         # def getOutputName(cls, choices=None):
#         #     return cls.getToolSelectionName()
