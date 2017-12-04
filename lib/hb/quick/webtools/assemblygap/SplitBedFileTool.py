from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.assemblygap.Legend import Legend


class SplitBedFileTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Split genomic regions into start, middle and end portions by a pred-defined size"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select file to be splitted', 'selFile'),
                ('Select part of genomic regions', 'splittedPart'),
                ('Define size of genomic regions (%)', 'splittedValue')]

    @classmethod
    def getOptionsBoxSelFile(cls):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @classmethod
    def getOptionsBoxSplittedPart(cls, prevChoices):
        return ['start', 'middle', 'end']

    @classmethod
    def getOptionsBoxSplittedValue(cls, prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selFile = choices.selFile
        splittedPart = choices.splittedPart
        splittedValue = choices.splittedValue
        if splittedPart == 'middle':
            splittedValue = 50 - float(splittedValue)

        percentage = float(splittedValue)/100

        data = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(selFile.split(':')),'r') as f:
            for line in f:
                l = line.strip('\n').split('\t')
                lineMod = l
                try:
                    if splittedPart == 'start':
                        val = int(percentage*(int(l[2]) - int(l[1])) + int(l[1]))
                        if val == int(l[1]):
                            val = val + 1
                        lineMod = [l[0], l[1], val]
                    if splittedPart == 'end':
                        val = int(int(l[2])-percentage*(int(l[2]) - int(l[1])))
                        l[2] = int(l[2])
                        if val == l[2] and val != 0:
                            val = l[2] - 1
                        if val == l[2] and val == 0:
                            val = 1
                            l[2] = 2
                        lineMod = [l[0], val, l[2]]
                    if splittedPart == 'middle':
                        val1 = int(percentage * (int(l[2]) - int(l[1])) + int(l[1]))
                        val2 = int(int(l[2]) - percentage * (int(l[2]) - int(l[1])))

                        if val1 == val2:
                            val2 = val2 + 1

                        lineMod = [l[0], val1, val2]
                except:
                    pass
                data.append(lineMod)

        outputFile = open(galaxyFn, 'w')
        for d in data:
            outputFile.write('\t'.join(str(e) for e in d) + '\n')
        outputFile.close()

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

    @classmethod
    def getToolDescription(cls):
        l = Legend()

        toolDescription = 'This tool create descriptive results for tabular file.'

        stepsToRunTool = ['Select file to be splitted',
                          'Select part of genomic regions (start [% counted from start], middle [% counted from middle in direction to start and end], end [% counted from end])'
                          'Define size of genomic regions (%)'
                          ]

        toolResult = 'The output of this tool is a .bed file.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult)
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
        return 'bed'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
