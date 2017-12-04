import os
import subprocess
from collections import OrderedDict

from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteComposer import composeToFile
from gold.gsuite.GSuiteEditor import selectRowsFromGSuiteByTitle
from gold.util.RandomUtil import random
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.CommonFunctions import ensurePathExists
from gold.gsuite import GSuiteConstants, GSuiteComposer
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool, GeneralGuiToolMixin
from gold.track.Track import Track, PlainTrack
from quick.webtools.assemblygap.Legend import Legend
from quick.webtools.gsuite.GSuiteConvertFromPreprocessedToPrimaryTool import GSuiteConvertFromPreprocessedToPrimaryTool, \
    FileFormatInfo
from quick.webtools.util import CommonFunctionsForTools


class RandomTracksFromGsuiteTool(GeneralGuiTool):
    INDEX_TITLE_DELIMITER = '_'

    @classmethod
    def getToolName(cls):
        return "Sample tracks from a collection of tracks (GSuite)"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite', 'gsuite'),
                ('Select number of tracks to be extracted', 'numTrack')]

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxNumTrack(cls, prevChoices):
        return '100'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        trackNumber = int(choices.numTrack)
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        genome = gSuite.genome

        allTracksLen = gSuite.numTracks()
        selectedIndices = random.sample(xrange(allTracksLen), trackNumber)

        resDict = OrderedDict()
        for i, trackTitle in enumerate(gSuite.allTrackTitles()):
            if (i) in selectedIndices:
                resDict[cls.addIndexToTitle((i), trackTitle)] = True
            else:
                resDict[cls.addIndexToTitle((i), trackTitle)] = False

        titleList = [cls.removeIndexFromTitleName(title) for title, selected in resDict.iteritems() if selected]
        filteredGSuite = selectRowsFromGSuiteByTitle(gSuite, titleList)

        composeToFile(filteredGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gsuite:
            return 'You need to specify GSuite'

        return None

    @classmethod
    def addIndexToTitle(cls, indx, title):
        return cls.INDEX_TITLE_DELIMITER.join([str(indx), title])

    @classmethod
    def removeIndexFromTitleName(cls, titleWithIndex):
        delimiterIndex = titleWithIndex.find(cls.INDEX_TITLE_DELIMITER)
        if delimiterIndex > -1:
            return titleWithIndex[(delimiterIndex + 1):]
        else:
            return titleWithIndex

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

        toolDescription = 'This tool creates a collection of tracks (GSuite) with specified number of tracks (randomly selected).'

        stepsToRunTool = ['Select GSuite',
                          'Select number of tracks to be extracted '
                          ]

        toolResult = 'The output of this tool is a randomly selected collection of tracks presented as GSuite.'

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
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'gsuite'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()




# import os
# import subprocess
# from collections import OrderedDict
#
# from gold.util.RandomUtil import random
# from quick.application.ExternalTrackManager import ExternalTrackManager
# from quick.util.CommonFunctions import ensurePathExists
# from gold.gsuite import GSuiteConstants
# from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
# from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
# from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
# from quick.util.GenomeInfo import GenomeInfo
# from quick.webtools.GeneralGuiTool import GeneralGuiTool, GeneralGuiToolMixin
# from gold.track.Track import Track, PlainTrack
# from quick.webtools.gsuite.GSuiteConvertFromPreprocessedToPrimaryTool import GSuiteConvertFromPreprocessedToPrimaryTool, \
#     FileFormatInfo
#
#
# class RandomizeGsuiteTool(GeneralGuiTool):
#     @classmethod
#     def getToolName(cls):
#         return "Randomize gsuite"
#
#     @classmethod
#     def getInputBoxNames(cls):
#         return [('Select a GSuite', 'gsuite'),
#                 ('With exclusion', 'excl'),
#                 ('Select track', 'track'),
#                 ('Number of tracks from gsuite which you want to randomise ', 'trackNumber'),
#                 ('Number of randomised variants', 'varTracks')]
#
#     @classmethod
#     def getOptionsBoxGsuite(cls):
#         return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')
#
#     @classmethod
#     def getOptionsBoxExcl(cls, prevChoices):
#         return ['yes', 'no']
#
#     @classmethod
#     def getOptionsBoxTrack(cls, prevChoices):
#         if prevChoices.excl == 'yes':
#             return GeneralGuiToolMixin.getHistorySelectionElement('bed')
#
#     @classmethod
#     def getOptionsBoxTrackNumber(cls, prevChoices):
#         return '10'
#
#     @classmethod
#     def getOptionsBoxVarTracks(cls, prevChoices):
#         return '100'
#
#     @classmethod
#     def execute(cls, choices, galaxyFn=None, username=''):
#         #http://bedtools.readthedocs.io/en/latest/content/tools/shuffle.html
#
#         import gold.gsuite.GSuiteComposer as GSuiteComposer
#         from gold.gsuite.GSuite import GSuite
#         from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
#         from quick.application.UserBinSource import GlobalBinSource
#         from quick.extra.ProgressViewer import ProgressViewer
#         from quick.extra.TrackExtractor import TrackExtractor
#
#         trackNumber = int(choices.trackNumber)
#         varTracks = int(choices.varTracks)
#
#         gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
#         genome = gSuite.genome
#         fullGenomeBins = GlobalBinSource(genome)
#
#
#         # progressViewer = ProgressViewer(
#         #     [(GSuiteConvertFromPreprocessedToPrimaryTool.PROGRESS_PROCESS_DESCRIPTION, len(gSuite))], galaxyFn)
#
#         outGSuite = GSuite()
#         hiddenStorageFn = cls.extraGalaxyFn[
#             getGSuiteHistoryOutputName('storage', datasetInfo=choices.gsuite)]
#
#         resFile = GalaxyRunSpecificFile(['genomeSize.bed'], galaxyFn)
#         rfPath = resFile.getDiskPath()
#         ensurePathExists(rfPath)
#
#         #genome
#         rf = open(rfPath, 'w')
#         gen = GenomeInfo.getStdChrLengthDict('hg19')
#         for keyG, itG in gen.items():
#             rf.write(str(keyG) + '\t' + str(itG) + '\n')
#         rf.close()
#
#
#         allTracksLen = gSuite.numTracks()
#         from random import randint
#
#         randTracks = random.sample(xrange(allTracksLen), trackNumber)
#
#         # print 'randTracks', randTracks, '<br>'
#
#         fileNameSet = set()
#         r = 0
#         for track in gSuite.allTracks():
#             if r in randTracks:
#                 for nt in range(0, varTracks):
#                     # print 'r', r, 'nt', nt, '<br>'
#                     variants = '---' + str(nt)
#                     fileName = cls._getUniqueFileName(fileNameSet, track.trackName, variants)
#                     title = track.title
#                     title = title.replace(' ','') + variants
#                     attributes = track.attributes
#                     #fi = cls._getFileFormatInfo(gSuite, genome, track)
#
#
#
#                     fi = FileFormatInfo(fileFormatName='BED', asOriginal=False, allowOverlaps=False,
#                                    suffix='bed')
#
#                     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn,
#                                                         extraFileName=fileName,
#                                                         suffix=fi.suffix)
#
#                     gSuiteTrack = GSuiteTrack(uri,
#                                               title=title,
#                                               genome=genome,
#                                               attributes={'orginalTrack': track.title})
#
#                     TrackExtractor.extractOneTrackManyRegsToOneFile(
#                         track.trackName, fullGenomeBins,
#                         gSuiteTrack.path,
#                         fileFormatName=fi.fileFormatName,
#                         globalCoords=True,
#                         asOriginal=fi.asOriginal,
#                         allowOverlaps=fi.allowOverlaps)
#
#                     # print 'gSuiteTrack.path', gSuiteTrack.path, '<br>'
#
#                     if choices.excl == 'no':
#                         command = """bedtools shuffle -i """ + str(
#                             gSuiteTrack.path) + """ -g """ + str(rfPath)
#                     else:
#                         bedFile = ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':'))
#                         command = """bedtools shuffle -i """ + str(
#                             gSuiteTrack.path) + """ -g """ + str(
#                             rfPath) + """ -excl """ + str(bedFile)
#
#                     process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
#                                                stdout=subprocess.PIPE,
#                                                stderr=subprocess.PIPE)
#
#                     results, errors = process.communicate()
#
#                     wr = open(gSuiteTrack.path, 'w')
#                     wr.write(results)
#                     wr.close()
#
#                     outGSuite.addTrack(gSuiteTrack)
#                     # progressViewer.update()
#             r = r+1
#
#         primaryFn = cls.extraGalaxyFn[
#             getGSuiteHistoryOutputName('primary', datasetInfo=choices.gsuite)]
#         GSuiteComposer.composeToFile(outGSuite, primaryFn)
#
#     @classmethod
#     def validateAndReturnErrors(cls, choices):
#
#         if choices.gsuite:
#             gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
#             allTracksLen = gSuite.numTracks()
#
#             if int(choices.trackNumber) > allTracksLen:
#                 return 'Max number of tracks is: ' + str(allTracksLen)
#         return None
#
#     @staticmethod
#     def _getUniqueFileName(fileNameSet, trackName, variants):
#         from gold.gsuite.GSuiteFunctions import \
#             renameBaseFileNameWithDuplicateIdx
#
#         candFileName = trackName[-1].replace(' ','') + variants
#         duplicateIdx = 1
#
#         while candFileName in fileNameSet:
#             duplicateIdx += 1
#             candFileName = renameBaseFileNameWithDuplicateIdx(candFileName,
#                                                               duplicateIdx)
#         fileNameSet.add(candFileName)
#         return candFileName
#
#     @classmethod
#     def _getFileFormatInfo(cls, gSuite, genome, track):
#
#         outputFormatDict = GSuiteConvertFromPreprocessedToPrimaryTool._getOutputFormatDict(gSuite, genome)
#
#         #FileFormatInfo(fileFormatName='BED', asOriginal=False, allowOverlaps=False, suffix='bed')
#
#         return outputFormatDict['BED (any overlaps merged)']
#
#
#     @classmethod
#     def getExtraHistElements(cls, choices):
#         from quick.webtools.GeneralGuiTool import HistElement
#         histList = []
#         histList.append(
#             HistElement(getGSuiteHistoryOutputName('primary', datasetInfo=choices.gsuite),
#                         GSuiteConstants.GSUITE_SUFFIX))
#         histList.append(
#             HistElement(getGSuiteHistoryOutputName('storage', datasetInfo=choices.gsuite),
#                         GSuiteConstants.GSUITE_SUFFIX, hidden=True))
#
#         return histList
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
#     #
#     # @classmethod
#     # def getOutputName(cls, choices=None):
#     #     return cls.getToolSelectionName()
