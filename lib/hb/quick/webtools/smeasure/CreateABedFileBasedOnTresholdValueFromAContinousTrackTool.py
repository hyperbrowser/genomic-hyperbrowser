from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.track.Track import Track
from proto.CommonFunctions import ensurePathExists
from proto.tools.GeneralGuiTool import HistElement
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.CountFunctionTrackBasedOnTresholdStat import \
    CountFunctionTrackBasedOnTresholdStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class CreateABedFileBasedOnTresholdValueFromAContinousTrackTool(GeneralGuiTool, GenomeMixin, UserBinMixin):
    @classmethod
    def getToolName(cls):

        return "Create a bed file based on treshold value from a continuous track"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select gsuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
                [('Select tresholds [values>treshold] (eg. 0.7,0.9)', 'treshold')
                 ] + cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxGsuite(cls):  # Alt: getOptionsBox1()
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxTreshold(cls, prevChoices):  # Alt: getOptionsBox2()
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        tresholdList = choices.treshold.encode('utf-8').replace(' ', '').split(',')
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        tracksList = [Track(x.trackName, trackTitle=x.title) for x in gSuite.allTracks()]

        outGSuite = GSuite()

        analysisSpec = AnalysisSpec(CountFunctionTrackBasedOnTresholdStat)
        for trNum, tr in enumerate(tresholdList):
            analysisSpec.addParameter("treshold", float(tr))
            regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
            analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=gSuite.genome)

            for i, track in enumerate(tracksList):

                attr = OrderedDict()
                attr['originalTrackName'] = str(track.trackTitle)
                attr['treshold'] = str(tr)


                fileName =  str(track.trackTitle)  + '-' + 'treshold-' + str(tr)

                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                    extraFileName=fileName,
                                                    suffix='bed')

                gSuiteTrack = GSuiteTrack(uri)
                outFn = gSuiteTrack.path
                ensurePathExists(outFn)

                results = doAnalysis(analysisSpec, analysisBins, [track])

                singleRegion = results.getAllRegionKeys()[0]
                resLocal = results.getAllValuesForResDictKey('Result')
                singleListOfElements = resLocal[0]

                chromosome = singleRegion.chr
                st = singleRegion.start

                data = []
                for s in singleListOfElements:
                    data.append([chromosome.encode('utf-8'), str(st+s), str(st+s+1)])

                writeFile = open(outFn, 'w')
                writeFile.write('\n'.join(['\t'.join(d) for d in data]))
                writeFile.close()

                outGSuite.addTrack(GSuiteTrack(uri, title=''.join(fileName), genome=choices.genome, attributes=attr))


        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['output treshold gSuite'])
        print 'Counted gSuite is in the history'


    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('output treshold gSuite', 'gsuite')]







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
