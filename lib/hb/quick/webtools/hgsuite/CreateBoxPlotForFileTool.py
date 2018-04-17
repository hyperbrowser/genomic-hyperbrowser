from collections import OrderedDict
import numpy
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons


class CreateBoxPlotForFileTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Create box plot for file"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select tabular file from history', 'selFile'),
                ('Do you want to have box plot separately for category', 'response'),
                ('Select category', 'responseValue'),
                ('Select column', 'selCol'),
                ('Include 0 values to count results', 'resValue')
                ]

    @staticmethod
    def getOptionsBoxSelFile():
        return GeneralGuiTool.getHistorySelectionElement('txt', 'tabular')

    @classmethod
    def getOptionsBoxResponse(cls, prevChoices):
        return ['yes', 'no']

    @classmethod
    def getOptionsBoxResponseValue(cls, prevChoices):
        if prevChoices.response == 'yes':
            if prevChoices.selFile:
                return cls.returnColFile(prevChoices.selFile, asListResponse=True)

    @classmethod
    def getOptionsBoxSelCol(cls, prevChoices):
        if prevChoices.selFile:
            if prevChoices.response == 'yes':
                return cls.returnColFile(prevChoices.selFile, asListResponse=True)
            else:
                return cls.returnColFile(prevChoices.selFile)

    @classmethod
    def getOptionsBoxResValue(cls, prevChoices):
        return ['yes', 'no']



    @classmethod
    def returnColFile(cls, selFile2, asListResponse=False):
        with open(ExternalTrackManager.extractFnFromGalaxyTN(selFile2.split(':')),
                  'r') as f:
            header = f.readline()
            header = header.strip('\n').split('\t')

            if asListResponse == False:
                hDict = OrderedDict()
                for h in header:
                    hDict[h] = False
            if asListResponse == True:
                hDict = []
                for h in header:
                    hDict.append(h)

            return hDict

    @classmethod
    def openFileWithCategories(cls, fileName, colName, colNameAttributes):
        allData = OrderedDict()
        categories = []
        fN = fileName.split(':')
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fN), 'r') as f:
            i = 0
            cna = 0

            for line in f:
                l = line.strip('\n').split('\t')
                if i == 0:
                    # inxColName = l.index(k.encode('utf-8'))
                    # allData[inxColName] = {}
                    #categories.append(k.encode('utf-8'))
                    cna = l.index(colNameAttributes)
                    k = l.index(colName)

                else:
                    if l != ['']:

                        try:
                            attr = l[cna]
                            if not attr in allData.keys():
                                allData[attr]=[]
                                categories.append(attr.encode('utf-8'))
                            if l[k] == 'nan':
                                allData[attr].append(0)
                            else:
                                allData[attr].append(float(l[k]))

                        except:
                            pass
                i += 1
        return allData, categories

    @classmethod
    def openFile(cls, fileName, colName):
        allData = OrderedDict()
        categories = []
        fN = fileName.split(':')
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fN), 'r') as f:
            i = 0
            for line in f:
                l = line.strip('\n').split('\t')
                if i == 0:
                    for k, it in colName.iteritems():
                        if it != False:
                            inxColName = l.index(k.encode('utf-8'))
                            allData[inxColName] = []
                            categories.append(k.encode('utf-8'))
                else:
                    if l != ['']:
                        for k in allData.keys():
                            try:
                                if l[k] == 'nan':
                                    allData[k].append(0)
                                else:
                                    allData[k].append(float(l[k]))
                            except:
                                pass
                i += 1
        return allData, categories

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selFile = choices.selFile
        selCol = choices.selCol
        resValue = choices.resValue
        response = choices.response
        if response == "yes":
            responseValue = choices.responseValue
            dataAll, categories = cls.openFileWithCategories(selFile, selCol, responseValue)
        else:
            dataAll, categories = cls.openFile(selFile, selCol)

        dataForBoxPlot = []
        prettyResults = {}
        i = 0

        for data in dataAll.itervalues():

            if resValue == 'no':
                data = [d for d in data if d > 0]
            countedData = [min(data), numpy.percentile(data, 25), numpy.percentile(data, 50),
                           numpy.percentile(data, 75), max(data)]
            dataForBoxPlot.append(countedData)
            s = 0
            if len(data) > 0:
                s = float(sum(data)) / float(len(data))
            prettyResults[categories[i]] = countedData + [s, float(sum(data)), float(len(data))]
            i += 1

        vg = visualizationGraphs()
        categoriesSorted, dataForBoxPlotSorted = (list(t) for t in zip(*sorted(zip(categories, dataForBoxPlot))))

        plot = vg.drawBoxPlotChart(dataForBoxPlotSorted,
                                   categories=categoriesSorted,
                                   seriesName='values',
                                   xAxisRotation=90)

        core = HtmlCore()
        core.begin()
        shortQuestion = 'results'

        addTableWithTabularAndGsuiteImportButtons(
            core,
            choices,
            galaxyFn,
            shortQuestion,
            tableDict=prettyResults,
            columnNames=['Column'] + ['Minimum', 'Lower quantile', 'Median', 'Upper quantile',
                                      'Maximum', 'Average', 'Sum', 'Elements number']
        )

        core.line(plot)
        core.end()
        print core

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'

    @staticmethod
    def isPublic():
        return True
