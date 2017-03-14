from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.HGsuiteClass import HGsuite
import quick.gsuite.GuiBasedTsFactory as factory


class CreateHGsuiteFromCsvFileTool(GeneralGuiTool):


    @classmethod
    def getToolName(cls):

        return "Create hGsuite from file"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select file with data', 'selectedFile'),
                ('Select gSuite:', 'gSuite'),
                ('Possible columns', 'possibleColumns'),
                ('Select columns numbers which you want to combain (e.g. 1,2, 4-6)', 'selectedColumns'),
                ]

    @classmethod
    def getOptionsBoxSelectedFile(cls):
        return GeneralGuiTool.getHistorySelectionElement('csv')

    @classmethod
    def getOptionsBoxGSuite(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxPossibleColumns(cls, prevChoices):
        if prevChoices.selectedFile:
            hGSuite = HGsuite()
            header = hGSuite.parseCvsFileHeader(prevChoices.selectedFile)

            tableElements = [['Column number', 'Column name']]
            i=1
            for h in header:
                tableElements.append([i, h])
                i+=1
            return tableElements

    @classmethod
    def getOptionsBoxSelectedColumns(cls, prevChoices):
        if prevChoices.selectedFile:
            return ''



    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.selectedFile:
            return 'Select csv file'


        # check if the number of lines in csv is more than in gsuite
        if choices.selectedFile and choices.gSuite:
            hGSuite = HGsuite()
            if hGSuite.parseGSuiteAndGetLineNumbers(choices.gSuite) != hGSuite.parseCvsAndGetLineNumbers(choices.selectedFile):

                info = 'You have different number of tracks in gsuite than attributes in csv filr. '
                info += 'In GSuite you have: ' + str(hGSuite.parseGSuiteAndGetLineNumbers(choices.gSuite)) + ' lines. '
                info += 'while in file you have: ' + str(hGSuite.parseCvsAndGetLineNumbers(choices.selectedFile)) + ' lines. '
                return info



        return

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        selectedFile = choices.selectedFile
        selectedColumns = choices.selectedColumns
        gSuite = choices.gSuite

        hGSuite = HGsuite()

        # get selected columns as a list with numbers: starting from 0
        selCol = hGSuite.parseColumnResponse(selectedColumns)

        #get the column with new atributes
        dataFromFile, header = hGSuite.parseCvsFileBasedOnColumsNumber(selectedFile, selCol)


        import quick.gsuite.GuiBasedTsFactory as factory
        from gold.track.TrackStructure import CategoricalTS, TrackStructureV2
        from gold.gsuite.GSuite import GSuite
        from quick.gsuite.GSuiteUtils import getAllTracksWithAttributes
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

        gSuiteTN = getGSuiteFromGalaxyTN(gSuite)


        refTS = factory.getFlatTracksTS(gSuiteTN.genome, gSuite)

        print refTS








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
