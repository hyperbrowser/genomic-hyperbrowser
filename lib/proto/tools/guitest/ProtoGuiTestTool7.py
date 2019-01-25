from os import makedirs, mkdir
from random import randint

from proto.FileBrowser import generateHtmlFileBrowserForGalaxyFilesDir
from proto.HtmlCore import HtmlCore
from proto.StaticFile import GalaxyRunSpecificFile
from proto.tools.GeneralGuiTool import GeneralGuiTool


class ProtoGuiTestTool7(GeneralGuiTool):
    MAX_DIRECTORY_LEVEL = 3
    MAX_FILES_PER_DIR = 10
    MIN_BASENAME_CHARS = 3
    MAX_BASENAME_CHARS = 10
    MIN_SUFFIX_CHARS = 2
    MAX_SUFFIX_CHARS = 3
    MIN_FILESIZE = 0
    MAX_FILESIZE = 1024
    ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_'
    FILE_BROWSER_FILENAME = 'files.html'

    AS_MAIN_CHOICE = 'As main dataset'
    AS_MAIN_LINK_CHOICE = 'As link in main dataset'
    AS_EXTRA_CHOICE = 'As extra dataset'
    AS_EXTRA_LINK_CHOICE = 'As link in extra dataset'
    EXTRA_OUTPUT_TITLE = 'File browser'

    @classmethod
    def getToolName(cls):
        return "HTML output with file browser: Test tool #7 for Galaxy ProTo GUI"

    @classmethod
    def getInputBoxNames(cls):
        return [('How to output the file browser', 'outputType')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None
    #
    @classmethod
    def getOptionsBoxOutputType(cls):
        return [cls.AS_MAIN_CHOICE,
                cls.AS_MAIN_LINK_CHOICE,
                cls.AS_EXTRA_CHOICE,
                cls.AS_EXTRA_LINK_CHOICE]
    #
    # @classmethod
    # def getOptionsBoxSecondKey(cls, prevChoices):
    #     return ''
    #
    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']

    @classmethod
    def getExtraHistElements(cls, choices):
        if choices.outputType in [cls.AS_EXTRA_CHOICE, cls.AS_EXTRA_LINK_CHOICE]:
            from proto.tools.GeneralGuiTool import HistElement
            return [HistElement(cls.EXTRA_OUTPUT_TITLE, 'customhtml')]
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        path = []

        cls._generateRandomDirStructure(galaxyFn, path)

        if choices.outputType == cls.AS_MAIN_CHOICE:
            generateHtmlFileBrowserForGalaxyFilesDir(
                crawlDataset=galaxyFn,
                outputDataset=galaxyFn,
                returnSeparateRootFile=False
            )
        elif choices.outputType == cls.AS_MAIN_LINK_CHOICE:
            rootFile = generateHtmlFileBrowserForGalaxyFilesDir(
                crawlDataset=galaxyFn,
                outputDataset=galaxyFn,
                returnSeparateRootFile=True
            )
            cls._writeDataset(galaxyFn, rootFile)
        elif choices.outputType == cls.AS_EXTRA_CHOICE:
            extraDataset = cls.extraGalaxyFn[cls.EXTRA_OUTPUT_TITLE]
            generateHtmlFileBrowserForGalaxyFilesDir(
                crawlDataset=galaxyFn,
                outputDataset=extraDataset,
                returnSeparateRootFile=False
            )
        else:
            assert choices.outputType == cls.AS_EXTRA_LINK_CHOICE
            extraDataset = cls.extraGalaxyFn[cls.EXTRA_OUTPUT_TITLE]
            rootFile = generateHtmlFileBrowserForGalaxyFilesDir(
                crawlDataset=galaxyFn,
                outputDataset=extraDataset,
                returnSeparateRootFile=True
            )
            cls._writeDataset(extraDataset, rootFile)


    @classmethod
    def _generateRandomDirStructure(cls, galaxyFn, path):
        for level in range(cls.MAX_DIRECTORY_LEVEL):
            if level > 0:
                path += [cls._createDirAndReturnDirName(galaxyFn, path)]
            for fileNum in range(randint(0, cls.MAX_FILES_PER_DIR)):
                with cls._createFile(galaxyFn, path) as curFile:
                    curFile.write(cls._generateRandomString(cls.MIN_FILESIZE, cls.MAX_FILESIZE))

    @classmethod
    def _createFile(cls, galaxyFn, path):
        fileName = '{}.{}'.format(
            cls._generateRandomString(cls.MIN_BASENAME_CHARS, cls.MAX_BASENAME_CHARS),
            cls._generateRandomString(cls.MIN_SUFFIX_CHARS, cls.MAX_SUFFIX_CHARS))
        return GalaxyRunSpecificFile(path + [fileName], galaxyFn).getFile('w')

    @classmethod
    def _createDirAndReturnDirName(cls, galaxyFn, path):
        dirName = cls._generateRandomString(cls.MIN_BASENAME_CHARS, cls.MAX_BASENAME_CHARS)
        dir = GalaxyRunSpecificFile(path + [dirName], galaxyFn)
        mkdir(dir.getDiskPath(ensurePath=True))
        return dirName

    @classmethod
    def _generateRandomString(cls, minChars, maxChars):
        return ''.join([cls.ALLOWED_CHARS[randint(0, len(cls.ALLOWED_CHARS)-1)]
                        for _ in range(randint(minChars, maxChars))])

    @classmethod
    def _writeDataset(cls, galaxyFn, rootFile):
        core = HtmlCore()
        core.begin()
        core.paragraph(rootFile.getLink('Result file browser'))
        core.end()
        with open(galaxyFn, 'w') as outputFile:
            outputFile.write(str(core))

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

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
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     return ''
    #
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
        return 'customhtml'

    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
