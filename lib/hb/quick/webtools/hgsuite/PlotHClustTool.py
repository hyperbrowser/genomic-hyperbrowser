from collections import OrderedDict

from proto.CommonFunctions import extractFileSuffixFromDatasetInfo, ensurePathExists, \
    extractFnFromDatasetInfo
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile, StaticImage
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.CreateBoxPlotForFileTool import CreateBoxPlotForFileTool
from quick.webtools.hgsuite.Legend import Legend


class PlotHClustTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Plot hierarchical clustering for tabular file or hGSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'selFile'),
                ('Select column with names', 'selColNames'),
                ('Select column with values', 'selCol'),
                ]

    @staticmethod
    def getOptionsBoxSelFile():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'tabular')

    @classmethod
    def getOptionsBoxSelColNames(cls, prevChoices):
        if prevChoices.selFile:
            suffixForFile = extractFileSuffixFromDatasetInfo(prevChoices.selFile)

            if suffixForFile == 'tabular':
                return CreateBoxPlotForFileTool.returnColFile(prevChoices.selFile,
                                                              asListResponse=True)
            if suffixForFile == 'gsuite':
                gSuite = getGSuiteFromGalaxyTN(prevChoices.selFile, asListResponse=True)
                return CreateBoxPlotForFileTool.returnColFile(prevChoices.selFile,
                                                              gSuiteAttributes=gSuite.attributes + [
                                                                  cls.TITLE])

    @classmethod
    def getOptionsBoxSelCol(cls, prevChoices):
        if prevChoices.selFile:
            suffixForFile = extractFileSuffixFromDatasetInfo(prevChoices.selFile)

            if suffixForFile == 'tabular':
                return CreateBoxPlotForFileTool.returnColFile(prevChoices.selFile, asListResponse=True)
            if suffixForFile == 'gsuite':
                gSuite = getGSuiteFromGalaxyTN(prevChoices.selFile, asListResponse=True)
                return CreateBoxPlotForFileTool.returnColFile(prevChoices.selFile,
                                         gSuiteAttributes=gSuite.attributes + [cls.TITLE])
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        selFile = choices.selFile
        selCol = {choices.selCol:True}
        suffixForFile = extractFileSuffixFromDatasetInfo(choices.selFile)
        if suffixForFile == 'tabular':
            dataAll, categories = CreateBoxPlotForFileTool.openFileWithCategories(selFile, choices.selCol, choices.selColNames)
        if suffixForFile == 'gsuite':
            dataAll, categories = CreateBoxPlotForFileTool.openGSuiteFileWithCategories(selFile, choices.selCol,
                                                                                  choices.selColNames)
        data =''
        for kDA, itDA in dataAll.iteritems():
            data += str(kDA) + '\t' + '\t'.join([str(d) for d in itDA]) + '\n'

        fileInput = GalaxyRunSpecificFile(['data' + '.tabular'], galaxyFn)
        ensurePathExists(fileInput.getDiskPath())
        pathInput = fileInput.getDiskPath()
        ww = open(pathInput, 'w')
        ww.write(data)
        ww.close()

        fileOutput = GalaxyRunSpecificFile(['hclust' + '.png'], galaxyFn)
        ensurePathExists(fileOutput.getDiskPath())
        pathOutput = fileOutput.getDiskPath()

        fileOutputPdf = GalaxyRunSpecificFile(['hclust' + '.pdf'], galaxyFn)
        ensurePathExists(fileOutputPdf.getDiskPath())
        pathOutputPdf = fileOutputPdf.getDiskPath()

        from proto.RSetup import r

        rCode = """
            myPlot <- function(pathInput, pathOutput, pathOutputPdf){
                rt <- read.table(pathInput, dec='\t', fill=T, header=F, row.names=1)
                clusters <- hclust(dist(rt))
                
                png(pathOutput, width = 800, height = 600, pointsize = 12)
                plot(clusters)
                dev.off()
                
                pdf(pathOutputPdf, 10,7)
                plot(clusters)
                dev.off()
            }

        """
        r(rCode)(pathInput, pathOutput, pathOutputPdf)
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('resultsDiv')

        htmlCore.link('Download file', fileOutputPdf.getURL())
        htmlCore.line("<br>")
        htmlCore.image(fileOutput.getURL())

        htmlCore.divEnd()
        htmlCore.end()
        print htmlCore


    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices.selFile:
            if choices.selCol:
                suffixForFile = extractFileSuffixFromDatasetInfo(choices.selFile)
                if suffixForFile == 'tabular':
                    dataAll, categories = CreateBoxPlotForFileTool.openFile(choices.selFile, {choices.selCol:True})
                if suffixForFile == 'gsuite':
                    dataAll, categories = CreateBoxPlotForFileTool.openGSuiteFile(choices.selFile, {choices.selCol:True})

                howManycY = 0
                cY = 0
                for keyD, itD in dataAll.iteritems():
                    cY += CreateBoxPlotForFileTool._checkType(dataAll[keyD])
                    howManycY += 1

                if cY != howManycY:
                    return 'All the values need to be number type.'

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

        toolDescription = 'The tool allow to plot hierarchical clustering from columns of hGSuite or results from tabular file.'

        stepsToRunTool = ['Select file',
                          'Select column with names',
                          'Select column with values'
                          ]

        urlexample1Output = StaticImage(['hgsuite', 'img',
                                         'PlotHClustTool-img.png']).getURL()

        example = {'Example ': ['', ["""
    attribute0	attribute1	attribute2	attribute3
    track6.bed-CG	track6.bed	CG	1
    track6.bed-CA	track6.bed	CA	0
    track3.bed-CG	track3.bed	CG	0
    track3.bed-CA	track3.bed	CA	1
    track1.bed-CG	track1.bed	CG	0
    track1.bed-CA	track1.bed	CA	2
    track2.bed-CG	track2.bed	CG	0
    track2.bed-CA	track2.bed	CA	5
    track4.bed-CG	track4.bed	CG	0
    track4.bed-CA	track4.bed	CA	1
    track5.bed-CG	track5.bed	CG	1
    track5.bed-CA	track5.bed	CA	0

                        """],
    [
             ['Select file','tabular'],
             ['Select column with names','attribute0'],
             ['Select column with values','attribute3'],
     ],
          [
              '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="600" src="' + urlexample1Output + '" /></div>'
          ]
        ]
        }

        toolResult = 'The results are presented in a chart (png, pdf).'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example
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
        return 'customhtml'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
