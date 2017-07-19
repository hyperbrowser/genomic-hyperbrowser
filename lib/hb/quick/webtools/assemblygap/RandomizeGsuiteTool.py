import os
import subprocess
from collections import OrderedDict
from quick.util.CommonFunctions import ensurePathExists, silenceRWarnings
from gold.description.TrackInfo import TrackInfo
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuite import GSuite
from gold.origdata.FileFormatComposer import getComposerClsFromFileSuffix
from gold.track.Track import PlainTrack
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool, GeneralGuiToolMixin
from gold.track.Track import Track, PlainTrack
from quick.webtools.gsuite.GSuiteConvertFromPreprocessedToPrimaryTool import GSuiteConvertFromPreprocessedToPrimaryTool, \
    FileFormatInfo


class RandomizeGsuiteTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Randomize gsuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select a GSuite', 'gsuite'),
                ('Select track', 'track')]

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxTrack(cls, prevChoices):
        return GeneralGuiToolMixin.getHistorySelectionElement('bed')

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        import gold.gsuite.GSuiteComposer as GSuiteComposer
        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
        from quick.application.UserBinSource import GlobalBinSource
        from quick.extra.ProgressViewer import ProgressViewer
        from quick.extra.TrackExtractor import TrackExtractor

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        genome = gSuite.genome
        fullGenomeBins = GlobalBinSource(genome)


        # progressViewer = ProgressViewer(
        #     [(GSuiteConvertFromPreprocessedToPrimaryTool.PROGRESS_PROCESS_DESCRIPTION, len(gSuite))], galaxyFn)

        outGSuite = GSuite()
        hiddenStorageFn = cls.extraGalaxyFn[
            getGSuiteHistoryOutputName('storage', datasetInfo=choices.gsuite)]

        resFile = GalaxyRunSpecificFile(['genomeSize.bed'], galaxyFn)
        rfPath = resFile.getDiskPath()
        ensurePathExists(rfPath)

        print rfPath

        rf = open(rfPath, 'w')
        gen = GenomeInfo.getStdChrLengthDict('hg19')
        for keyG, itG in gen.items():
            rf.write(str(keyG) + '\t' + str(itG) + '\n')
        rf.close()


        allTracksLen = gSuite.numTracks()
        from random import randint
        randTracks = [randint(0,1) for p in range(0, allTracksLen)]

        fileNameSet = set()
        r = 0
        for track in gSuite.allTracks():
            if r in randTracks:
                fileName = GSuiteConvertFromPreprocessedToPrimaryTool._getUniqueFileName(fileNameSet, track.trackName)
                title = track.title
                attributes = track.attributes
                fi = cls._getFileFormatInfo(genome, track)

                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn,
                                                    extraFileName=fileName,
                                                    suffix=fi.suffix)
                print 'title', title, '<br>'

                gSuiteTrack = GSuiteTrack(uri, title=title,
                                          genome=genome, attributes=attributes)

                TrackExtractor.extractOneTrackManyRegsToOneFile(
                    track.trackName, fullGenomeBins,
                    gSuiteTrack.path,
                    fileFormatName=fi.fileFormatName,
                    globalCoords=True,
                    asOriginal=fi.asOriginal,
                    allowOverlaps=fi.allowOverlaps)

                print gSuiteTrack.path, '<br>'
                print uri

                command = """
                bedtools shuffle -i """ + str(gSuiteTrack.path) + """ -g """ + str(rfPath)
                process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

                results, errors = process.communicate()

                print results, errors

                # wr = open(gSuiteTrack.path, 'w')
                # wr.write(results)
                # wr.close()

                outGSuite.addTrack(gSuiteTrack)
                # progressViewer.update()
            r = r+1

        primaryFn = cls.extraGalaxyFn[
            getGSuiteHistoryOutputName('primary', datasetInfo=choices.gsuite)]
        GSuiteComposer.composeToFile(outGSuite, primaryFn)




    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    @classmethod
    def _getFileFormatInfo(cls, genome, track):

        suffix = TrackInfo(genome, track.trackName).fileType
        fileFormatName = 'BED'
        asOriginal = True
        allowOverlaps = True

        return FileFormatInfo(fileFormatName,
                                  asOriginal,
                                  allowOverlaps,
                                  suffix)

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
        return 'customhtml'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
