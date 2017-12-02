from collections import OrderedDict
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.assemblygap.Legend import Legend
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

class CreateHistogramTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Create descriptive results"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select file:', 'selectedFile'),
                ('Result counted for:', 'resRC'),
                ('Result counted as:', 'resStat'),
                ('Select break number (default: 20):', 'breaksNumber'),
                ('Include 0 values to count results:', 'resValue')]

    #how many times the region is presented in track (plot plus table)
    # average excluding zero and including zero


    @classmethod
    def getOptionsBoxSelectedFile(cls):
        return GeneralGuiTool.getHistorySelectionElement('tabular')

    @classmethod
    def getOptionsBoxResRC(cls, prevChoices):
        return ['rows', 'columns']

    @classmethod
    def getOptionsBoxResStat(cls, prevChoices):
        return ['sum', 'average']

    @classmethod
    def getOptionsBoxBreaksNumber(cls, prevChoices):
        return '20'

    @classmethod
    def getOptionsBoxResValue(cls, prevChoices):
        if prevChoices.resStat == 'average':
            return ['yes', 'no']



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selectedFile = choices.selectedFile
        breaksNumber = choices.breaksNumber
        resRC = choices.resRC
        resStat = choices.resStat

        resValue = 'yes'
        if resStat == 'average':
            resValue = choices.resValue

        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(selectedFile.split(':')),
                         'r')

        i = 0
        allDataNotProcessed = []
        data = OrderedDict()
        with inputFile as f:
            for x in f:
                line = x.strip('\n').split('\t')
                allDataNotProcessed.append(line)

        if resRC == 'columns':
            allDataNotProcessed = zip(*allDataNotProcessed)


        for line in allDataNotProcessed:
            if i == 0:
                header = line
            else:
                j=0
                for l in line:
                    if j==0:
                        hLine = l
                        data[l] = 0
                    else:
                        if resStat == 'sum':
                            data[hLine] += float(l)
                        elif resStat == 'average' and resValue == 'yes':
                            s = len(line)-1
                            if s>0:
                                data[hLine] += float(l)/(s)
                            else:
                                data[hLine] += 0
                        elif resStat == 'average' and resValue == 'no':
                            s = sum([1 if float(s) > 0 else 0 for s in line[1:]])
                            if s > 0:
                                data[hLine] += float(l) / (s)
                            else:
                                data[hLine] += 0
                    j+=1
            i+=1

        keySum = data.keys()
        itSum = data.values()

        vg = visualizationGraphs()
        plot = vg.drawColumnChart(
            itSum,
            categories=keySum,
            showInLegend=False,
            height=600,
            xAxisRotation=90
        )

        import operator
        sortedData = sorted(data.items(), key=operator.itemgetter(1), reverse=True)


        text = '<br> The regions with the highest (' + str(choices.resStat) + ') coverage are: <br>'
        if len(sortedData) >= 3:
            for sd in range(0, 3):
                text += str(sortedData[sd][0]) + ' with value equal ' + str(sortedData[sd][1])
                if sd != 2:
                    text += ', '
                else:
                    text += '.'
        else:
            for sd in range(0, len(sortedData)):
                text += str(sortedData[sd][0]) + ' with value equal ' + str(sortedData[sd][1])
                if sd != len(sortedData)-1:
                    text += ', '
                else:
                    text += '.'


        from proto.RSetup import robjects, r
        rCode = 'ourHist <- function(vec) {hist(vec, breaks=' + str(breaksNumber) + ', plot=FALSE)}'
        dd=robjects.FloatVector(itSum)
        simpleHist = r(rCode)(dd)

        breaks = list(simpleHist.rx2('breaks'))
        counts = list(simpleHist.rx2('counts'))


        res = vg.drawColumnChart(counts,
                                xAxisRotation=90,
                                categories=breaks,
                                showInLegend=False,
                                histogram=True,
                                height=400
                                )

        core = HtmlCore()
        core.begin()
        prettyResults = {}
        prettyResults[resStat] = itSum
        shortQuestion = 'results'

        core.line('Cover of the tracks per region (' + choices.resStat + ')')
        core.line(plot)
        core.line('Histogram (based on ' + choices.resStat + ')')
        core.line(res)
        core.line('Results for: ' + 'Cover of the tracks per region (' + choices.resStat + ')')
        addTableWithTabularAndGsuiteImportButtons(
            core,
            choices,
            galaxyFn,
            shortQuestion,
            tableDict=prettyResults,
            columnNames=['Measure'] + keySum
        )
        core.line(text)

        core.paragraph('Summary results')
        core.divBegin()
        core.tableHeader(['Measure', 'Values'], tableId='tab1')
        core.tableLine(['Sum', sum(itSum)])

        s = len(itSum)
        if s>0:
            avg = sum(itSum)/(s)
        else:
            avg = 0
        core.tableLine(['Average', avg])
        core.tableFooter()
        core.divEnd()




        core.divEnd()
        core.end()

        print core


    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     return False
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

        stepsToRunTool = ['Select file from history',
                          'Result counted for'
                          'Result counted as',
                          'Select break number (default: 20)',
                          'Include 0 values to count results'
                          ]

        toolResult = 'The results are presented as plots (cover of the tracks in the region and histogram (based on average)) and also overview of results are visible in the tables.'

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
        return 'customhtml'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()

    @staticmethod
    def isPublic():
        return True
