import gold.gsuite.GSuiteConstants as GSuiteConstants
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class CreateGSuiteFileFromHistoryElementsTool(GeneralGuiTool):
    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = ', '.join([GSuiteConstants.UNKNOWN, GSuiteConstants.PRIMARY])
    GSUITE_OUTPUT_TRACK_TYPE = 'any, dependent on the file format of the selected elements'

    @classmethod
    def getToolName(cls):
        return "Create a GSuite from datasets in your history"

    @classmethod
    def getInputBoxNames(cls):
        return [('', 'basicQuestionId'), \
                ('Select a specific genome build:', 'selectGenome'), \
                ('Genome build:', 'genome'), \
                ('Select history elements', 'history')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxBasicQuestionId(cls):
        return '__hidden__', None

    @classmethod
    def getOptionsBoxSelectGenome(cls, prevChoices):
        return ['No', 'Yes']

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        if prevChoices.selectGenome == 'Yes':
            return '__genome__'

    @classmethod
    def getOptionsBoxHistory(cls, prevChoices):
        from gold.application.DataTypes import getSupportedFileSuffixesForGSuite
        return tuple(['__multihistory__'] + getSupportedFileSuffixesForGSuite())

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
        import gold.gsuite.GSuiteComposer as GSuiteComposer
        from quick.application.ExternalTrackManager import ExternalTrackManager

        genome = choices.genome if choices.selectGenome == 'Yes' else None
        selectedHistories = [key for key,val in choices.history.iteritems() if val is not None]

        gSuite = GSuite()

        for histGalaxyId in selectedHistories:
            galaxyTrackName = choices.history[histGalaxyId].split(':')

            histGalaxyFn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTrackName)
            histName = ExternalTrackManager.extractNameFromHistoryTN(galaxyTrackName)
            histSuffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(galaxyTrackName)

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=histGalaxyFn, suffix=histSuffix)
            gSuite.addTrack(GSuiteTrack(uri, title=histName, genome=genome))

        GSuiteComposer.composeToFile(gSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices.selectGenome == 'Yes':
            errorStr = cls._checkGenome(choices.genome)
            if errorStr:
                return errorStr

        if not any(val is not None for val in choices.history.values()):
            return 'Please select at least one history element'

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None

    @classmethod
    def isPublic(cls):
        return True

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

    @classmethod
    def getToolDescription(cls):
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('This tool can be used to compile a GSuite file referring to a selection '
                        'of files from the current Galaxy history. Selection of a genome build is optional.')
        core.divider()
        core.smallHeader('Note')
        core.paragraph('Even though this tool can be used to build GSuite compilations of any history elements, '
                       'the resulting GSuite file will be more usable if the elements are somewhat homogeneous '
                       'in file format and/or track type.')

        cls._addGSuiteFileDescription(core,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE)

        return str(core)

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

    @classmethod
    def getOutputFormat(cls, choices):
        return 'gsuite'

    @classmethod
    def getOutputName(cls, choices):
        from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
        from proto.CommonFunctions import extractNameFromDatasetInfo

        selected = [extractNameFromDatasetInfo(val)
                    for val in choices.history.values() if val is not None]
        if len(selected) > 0:
            description = selected[0] + \
                          (' + %s more' % (len(selected)-1) if len(selected) > 1 else '')
        else:
            description = None

        return getGSuiteHistoryOutputName('primary', description)
