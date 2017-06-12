from proto.tools.hyperbrowser.GeneralGuiTool import GeneralGuiTool
from collections import OrderedDict
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.util.CommonFunctions import ensurePathExists
from quick.application.ExternalTrackManager import ExternalTrackManager

class MergeContentForWelcomePageTool(GeneralGuiTool):
    MAX_NUM_OF_FILES_TO_ORDER = 20

    @classmethod
    def getToolName(cls):
        return "Concatenate content for welcome page"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select content', 'content'), \
                ('Specify order of files?', 'order')] +\
                [('Select file number %s' % (i+1), 'select%s' % i) for i \
                 in range(cls.MAX_NUM_OF_FILES_TO_ORDER)]


    @classmethod
    def getOptionsBoxContent(cls):
        return '__multihistory__', 'txt'

    @classmethod
    def getOptionsBoxOrder(cls, prevChoices):  # Alternatively: getOptionsBox2()
        numSeleted = sum(1 for tn in cls.getAllSelectedFiles(prevChoices))
        if numSeleted >= 2:
            return ['No', 'Yes']

    @classmethod
    def getAllSelectedFiles(cls, choices):
        return [x for x in choices.content.values() if x is not None]

    @classmethod
    def getOptionsBoxForSelectedFile(cls, prevChoices, index):
        if prevChoices.order == 'Yes':
            selectionList = []
            allSelected = cls.getAllSelectedFiles(prevChoices)

            for selected in allSelected:
                selectedHistElName = ExternalTrackManager.extractNameFromHistoryTN(
                    selected)
                if not any(selectedHistElName in getattr(prevChoices, 'select%s' % i) for i
                           in xrange(index)):
                    selectionList.append(selectedHistElName)

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_FILES_TO_ORDER):
            setattr(cls, 'getOptionsBoxSelect%s' % i,
                    partial(cls.getOptionsBoxForSelectedFile, index=i))

    @classmethod
    def getSelectedFilesInOrder(cls, choices):
        from quick.application.ExternalTrackManager import ExternalTrackManager

        allSelectedFiles = cls.getAllSelectedFiles(choices)

        if choices.order == 'No':
            return allSelectedFiles
        else:  # Yes
            nameToSelectedFile = dict(
                [(ExternalTrackManager.extractNameFromHistoryTN(galaxyTN), galaxyTN) \
                 for galaxyTN in allSelectedFiles])
            selectedFilesNamesInOrder = [getattr(choices, 'select%s' % i) \
                                          for i in range(len(allSelectedFiles))]
            return [nameToSelectedFile[name] for name in selectedFilesNamesInOrder]


    @classmethod
    def getFileContent(cls, fileName):
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
            data = ''.join(f.readlines())
        f.close()

        return data

    @classmethod
    def composeToFile(cls, filesList, outFileName):
        with open(outFileName, 'w') as out:
            for fl in filesList:
                data = cls.getFileContent(fl)
                out.writelines(data)
        out.close()
        print  'File is in history'

    @classmethod
    def compose(cls, filesList):
        data = ''
        for fl in filesList:
            data += cls.getFileContent(fl)
        return data


    # @classmethod
    # def generateEmptyFile(cls, fileName, suffix, galaxyFn):
    #     resFile = GalaxyRunSpecificFile([fileName + '.' + suffix], galaxyFn)
    #     ensurePathExists(resFile.getDiskPath())

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        filesList = cls.getSelectedFilesInOrder(choices)
        #histEl = cls.makeHistElement(galaxyExt='txt', title='Content')
        #cls.composeToFile(filesList, histEl)
        data = cls.compose(filesList)

        print>> open(galaxyFn, 'w'), data




    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    @classmethod
    def isPublic(cls):
        return True
    #
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
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'txt'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()

MergeContentForWelcomePageTool.setupSelectMethods()