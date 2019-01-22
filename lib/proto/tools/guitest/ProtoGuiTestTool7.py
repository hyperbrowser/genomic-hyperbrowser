from os import makedirs, mkdir
from random import randint

from proto.FileBrowser import generateHtmlFileBrowserForGalaxyFilesDir
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

    @classmethod
    def getToolName(cls):
        return "HTML output with file browser: Test tool #7 for Galaxy ProTo GUI"

    @classmethod
    def getInputBoxNames(cls):
        return []

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None
    #
    # @classmethod
    # def getOptionsBoxFirstKey(cls):
    #     return ['testChoice1', 'testChoice2', '...']
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
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        path = []

        for level in range(cls.MAX_DIRECTORY_LEVEL):
            if level > 0:
                path += [cls._createDirAndReturnDirName(galaxyFn, path)]
            for fileNum in range(randint(0, cls.MAX_FILES_PER_DIR)):
                with cls._createFile(galaxyFn, path) as curFile:
                    curFile.write(cls._generateRandomString(cls.MIN_FILESIZE, cls.MAX_FILESIZE))

        rootFile = generateHtmlFileBrowserForGalaxyFilesDir(galaxyFn, writeRootPageToGalaxyFn=False)
        print rootFile.getLink('File browser')

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
        return 'html'

    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
