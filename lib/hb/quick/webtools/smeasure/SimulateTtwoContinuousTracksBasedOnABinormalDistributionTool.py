import os
from rpy2 import robjects
from rpy2.robjects import r

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
from proto.CommonFunctions import ensurePathExists
from proto.tools.GeneralGuiTool import HistElement
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class SimulateTtwoContinuousTracksBasedOnABinormalDistributionTool(GeneralGuiTool, UserBinMixin):
    @classmethod
    def getToolName(cls):
        return "Simulate two continuous tracks based on a binormal distribution"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select covariance value', 'covValue'),
                ('Select values for mean (eg. 0.5)', 'meanValue'),
                ('Select genome', 'genome'),
                ] + cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxCovValue(cls):  # Alt: getOptionsBox1()
        return ''

    @classmethod
    def getOptionsBoxMeanValue(cls, prevChoices):  # Alt: getOptionsBox2()
        return ''

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):  # Alt: getOptionsBox2()
        return '__genome__'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        covValue = choices.covValue.encode('utf-8').replace(' ', '').split(',')
        meanValue = choices.meanValue.encode('utf-8').replace(' ', '').split(',')

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        parsedRegSpec = cls._readRegSpec(regSpec)

        outGSuite = GSuite()
        for iCov, cov in enumerate(covValue):

            fileName = 'syn-cov' + str(cov) + '-' + str(meanValue[iCov]) + '-iter-' + str(iCov)

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=fileName,
                                                suffix='gtrack')

            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            countData = "##Track type: function" + '\n'
            countData += '###value' + '\n'

            for chromosome in parsedRegSpec.keys():

                for prs in parsedRegSpec[chromosome]:
                    elementsNumber = int(prs[1]) - int(prs[0])

                    countData += ';'.join(['####genome=' + str(choices.genome), 'seqid=' + str(chromosome),'start=' + str(str(prs[0])),'end=' + str(str(prs[1]))]) + '\n'

                    rCode = """ 
                                library(MASS)
                                createTrack <- 
                                function(vec) {
                                    covChosen <- vec[1]
                                    mu <- vec[2]
                                    Sigma <- matrix(covChosen, nrow=1, ncol=1)
                                    rawvars <- mvrnorm(n=vec[3], mu=mu, Sigma=Sigma)
                                }"""
                    dd=robjects.FloatVector([covValue[iCov], meanValue[iCov], elementsNumber])
                    data = r(rCode)(dd)

                    countData += '\n'.join([str(d) for d in list(data)]) + '\n'

            writeFile = open(outFn, 'w')
            writeFile.write(countData)
            writeFile.close()

            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(fileName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['output gSuite'])
        print 'Counted gSuite is in the history'

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('output gSuite', 'gsuite')]

    @classmethod
    def _readRegSpec(cls, parameters):
        parameters = parameters.encode('utf-8')

        dataOut = {}
        parameters = parameters.replace(' ', '').split(',')
        for p in parameters:
            chromosme = p.split(':')[0]
            chromosmeSt = int(p.split(':')[1].split('-')[0])
            chromosmeEnd = int(p.split(':')[1].split('-')[1])

            if not chromosme in dataOut.keys():
                dataOut[chromosme] = []
            dataOut[chromosme].append([chromosmeSt, chromosmeEnd])

        return dataOut

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
        return 'gsuite'
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
