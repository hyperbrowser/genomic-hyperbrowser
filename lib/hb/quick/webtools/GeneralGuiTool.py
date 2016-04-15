import os
from collections import namedtuple
from urllib import quote

from config.Config import DATA_FILES_PATH
from gold.application.LogSetup import logMessage
from gold.util.CustomExceptions import Warning
from quick.application.SignatureDevianceLogging import takes,returns
from third_party.typecheck import list_of
from gold.gsuite.GSuiteParser import GSuiteContents
from gold.gsuite import GSuiteConstants

class HistElement(object):
    def __init__(self, name, format, label=None, hidden=False):
        self.name = name
        self.format = format
        self.label = label
        self.hidden = hidden

BoxGroup = namedtuple('BoxGroup', ['label','first','last'])

class GeneralGuiTool(object):

    ##CONSTANTS
    ##Don't change values of this variables, they are intended to be constant

    GENOME_SELECT_ELEMENT = '__genome__'
    TRACK_SELECT_ELEMENT = '__track__'
    HISTORY_SELECT_ELEMENT = '__history__'

    ##END CONSTANTS##

    #TODO: boris 20141001: move this function
    @staticmethod
    @takes(list_of(str))
    @returns(tuple)
    def getHistorySelectionElement(*args):
        '''
        Construct a history element tuple.
        If any arguments are supplied, the list of history element list will be filtered accordingly'
        e.g. GenericGuiTool.getHistorySelectionElement('beg', 'wig')
        '''
        if args:
            return tuple([GeneralGuiTool.HISTORY_SELECT_ELEMENT] + list(args))
        else:
            return tuple([GeneralGuiTool.HISTORY_SELECT_ELEMENT])


    ################

    def __init__(self, toolId=None):
        self.__class__.toolId = toolId

    # API methods
    @staticmethod
    def getInputBoxOrder():
        return None

    @staticmethod
    def getInputBoxGroups(choices=None):
        return None

    @staticmethod
    def getSubToolClasses():
        return None

    @classmethod
    def getToolSelectionName(cls):
        return cls.getToolName()

    @staticmethod
    def isPublic():
        return False

    @staticmethod
    def isRedirectTool(choices=None):
        return False

    @staticmethod
    def isHistoryTool():
        return True

    @classmethod
    def isBatchTool(cls):
        return cls.isHistoryTool()

    @staticmethod
    def isDynamic():
        return True

    @staticmethod
    def getResetBoxes():
        '''
        List of boxes which if their values are changed causes the succeding boxes to be reset to default values
        '''
        return []

    @staticmethod
    def getToolDescription():
        return ''

    @staticmethod
    def getToolIllustration():
        return None

    @staticmethod
    def getFullExampleURL():
        return None

    @classmethod
    def doTestsOnTool(cls, galaxyFn, title, label):
        from quick.application.GalaxyInterface import GalaxyInterface
        from collections import OrderedDict
        import sys

        if hasattr(cls, 'getTests'):
            galaxy_ext = None
            testRunList = cls.getTests()
            for indx, tRun in enumerate(testRunList):
                choices = tRun.split('(',1)[1].rsplit(')',1)[0].split('|')
                choices = [eval(v) for v in choices]
                if not galaxy_ext:
                    galaxy_ext = cls.getOutputFormat(choices)
                output_filename = cls.makeHistElement(galaxyExt=galaxy_ext, title=title+str(indx), label=label+str(indx))
                sys.stdout = open(output_filename, "w", 0)
                cls.execute(choices, output_filename)
            sys.stdout = open(galaxyFn, "a", 0)
        else:
            print open(galaxyFn, "a").write('No tests specified for %s' % cls.__name__)


    @classmethod
    def getTests(cls):
        import shelve
        SHELVE_FN = DATA_FILES_PATH + os.sep + 'tests' + os.sep + '%s.shelve'%cls.toolId
        if os.path.isfile(SHELVE_FN):

            testDict = shelve.open(SHELVE_FN)
            resDict = dict()
            for k, v in testDict.items():
                resDict[k] = cls.convertHttpParamsStr(v)
            return resDict
        return None

    @staticmethod
    def isDebugMode():
        return False

    @staticmethod
    def getOutputFormat(choices=None):
        return 'html'

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None

    # Convenience methods

    @classmethod
    def convertHttpParamsStr(cls, streng):
        strTab = []
        for v in streng.split('\n'):
            if v:
                strTab.append(v)

        return dict([tuple(v.split(':',1)) for v in strTab])

    @classmethod
    def getOptionBoxNames(cls):
        labels = cls.getInputBoxNames()
        #inputOrder = range(len(labels) if not cls.getInputBoxOrder() else cls.getInputBoxOrder()
        boxMal = 'box%i'
        if type(labels[0]).__name__ == 'str':
            return [boxMal%i for i in range(1, len(labels)+1)]
            #return [boxMal % i for i in inputOrder]
        else:
            return [i[0] for i in labels]
            #return [labels[i][0] for i in inputOrder]

    @classmethod
    def formatTests(cls, choicesFormType, testRunList):
        labels = cls.getOptionBoxNames()
        if len(labels) != len(choicesFormType):
            logMessage('labels and choicesFormType are different:(labels=%i, choicesFormType=%i)' % (len(labels), len(choicesFormType)))
        return (testRunList, zip(labels, choicesFormType))

    @classmethod
    def _getGalaxyFnFromHistoryChoice(self, historyChoice):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        return ExternalTrackManager.extractFnFromGalaxyTN(historyChoice)

    #@classmethod
    #def _getPathAndUrlForFile(cls, galaxyFn, relFn):
    #    '''
    #    Gets a disk path and a URL for storing a run-specific file.
    #    galaxyFn is connected to the resulting history item in Galaxy,
    #      and is used to determine a unique disk path for this specific run.
    #    relFn is a relative file name (i.e. only name, not full path) that one
    #      wants a full disk path for, as well as a URL referring to the file.
    #    '''
    #    fullFn = cls._getDiskPathForFiles(galaxyFn) + os.sep + relFn
    #    url = cls._getBaseUrlForFiles(fullFn)
    #    return fullFn, url
    #
    #@staticmethod
    #def _getDiskPathForFiles(galaxyFn):
    #    galaxyId = extractIdFromGalaxyFn(galaxyFn)
    #    return getUniqueWebPath(galaxyId)
    #
    #@staticmethod
    #def _getBaseUrlForFiles(diskPath):
    #    return getRelativeUrlFromWebPath(diskPath)

    @staticmethod
    def _getGenomeChoice(choices, genomeChoiceIndex):
        if genomeChoiceIndex is None:
            genome = None
        else:
            if type(genomeChoiceIndex) == int:
                genome = choices[genomeChoiceIndex]
            else:
                genome = getattr(choices, genomeChoiceIndex)

            if genome in [None, '']:
                return genome, 'Please select a genome build'

        return genome, None

    @staticmethod
    def _getTrackChoice(choices, trackChoiceIndex):
        if type(trackChoiceIndex) == int:
            trackChoice = choices[trackChoiceIndex]
        else:
            trackChoice = getattr(choices, trackChoiceIndex)

        if trackChoice is None:
            return trackChoice, 'Please select a track'

        trackName = trackChoice.split(':')
        return trackName, None

    @staticmethod
    def _checkGenome(genomeChoice):
        if genomeChoice in [None, '']:
            return 'Please select a genome build'

    @staticmethod
    def _checkTrack(choices, trackChoiceIndex=1, genomeChoiceIndex=0, filetype=None,
                    validateFirstLine=True):
        genome, errorStr = GeneralGuiTool._getGenomeChoice(choices, genomeChoiceIndex)
        if errorStr:
            return errorStr

        trackName, errorStr = GeneralGuiTool._getTrackChoice(choices, trackChoiceIndex)
        if errorStr:
            return errorStr

        from quick.application.ExternalTrackManager import ExternalTrackManager
        if ExternalTrackManager.isGalaxyTrack(trackName):
            errorStr = GeneralGuiTool._checkHistoryTrack(choices, trackChoiceIndex, genome,
                                                         filetype, validateFirstLine)
            if errorStr:
                return errorStr
        else:
            if not GeneralGuiTool._isValidTrack(choices, trackChoiceIndex, genomeChoiceIndex):
                return 'Please select a valid track'

    @staticmethod
    def _isValidTrack(choices, tnChoiceIndex=1, genomeChoiceIndex=0):
        from quick.application.GalaxyInterface import GalaxyInterface
        from quick.application.ProcTrackOptions import ProcTrackOptions

        genome, errorStr = GeneralGuiTool._getGenomeChoice(choices, genomeChoiceIndex)
        if errorStr or genome is None:
            return False

        trackName, errorStr = GeneralGuiTool._getTrackChoice(choices, tnChoiceIndex)
        if errorStr:
            return False

        return ProcTrackOptions.isValidTrack(genome, trackName, True) or \
            GalaxyInterface.isNmerTrackName(genome, trackName)

    @staticmethod
    def _checkHistoryTrack(choices, historyChoiceIndex, genome, filetype=None,
                           validateFirstLine=True):
        fileStr = filetype + ' file' if filetype else 'file'

        trackName, errorStr = GeneralGuiTool._getTrackChoice(choices, historyChoiceIndex)
        if errorStr:
            return 'Please select a ' + fileStr + ' from history.'

        if validateFirstLine:
            return GeneralGuiTool._validateFirstLine(trackName, genome, fileStr)

    @staticmethod
    def _validateFirstLine(galaxyTN, genome=None, fileStr='file'):
        try:
            from quick.application.ExternalTrackManager import ExternalTrackManager
            from gold.origdata.GenomeElementSource import GenomeElementSource

            suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(galaxyTN)
            fn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN)

            GenomeElementSource(fn, genome, suffix=suffix).parseFirstDataLine()

        except Exception, e:
            return fileStr.capitalize() + ' invalid: ' + str(e)

    @staticmethod
    def _validateGSuiteFile(galaxyTN):
        import gold.gsuite.GSuiteParser as GSuiteParser
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from cStringIO import StringIO

        galaxyFn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTN)
        outFile = StringIO()
        ok = GSuiteParser.validate(galaxyFn, outFile=outFile, printHelpText=False)
        if not ok:
            return outFile.getvalue()

    @staticmethod
    def _checkGSuiteFile(gSuiteChoice, validate=True):
        if not gSuiteChoice:
            return 'Please select a GSuite file'

        if validate:
            return GeneralGuiTool._validateGSuiteFile(gSuiteChoice)

    @staticmethod
    def _checkGenomeEquality(targetTrackGenome, refTrackGenome):
        from gold.gsuite.GSuiteConstants import UNKNOWN
        if targetTrackGenome in [None, UNKNOWN]:
            return 'The target track lacks a genome'
        elif refTrackGenome is [None, UNKNOWN]:
            return 'The reference track lacks a genome'

        if not targetTrackGenome == refTrackGenome:
            return 'Reference genome must be same for both target and reference tracks.'

    @staticmethod
    def _checkGSuiteTrackListSize(gSuite, minSize=1, maxSize=10000):
        errorString = ''
        if gSuite.numTracks() < minSize:
            errorString = 'Selected GSuite must have at least %s tracks' %minSize
            errorString += '. Current number of tracks = ' + str(gSuite.numTracks())
        if gSuite.numTracks() > maxSize:
            errorString = 'Selected GSuite must have at most %s tracks' %maxSize
            errorString += '. Current number of tracks = ' + str(gSuite.numTracks())
        return errorString

    @staticmethod
    def _getBasicTrackFormat(choices, tnChoiceIndex=1, genomeChoiceIndex=0):
        genome = GeneralGuiTool._getGenomeChoice(choices, genomeChoiceIndex)[0]
        tn = GeneralGuiTool._getTrackChoice(choices, tnChoiceIndex)[0]

        from quick.application.GalaxyInterface import GalaxyInterface
        from gold.description.TrackInfo import TrackInfo
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from gold.track.TrackFormat import TrackFormat

        if ExternalTrackManager.isGalaxyTrack(tn):
            geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(tn, genome)
            try:
                tf = GeneralGuiTool._convertToBasicTrackFormat(TrackFormat.createInstanceFromGeSource(geSource).getFormatName())
            except Warning:
                return genome, tn, ''
        else:
            if GalaxyInterface.isNmerTrackName(genome, tn):
                tfName = 'Points'
            else:
                tfName = TrackInfo(genome, tn).trackFormatName
            tf = GeneralGuiTool._convertToBasicTrackFormat(tfName)
        return genome, tn, tf

    @classmethod
    def _checkBasicTrackType(cls, choices, allowedTrackTypes, tnChoiceIndex=0, genomeChoiceIndex=1):
        basicTrackType = cls._getBasicTrackFormat(choices, tnChoiceIndex, genomeChoiceIndex)[2]
        if basicTrackType.lower() not in allowedTrackTypes:
            return 'Basic track type is "%s", which is not supported. ' % basicTrackType + \
                   'Supported basic track types are "%s".' % ', '.join(allowedTrackTypes)

    @staticmethod
    def _getValueTypeName(choices, tnChoiceIndex=1, genomeChoiceIndex=0):
        genome = GeneralGuiTool._getGenomeChoice(choices, genomeChoiceIndex)[0]
        tn = GeneralGuiTool._getTrackChoice(choices, tnChoiceIndex)[0]

        from quick.application.GalaxyInterface import GalaxyInterface
        from gold.description.TrackInfo import TrackInfo
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from gold.track.TrackFormat import TrackFormat

        if ExternalTrackManager.isGalaxyTrack(tn):
            geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(tn, genome)
            valTypeName = TrackFormat.createInstanceFromGeSource(geSource).getValTypeName()
        else:
            if GalaxyInterface.isNmerTrackName(genome, tn):
                valTypeName = ''
            else:
                valTypeName = TrackInfo(genome, tn).markType
        return valTypeName.lower()

    #@staticmethod
    #def _getBasicTrackFormatFromHistory(choices, tnChoiceIndex=1):
    #    from quick.application.ExternalTrackManager import ExternalTrackManager
    #    from gold.track.TrackFormat import TrackFormat
    #    genome = choices[0]
    #    tn = choices[tnChoiceIndex].split(':')
    #    geSource = ExternalTrackManager.getGESourceFromGalaxyOrVirtualTN(tn, genome)
    #    tf = GeneralGuiTool._convertToBasicTrackFormat(TrackFormat.createInstanceFromGeSource(geSource).getFormatName())
    #
    #
    #    return genome, tn, tf


    @staticmethod
    def _convertToBasicTrackFormat(tfName):
        tfName = tfName.lower()

        if tfName.startswith('linked '):
            tfName = tfName[7:]

        tfName = tfName.replace('unmarked ','')
        tfName = tfName.replace('marked','valued')

        return tfName

    @classmethod
    def getNamedTuple(cls):
        names = cls.getInputBoxNames()
        anyTuples = False
        vals = []
        for i in range(len(names)):
            name = names[i]
            if isinstance(name, tuple):
                anyTuples = True
                vals.append(name[1])
            else:
                vals.append('box' + str(1 + i))

        if anyTuples:
            return namedtuple('ChoiceTuple', vals)
        else:
            return None

    @staticmethod
    def _exampleText(text):
        from gold.result.HtmlCore import HtmlCore
        core = HtmlCore()
        core.styleInfoBegin(styleClass='debug', linesep=False)
        core.append(text.replace('\t','\\t'))
        core.styleInfoEnd()
        return str(core)

    @classmethod
    def makeHistElement(cls,  galaxyExt='html', title='new Dataset', label='Newly created dataset',):
        import simplejson, glob
        json_params =  cls.runParams
        #print json_params
        datasetId = json_params['output_data'][0]['dataset_id'] # dataset_id fra output_data
        hdaId = json_params['output_data'][0]['hda_id'] # # hda_id fra output_data
        metadata_parameter_file = open( json_params['job_config']['TOOL_PROVIDED_JOB_METADATA_FILE'], 'a' )
        newFilePath = json_params['param_dict']['__new_file_path__']
        numFiles = len(glob.glob(newFilePath+'/primary_%i_*'%hdaId))
        #title += str(numFiles+1)
        #print 'datasetId', datasetId
        #print 'newFilePath', newFilePath
        #print 'numFiles', numFiles
        outputFilename = os.path.join(newFilePath , 'primary_%i_%s_visible_%s' % ( hdaId, title, galaxyExt ) )
        #print 'outputFilename', outputFilename
        metadata_parameter_file.write( "%s\n" % simplejson.dumps( dict( type = 'dataset', #new_primary_
                                         dataset_id = datasetId,#base_
                                         ext = galaxyExt,
                                         #filename = outputFilename,
                                         #name = label,
                                         metadata = {'dbkey':['hg18']} )) )
        metadata_parameter_file.close()
        return outputFilename


    @classmethod
    def createGenericGuiToolURL(cls, tool_id, sub_class_name=None, tool_choices=None):
        from GeneralGuiToolsFactory import GeneralGuiToolsFactory
        tool = GeneralGuiToolsFactory.getWebTool(tool_id)
        base_url = '?mako=generictool&tool_id=' + tool_id + '&'
        if sub_class_name and isinstance(tool, MultiGeneralGuiTool):
            for subClass in tool.getSubToolClasses():
                if sub_class_name == subClass.__name__:
                    tool = subClass()
                    base_url += 'sub_class_id=' + quote(tool.getToolSelectionName()) + '&'

        #keys = tool.getNamedTuple()._fields
        if not tool_choices:
            args = []
        elif isinstance(tool_choices, dict):
            args = [ '%s=%s' % (k,quote(v)) for k,v in tool_choices.items()]
        elif isinstance(tool_choices, list):
            args = [ '%s=%s' % ('box%d'%(i+1,), quote(tool_choices[i])) for i in range(0, len(tool_choices)) ]

        return base_url + '&'.join(args)

    @classmethod
    def _checkGSuiteRequirements(cls, gSuite, allowedFileFormats = [], allowedLocations = [],
                                 allowedTrackTypes = [], disallowedGenomes = []):
        errorString = ''
        from config.Config import URL_PREFIX
        if allowedLocations and gSuite.location not in allowedLocations:
            errorString += '\'%s\' is not a supported GSuite location for this tool. Supported locations are ' %gSuite.location
            errorString += str(allowedLocations) + '</br>'

            if gSuite.location in [GSuiteConstants.REMOTE] and allowedLocations == [GSuiteConstants.LOCAL]:
                errorString += '''To download the tracks in the GSuite use the
                <a href="%s/hyper?mako=generictool&tool_id=hb_g_suite_download_files">
                Convert GSuite tracks from remote to primary (Download tracks)</a> tool</br>''' % URL_PREFIX

        if errorString:
            return errorString

        if allowedFileFormats and gSuite.fileFormat not in allowedFileFormats:
            errorString += '\'%s\' is not a supported GSuite file format value for this tool. Supported file format values are ' %gSuite.fileFormat
            errorString += str(allowedFileFormats) + '</br>'

            if allowedFileFormats == [GSuiteConstants.PREPROCESSED]:
                errorString +=  '''This tool needs a pre-processed local GSuite, please see the note
                <a href="%s/static/welcome_note.html"> on different types of GSuites</a></br>
                ''' % URL_PREFIX

            if allowedFileFormats == [GSuiteConstants.PRIMARY]:
                from config.Config import URL_PREFIX
                errorString +=  '''This tool needs a primary local GSuite, please see the note
                <a href="%s/static/welcome_note.html"> on different types of GSuites</a></br>
                ''' % URL_PREFIX

            if gSuite.fileFormat in [GSuiteConstants.PRIMARY] and allowedFileFormats == [GSuiteConstants.PREPROCESSED]:
                errorString += '''To convert your GSuite to the required format use the
                <a href="%s/hyper?mako=generictool&tool_id=hb_preprocess_g_suite_tracks_tool">
                Preprocess a GSuite for analysis</a> tool</br>''' % URL_PREFIX

            if gSuite.fileFormat in [GSuiteConstants.PREPROCESSED] and allowedFileFormats == [GSuiteConstants.PRIMARY]:
                errorString += '''To convert your GSuite to the required format use the
                <a href="%s/hyper?mako=generictool&tool_id=hb_g_suite_convert_from_preprocessed_to_primary_tool">
                Convert GSuite tracks from preprocessed to primary</a> tool</br>''' % URL_PREFIX

        if errorString:
            return errorString


        basicTrackType = cls._convertToBasicTrackFormat(gSuite.trackType)
        if allowedTrackTypes and basicTrackType not in allowedTrackTypes:
            errorString += '\'%s\' is not a supported GSuite track type for this tool. Supported track types are ' %gSuite.trackType
            errorString += str(allowedTrackTypes) + ' and their variations.'

        if disallowedGenomes and gSuite.genome in disallowedGenomes:
            if gSuite.genome == GSuiteConstants.UNKNOWN:
                errorString += '<br>Unknown genomes are not supported by this tool. Please specify a genome for the GSuite.'
            elif gSuite.genome == GSuiteConstants.MULTIPLE:
                errorString += '<br>Multiple genomes are not supported by this tool. Please specify a single genome for the GSuite.'

        if errorString:
            return errorString

    @classmethod
    def _addGSuiteFileDescription(cls, core, allowedLocations=[], allowedFileFormats=[], allowedTrackTypes=[],
                                  disallowedGenomes=[], outputLocation='',  outputFileFormat='', outputTrackType='',
                                  errorFile=False, alwaysShowRequirements=False, alwaysShowOutputFile=False,
                                  minTrackCount=None, maxTrackCount=None):
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        if alwaysShowRequirements or any((allowedLocations, allowedFileFormats, allowedTrackTypes, disallowedGenomes)):
            core.divider()
            core.smallHeader('Requirements for GSuite input file')

            core.descriptionLine('Locations', ', '.join(allowedLocations) if allowedLocations else 'any', emphasize=True)
            core.descriptionLine('File formats', ', '.join(allowedFileFormats) if allowedFileFormats else 'any', emphasize=True)
            core.descriptionLine('Track types', ', '.join(allowedTrackTypes) if allowedTrackTypes else 'any', emphasize=True)

            genomeText = 'required' if UNKNOWN in disallowedGenomes else 'optional'
            genomeText += ', only single genome allowed' if MULTIPLE in disallowedGenomes else ', multiple genomes allowed'
            core.descriptionLine('Genome', genomeText, emphasize=True)

        if alwaysShowOutputFile or any((outputLocation, outputFileFormat, outputTrackType)):
            core.divider()
            core.smallHeader('Format of GSuite output file')

            core.descriptionLine('Location', outputLocation if outputLocation else 'as input file', emphasize=True)
            core.descriptionLine('File format', outputFileFormat if outputFileFormat else 'as input file', emphasize=True)
            core.descriptionLine('Track type', outputTrackType if outputTrackType else 'as input file', emphasize=True)

        if errorFile:
            core.divider()
            core.smallHeader('Format of GSuite error file')
            core.paragraph('The error GSuite file contains references to all track lines '
                           'that failed in the execution of the tool. This is a valid GSuite '
                           'file that can be used as input in manipulation tools, if one needs to '
                           'change the contents somehow, or used directly as a '
                           'input in the current tool to reexecute it only on the '
                           'failed tracks.')

            core.descriptionLine('Location', allowedLocations[0] if len(allowedLocations) ==  1 else 'as input file', emphasize=True)
            core.descriptionLine('File format', allowedFileFormats[0] if len(allowedFileFormats) == 1 else  'as input file', emphasize=True)
            core.descriptionLine('Track type', allowedTrackTypes[0] if len(allowedTrackTypes) == 1 else  'as input file', emphasize=True)

        if minTrackCount or maxTrackCount:
            core.divider()
            core.smallHeader('Limitations on number of tracks in input GSuites')

            core.descriptionLine('Minimal number of tracks', str(minTrackCount) if minTrackCount else 'no limit', emphasize=True)
            core.descriptionLine('Maximal number of tracks', str(maxTrackCount) if maxTrackCount else 'no limit', emphasize=True)


class MultiGeneralGuiTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "-----  Select tool -----"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select tool -----"

    @staticmethod
    def getSubToolSelectionTitle():
        return 'Select subtool:'

    @staticmethod
    def validateAndReturnErrors(choices):
        return ''

    @staticmethod
    def getInputBoxNames():
        return []
