from proto.CommonFunctions import extractFileSuffixFromDatasetInfo, ensurePathExists, \
    extractFnFromDatasetInfo
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class PlotHClustTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Plot hierarchical clustering"

    @staticmethod
    def getInputBoxNames():
        return [('Select file', 'selFile')]

    @staticmethod
    def getOptionsBoxSelFile():
        return GeneralGuiTool.getHistorySelectionElement('tabular')


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selFile = choices.selFile
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.selFile.split(':')),
                         'r')

        data = ''
        with inputFile as f:
            i = 0
            for line in f.readlines():
                if i == 0:
                    data += line
                else:
                    x = line.strip('\n').split('\t')
                    data += '\t'.join([str(d) for d in [x[0].replace(' ','')] + x[1:]])+'\n'
                i+=1
        f.closed

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
                rt <- read.table(pathInput, dec='\t', fill=T, header=T, row.names=1)
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
