import os
from functools import partial

import gold.gsuite.GSuiteComposer as GSuiteComposer
from gold.application.HBAPI import doAnalysis, doAnalysisYaml
from gold.application.LogSetup import setupDebugModeAndLogging
from gold.description.AnalysisDefHandler import AnalysisDefHandler, \
    YamlAnalysisDefHandlerWithChoices
from gold.description.TrackInfo import TrackInfo
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack, HbGSuiteTrack, GalaxyGSuiteTrack
from gold.origdata.GtrackComposer import StdGtrackComposer
from gold.origdata.PreProcessTracksJob import PreProcessTrackGESourceJob
from gold.origdata.TrackGenomeElementSource import TrackViewListGenomeElementSource
from gold.track.Track import Track
from proto.tools.GeneralGuiTool import HistElement
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.UserBinSource import GlobalBinSource
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.track_operations.utils.TrackHandling import getKwArgOperationDictStat, parseBoolean, \
    getYamlAnalysisSpecs
from quick.util.CommonFunctions import convertTNstrToTNListFormat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.application.ExternalTrackManager import ExternalTrackManager as etm


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

    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PREPROCESSED
    GSUITE_OUTPUT_TRACK_TYPE = GSuiteConstants.SEGMENTS

    OUTPUT_GSUITE_DESCRIPTION = 'operation result'
    PROGRESS_INTERSECT_MSG = 'Intersect tracks'
    PROGRESS_PREPROCESS_MSG = 'Preprocess tracks'

    OPERATIONS_TWO_TRACKS = ['IntersectionStat']
    SELECT_CHOICE = '--- Select ---'

    ANALYSIS_SPEC_STRS = ['Track operations - intersection: test of track operations '
                          '[resultAllowOverlap:Allow overlap in the result track=False:FalseLabel/True:TrueLabel]'
                          '[useStrands:Follow the strand direction=True:TrueLabel/False:FalseLabel]'
                          '[treatMissingAsNegative:Treat any missing strand as if they are negative=True:TrueLabel/False:FalseLabel]'
                          ' -> IntersectionStat',
                          'Track operations - complement: test of track operations2 '
                          '[useStrands:Follow the strand direction=True:TrueLabel/False:FalseLabel]'
                          '[treatMissingAsNegative:Treat any missing strand as if they are negative=False:FalseLabel/True:TrueLabel]'
                          ' -> ComplementStat',
                          'Track operations - merge: Merge any overlapping elements in a track '                          
                          '[useStrands:Follow the strand direction=True:TrueLabel/False:FalseLabel]'
                          '[treatMissingAsNegative:Treat any missing strand as if they are negative=False:FalseLabel/True:TrueLabel]'
                          ' -> MergeStat',
                          'Track operations - expand: Expand the elements in a track '
                          '[resultAllowOverlap:Allow overlap in the result track=False:FalseLabel/True:TrueLabel]'
                          '[useStrands:Follow the strand direction=True:TrueLabel/False:FalseLabel]'
                          '[treatMissingAsNegative:Treat any missing strand as if they are negative=False:FalseLabel/True:TrueLabel]'
                          '[useFraction:Interpret flak size as a fraction of the element size=False:FalseLabel/True:TrueLabel]'
                          '[upstream:Size of the upstream flank. In number of base pairs=0]'
                          '[downstream:Size of the downstream flank. In number of base pairs=0]'
                          '[both:Extract the segments in in both directions. In number of base pairs=0]'
                          ' -> ExpandStat'
                          ]


    ANALYSIS_SPECS_LIST = [AnalysisDefHandler(analysisSpecStr) for analysisSpecStr in ANALYSIS_SPEC_STRS]
    ANALYSIS_SPECS = {spec.getStatClass().__name__: spec for spec in ANALYSIS_SPECS_LIST}

    YAML_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'analysis.yaml')
    YAML_ANALYSIS_SPECS_LIST = getYamlAnalysisSpecs(YAML_FILE_PATH)
    YAML_ANALYSIS_SPECS = {spec.getStatClass().__name__: spec for spec in YAML_ANALYSIS_SPECS_LIST}

    OPERATIONS = {statClassName:spec.getStatClass() for statClassName,spec in ANALYSIS_SPECS.iteritems()}
    YAML_OPERATIONS = {statClassName:spec.getStatClass() for statClassName,spec in YAML_ANALYSIS_SPECS.iteritems()}

    KW_OPERATION_DICT = getKwArgOperationDictStat(ANALYSIS_SPECS)
    YAML_KW_OPERATION_DICT = getKwArgOperationDictStat(ANALYSIS_SPECS)

    NO = 'No'
    YES = 'Yes'

    YAML_DEF_OPERATIONS = ['IntersectionStat']

    @classmethod
    def getToolName(cls):
        return "Track operations"

    @classmethod
    def getInputBoxNames(cls):
        attrBoxes = []
        attrBoxes.append(('Select operation', 'operation'))
        attrBoxes.append(('Operation help', 'operationHelp'))
        attrBoxes.append(('Show optional keyword parameters', 'showOptionalKwArgs'))
        attrBoxes += cls.getInputBoxNamesForKwArgs()
        attrBoxes.append(('Select GSuite file from history:', 'gSuite'))
        attrBoxes += cls.getInputBoxNamesForGenomeSelection()
        attrBoxes.append(('Select source of filtering track:', 'trackSource'))
        attrBoxes.append(('Select track from history:', 'trackHistory'))
        attrBoxes.append(('Select track:', 'track'))
        attrBoxes.append(('Overlap handling:', 'withOverlaps'))

        return attrBoxes

    @classmethod
    def setupExtraBoxMethods(cls):
        for kwArg, opNames in cls.KW_OPERATION_DICT.items():
            defaultVals = []
            isRequired = []
            for opName in opNames:
                if opName in cls.YAML_DEF_OPERATIONS:
                    kwArgInfo = cls.YAML_ANALYSIS_SPECS[opName].getKwArgsWithInfo()[kwArg]

                    defaultVal = kwArgInfo.getDefaultValue()
                    defaultVals.append(str(defaultVal))

                    required = kwArgInfo.isRequired()
                    isRequired.append(required)
                    pass
                else:
                    analysisSpec = cls.ANALYSIS_SPECS[opName]

                    defaultVal = analysisSpec.getChoice(kwArg)
                    defaultVals.append(defaultVal)

                    required = True
                    isRequired.append(required)

            argType = cls.determineArgType(defaultVals[0])
            if argType == bool:
                setattr(cls, 'getOptionsBox' + kwArg[:1].upper() + kwArg[1:], partial(cls._getBooleanBox, ops=opNames, defaultVals=defaultVals, isRequired=isRequired))
            else:
                setattr(cls, 'getOptionsBox' + kwArg[:1].upper() + kwArg[1:], partial(cls._getTextBox, ops=opNames, defaultVals=defaultVals, isRequired=isRequired))

    @classmethod
    def determineArgType(cls, defaultVal):
        if defaultVal in ['True', 'False']:
            return bool

        return str

    @classmethod
    def _getBooleanBox(cls, prevChoices, ops, defaultVals, isRequired):
        if prevChoices.operation in ops:
            required = isRequired[ops.index(prevChoices.operation)]
            if not required and prevChoices.showOptionalKwArgs == cls.NO:
                return

            defaultValStr = defaultVals[ops.index(prevChoices.operation)]

            if defaultValStr == 'True':
                defaultVal = True
            else:
                defaultVal = False

            return [str(defaultVal), str(not defaultVal)]

    @classmethod
    def _getTextBox(cls, prevChoices, ops, defaultVals, isRequired):
        if prevChoices.operation in ops:
            required = isRequired[ops.index(prevChoices.operation)]

            if not required and prevChoices.showOptionalKwArgs == cls.NO:
                return

            defaultVal = defaultVals[ops.index(prevChoices.operation)]

            if defaultVal is not None:
                return str(defaultVal)
            else:
                return ''

    @classmethod
    def getOptionsBoxGSuite(cls, prevChoices):
        if prevChoices.operation in [None, cls.SELECT_CHOICE, '']:
            return

        return cls.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxShowOptionalKwArgs(cls, prevChoices):
        if prevChoices.operation in [None, cls.SELECT_CHOICE, '']:
            return

        return [cls.NO, cls.YES]

    @classmethod
    def getOptionsBoxTrackSource(cls, prevChoices):
        if prevChoices.operation in cls.OPERATIONS_TWO_TRACKS:
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

    @classmethod
    def getOptionsBoxOperation(cls):
        operations = cls._getOperationList()

        operations.insert(0, cls.SELECT_CHOICE)
        return operations

    @classmethod
    def getOptionsBoxOperationHelp(cls, prevChoices):
        if prevChoices.operation in [None, cls.SELECT_CHOICE, '']:
            return

        operationSpec = cls.ANALYSIS_SPECS[prevChoices.operation]
        operationLabel = operationSpec.getText()
        kwArgsLabels = operationSpec.getOptionsAsKeysAndTexts()

        kwArgsPrint = ''

        for key,label in kwArgsLabels:
            kwArgsPrint += key + ': ' + label + '\n'

        return (operationLabel + '\n' + kwArgsPrint, 5 , True)

    @classmethod
    def _getOperationList(cls):

        return cls.OPERATIONS.keys()

    @classmethod
    def getInputBoxNamesForKwArgs(cls):
        boxes = []
        for kwArg in cls.KW_OPERATION_DICT.keys():
            boxes.append((kwArg, kwArg))

        return boxes

    


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
    @classmethod
    def getInputBoxGroups(cls, choices=None):
        """
        Creates a visual separation of groups of consecutive option boxes
        from the rest (fieldset). Each such group has an associated label
        (string), which is shown to the user. To define groups of option
        boxes, return a list of BoxGroup namedtuples with the label, the key
        (or index) of the first and last options boxes (inclusive).

        Example:
           from quick.webtool.GeneralGuiTool import BoxGroup
           return [BoxGroup(label='A group of choices', first='firstKey',
                            last='secondKey')]

        Optional method. Default return value if method is not defined: None
        """
        return None


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


    def checkIsFloat(self, val):
        import re
        if re.match("^\d+?\.\d+?$", val) is None:
            return False

        return True

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

        genomeName = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)

        #if choices.withOverlaps == cls.NO_OVERLAPS:
        if choices.trackSource == cls.FROM_HISTORY_TEXT:
            filterTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genomeName,
                                                                                    choices.trackHistory)
        else:
            filterTrackName = choices.track.split(':')

        desc = cls.OUTPUT_GSUITE_DESCRIPTION

        primaryFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName('primary', description=desc, datasetInfo=choices.gSuite)]

        hiddenStorageFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName('storage', description=desc, datasetInfo=choices.gSuite)]
        # emptyFn = cls.extraGalaxyFn \
        #     [getGSuiteHistoryOutputName('nointersect', description=desc,
        #                                 datasetInfo=choices.gSuite)]
        # errorFn = cls.extraGalaxyFn \
        #     [getGSuiteHistoryOutputName('nopreprocessed', description=desc,
        #                                 datasetInfo=choices.gSuite)]
        # preprocessedFn = cls.extraGalaxyFn \
        #     [getGSuiteHistoryOutputName('preprocessed', description=desc,
        #                                 datasetInfo=choices.gSuite)]
        # progressViewer = ProgressViewer([(cls.PROGRESS_INTERSECT_MSG, numTracks),
        #                                  (cls.PROGRESS_PREPROCESS_MSG, numTracks)], galaxyFn)

        primaryGSuite = GSuite()
        chosenOperation = choices.operation

        if chosenOperation in cls.YAML_DEF_OPERATIONS:
            analysisDef = cls.YAML_ANALYSIS_SPECS[choices.operation]

            operationKwArgs = analysisDef.getKwArgsWithInfo()

            kwArgsWithChoices = cls.getKwArgsFromChoices(choices, operationKwArgs)

            analysisSpec = YamlAnalysisDefHandlerWithChoices(analysisDef)
            analysisSpec.setChoices(kwArgsWithChoices)

            doAnalysisMethod = doAnalysisYaml

        else:
            #operationCls = cls.OPERATIONS[choices.operation]
            analysisSpec = cls.ANALYSIS_SPECS[choices.operation]
            operationKwArgs = analysisSpec.getOptionsAsKeys()

            kwArgsWithChoices = cls.getKwArgsFromChoices(choices, operationKwArgs)

            for kwArg, val in kwArgsWithChoices.iteritems():
                if parseBoolean(val) is None:
                    # handling float values like this for now..
                    if val not in operationKwArgs[kwArg]:
                        analysisSpec.changeChoices(kwArg, [[str(val), str(val)]])
                analysisSpec.setChoice(kwArg, val)

            doAnalysisMethod = doAnalysis


        #print operationKwArgs

        # temporary
        if 'useStrands' in kwArgsWithChoices:
            analysisSpec.setChoice('useStrands', 'False')


        for gsuiteTrack in gSuite.allTracks():
            trackName = etm.createStdTrackName(etm.extractIdFromGalaxyFn(galaxyFn), name=gsuiteTrack.title)

            title = gsuiteTrack.title

            track = Track(gsuiteTrack.trackName)
            analysisBins = GlobalBinSource(genomeName)
            setupDebugModeAndLogging()
            #track.addFormatReq(TrackFormatReq(allowOverlaps=False, borderHandling='crop'))

            if choices.operation in cls.OPERATIONS_TWO_TRACKS:
                filterTrack = Track(filterTrackName)
                #filterTrack.addFormatReq(TrackFormatReq(allowOverlaps=False, borderHandling='crop')

                res = doAnalysisMethod(analysisSpec, analysisBins, [track, filterTrack])

            else:
                res = doAnalysisMethod(analysisSpec, analysisBins, [track])
                #print 'got res ' + str(res)

            trackViewList = [res[key]['Result'] for key in sorted(res.keys())]

            tvGeSource = TrackViewListGenomeElementSource(genomeName, trackViewList, trackName)

            job = PreProcessTrackGESourceJob(genomeName, trackName, tvGeSource)
            job.process()
            trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
            hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
            primaryGSuite.addTrack(GSuiteTrack(hbUri, title=title, trackType=trackType, genome=genomeName))

            # primaryTrackUri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn, extraFileName=extraFileName)
            # primaryTrack = GSuiteTrack(primaryTrackUri, title=title, genome=genomeName,
            #                            attributes=gsuiteTrack.attributes)
            # StdGtrackComposer(tvGeSource).composeToFile(primaryTrack.path)
            # primaryGSuite.addTrack(primaryTrack)


        GSuiteComposer.composeToFile(primaryGSuite, primaryFn)

    @classmethod
    def getKwArgsFromChoices(cls, choices, operationKwArgs):
        kwArgs = {}
        for kwArg in operationKwArgs:
            chosenVal = getattr(choices, kwArg)
            kwArgs[kwArg] = chosenVal

        return kwArgs

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


TrackOperationsTool.setupExtraBoxMethods()

