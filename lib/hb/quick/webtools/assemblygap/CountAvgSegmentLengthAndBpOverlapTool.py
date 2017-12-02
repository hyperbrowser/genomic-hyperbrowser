from collections import OrderedDict
from operator import itemgetter

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteConstants
from gold.statistic.CountPointStat import CountPointStat
from gold.statistic.CountSegmentStat import CountSegmentStat
from gold.statistic.ProportionCountStat import ProportionCountStat
from gold.track.Track import PlainTrack
from gold.track.TrackStructure import SingleTrackTS
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.AvgSegLenStat import AvgSegLenStat
from quick.statistic.SingleTSStat import SingleTSStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.assemblygap.Legend import Legend
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class CountAvgSegmentLengthAndBpOverlapTool(GeneralGuiTool, UserBinMixin, GenomeMixin):
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
    @classmethod
    def getToolName(cls):
        return "Count average segment length according to bp overlap values"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite from history', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [
                   ('Select track from history', 'track')

               ] + cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxTrack(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @classmethod
    def getInputBoxNamesForGenomeSelection(cls):
        return [(cls.OPTIONS_BOX_MSG % cls.WHAT_GENOME_IS_USED_FOR, 'specifyGenomeFromGsuites'),
                ('Genome mismatch note', 'genomeMismatchNote'),
                ('Genome build:', 'specifyGenomeFromList'),
                ('Genome', 'genome')]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        genome = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        analysisSpec = AnalysisSpec(SingleTSStat)
        analysisSpec.addParameter('rawStatistic', AvgSegLenStat.__name__)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                         binSpec,
                                                         choices.genome)

        # analysisSpec1 = AnalysisSpec(SingleTSStat)
        # analysisSpec1.addParameter('rawStatistic', CountSegmentStat.__name__)
        #
        analysisSpec2 = AnalysisSpec(SingleTSStat)
        analysisSpec2.addParameter('rawStatistic', ProportionCountStat.__name__)
        regSpec2 = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices.track, False)
        binSpec2 = ExternalTrackManager.extractFnFromGalaxyTN(choices.track)
        analysisBins2 = GalaxyInterface._getUserBinSource(regSpec2,
                                                         binSpec2,
                                                         choices.genome)


        results = []
        trackTitles = []
        for i, track in enumerate(gSuite.allTracks()):
            tt = track.title
            trackTitles.append(tt)

            sts = SingleTrackTS(PlainTrack(track.trackName),OrderedDict(title=tt, genome=str(genome)))
            res = doAnalysis(analysisSpec, analysisBins, sts)
            avgSegLenPerTrack = res.getGlobalResult()['Result'].result

            # res1 = doAnalysis(analysisSpec1, analysisBins, sts)
            # genomeCoveragePerTrack = res1.getGlobalResult()['Result'].result

            res2 = doAnalysis(analysisSpec2, analysisBins2, sts)
            bpOverlapPerTrack = res2.getGlobalResult()['Result'].result

            results.append([tt, avgSegLenPerTrack, bpOverlapPerTrack])

        sortedRes = sorted(results, key=itemgetter(1))
        zipSorted = zip(*sortedRes)
        zipSorted = [list(i) for i in zipSorted]

        writeFile = open(
            cls.makeHistElement(galaxyExt='tabular',
                                title='Result for average segment length according to bp overlap values'), 'w')

        header = ['Track name', 'AvgSegLen', 'RatioBpOverlapWithinTrack']
        output = '\t'.join(header) + '\n'
        for sr in sortedRes:
            output += '\t'.join([str(s) for s in sr]) + '\n'

        writeFile.write(output)
        writeFile.close()

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.tableHeader(['Column name', 'Minimum', 'Maximum', 'Average', 'Median'])
        htmlCore.tableLine(['AvgSegLen', zipSorted[1][0], zipSorted[1][len(zipSorted[1])-1], sum(zipSorted[1])/len(zipSorted[1]), cls.median(zipSorted[1])])
        htmlCore.tableLine(['RatioBpOverlapWithinTrackAndGenome', zipSorted[2][0], zipSorted[2][len(zipSorted[2])-1], sum(zipSorted[2]) / len(zipSorted[2]), cls.median(zipSorted[2])])
        htmlCore.end()

        print htmlCore

    @classmethod
    def median(cls, x):
        if len(x) % 2 != 0:
            return sorted(x)[len(x) / 2]
        else:
            midavg = (sorted(x)[len(x) / 2] + sorted(x)[len(x) / 2 - 1]) / 2.0
            return midavg

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
    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'The tool allow to count average segment length according to bp overlap values.'

        stepsToRunTool = ['Select GSuite from history',
                          'Select track from history',
                          'Region and scale (deafult option: chromosomes)']

        toolResult = 'The results are presented as s table with two information: AvgSegLen (average segment length) and RatioBpOverlapWithinTrackAndGenome (ratio of overlap between every track in GSuite and track from history to global segment size ).'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult)
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
