import os
from collections import OrderedDict
from functools import partial
from itertools import chain
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuiteFunctions import changeSuffixIfPresent
from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ConvertMAFFileToBEDFileTool(GeneralGuiTool):

    NUM_EXAMPLE_LINES = 12
    NUM_PARAM_BOXES = 10

    ALL_PUBLIC_OPERATIONS = OrderedDict([('Convert maf to 4-column bed', 'ConvertMafTo4ColBed')])
    ALL_OPERATIONS = ALL_PUBLIC_OPERATIONS

    NO_OPERATION_TEXT = '-- Select --'
    NO_PARAM_TEXT = '-- Select --'

    METADATA_FROM_FILE = ''

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PRIMARY, GSuiteConstants.UNKNOWN]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]

    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = 'as input, but may be changed if a new file suffix is selected'
    GSUITE_OUTPUT_TRACK_TYPE = 'as input, but may be changed according to the selected operation'

    OUTPUT_DESCRIPTION = ', tracks manipulated'

    @classmethod
    def getToolName(cls):
        return "Convert MAF GSuite to BED GSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite file from history: ', 'history'),
                ('Example track (from GSuite): ', 'exampleTrack'),
                ('First %s lines of text file for example track: ' \
                 % cls.NUM_EXAMPLE_LINES, 'firstLinesIn')] + \
                [x for x in chain(*((('Select metatada %s:' % (i) + '', 'selectedMetadata%s' % i), \
                 ('Limit to single value %s:' % (i), 'selectedMetadataLimitation%s' % i)) \
                for i in xrange(cls.NUM_PARAM_BOXES)))] + \
        [('First %s lines of example track text file after manipulation: ' \
                 % cls.NUM_EXAMPLE_LINES, 'firstLinesOut')]
                # ('Change file suffix (e.g. "bed") of output tracks?', 'changeSuffix'),
                # ('New file suffix for all output tracks', 'suffix')]

    @classmethod
    def setupParameterOptionBoxes(cls):
        from functools import partial
        for i in xrange(cls.NUM_PARAM_BOXES):
            setattr(cls, 'getOptionsBoxParam%s' % i, partial(cls.getParamOptionsBox, i))
            setattr(cls, 'getOptionsBoxParamValue%s' % i,
                    partial(cls.getParamValueOptionsBox, i))

    @staticmethod
    def getOptionsBoxHistory():  # Alternatively: getOptionsBox1()
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxExampleTrack(prevChoices):  # Alternatively: getOptionsBox2()
        if prevChoices.history:
            try:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
                if gSuite.fileFormat in [GSuiteConstants.PRIMARY, GSuiteConstants.UNKNOWN]:
                    return [x for x in gSuite.allTrackTitles()]
            except:
                pass

    @classmethod
    def _getExampleContents(cls, fn):
        with open(fn) as trackFile:
            contents = ''
            for i in xrange(cls.NUM_EXAMPLE_LINES):
                contents += trackFile.readline()
        return contents

    @classmethod
    def _getExampleLines(cls, prevChoices):
        gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
        gSuiteTrack = gSuite.getTrackFromTitle(prevChoices.exampleTrack)
        return cls._getExampleContents(gSuiteTrack.path)

    @classmethod
    def getOptionsBoxFirstLinesIn(cls, prevChoices):
        if prevChoices.exampleTrack:
            try:
                return cls._getExampleLines(prevChoices), cls.NUM_EXAMPLE_LINES, True
            except:
                pass

    @classmethod
    def _getAllParamsWithDefaultValues(cls, prevChoices):
        from quick.extra.StandardizeTrackFiles import getFormattedParamList
        operation = cls.ALL_OPERATIONS.keys()[0]
        formattedParamList = getFormattedParamList(cls.ALL_OPERATIONS[operation])
        paramDict = OrderedDict()
        for param in formattedParamList:
            if '=' in param:
                key, default = param.split('=')
                if default.startswith('"') and default.endswith('"'):
                    default = default[1:-1]
                paramDict[key] = default
            else:
                paramDict[param] = ''

        return paramDict

    @classmethod
    def _getAllParamsWithMetadataValues(cls, prevChoices, paramDict):
        for i in range(0, cls.NUM_PARAM_BOXES):

            if cls.METADATA_FROM_FILE == '':
                cls.METADATA_FROM_FILE = cls.getMetadataFromFile(prevChoices)

            paramValue = getattr(prevChoices, 'selectedMetadata%s' % i)
            paramValueLimitation = getattr(prevChoices, 'selectedMetadataLimitation%s' % i)
            if paramValue is not None and paramValue is not '' and paramValue != cls.NO_PARAM_TEXT:
                paramValue = paramValue.encode('utf-8')
                paramDict[paramValue] = [cls.METADATA_FROM_FILE.index(paramValue) - 1, paramValueLimitation.encode('utf-8')]
        return paramDict



    @classmethod
    def _getOptionsBoxForSelectedMetadata(cls, prevChoices, index):
        if prevChoices.history:
            if not any(cls.NO_PARAM_TEXT in getattr(prevChoices, 'selectedMetadata%s' % i) for i in
                       xrange(index)):

                if cls.METADATA_FROM_FILE == '':
                    return cls.getMetadataFromFile(prevChoices)
                else:
                    return cls.METADATA_FROM_FILE

    @classmethod
    def getMetadataFromFile(cls, prevChoices):
        gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
        gSuiteTrack = gSuite.getTrackFromTitle(prevChoices.exampleTrack)
        with open(gSuiteTrack.path) as trackFile:
            for line in trackFile.readlines():
                if line.startswith('#'):
                    continue
                if line.startswith('Hugo_Symbol'):
                    cls.METADATA_FROM_FILE = [cls.NO_PARAM_TEXT] + line.strip('\n').split('\t')
                    break
        return cls.METADATA_FROM_FILE

    @classmethod
    def setupSelectedMetadataMethods(cls):
        for i in xrange(cls.NUM_PARAM_BOXES):
            setattr(cls, 'getOptionsBoxSelectedMetadata%s' % i,
                    partial(cls._getOptionsBoxForSelectedMetadata, index=i))



    @classmethod
    def _getOptionsBoxForSelectedMetadataLimitation(cls, prevChoices, index):
        if prevChoices.history:
            if not any(cls.NO_PARAM_TEXT in getattr(prevChoices, 'selectedMetadata%s' % i) for i in
                       xrange(index)):

                return ['yes', 'no']

    @classmethod
    def setupSelectedMetadataLimitationMethods(cls):
        for i in xrange(cls.NUM_PARAM_BOXES):
            setattr(cls, 'getOptionsBoxSelectedMetadataLimitation%s' % i,
                    partial(cls._getOptionsBoxForSelectedMetadataLimitation, index=i))
    #
    # @staticmethod
    # def _getParamKeyFromListedParam(prevChoices, index):
    #     listedParam = getattr(prevChoices, 'param%s' % index)
    #     if listedParam:
    #         defaultStart = listedParam.find(' (')
    #         if defaultStart == -1:
    #             return listedParam.encode('utf-8')
    #         else:
    #             return listedParam[:defaultStart]
    #
    # @classmethod
    # def getParamOptionsBox(cls, index, prevChoices):
    #     operation = cls.ALL_OPERATIONS.keys()[0]
    #     prevParamChoices = set(
    #         [cls._getParamKeyFromListedParam(prevChoices, i) for i in xrange(index)])
    #     paramDict = cls._getAllParamsWithDefaultValues(prevChoices)
    #
    #     if index < len(paramDict):
    #         unselectedParamList = ['%s (default: %s)' % (key, val) for key, val
    #                                in paramDict.iteritems() if key not in prevParamChoices]
    #         if len(unselectedParamList) > 0:
    #             return [cls.NO_PARAM_TEXT] + unselectedParamList
    #
    # @classmethod
    # def getParamValueOptionsBox(cls, index, prevChoices):
    #     paramChoice = cls._getParamKeyFromListedParam(prevChoices, index)
    #     if paramChoice and paramChoice != cls.NO_PARAM_TEXT:
    #         paramDict = cls._getAllParamsWithDefaultValues(prevChoices)
    #         return paramDict[paramChoice]
    #






    @classmethod
    def _getAllParamsWithChoices(cls, prevChoices):
        paramDict = cls._getAllParamsWithDefaultValues(prevChoices)
        paramDict = cls._getAllParamsWithMetadataValues(prevChoices, paramDict)

        return paramDict

    @classmethod
    def _runOperation(cls, prevChoices, inFn, outFn):
        from quick.extra.StandardizeTrackFiles import runParserClassDirectly
        parserClassName = cls.ALL_OPERATIONS[cls.ALL_OPERATIONS.keys()[0]]
        paramDict = cls._getAllParamsWithChoices(prevChoices)
        runParserClassDirectly(parserClassName, inFn, outFn, **paramDict)

    @classmethod
    def _runOperationOnExampleDataAndReturnOutput(cls, prevChoices):
        from tempfile import NamedTemporaryFile

        inFile = NamedTemporaryFile()
        inFile.write(cls._getExampleLines(prevChoices))
        inFile.flush()

        outFile = NamedTemporaryFile()
        cls._runOperation(prevChoices, inFile.name, outFile.name)
        outFile.flush()

        return cls._getExampleContents(outFile.name)

    @classmethod
    def getOptionsBoxFirstLinesOut(cls, prevChoices):
        operation = cls.ALL_OPERATIONS.keys()[0]
        try:
            return cls._runOperationOnExampleDataAndReturnOutput(prevChoices), cls.NUM_EXAMPLE_LINES, True
        except:
            pass

    # @classmethod
    # def getOptionsBoxChangeSuffix(cls, prevChoices):
    #     return ['bed']

    @staticmethod
    def _getTrackSuffix(gSuiteTrack):
        return 'bed'
        # if gSuiteTrack.suffix:
        #     return 'bed'
        # else:
        #     return 'txt'

    # @classmethod
    # def _getSuffix(cls, choices, gSuiteTrack):
    #     if choices.changeSuffix == 'Yes':
    #         return choices.suffix
    #     else:
    #         return cls._getTrackSuffix(gSuiteTrack)
    #
    # @classmethod
    # def getOptionsBoxSuffix(cls, prevChoices):
    #     if prevChoices.changeSuffix == 'Yes':
    #         try:
    #             gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
    #             for track in gSuite.allTracks():
    #                 return cls._getTrackSuffix(track)
    #         except:
    #             pass

    @classmethod
    def getInfoForOptionsBoxOperation(cls, prevChoices):
        '''
        If not None, defines the string content of an clickable info box beside
        the corresponding input box. HTML is allowed.
        '''
        operation = cls.ALL_OPERATIONS.keys()[0]
        from quick.extra.StandardizeTrackFiles import getParserClassDocString
        from proto.hyperbrowser.HtmlCore import HtmlCore

        docString = getParserClassDocString(cls.ALL_OPERATIONS[cls.ALL_OPERATIONS.keys()[0]])

        core = HtmlCore()
        for line in docString.split(os.linesep):
            core.line(line)

        return str(core)

    # @staticmethod
    # def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def getExtraHistElements(cls, choices):
        from quick.webtools.GeneralGuiTool import HistElement
        from gold.gsuite.GSuiteConstants import GSUITE_SUFFIX, GSUITE_STORAGE_SUFFIX

        fileList = [HistElement(getGSuiteHistoryOutputName(
            'nomanipulate', datasetInfo=choices.history), GSUITE_SUFFIX)]
        fileList += [HistElement(getGSuiteHistoryOutputName(
            'primary', cls.OUTPUT_DESCRIPTION, choices.history), GSUITE_SUFFIX)]
        fileList += [HistElement(getGSuiteHistoryOutputName(
            'storage', cls.OUTPUT_DESCRIPTION, choices.history),
            GSUITE_STORAGE_SUFFIX, hidden=True)]

        return fileList


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
        from gold.gsuite.GSuiteComposer import composeToFile
        from gold.gsuite.GSuiteFunctions import getTitleWithSuffixReplaced
        from quick.gsuite.GSuiteHbIntegration import \
            writeGSuiteHiddenTrackStorageHtml
        from quick.extra.ProgressViewer import ProgressViewer
        from quick.util.CommonFunctions import ensurePathExists

        gSuite = getGSuiteFromGalaxyTN(choices.history)
        outGSuite = GSuite()
        errorGSuite = GSuite()

        progressViewer = ProgressViewer([('Manipulate tracks', gSuite.numTracks())], galaxyFn)

        hiddenStorageFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName(
            'storage', cls.OUTPUT_DESCRIPTION, choices.history)]

        for track in gSuite.allTracks():
            newSuffix = 'bed'

            fileName = os.path.basename(track.path)
            fileName = changeSuffixIfPresent(fileName, oldSuffix=track.suffix, newSuffix=newSuffix)
            title = getTitleWithSuffixReplaced(track.title, newSuffix)

            try:

                if fileName.endswith('.' + newSuffix):
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn,
                                                        extraFileName=fileName)
                else:
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=hiddenStorageFn,
                                                        extraFileName=fileName,
                                                        suffix=newSuffix)

                gSuiteTrack = GSuiteTrack(uri, title=title, genome=track.genome,
                                          attributes=track.attributes)

                trackFn = gSuiteTrack.path
                ensurePathExists(trackFn)
                cls._runOperation(choices, track.path, trackFn)

                outGSuite.addTrack(gSuiteTrack)

            except Exception as e:
                track.comment = 'An error occurred for the following track: ' + str(e) + str()
                errorGSuite.addTrack(track)

            progressViewer.update()

        primaryFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName(
            'primary', cls.OUTPUT_DESCRIPTION, choices.history)]

        composeToFile(outGSuite, primaryFn)

        errorFn = cls.extraGalaxyFn[getGSuiteHistoryOutputName(
            'nomanipulate', datasetInfo=choices.history)]
        composeToFile(errorGSuite, errorFn)

        writeGSuiteHiddenTrackStorageHtml(hiddenStorageFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.history)
        if errorStr:
            return errorStr

        gSuite = getGSuiteFromGalaxyTN(choices.history)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        errorStr = cls._checkGSuiteRequirements(
            gSuite,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS)
        if errorStr:
            return errorStr

        operation = cls.ALL_OPERATIONS.keys()[0]
        try:
            cls._runOperationOnExampleDataAndReturnOutput(choices)
        except Exception as e:
            return 'An error occured testing operation "%s": ' % operation + str(
                e)

        # if choices.changeSuffix == 'Yes' and choices.suffix.strip() == '':
        #     return 'Please select a file suffix'

    @classmethod
    def getOutputName(cls, choices):
        return getGSuiteHistoryOutputName('progress', cls.OUTPUT_DESCRIPTION, choices.history)

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

    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('This tool contains various operations for manipulating textual '
                       'track files referred to in a GSuite file.')
        core.divider()
        core.smallHeader('Instructions')
        core.orderedList(['Select a GSuite file referring to local textual track files',
                          'The first track referred to in the GSuite is automatically selected '
                          'as an example track, with the beginning of the file shown in a '
                          'text box. The example file is later used to show the results of the '
                          'selected operation. If you want to use another file as the example track '
                          'please select it in the selection box. ',
                          'Select the required operation from the list of operations '
                          '(click the info box if you need further description of each operation '
                          'and its parameters):' +
                          str(HtmlCore().unorderedList(
                              [key for key in cls.ALL_OPERATIONS.keys()])),
                          'Each parameter for the selected operation is shown in a selection box, '
                          'with the default value indicated. If another value than the default is '
                          'needed, please select the parameter and change its value. '
                          'the order in which the parameters is selected is unimportant.',
                          'The output of the selected operation with the selected parameter values '
                          'on the beginning of the selected example track is shown in a text box.',
                          'If the file format (e.g. "bed") of the track is changed as a result of '
                          'carrying out the operation, please indicate the new file suffix. '
                          'It is important for the tracks to have the correct file suffix for further '
                          'analysis.'])

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
                                      errorFile=True)

        return str(core)

    #
    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #     return 'u/hb-superuser/p/manipulate-textual-track-files-referred-to-in-gsuite---example'
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'

# ConvertMAFFileToBEDFileTool.setupParameterOptionBoxes()
ConvertMAFFileToBEDFileTool.setupSelectedMetadataMethods()
ConvertMAFFileToBEDFileTool.setupSelectedMetadataLimitationMethods()
