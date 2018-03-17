from proto.CommonFunctions import ensurePathExists
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from proto.RSetup import r


class PlotDenistyTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Plot chart with density per bin"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select file ', 'selFile'),
                ('Select bin', 'bin'),
                ('Description for label x', 'xLabel'),
                ('Description for label y', 'yLabel'),
                ('Title', 'title'),
                ('Extra option', 'selColor'),
                ]

    @classmethod
    def getOptionsBoxSelFile(cls):  # Alt: getOptionsBox1()
        return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxBin(cls, prevChoices):  # Alt: getOptionsBox2()
        return ''

    @classmethod
    def getOptionsBoxXLabel(cls, prevChoices):  # Alt: getOptionsBox2()
        return ''

    @classmethod
    def getOptionsBoxYLabel(cls, prevChoices):  # Alt: getOptionsBox2()
        return ''

    @classmethod
    def getOptionsBoxTitle(cls, prevChoices):  # Alt: getOptionsBox2()
        return ''

    @classmethod
    def getOptionsBoxSelColor(cls, prevChoices):  # Alt: getOptionsBox2()
        return ['color black-blue', 'colorful', 'colorful with contour']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selFile = choices.selFile
        bin = int(choices.bin)
        xLabel = choices.xLabel.encode('utf-8')
        yLabel = choices.yLabel.encode('utf-8')
        imgTitle = choices.title.encode('utf-8')
        selColor = choices.selColor.encode('utf-8')

        pathInput = ExternalTrackManager.extractFnFromGalaxyTN(selFile.split(':'))

        filename = 'output'
        fileOutputPdf = GalaxyRunSpecificFile([filename, filename + '.pdf'], galaxyFn)
        ensurePathExists(fileOutputPdf.getDiskPath())
        pathOutputPdf = fileOutputPdf.getDiskPath()

        fileOutputPng = GalaxyRunSpecificFile([filename, filename + '.png'], galaxyFn)
        ensurePathExists(fileOutputPng.getDiskPath())
        pathOutputPng = fileOutputPng.getDiskPath()

        cls.prepareDensityPlot(pathInput, pathOutputPdf, pathOutputPng, selColor, bin, xLabel,
                               yLabel, imgTitle)

        htmlCore = HtmlCore()
        htmlCore.paragraph('Selection')
        htmlCore.line('Bin: ' + str(bin))
        htmlCore.line('Extra option: ' + str(selColor))
        htmlCore.paragraph('Image PNG')
        htmlCore.link('Download', fileOutputPng.getURL())
        htmlCore.paragraph('Image PDF')
        htmlCore.link('Download', fileOutputPdf.getURL())
        htmlCore.paragraph('Plot')
        htmlCore.image(fileOutputPng.getURL())
        print htmlCore

    @classmethod
    def prepareDensityPlot(cls, pathInput, pathOutputPdf, pathOutputPng, selColor, bin, xLabel,
                           yLabel, imgTitle):
        rCode = """
                suppressMessages(library(ggplot2));
                suppressMessages(library(hexbin));

                plotDraw <- function(pathInput, pathOutputPdf, pathOutputPng, selColor, bin, xLabel, yLabel, imgTitle) {
                data <- read.table(pathInput, sep='\t', header = F)
                df <- data.frame(t(data))
                head(df)
                ## Use densCols() output to get density at each point
                x1<-df$X1
                x2<-df$X2

                p <- ggplot(df, aes(x = x1, y = x2))
                bins <- bin
                if (selColor == "color black-blue")
                {
                    p1 <- p + stat_binhex(bins = bins) + labs(x = xLabel) + labs(y = yLabel) + labs(title = imgTitle)
                } else {
                    myColor <- rev(RColorBrewer::brewer.pal(11, "Spectral"))
                    myColor_scale_fill_sqrt <- scale_fill_gradientn(colours = myColor, trans = "sqrt")

                    if (selColor == "colorful")
                    {
                        p1 <- p + myColor_scale_fill_sqrt + stat_binhex(bins = bins) + labs(x = xLabel) + labs(y = yLabel) + labs(title = imgTitle)
                    } else {
                        p <- p + myColor_scale_fill
                        p1 <- p + stat_binhex(bins = bins) + geom_density2d(colour = "black") + labs(x = xLabel) + labs(y = yLabel) + labs(title = imgTitle)
                    }
                }

                png(pathOutputPng)
                plot(p1)
                dev.off()

                pdf(pathOutputPdf)
                plot(p1)
                dev.off()


                #ggsave(pathOutputPdf, width = 6, height = 4)
                #ggsave(pathOutputPng)

            }
            """
        r(rCode)(pathInput, pathOutputPdf, pathOutputPng, selColor, bin, xLabel, yLabel, imgTitle)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None, which enables
        the execute button.

        Optional method. Default return value if method is not defined: None
        """
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     """
    #     Specifies a list of classes for subtools of the main tool. These
    #     subtools will be selectable from a selection box at the top of the
    #     page. The input boxes will change according to which subtool is
    #     selected.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    @classmethod
    def isPublic(cls):
        return True

    #
    # @classmethod
    # def isRedirectTool(cls):
    #     """
    #     Specifies whether the tool should redirect to an URL when the Execute
    #     button is clicked.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     """
    #     This method is called to return an URL if the isRedirectTool method
    #     returns True.
    #
    #     Mandatory method if isRedirectTool() returns True.
    #     """
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     """
    #     Specifies if a History item should be created when the Execute button
    #     is clicked.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     """
    #     Specifies if this tool could be run from batch using the batch. The
    #     batch run line can be fetched from the info box at the bottom of the
    #     tool.
    #
    #     Optional method. Default return value if method is not defined:
    #         same as isHistoryTool()
    #     """
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     """
    #     Specifies whether changing the content of textboxes causes the page
    #     to reload. Returning False stops the need for reloading the tool
    #     after each input, resulting in less lags for the user.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     """
    #     Specifies a list of input boxes which resets the subsequent stored
    #     choices previously made. The input boxes are specified by index
    #     (starting with 1) or by key.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     """
    #     Specifies a help text in HTML that is displayed below the tool.
    #
    #     Optional method. Default return value if method is not defined: ''
    #     """
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     """
    #     Specifies an id used by StaticFile.py to reference an illustration
    #     file on disk. The id is a list of optional directory names followed
    #     by a filename. The base directory is STATIC_PATH as defined by
    #     Config.py. The full path is created from the base directory
    #     followed by the id.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     """
    #     Specifies an URL to an example page that describes the tool, for
    #     instance a Galaxy page.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     """
    #     Specifies whether the debug mode is turned on. Debug mode is
    #     currently mostly used within the Genomic HyperBrowser and will make
    #     little difference in a plain Galaxy ProTo installation.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'
        #
        # @classmethod
        # def getOutputName(cls, choices=None):
        #     return cls.getToolSelectionName()
        #     """
        #     The title (name) of the main output history element.
        #
        #     Optional method. Default return value if method is not defined:
        #     the name of the tool.
        #     """