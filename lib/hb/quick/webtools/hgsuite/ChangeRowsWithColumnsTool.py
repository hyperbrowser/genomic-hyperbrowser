from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.Legend import Legend


class ChangeRowsWithColumnsTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Change rows with columns (transpose)"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select file', 'selFile')]

    @classmethod
    def getOptionsBoxSelFile(cls):
        return GeneralGuiTool.getHistorySelectionElement('tabular')

    @classmethod
    def readFile(cls, selFile2):

        allDataList = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(selFile2.split(':')),
                  'r') as f:
            for r in f:
                line = r.strip('\n').split('\t')
                if line != ['']:
                    allDataList.append(line)
        return allDataList

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selFile = choices.selFile
        orgFile = cls.readFile(selFile)
        modFile = zip(*orgFile)

        f = open(galaxyFn, 'w')
        for m in modFile:
            f.write('\t'.join(m) + '\n')
        f.close()

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.selFile:
            return 'Please select tabular file'

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
    @classmethod
    def isPublic(cls):
        return True
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
    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'The tool allow to transpose tabular file.'

        stepsToRunTool = ['Select file'
                          ]


        example = {'Example ': ['', ["""
    attribute0	attribute1	attribute2	attribute3
    track6.bed-CG	track6.bed	CG	1
    track6.bed-CA	track6.bed	CA	0
    track3.bed-CG	track3.bed	CG	0
    track3.bed-CA	track3.bed	CA	1
    track1.bed-CG	track1.bed	CG	0
    track1.bed-CA	track1.bed	CA	2
    track2.bed-CG	track2.bed	CG	0
    track2.bed-CA	track2.bed	CA	5
    track4.bed-CG	track4.bed	CG	0
    track4.bed-CA	track4.bed	CA	1
    track5.bed-CG	track5.bed	CG	1
    track5.bed-CA	track5.bed	CA	0

                            """],
                                [
                                    ['Select file', 'tabular'],
                                ],
                                [
                                    """
    attribute0	track6.bed-CG	track6.bed-CA	track3.bed-CG	track3.bed-CA	track1.bed-CG	track1.bed-CA	track2.bed-CG	track2.bed-CA	track4.bed-CG	track4.bed-CA	track5.bed-CG	track5.bed-CA
    attribute1	track6.bed	track6.bed	track3.bed	track3.bed	track1.bed	track1.bed	track2.bed	track2.bed	track4.bed	track4.bed	track5.bed	track5.bed
    attribute2	CG	CA	CG	CA	CG	CA	CG	CA	CG	CA	CG	CA
    attribute3	1	0	0	1	0	2	0	5	0	1	1	0
                                    """
                                ]
                                ]
                   }

        toolResult = 'The results are presented as transposed tabular file.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example
                                          )
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
        return 'tabular'
