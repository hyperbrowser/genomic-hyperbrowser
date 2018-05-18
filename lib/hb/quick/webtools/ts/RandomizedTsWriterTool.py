import os

from proto.tools.hyperbrowser.GeneralGuiTool import GeneralGuiTool

import quick.gsuite.GuiBasedTsFactory as factory
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from gold.track.TrackStructure import TrackStructureV2
from gold.track.trackstructure import TsRandAlgorithmRegistry as TsRandAlgReg
from gold.track.trackstructure.TsUtils import getRandomizedVersionOfTs
from quick.application.UserBinSource import GlobalBinSource
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.TsWriterStat import TsWriterStat
from quick.webtools.GeneralGuiTool import GeneralGuiToolMixin
from quick.webtools.mixin.RandAlgorithmMixin import RandAlgorithmMixin


class RandomizedTsWriterTool(GeneralGuiTool, RandAlgorithmMixin):
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = []

    NO_CATEGORY_STR = 'None'

    @classmethod
    def getToolName(cls):
        """from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Create a randomized version of a GSuite"

    @classmethod
    def getInputBoxNames(cls):
        """
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of strings denoting the headers for the inputg+ cls.getInputBoxNamesForDebug()et boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase and start with a non-capital letter
              (e.g. "firstKey")

        Optional method. Default return value if method is not defined: []
        """
        return [('Select a GSuite', 'gs')] + \
               cls.getInputBoxNamesForRandAlgSelection() + \
               [('Category to randomize within (set to \'None\' in order to '
                 'randomize between all tracks in the GSuite)', 'category')]

    @staticmethod
    def isPublic():
        """
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        """
        return True

    @classmethod
    def getOptionsBoxGs(cls):  # Alt: getOptionsBox1()
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxCategory(cls, prevChoices):
        if prevChoices.randType == TsRandAlgReg.BETWEEN_TRACKS_CATEGORY:
            try:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.gs)
                if len(gSuite.attributes) > 0:
                    return [cls.NO_CATEGORY_STR] + gSuite.attributes
            except:
                return

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        """
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than
        'html', the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional
        files can be put (cls, e.g. generated image files). choices is a list
        of selections made by web-user in each options box.

        Mandatory unless isRedirectTool() returns True.
        """
        #TODO: add functionality for single gtrack within-track randomization

        print 'Executing...'

        inputGsuite = getGSuiteFromGalaxyTN(choices.gs)
        outputGSuite = GSuite()
        genome = inputGsuite.genome
        ts = factory.getFlatTracksTS(genome, choices.gs)
        randIndex = 0
        bins = GlobalBinSource(genome)

        if choices.randType == TsRandAlgReg.BETWEEN_TRACKS_CATEGORY and \
                choices.category not in [None, 'None']:
            ts = ts.getSplittedByCategoryTS(choices.category)
            randomizedTs = TrackStructureV2()
            for subTsKey, subTs in ts.items():
                tvProvider = cls.createTrackViewProvider(choices, subTs, bins, genome)
                randomizedTs[subTsKey] = getRandomizedVersionOfTs(subTs, tvProvider, randIndex)
            randomizedTs = randomizedTs.getFlattenedTS()
        else:
            tvProvider = cls.createTrackViewProvider(choices, ts, bins, genome)
            randomizedTs = getRandomizedVersionOfTs(ts, tvProvider, randIndex)

        for singleTrackTs in randomizedTs.getLeafNodes():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName= os.path.sep.join(singleTrackTs.track.trackName) + '.randomized',
                                                suffix='bed')

            title = singleTrackTs.metadata.pop('title')
            gSuiteTrack = GSuiteTrack(uri, title=title + '.randomized', fileFormat='primary', trackType='segments', genome=genome, attributes=singleTrackTs.metadata)
            outputGSuite.addTrack(gSuiteTrack)
            singleTrackTs.metadata['trackFilePath'] = gSuiteTrack.path

        spec = AnalysisSpec(TsWriterStat)
        res = doAnalysis(spec, bins, randomizedTs)
        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None

        , which enables
        the execute button.

        Optional method. Default return value if method is not defined: None
        """
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gs)
        if errorString:
            return errorString

        gsuite = getGSuiteFromGalaxyTN(choices.gs)

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

        errorString = cls.validateRandAlgorithmSelection(choices)
        if errorString:
            return errorString

    @classmethod
    def getOutputFormat(cls, choices):
        """
        The format of the history element with the output of the tool. Note
        that if 'html' is returned, any print statements in the execute()
        method is printed to the output dataset. For text-based output
        (e.g. bed) the output dataset only contains text written to the
        galaxyFn file, while all print statements are redirected to the info
        field of the history item box.

        Note that for 'html' output, standard HTML header and footer code is
        added to the output dataset. If one wants to write the complete HTML
        page, use the restricted output format 'customhtml' instead.

        Optional method. Default return value if method is not defined:
        'html'
        """
       # return 'html'
        return 'gsuite'
