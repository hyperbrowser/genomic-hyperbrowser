import os
from collections import OrderedDict

from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuiteFunctions import changeSuffixIfPresent, getTitleWithSuffixReplaced
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack
from gold.track.Track import Track
from gold.track.TrackFormat import TrackFormatReq
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.tools.GeneralGuiTool import HistElement
from quick.extra.ProgressViewer import ProgressViewer
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.track_operations.Genome import Genome
from quick.track_operations.TrackContents import TrackContents
from quick.track_operations.operations.Complement import Complement
from quick.track_operations.operations.Merge import Merge
from quick.track_operations.operations.PrintTrack import PrintTrack
from quick.track_operations.operations.Union import Union
from quick.track_operations.utils.TrackHandling import createTrackContentFromTrack
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin


class TrackOperationsTool(GeneralGuiTool, GenomeMixin):
    GSUITE_FILE_OPTIONS_BOX_KEYS = ['gSuite']
    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False
    ALLOW_MULTIPLE_GENOMES = False
    WHAT_GENOME_IS_USED_FOR = 'the output GSuite file'  # Other common possibility: 'the analysis'

    FROM_HISTORY_TEXT = 'From history'
    FROM_HYPERBROWSER_TEXT = 'From HyperBrowser repository'

    WITH_OVERLAPS = 'Allow multiple overlapping points/segments within the same track'
    NO_OVERLAPS = 'Merge any overlapping points/segments within the same track'

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    OUTPUT_TRACKS_SUFFIX = 'bed'
    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PREPROCESSED
    GSUITE_OUTPUT_TRACK_TYPE = GSuiteConstants.SEGMENTS

    OUTPUT_GSUITE_DESCRIPTION = 'operation result'
    PROGRESS_INTERSECT_MSG = 'Intersect tracks'
    PROGRESS_PREPROCESS_MSG = 'Preprocess tracks'

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Track operations"

    @classmethod
    def getInputBoxNames(cls):
        """
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
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
        return [('Select GSuite file from history:', 'gSuite')] + cls.getInputBoxNamesForGenomeSelection() +\
               [('Select source of filtering track:', 'trackSource'),
                ('Select track from history:', 'trackHistory'),
                ('Select track:', 'track'),
                ('Overlap handling:', 'withOverlaps')]


    @classmethod
    def getInputBoxNamesForGenomeSelection(cls):
        return [(cls.OPTIONS_BOX_MSG % cls.WHAT_GENOME_IS_USED_FOR, 'specifyGenomeFromGsuites'),
                ('Genome mismatch note', 'genomeMismatchNote'),
                ('Genome build:', 'specifyGenomeFromList'),
                ('Genome', 'genome')]

    @classmethod
    def getOptionsBoxGSuite(cls):  # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return cls.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxTrackSource(cls, prevChoices):
        return [cls.FROM_HISTORY_TEXT, cls.FROM_HYPERBROWSER_TEXT]

    @classmethod
    def getOptionsBoxTrackHistory(cls, prevChoices):
        if prevChoices.trackSource == cls.FROM_HISTORY_TEXT:
            from gold.application.DataTypes import getSupportedFileSuffixesForPointsAndSegments
            return cls.getHistorySelectionElement(*getSupportedFileSuffixesForPointsAndSegments())

    @classmethod
    def getOptionsBoxTrack(cls, prevChoices):
        if prevChoices.trackSource == cls.FROM_HYPERBROWSER_TEXT:
            return cls.TRACK_SELECT_ELEMENT

    @classmethod
    def getOptionsBoxWithOverlaps(cls, prevChoices):
        if prevChoices.trackHistory or prevChoices.track:
            return [cls.NO_OVERLAPS, cls.WITH_OVERLAPS]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     """
    #     Specifies the order in which the input boxes should be displayed,
    #     as a list. The input boxes are specified by index (starting with 1)
    #     or by key. If None, the order of the input boxes is in the order
    #     specified by getInputBoxNames().
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     """
    #     Creates a visual separation of groups of consecutive option boxes
    #     from the rest (fieldset). Each such group has an associated label
    #     (string), which is shown to the user. To define groups of option
    #     boxes, return a list of BoxGroup namedtuples with the label, the key
    #     (or index) of the first and last options boxes (inclusive).
    #
    #     Example:
    #        from quick.webtool.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey',
    #                         last='secondKey')]
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None


    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     """
    #     If not None, defines the string content of an clickable info box
    #     beside the corresponding input box. HTML is allowed.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     """
    #     Defines a set of demo inputs to the option boxes in the
    #     order defined by getOptionBoxNames and getOptionsBoxOrder.
    #     If not None, a Demo button appears in the interface. Clicking the
    #     button fills the option boxed with the defined demo values.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return ['testChoice1', '..']
    #
    @classmethod
    def getExtraHistElements(cls, choices):
        desc = cls.OUTPUT_GSUITE_DESCRIPTION
        # return [HistElement(getGSuiteHistoryOutputName(
        #     'nointersect', description=desc, datasetInfo=choices.gSuite),
        #     GSuiteConstants.GSUITE_SUFFIX),
        return [HistElement(getGSuiteHistoryOutputName(
                'primary', description=desc, datasetInfo=choices.gSuite),
                GSuiteConstants.GSUITE_SUFFIX),
            # HistElement(getGSuiteHistoryOutputName(
            #     'nopreprocessed', description=desc, datasetInfo=choices.gSuite),
            #     GSuiteConstants.GSUITE_SUFFIX),
            # HistElement(getGSuiteHistoryOutputName(
            #     'preprocessed', description=desc, datasetInfo=choices.gSuite),
            #     GSuiteConstants.GSUITE_SUFFIX),
            HistElement(getGSuiteHistoryOutputName(
                'storage', description=desc, datasetInfo=choices.gSuite),
                GSuiteConstants.GSUITE_STORAGE_SUFFIX, hidden=True)]

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
        import gold.gsuite.GSuiteComposer as GSuiteComposer
        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GSuiteTrack, HbGSuiteTrack
        from gold.origdata.TrackGenomeElementSource import TrackViewListGenomeElementSource
        from gold.origdata.FileFormatComposer import getComposerClsFromFileSuffix
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from quick.application.GalaxyInterface import GalaxyInterface
        from quick.application.UserBinSource import UserBinSource
        from quick.extra.TrackExtractor import TrackExtractor

        genomeName = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)

        if choices.withOverlaps == cls.NO_OVERLAPS:
            if choices.trackSource == cls.FROM_HISTORY_TEXT:
                filterTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genomeName,
                                                                                        choices.trackHistory)
            else:
                filterTrackName = choices.track.split(':')
        else:
            if choices.trackSource == cls.FROM_HISTORY_TEXT:
                regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices.trackHistory)
                binSpec = ExternalTrackManager.extractFnFromGalaxyTN(choices.trackHistory)
            else:
                regSpec = 'track'
                binSpec = choices.track

            #userBinSource = UserBinSource(regSpec, binSpec, genomeName)

        desc = cls.OUTPUT_GSUITE_DESCRIPTION
        # emptyFn = cls.extraGalaxyFn \
        #     [getGSuiteHistoryOutputName('nointersect', description=desc,
        #                                 datasetInfo=choices.gSuite)]
        primaryFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName('primary', description=desc, datasetInfo=choices.gSuite)]
        # errorFn = cls.extraGalaxyFn \
        #     [getGSuiteHistoryOutputName('nopreprocessed', description=desc,
        #                                 datasetInfo=choices.gSuite)]
        # preprocessedFn = cls.extraGalaxyFn \
        #     [getGSuiteHistoryOutputName('preprocessed', description=desc,
        #                                 datasetInfo=choices.gSuite)]
        hiddenStorageFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName('storage', description=desc, datasetInfo=choices.gSuite)]

        # progressViewer = ProgressViewer([(cls.PROGRESS_INTERSECT_MSG, numTracks),
        #                                  (cls.PROGRESS_PREPROCESS_MSG, numTracks)], galaxyFn)
        emptyGSuite = GSuite()
        primaryGSuite = GSuite()


        for gsuiteTrack in gSuite.allTracks():
            newSuffix = cls.OUTPUT_TRACKS_SUFFIX
            extraFileName = os.path.sep.join(gsuiteTrack.trackName)
            extraFileName = changeSuffixIfPresent(extraFileName, newSuffix=newSuffix)
            title = getTitleWithSuffixReplaced(gsuiteTrack.title, newSuffix)
            genomeDict = GenomeInfo.getStdChrLengthDict(genomeName)

            genome = Genome(genomeName, genomeDict)
            track = Track(gsuiteTrack.trackName)


            track.addFormatReq(TrackFormatReq(allowOverlaps=False, borderHandling='crop'))
            trackContents = createTrackContentFromTrack(track, genome)


            primaryTrackUri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn, extraFileName=extraFileName,
                suffix=newSuffix if not extraFileName.endswith(newSuffix) else '')

            primaryTrack = GSuiteTrack(primaryTrackUri, title=title, genome=choices.genome,
                                       attributes=gsuiteTrack.attributes)

            filterTrack = Track(filterTrackName)
            filterTrack.addFormatReq(TrackFormatReq(allowOverlaps=False, borderHandling='crop'))
            filterTrackContents = createTrackContentFromTrack(filterTrack, genome)

            res = Union(trackContents, filterTrackContents, useStrands=False)
            newTrackContents = res.calculate()

            newTrackContents.createTrack(extraFileName, primaryTrack.path)
            primaryGSuite.addTrack(primaryTrack)

        GSuiteComposer.composeToFile(primaryGSuite, primaryFn)



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
    # @classmethod
    # def isPublic(cls):
    #     """
    #     Specifies whether the tool is accessible to all users. If False, the
    #     tool is only accessible to a restricted set of users as well as admin
    #     users, as defined in the galaxy.ini file.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
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
    #     return True

    # @classmethod
    # def getOutputFormat(cls, choices):
    #     """
    #     The format of the history element with the output of the tool. Note
    #     that if 'html' is returned, any print statements in the execute()
    #     method is printed to the output dataset. For text-based output
    #     (e.g. bed) the output dataset only contains text written to the
    #     galaxyFn file, while all print statements are redirected to the info
    #     field of the history item box.
    #
    #     Note that for 'html' output, standard HTML header and footer code is
    #     added to the output dataset. If one wants to write the complete HTML
    #     page, use the restricted output format 'customhtml' instead.
    #
    #     Optional method. Default return value if method is not defined:
    #     'html'
    #     """
    #     return 'customhtml'
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
