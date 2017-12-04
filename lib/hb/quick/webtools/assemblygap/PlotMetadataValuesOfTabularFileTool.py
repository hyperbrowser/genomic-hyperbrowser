from collections import OrderedDict
from gold.gsuite.GSuiteConstants import TITLE_COL
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.assemblygap.Legend import *
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
import math
from gold.gsuite import GSuiteConstants, GSuiteFunctions

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class PlotMetadataValuesOfTabularFileTool(GeneralGuiTool):

    ALLOW_UNKNOWN_GENOME = True

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot metadata values of a GSuite file"
        # Plot tabular values

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select tabular file', 'selFile'),
            ('Select way of showing series as', 'plotSeries'),
            ('Select type of chart', 'plotType'),
            ('Select value for x-Axis', 'columnX'),
            ('Select type of scale for x-Axis', 'axesScaleX'),
            ('Select value for y-Axis', 'columnY'),
            ('Select type of scale for y-Axis', 'axesScaleY'),
            ('Add trend', 'trend'),
            # ('Select results of plotting', 'plotRes'),
        ]

    @staticmethod
    def getOptionsBoxSelFile():
        return GeneralGuiTool.getHistorySelectionElement('txt', 'tabular')

    @classmethod
    def getOptionsBoxPlotSeries(cls, prevChoices):
        return ['Single', 'Multi']

    @classmethod
    def getOptionsBoxPlotType(cls, prevChoices):
        if prevChoices.plotSeries == 'Single':
            return ['Column', 'Heatmap', 'Line', 'Pie', 'Scatter']
            #return ['Column', 'Scatter']
        else:
            #return ['Column', 'Scatter']
            return ['Column', 'Line', 'Pie', 'Scatter']

    @classmethod
    def getOptionsBoxColumnX(cls, prevChoices):  # Alternatively: getOptionsBox2()
        if not prevChoices.selFile:
            return

        input = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.selFile.split(':')), 'r')
        attribute = input.readline().strip('\n').split('\t')

        return ['line number'] + attribute

    @staticmethod
    def getOptionsBoxAxesScaleX(prevChoices):
        return ['linear', 'log10', 'no uniform scale (sorted values as labels)']

    @classmethod
    def getOptionsBoxColumnY(cls, prevChoices):  # Alternatively: getOptionsBox2()
        if not prevChoices.selFile:
            return

        input = open(
                ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.selFile.split(':')), 'r')
        attribute = input.readline().strip('\n').split('\t')

        att = OrderedDict()
        for key in attribute:
            att[key] = False

        if prevChoices.plotSeries == 'Single':
            if prevChoices.plotType == 'Pie':
                return att.keys()

        return att

    @staticmethod
    def getOptionsBoxAxesScaleY(prevChoices):
        return ['linear', 'log10']

        #     @staticmethod
        #     def getOptionsBoxPlotRes(prevChoices):
        #
        #         if not prevChoices.gSuite:
        #             return
        #
        #         columnX = prevChoices.columnX
        #         columnY = prevChoices.columnY
        #
        #         if prevChoices.plotType == 'Scatter' or prevChoices.plotType == 'Line':
        #             if columnX in columnY.keys():
        #                 return ['separate', 'combine']
        #

    @classmethod
    def getOptionsBoxTrend(cls, prevChoices):
        if prevChoices.plotType == 'Scatter' and prevChoices.plotSeries == 'Single':
            return ['yes', 'no']


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        # data from choices
        selFile = choices.selFile
        plotType = choices.plotType
        columnX = choices.columnX
        columnY = choices.columnY
        plotSeries = choices.plotSeries

        axesScaleX = choices.axesScaleX
        axesScaleY = choices.axesScaleY

        # 'linear', 'log10', 'no uniform scale (sorted values as labels)'
        if axesScaleX == 'linear':
            # plotRes = choices.plotRes
            plotRes = 'combine'
        elif axesScaleX == 'log10':
            plotRes = 'separate'
        elif axesScaleX == 'no uniform scale (sorted values as labels)':
            plotRes = 'separate'

        # unpack gsuite
        input = open(ExternalTrackManager.extractFnFromGalaxyTN(selFile.split(':')),
                     'r')
        dictVal=OrderedDict()
        iD=0
        for line in input:
            l = line.strip('\n').split('\t')
            if iD == 0:
                header = l
                for ll in l:
                    dictVal[ll] = []
            else:
                iDL = 0
                for ll in l:
                    dictVal[header[iDL]].append(ll)
                    iDL+=1
            iD+=1



        # full list of attributes (meta-data)
        attributeList = input.readline().strip('\n').split('\t')

        # dictNum - include numerical values which can be presented in y-axes
        # need to do that because pie can have only one chocie and then it is not returing dict


        dictNum = OrderedDict()
        for key in attributeList:
            dictNum[key] = False

        # check if it is dict or not
        if not isinstance(columnY, dict):
            tempDict = {}
            tempDict[columnY] = 'True'
            columnY = tempDict

        seriesName = []

        # check if user selected categoriesNumber and it is possible to use combinate
        categoriesNumber = False

        sortedCat = None
        categories = None
        if columnX == 'line number':
            categories = None
        else:
            if columnX in dictNum.keys():
                categoriesBefore = [float(v) for v in dictVal[columnX]]

                if axesScaleX == 'log10':
                    for cbN in range(0, len(categoriesBefore)):
                        if categoriesBefore[cbN] != 0:
                            categoriesBefore[cbN] = math.log(categoriesBefore[cbN], 10)

                sortedCat = sorted(range(len(categoriesBefore)),
                                   key=lambda k: categoriesBefore[k])
                categories = []
                for n in sortedCat:
                    categories.append(categoriesBefore[n])

                categoriesNumber = True

            else:
                categories = dictVal[columnX]#gSuite.getAttributeValueList(columnX)



        # data are sorted according to numerical values
        data = []
        for key, it in columnY.iteritems():
            if it == 'True':
                dataPart = []
                seriesName.append(key)
                dataPart = []
                for x in dictVal[key]:#gSuite.getAttributeValueList(key):
                    try:
                        if axesScaleY == 'log10':
                            if x != 0:
                                dataPart.append(math.log(float(x), 10))
                            else:
                                dataPart.append(0)
                        else:
                            dataPart.append(float(x))
                    except:
                        # need to support None in heatmap
                        if plotType == 'Heatmap':
                            dataPart.append(0)
                        else:
                            dataPart.append(x)
                if sortedCat != None:
                    dataPartTemp = []
                    for n in sortedCat:
                        dataPartTemp.append(dataPart[n])
                    dataPart = dataPartTemp
                data.append(dataPart)

        label = ''
        if len(seriesName) != 0:
            label = '<b>{series.name}</b>: {point.x} {point.y}'
        else:
            label = '{point.x} {point.y}'

        vg = visualizationGraphs()

        #         'Column', 'Scatter', 'Heatmap'

        if axesScaleX == 'log10':
            xAxisTitle = str(columnX) + ' (' + str(axesScaleX) + ')'
        else:
            xAxisTitle = str(columnX)

        if axesScaleY == 'log10':
            yAxisTitle = str('values') + ' (' + str(axesScaleY) + ')'
        else:
            yAxisTitle = str('values')

        minFromList = min(min(d) for d in data)
        if minFromList > 0:
            minFromList = 0

        # combain series with data
        if plotRes == 'combine':
            if categoriesNumber == True:
                newData = []
                for d in data:
                    newDataPart = []
                    for cN in range(0, len(categories)):
                        newDataPart.append([categories[cN], d[cN]])
                    newData.append(newDataPart)
                data = newData
                categories = None

        res = ''
        if plotSeries == 'Single':
            if plotType == 'Scatter':


                if choices.trend == 'yes':

                    dataTrendAll = []
                    dataTrendNameAll = []

                    st = ['scatter' for l in data] + ['line' for l in data]

                    for ny, y in enumerate(data):
                        N = len(y)
                        if categories != None:
                            x = [float(c) for c in categories]
                        else:
                            x = xrange(N)
                        B = (sum(x[i] * y[i] for i in xrange(N)) - 1. / N * sum(x) * sum(y)) / (
                        sum(x[i] ** 2 for i in xrange(N)) - 1. / N * sum(x) ** 2)

                        A = 1. * sum(y) / N - B * 1. * sum(x) / N

                        dataTrendNameAll.append(seriesName[ny] + ' - trend')
                        dataTrend = []

                        for x1 in x:
                            dataTrend.append(A+B*x1)
                        dataTrendAll.append(dataTrend)



                    data = data + dataTrendAll
                    seriesName = seriesName + dataTrendNameAll
                    res += vg.drawMultiTypeChart(
                        data,
                        categories=categories,
                        xAxisRotation=90,
                        marginTop=30,
                        xAxisTitle=xAxisTitle,
                        yAxisTitle=yAxisTitle,
                        height=500,
                        seriesName=seriesName,
                        label=label,
                        seriesType = st
                        #                      titleText = 'Plot',
                    )

                else:
                    res += vg.drawScatterChart(
                        data,
                        categories=categories,
                        xAxisRotation=90,
                        marginTop=30,
                        xAxisTitle=xAxisTitle,
                        yAxisTitle=yAxisTitle,
                        height=500,
                        seriesName=seriesName,
                        label=label,
                        minY=minFromList
                        #                      titleText = 'Plot',
                    )


            if plotType == 'Pie':
                res += vg.drawPieChart(
                    data[0],
                    seriesName=categories,
                    height=400,
                    titleText=seriesName[0],
                )

            if plotType == 'Column':
                res += vg.drawColumnChart(
                    data,
                    categories=categories,
                    xAxisRotation=90,
                    marginTop=30,
                    xAxisTitle=xAxisTitle,
                    yAxisTitle=yAxisTitle,
                    height=500,
                    seriesName=seriesName,
                    label=label,
                    minY=minFromList
                    #                      titleText = 'Plot',
                )
            if plotType == 'Line':
                res += vg.drawLineChart(
                    data,
                    categories=categories,
                    xAxisRotation=90,
                    marginTop=30,
                    xAxisTitle=xAxisTitle,
                    yAxisTitle=yAxisTitle,
                    height=500,
                    seriesName=seriesName,
                    label=label,
                    minY=minFromList
                    #                      titleText = 'Plot',
                )
            if plotType == 'Heatmap':
                res += vg.drawHeatmapSmallChart(
                    data,
                    categories=categories,
                    xAxisRotation=90,
                    marginTop=30,
                    xAxisTitle=xAxisTitle,
                    yAxisTitle=yAxisTitle,
                    height=500,
                    seriesName=seriesName,
                    label=label,
                    #                      titleText = 'Plot',
                )
        elif plotSeries == 'Multi':
            if plotType == 'Scatter':
                for nrD in range(0, len(data)):
                    if plotRes == 'combine':
                        data[nrD] = [data[nrD]]
                    res += vg.drawScatterChart(
                        data[nrD],
                        categories=categories,
                        xAxisRotation=90,
                        marginTop=30,
                        xAxisTitle=xAxisTitle,
                        yAxisTitle=yAxisTitle,
                        height=500,
                        seriesName=[seriesName[nrD]],
                        label=label,
                        minY=minFromList
                        #                      titleText = 'Plot',
                    )
            if plotType == 'Column':
                res += vg.drawColumnCharts(
                    data,
                    categories=[categories for x in range(0, len(data))],
                    xAxisRotation=90,
                    marginTop=30,
                    xAxisTitle=xAxisTitle,
                    yAxisTitle=yAxisTitle,
                    height=500,
                    seriesName=[[seriesName[elD]] for elD in range(0, len(data))],
                    label=label,
                    minY=minFromList
                    #                      titleText = 'Plot',
                )
            if plotType == 'Line':
                for nrD in range(0, len(data)):
                    if plotRes == 'combine':
                        data[nrD] = [data[nrD]]
                    res += vg.drawLineChart(
                        data[nrD],
                        categories=categories,
                        xAxisRotation=90,
                        marginTop=30,
                        xAxisTitle=xAxisTitle,
                        yAxisTitle=yAxisTitle,
                        height=500,
                        seriesName=[seriesName[nrD]],
                        label=label,
                        minY=minFromList
                        #                      titleText = 'Plot',
                    )

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin(divId='results-page')
        htmlCore.divBegin(divClass='results-section')

        htmlCore.line(res)

        htmlCore.divEnd()
        htmlCore.divEnd()
        htmlCore.end()

        print htmlCore

    @classmethod
    def validateAndReturnErrors(cls, choices):



        columnY = choices.columnY
        if isinstance(columnY, dict):
            if not True in columnY.values():
                errorString = 'Check at least one value for y-Axis'
                return errorString

    # @staticmethod
    # def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    #
    # @staticmethod
    # def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    # @staticmethod
    # def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    # @staticmethod
    # def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    # @staticmethod
    # def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    # @staticmethod
    # def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #



    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'The tool allow to compute average semgemnt lenght of the track and its  overlap [bp proportion] with a query track].'

        stepsToRunTool = ['Select GSuite or file with tabular from history',
                          'Select way of showing series as single or multi charts',
                          'Select type of chart',
                          'Select value for x-Axis',
                          'Select type of scale for x-Axis',
                          'Select value for y-Axis',
                          'Select type of scale for y-Axis',
                          'Select results of plotting (option available for selected type of charts)',
                          'Add trend (option available for selected type of charts)']

        toolResult = 'The results are presented in an interactive chart.'

        return Legend().createDescription(toolDescription=toolDescription,
                                                     stepsToRunTool=stepsToRunTool,
                                                     toolResult=toolResult)

    # @staticmethod
    # def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #    return None
    #
    # @staticmethod
    # def isDebugMode():
    #    '''
    #    Specifies whether the debug mode is turned on.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

