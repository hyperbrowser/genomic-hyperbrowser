from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteConstants
from gold.statistic.CountSegmentStat import CountSegmentStat
from gold.statistic.ProportionCountStat import ProportionCountStat
from gold.track.Track import PlainTrack, Track
from quick.statistic.SingleTSStat import SingleTSStat
from proto.CommonFunctions import ensurePathExists
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from proto.StaticFile import GalaxyRunSpecificFile
from collections import OrderedDict
from gold.track.TrackStructure import SingleTrackTS
from proto.hyperbrowser.HtmlCore import HtmlCore
# Author: Diana Domanska
from quick.webtools.mixin.UserBinMixin import UserBinMixin

'''
Input:
1 - Track
2 - GSuite file

Calculation:
Calculate overlaps in segments among track and other tracks
Vizualization: heatmap, column and line plots


Output:
hmtl file

'''

colorMaps = {
    'BlueYellowRedBlack': [[0, '#3060cf'], [0.5, '#fffbbc'], [0.9, '#c4463a'], [1, '#000000']],
    'WhiteGrayBlack': [[0, '#ffffff'], [0.5, '#cccccc'], [0.9, '#4a525a'], [1.0, '#000000']],
    'GreenOrangeBlue': [[0, '#c2ecb5'], [0.5, '#ff6600'], [1.0, '#31698a']],
    'GrayPinkBlack': [[0, '#cdc5bf'], [0.5, '#ffe4e1'], [0.9, '#fa5d68'], [1, '#000000']],
    'YellowVioletRed': [[0, '#ffffc1'], [0.5, '#9304ec'], [1.0, '#c4463a']]
}


class GenerateVisualizationOverlapHeatmapTool(GeneralGuiTool, UserBinMixin, GenomeMixin):
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False

    exception = None

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    TRACK_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                 GSuiteConstants.VALUED_SEGMENTS]  # points?

    @staticmethod
    def getToolName():
        return "Count bp coverage in a bin (region) between tracks in GSuite"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select GSuite file from history', 'gsuite'), \
                ('Select metadata from GSuite', 'selectColumns')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [
                   ('Select a color map:', 'colorMapSelectList')
               ] + cls.getInputBoxNamesForUserBinSelection()


    # @staticmethod
    # def getOptionsBoxTargetTrack():  # refTrack
    #     return GeneralGuiTool.getHistorySelectionElement('bed', 'gtrack')

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxSelectColumns(cls, prevChoices):
        from gold.gsuite.GSuiteConstants import TITLE_COL
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

        if prevChoices.gsuite == None:
            return
        try:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
        except:
            return

        cols = []
        if gSuite.hasCustomTitles():
            cols.append(TITLE_COL)
        cols += gSuite.attributes

        return cols

    @staticmethod
    def getOptionsBoxColorMapSelectList(prevChoices):  # Alternatively: getOptionsBox1()
        return colorMaps.keys()

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        # DebugUtil.insertBreakPoint()
        #cls._setDebugModeIfSelected(choices)
        genome = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        #queryTrackName = ExternalTrackManager.extractFnFromGalaxyTN(choices.targetTrack)

        from gold.gsuite.GSuiteConstants import TITLE_COL
        staticFile = []

        analysisSpec = AnalysisSpec(SingleTSStat)

        analysisSpec.addParameter('rawStatistic', CountSegmentStat.__name__)
        #analysisSpec.addParameter('rawStatistic', ProportionCountStat.__name__)
        # regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices.targetTrack, False)
        # binSpec = queryTrackName

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                         binSpec,
                                                         choices.genome)
        # analysisBins = GlobalBinSource(genome)
        segmentsList=[]
        results = []
        trackTitles = []
        for i, track in enumerate(gSuite.allTracks()):
            tt = track.title
            sts = SingleTrackTS(PlainTrack(track.trackName),OrderedDict(title=tt, genome=str(genome)))
            trackTitles.append(tt)
            #resultsAvgSegLen
            res = doAnalysis(analysisSpec, analysisBins, sts)

            segCoverageProp = [res[seg]['Result'].result for seg in res.getAllRegionKeys()]
            results.append(segCoverageProp)



            regFileNamer = GalaxyRunSpecificFile(track.trackName, galaxyFn)
            staticFile.append([regFileNamer.getLink('Download bed-file'),
                               regFileNamer.getLoadToHistoryLink('Download bed-file to History')])


        refGSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        if TITLE_COL == choices.selectColumns:
            selected = trackTitles
        else:
            selected = refGSuite.getAttributeValueList(choices.selectColumns)

        yAxisNameOverMouse = []
        metadataAll = []

        for x in range(0, len(selected)):
            if selected[x] == None:
                yAxisNameOverMouse.append(str(trackTitles[x]) + ' --- ' + 'None')
            else:
                if TITLE_COL == choices.selectColumns:
                    yAxisNameOverMouse.append(selected[x].replace('\'', '').replace('"', ''))
                else:
                    metadata = str(selected[x].replace('\'', '').replace('"', ''))
                    yAxisNameOverMouse.append(str(trackTitles[x]) + ' --- ' + metadata)
                    metadataAll.append(metadata)

        colorListForYAxisNameOverMouse = []

        # startEnd - order in res
        startEndInterval = []
        startEnd = []
        i = 0

        extraX = []
        rowLabel = []
        for ch in res.getAllRegionKeys():
            rowLabel.append(str(ch.chr) + ":" + str(ch.start) + "-" + str(ch.end))
            if not i == 0 and not i == len(segmentsList) - 1:
                start = ch.start
                if start - end > 0:
                    startEnd.append(start - end)
                else:
                    startEnd.append('null')
                    extraX.append(
                        """{ color: 'orange', width: 5, value: '""" + str(i - 0.5) + """' }""")
                startEndInterval.append(ch.end - ch.start)
            else:
                startEndInterval.append(ch.end - ch.start)
            end = ch.end
            i += 1

        htmlCore = HtmlCore()
        htmlCore.begin()

        writeFile = open(
            cls.makeHistElement(galaxyExt='tabular',
                                title='result'), 'w')

        i = 0

        writeFile.write('Track' + '\t' + '\t'.join(rowLabel) + '\n')
        for rList in results:
            writeFile.write(
                str(yAxisNameOverMouse[i]) + '\t' + '\t'.join([str(r) for r in rList]) + '\n')
            i += 1

        fileOutput = GalaxyRunSpecificFile(['heatmap.png'], galaxyFn)
        ensurePathExists(fileOutput.getDiskPath())

        fileOutputPdf = GalaxyRunSpecificFile(['heatmap.pdf'],galaxyFn)
        ensurePathExists(fileOutputPdf.getDiskPath())


        cls.generateStaticRPlot(results, colorListForYAxisNameOverMouse, rowLabel,
                                yAxisNameOverMouse,
                                colorMaps[choices.colorMapSelectList],
                                fileOutput.getDiskPath(), fileOutputPdf.getDiskPath())

        htmlCore.divBegin()
        htmlCore.link('Download heatmap of bp coverage in a bin (region)', fileOutputPdf.getURL())
        htmlCore.divEnd()
        # htmlCore.divBegin()
        # htmlCore.image(fileOutput.getURL())
        # htmlCore.divEnd()
        htmlCore.end()

        print htmlCore

        # create tmp file
        # import tempfile,os
        # tmp = tempfile.NamedTemporaryFile(delete = False, suffix='.png')
        # plt.savefig(tmp.name)
        # os.rename(tmp.name,galaxyFn)

    @classmethod
    def generateStaticRPlot(cls, inputData, colorListForYAxisNameOverMouse, colDataLabel,
                            rowDatalabel, colorMap, pathOutput, pathOutputPdf):

        from proto.RSetup import r

        colorList = []
        for c in colorMap:
            colorList.append(c[1])

        rCode = """

        suppressMessages(library(gplots));

         myHeatmap <- function(inputData, colorListForYAxisNameOverMouse, colDataLabel, rowDataLabel,colorList,  pathOutput, pathOutputPdf){

         dt <- inputData

         hscale=2+0.09*nrow(dt)
         wscale=2+0.09*ncol(dt)

         rownames(dt) <- as.array(rowDataLabel)
         colnames(dt) <- as.array(colDataLabel)
         dt <- as.matrix(dt)



         my_palette <- colorRampPalette(colorList)

         #png(pathOutput, width=1000, height=max(hscale*100, 1000))


         colorListForYAxisNameOverMouseWhite <- colorListForYAxisNameOverMouse
         colorListForYAxisNameOverMouseBlack <- colorListForYAxisNameOverMouse

         if (length(colorListForYAxisNameOverMouse) == 0 || length(colorListForYAxisNameOverMouse) != nrow(dt)) {
            colorListForYAxisNameOverMouseWhite <- rep("#FFFFFF", nrow(dt))
            colorListForYAxisNameOverMouseBlack <- rep("#000000", nrow(dt))
         }

        
        #   heatmap.2(dt,
        #     Colv=NA,
        #     margins=c(20,24),
        #     xlab="",
        #     ylab="",
        #     trace="none",
        #     dendrogram="row",
        #     key.title=NA,
        #     keysize=0.6,
        #     cexRow=0.4 + 1/log2(nrow(dt)),
        #     cexCol=0.4 + 1/log2(ncol(dt)),
        #     colRow=colorListForYAxisNameOverMouseBlack,
        #     RowSideColors=colorListForYAxisNameOverMouseWhite,
        #     symm=F,
        #     col=my_palette,
        #     symkey=F,
        #     symbreaks=T,
        # )
        # 
        # 
        # 
        # dev.off()

        pdf(pathOutputPdf, width=max(wscale, 10), height=max(hscale,10))


        heatmap.2(
          dt,
          Colv=NA,
          margins=c(20,24),
          xlab="",
            ylab="",
            trace="none",
            dendrogram="row",
            key.title=NA,
            keysize=0.6,
            cexRow=0.4 + 1/log2(nrow(dt)),
            cexCol=0.4 + 1/log2(ncol(dt)),
            colRow=colorListForYAxisNameOverMouseBlack,
            RowSideColors=colorListForYAxisNameOverMouseWhite,
            symm=F,
            col=my_palette,
            symkey=F,
            symbreaks=T,
          )


        dev.off()

        }

        """

        r(rCode)(inputData, colorListForYAxisNameOverMouse, colDataLabel, rowDatalabel, colorList,
                 pathOutput, pathOutputPdf)

        return 1

    @classmethod
    def validateAndReturnErrors(cls, choices):

        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gsuite,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)

        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(gsuite)
        if errorString:
            return errorString



    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()

        core.paragraph('This tool computes the bp overlap between the segments '
                       'of selected bin against each track in a collection of reference tracks '
                       'described in a GSuite file. The overlap bp are output in an '
                       'heatmap, where each cell is colored according to the '
                       'overlap between each query segment (column) with each reference '
                       'track (row).')

        core.divider()
        core.paragraph('To carry out the analysis, please follow these steps:')
        core.orderedList(['Select a genome build. Both the query track and the reference tracks'
                          'need to use the same genome build.',
                          'Select the color map, going from no overlap to full overlap.',
                          'Select region and scale (bin)',
                          'Click "Execute"'])

        core.divider()
        core.smallHeader('Requirements for query track')
        core.descriptionLine('Track types', ', '.join(cls.TRACK_ALLOWED_TRACK_TYPES),
                             emphasize=True)

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)
        #
        # htmlCore.divBegin(divId ='toolDesc')
        # htmlCore.descriptionLine('Tool description',
        #                         """This tool computes the proportions between overlaped segments.
        #                         Output are three plots: overlap with reference tracks for each local region,
        #                         lenghts of segments (local regions) and gaps between consecutive
        #                         segments. """)
        # htmlCore.divEnd()
        #
        # htmlCore.divBegin(divId ='toolExample')
        # htmlCore.line('<b>Example</b>')
        # htmlCore.line('<b>Input:</b>')
        # htmlCore.line('Genome build: Human Feb. 2009 (GRCh37/hg19) (hg19)')
        # htmlCore.line('Select track: Phenotype_and_disease_associations:Assorted_experiments:Virus_integration,_HPV_specific,_Kraus_et_al')
        # htmlCore.line('Select GSuite file from history: Genes and gene subsets:Genes')
        # htmlCore.line('Select a color map')
        # htmlCore.line('<b>Output:</b>')
        # htmlCore.line('Plots')
        #
        # htmlCore.divEnd()
        #
        # return htmlCore

    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None

    # @staticmethod
    # def getFullExampleURL():
    #     return 'u/hb-superuser/p/visualize-overlap-between-query-segments-and-reference-tracks-by-heatmap'

    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    @staticmethod
    def isDebugMode():
       return False

    @staticmethod
    def getOutputFormat(choices=None):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'
