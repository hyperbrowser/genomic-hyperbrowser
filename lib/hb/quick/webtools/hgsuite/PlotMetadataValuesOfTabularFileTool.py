from collections import OrderedDict

from gold.gsuite.GSuiteConstants import TITLE_COL
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import StaticImage
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.Legend import Legend
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
import math
from gold.gsuite import GSuiteConstants, GSuiteFunctions

# This is a template prototyping GUI that comes together with a corresponding
# web page.
from quick.util.CommonFunctions import extractFileSuffixFromDatasetInfo


class PlotMetadataValuesOfTabularFileTool(GeneralGuiTool):

    ALLOW_UNKNOWN_GENOME = True
    TITLE = 'title'

    @staticmethod
    def getToolName():
        return "Plot data for tabular file or hGSuite"

    @staticmethod
    def getInputBoxNames():
        return [
            ('Select file', 'selFile'),
            ('Select way of showing series as', 'plotSeries'),
            ('Select type of chart', 'plotType'),
            ('Select value for x-Axis', 'columnX'),
            ('Select type of scale for x-Axis', 'axesScaleX'),
            ('Select value for y-Axis', 'columnY'),
            ('Select value for plot', 'values'),
            ('Select type of scale for y-Axis', 'axesScaleY'),
            # ('Select results of plotting', 'plotRes'),
        ]

    @staticmethod
    def getOptionsBoxSelFile():
        return GeneralGuiTool.getHistorySelectionElement('tabular', 'gsuite')

    @classmethod
    def getOptionsBoxPlotSeries(cls, prevChoices):
        if prevChoices.selFile:
            return ['Single', 'Multi']

    @classmethod
    def getOptionsBoxPlotType(cls, prevChoices):
        if prevChoices.selFile:
            if prevChoices.plotSeries == 'Single':
                return ['Column', 'Heatmap', 'Line', 'Pie', 'Scatter']
            else:
                return ['Column', 'Line', 'Pie', 'Scatter']

    @classmethod
    def getOptionsBoxColumnX(cls, prevChoices):  # Alternatively: getOptionsBox2()
        if not prevChoices.selFile:
            return

        suffixForFile = extractFileSuffixFromDatasetInfo(prevChoices.selFile)
        if suffixForFile == 'tabular':
            input = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.selFile.split(':')), 'r')
            attribute = input.readline().strip('\n').split('\t')
            if prevChoices.plotType== 'Pie':
                return attribute
            return ['line number'] + attribute
        if suffixForFile == 'gsuite':
            gSuite = getGSuiteFromGalaxyTN(prevChoices.selFile)
            if prevChoices.plotType== 'Pie':
                return [cls.TITLE] + gSuite.attributes
            return ['line number'] + [cls.TITLE] + gSuite.attributes
        return

    @staticmethod
    def getOptionsBoxAxesScaleX(prevChoices):
        if prevChoices.selFile:
            if prevChoices.columnX == 'line number':
                return
            if prevChoices.plotType == 'Heatmap' or prevChoices.plotType == 'Pie':
                return
            return ['linear', 'log10', 'no uniform scale (sorted values as labels)']

    @classmethod
    def getOptionsBoxColumnY(cls, prevChoices):  # Alternatively: getOptionsBox2()
        if not prevChoices.selFile:
            return

        suffixForFile = extractFileSuffixFromDatasetInfo(prevChoices.selFile)
        if suffixForFile == 'tabular':
            input = open(
                    ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.selFile.split(':')), 'r')
            attribute = input.readline().strip('\n').split('\t')

        if suffixForFile == 'gsuite':
            gSuite = getGSuiteFromGalaxyTN(prevChoices.selFile)
            attribute = [cls.TITLE] + gSuite.attributes

        att = OrderedDict()
        for key in attribute:
            att[key] = False

        if prevChoices.plotSeries == 'Single':
            if prevChoices.plotType == 'Pie':
                return att.keys()

        if prevChoices.plotType == 'Heatmap':
            return attribute

        return att

    @classmethod
    def getOptionsBoxValues(cls, prevChoices):
        if prevChoices.selFile:
            if prevChoices.plotType == 'Heatmap':

                suffixForFile = extractFileSuffixFromDatasetInfo(prevChoices.selFile)
                if suffixForFile == 'tabular':
                    input = open(
                        ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.selFile.split(':')), 'r')
                    attribute = input.readline().strip('\n').split('\t')
                if suffixForFile == 'gsuite':
                    gSuite = getGSuiteFromGalaxyTN(prevChoices.selFile)
                    attribute = [cls.TITLE] + gSuite.attributes

                return attribute

    @staticmethod
    def getOptionsBoxAxesScaleY(prevChoices):
        if prevChoices.selFile:
            return ['linear', 'log10']


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        attributeList, axesScaleX, axesScaleY, columnX, columnY, columnYTitle, dictVal, plotRes, plotSeries, plotType = cls.prepareVariables(
            choices)

        # print 'attributeList',  attributeList, '<br>'
        # print 'dictVal', dictVal, '<br>'
        # print 'axesScaleX', axesScaleX, '<br>'
        # print 'axesScaleY', axesScaleY, '<br>'
        # print 'columnX', columnX, '<br>'
        # print 'columnY', columnY, '<br>'
        # print 'columnYTitle', columnYTitle, '<br>'
        # print 'dictVal', dictVal, '<br>'
        # print 'plotType', plotType, '<br>'
        # print 'attributeList', attributeList, '<br>'


        categories, categoriesNumber, categoriesY, data, label, maxY, minFromList, minY, seriesName, vg, xAxisTitle, yAxisTitle = cls.prepareDataForPlots(
            axesScaleX, axesScaleY, columnX, columnY, columnYTitle, dictVal, plotType, attributeList)

        res = cls.plotData(categories, categoriesNumber, categoriesY, data, label, maxY,
                           minFromList, minY, plotRes, plotSeries, plotType, seriesName, vg,
                           xAxisTitle, yAxisTitle)

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
    def prepareVariables(cls, choices):
        # data from choices
        selFile = choices.selFile
        suffixForFile = extractFileSuffixFromDatasetInfo(selFile)
        plotType = choices.plotType
        columnX = choices.columnX.encode('utf-8')

        if choices.plotType == "Heatmap":
            columnY = choices.values.encode('utf-8')
            columnYTitle = choices.columnY.encode('utf-8')
            axesScaleX = choices.axesScaleY
        else:
            columnY = choices.columnY
            axesScaleX = choices.axesScaleX
            columnYTitle = choices.columnY
        plotSeries = choices.plotSeries
        axesScaleY = choices.axesScaleY
        # 'linear', 'log10', 'no uniform scale (sorted values as labels)'
        if choices.plotType == 'Pie' or choices.columnX == 'line number':
            plotRes = 'separate'
            axesScaleX = 'linear'
        else:
            if axesScaleX == 'linear':
                # plotRes = choices.plotRes
                plotRes = 'combine'
            elif axesScaleX == 'log10':
                plotRes = 'separate'
            elif axesScaleX == 'no uniform scale (sorted values as labels)':
                plotRes = 'separate'
        attributeList, dictVal = cls.readFile(choices, selFile, suffixForFile)
        return attributeList, axesScaleX, axesScaleY, columnX, columnY, columnYTitle, dictVal, plotRes, plotSeries, plotType

    @classmethod
    def _checkType(cls, l):
        if len(l) == 0:
            return 0
        for x in l:
            try:
                float(x)
            except:
                return 0
        return 1

    @classmethod
    def readFile(cls, choices, selFile, suffixForFile):
        # unpack tabular file
        dictVal = OrderedDict()
        if suffixForFile == 'tabular':
            input = open(ExternalTrackManager.extractFnFromGalaxyTN(selFile.split(':')),
                         'r')
            iD = 0
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
                        iDL += 1
                iD += 1

            # full list of attributes (meta-data)
            attributeList = input.readline().strip('\n').split('\t')
        if suffixForFile == 'gsuite':
            gSuite = getGSuiteFromGalaxyTN(choices.selFile)
            attributeList = gSuite.attributes
            dictVal[cls.TITLE] = gSuite.allTrackTitles()
            for attr in attributeList:
                if not attr in dictVal.keys():
                    dictVal[attr] = gSuite.getAttributeValueList(attr)
        return attributeList, dictVal

    @classmethod
    def prepareDataForPlots(cls, axesScaleX, axesScaleY, columnX, columnY, columnYTitle,
                            dictVal, plotType, attributeList):
        # dictNum - include numerical values which can be presented in y-axes
        # need to do that because pie can have only one chocie and then it is not returing dict
        dictNum = OrderedDict()
        for key in attributeList:
            dictNum[key] = False

        seriesName = []
        # check if user selected categoriesNumber and it is possible to use combinate
        categoriesNumber = False
        data = []
        if plotType == 'Heatmap':
            columnXTitleChange = list(set(dictVal[columnX]))
            columnYTitleChange = list(set(dictVal[columnYTitle]))

            allData = zip(dictVal[columnX], dictVal[columnYTitle], dictVal[columnY])

            tempDict = {}

            maxY = 0
            minY = 100000000
            for d in allData:
                if d[2] == None or d[2] == 'nan':
                    pass
                else:
                    if axesScaleY == 'log10':
                        if float(d[2]) != 0:
                            val = math.log(float(d[2]), 10)
                            tempDict[tuple([d[0], d[1]])] = val
                            if maxY < val:
                                maxY = val
                            if minY > val:
                                minY = val
                        else:
                            tempDict[tuple([d[0], d[1]])] = 0
                    else:
                        tempDict[tuple([d[0], d[1]])] = d[2]
                        if maxY < float(d[2]):
                            maxY = float(d[2])
                        if minY > float(d[2]):
                            minY = float(d[2])

            if minY >= 0:
                minY = 0
            maxY = math.ceil(maxY)


            data = []
            for cy in columnYTitleChange:
                d = []
                for cx in columnXTitleChange:
                    if tuple([cx, cy]) in tempDict.keys():
                        d.append(tempDict[tuple([cx, cy])])
                    else:
                        d.append(0)
                data.append(d)


            categories = columnXTitleChange
            categoriesY = columnYTitleChange
            seriesName = categoriesY


        else:
            # check if it is dict or not
            if not isinstance(columnY, dict):
                tempDict = {}
                tempDict[columnY] = 'True'
                columnY = tempDict

            # print 'columnY', columnY, '<br>'

            sortedCat = None
            if columnX == 'line number':
                categories = None
            else:
                if columnX in dictNum.keys():
                    try:
                        categoriesBefore = [float(v) for v in dictVal[columnX]]
                        categoriesNumber = True
                    except:
                        categoriesBefore = [v for v in dictVal[columnX]]
                        categoriesNumber = False

                    if axesScaleX == 'log10':
                        for cbN in range(0, len(categoriesBefore)):
                            if categoriesBefore[cbN] != 0:
                                categoriesBefore[cbN] = math.log(categoriesBefore[cbN], 10)

                    sortedCat = sorted(range(len(categoriesBefore)),
                                       key=lambda k: categoriesBefore[k])
                    categories = []
                    for n in sortedCat:
                        categories.append(categoriesBefore[n])
                else:
                    categories = dictVal[columnX]  # gSuite.getAttributeValueList(columnX)


                    # data are sorted according to numerical values
                categoriesTemp = categories
                # print 'dictVal', dictVal, '<br>'
                # print '-----categories', categories, '<br>'

                #remove duplicates from list
                categoriesNoDuplicates = list(set(categories))
                categories01 = []
                for cNum, c in enumerate(categoriesTemp):
                    if c in categoriesNoDuplicates:
                        categories01.append(1)
                        categoriesNoDuplicates[categoriesNoDuplicates.index(c)] = ''
                    else:
                        categories01.append(0)



            for key, it in columnY.iteritems():
                if it == 'True':
                    dataPart = []
                    seriesName.append(key)

                    for x in dictVal[key]:  # gSuite.getAttributeValueList(key):
                        if x == 'nan':
                            x = 0
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

                    # print '-----dataPart', dataPart, '<br>'

                    #remove duplicates
                    if plotType != 'Heatmap' and categories!=None:
                        dp = []
                        for numc01, c01 in enumerate(categories01):
                            if c01 == 1:
                               dp.append(dataPart[numc01])
                        data.append(dp)
                    else:
                        data.append(dataPart)
            categoriesY = ''
            maxY = 0
            minY = 0

            # print '--------<br> data', data, '<br>'

        # remove duplicates
        if plotType != 'Heatmap' and categories!= None:
            categories = []
            for numc01, c01 in enumerate(categories01):
                if c01 == 1:
                    categories.append(categoriesTemp[numc01])

        label = ''
        if len(seriesName) != 0:
            label = '<b>{series.name}</b>: {point.x} {point.y}'
        else:
            label = '{point.x} {point.y}'
        vg = visualizationGraphs()
        # 'Column', 'Scatter', 'Heatmap'
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

        return categories, categoriesNumber, categoriesY, data, label, maxY, minFromList, minY, seriesName, vg, xAxisTitle, yAxisTitle

    @classmethod
    def plotData(cls, categories, categoriesNumber, categoriesY, data, label, maxY, minFromList,
                 minY, plotRes, plotSeries, plotType, seriesName, vg, xAxisTitle, yAxisTitle):
        # combain series with data

        # print '<br>BBBB<br>', data
        # print 'plotRes', plotRes, '<br>'
        # print 'categoriesNumber', categoriesNumber, '<br>'

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

        # print '<br>AAAA<br>', data

        res = ''
        if plotSeries == 'Single':
            if plotType == 'Scatter':
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
                # print 'data', data, '<br>'
                # print 'categories', categories, '<br>'
                # print 'xAxisTitle', xAxisTitle, '<br>'
                # print 'yAxisTitle', yAxisTitle, '<br>'
                # print 'seriesName', seriesName, '<br>'
                # print 'label', label, '<br>'
                # print 'minFromList', minFromList, '<br>'

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
                if len(categories) * len(categoriesY) < 400:
                    res += vg.drawHeatmapSmallChart(
                        data,
                        categories=categories,
                        xAxisRotation=90,
                        marginTop=30,
                        xAxisTitle=xAxisTitle,
                        yAxisTitle=yAxisTitle,
                        height=500,
                        minY=minY,
                        maxY=maxY,
                        seriesName=seriesName,
                        label=label,
                        categoriesY=categoriesY
                    )
                else:
                    res += vg.drawHeatmapLargeChart(
                        data,
                        categories=categories,
                        xAxisRotation=90,
                        marginTop=30,
                        xAxisTitle=xAxisTitle,
                        yAxisTitle=yAxisTitle,
                        height=500,
                        minY=minY,
                        maxY=maxY,
                        zoomType='xy',
                        seriesName=seriesName,
                        label=label,
                        categoriesY=categoriesY
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
            if plotType == 'Pie':
                for nrD in range(0, len(data)):
                    res += vg.drawPieChart(
                        data[nrD],
                        seriesName=categories,
                        height=400,
                        titleText=seriesName[nrD],
                )
        return res

    @classmethod
    def validateAndReturnErrors(cls, choices):

        columnY = choices.columnY
        if isinstance(columnY, dict):
            if not True in columnY.values():
                errorString = 'Check at least one value for y-Axis'
                return errorString

        if choices.selFile:
            attributeList, axesScaleX, axesScaleY, columnX, columnY, columnYTitle, dictVal, plotRes, plotSeries, plotType = cls.prepareVariables(
                choices)


            howManycY = 0
            if (choices.plotType == 'Heatmap' or choices.plotType == 'Pie') and choices.plotSeries == 'Single':
                cY = cls._checkType(dictVal[columnY])
                if cY == 0:
                     return '<b>value for plot</b> need to be number type.'
            elif choices.columnX == 'line number':
                cX = 0
                cY = 0
                if cX == 0:
                    for keyD, itD in dictVal.items():
                        if columnY[keyD] == True:
                            cY += cls._checkType(dictVal[keyD])
                            howManycY += 1
                if cX == 0:
                    if cY != howManycY:
                        return '<b>value for y-Axis</b> need to be number type.'

            else:
                cX = cls._checkType(dictVal[columnX])
                cY = 0
                if cX == 0:
                    for keyD, itD in dictVal.items():
                        if columnY[keyD] == True:
                            cY += cls._checkType(dictVal[keyD])
                            howManycY += 1
                if cX == 0:
                    if cY != howManycY:
                        return 'At least on of the values, either <b>value for x-Axis</b> or  <b>value for y-Axis</b> need to be number type.'

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

        toolDescription = 'The tool allow to present metadata columns from hGSuite or results from tabular file in the chart.'

        stepsToRunTool = ['Select file',
                          'Select way of showing series as (Single, Multi)',
                          'Select type of chart (Single: Column, Heatmap, Line, Pie, Scatter; Multi: Column, Line, Pie, Scatter)',
                          'Select value for x-Axis',
                          'Select type of scale for x-Axis',
                          'Select value for y-Axis',
                          'Select type of scale for y-Axis',
                          'Select results of plotting (option available for selected type of charts)'
                          ]

        urlexample1Output = StaticImage(['hgsuite', 'img',
                                         'PlotMetadataValuesOfTabularFileTool-img1.png']).getURL()
        urlexample2Output = StaticImage(['hgsuite', 'img',
                                         'PlotMetadataValuesOfTabularFileTool-img2.png']).getURL()

        urlexample3Output = StaticImage(['hgsuite', 'img',
                                         'PlotMetadataValuesOfTabularFileTool-img3.png']).getURL()
        urlexample4Output = StaticImage(['hgsuite', 'img',
                                         'PlotMetadataValuesOfTabularFileTool-img4.png']).getURL()

        example = {'Example 1 (Series: Single; chart type: heatmap; file: tabular)': ['', ["""
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
                     ['Select way of showing series as','Single'],
                     ['Select type of chart', 'Heatmap'],
                     ['Select value for x-Axis', 'attribute0'],
                     ['Select value for y-Axis', 'attribute1'],
                     ['Select value for plot', 'attribute2'],
                     ['Select type of scale for y-Axis', 'linear']
                 ],
                                 [
                                     '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample1Output + '" /></div>'
                                 ]
                                 ],
           'Example 2 (Series: Single; chart type: pie; file: tabular)': ['', ["""
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
                 ['Select way of showing series as', 'Single'],
                 ['Select type of chart', 'Pie'],
                 ['Select value for x-Axis', 'attribute0'],
                 ['Select value for y-Axis', 'attribute3'],
                 ['Select type of scale for y-Axis', 'linear']
             ],
             [
                 '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample2Output + '" /></div>'
             ]
             ],
                   'Example 3 (Series: Multi; chart type: column; file: gSuite)': ['', ["""
    ##location: local
    ##file format: preprocessed
    ##track type: valued segments
    ##genome: mm10
    ###uri	title	genotype	text	Base-pair coverage	Base-pair coverage-max	Base-pair coverage-min
    hb:/external/dianadom_sandbox/42/4261a5a91e856c76/1%20-%20243-2--eta-.bed	1 - 243-2--eta-.bed	eta-	one	eta-	17117	9078
    hb:/external/dianadom_sandbox/c5/c58080e55c07e57e/2%20-%20243-4--eta-.bed	2 - 243-4--eta-.bed	eta-	No group	eta-	17117	9078
    hb:/external/dianadom_sandbox/5d/5d6d295d538d18a1/3%20-%20255-1--eta-.iota-.bed	3 - 255-1--eta-:iota-.bed	eta-/iota-	two	eta-/iota-	4236	3340
    hb:/external/dianadom_sandbox/36/369b5a0c1086deb2/4%20-%20255-4--eta-.iota-.bed	4 - 255-4--eta-:iota-.bed	eta-/iota-	No group	eta-/iota-	4236	3340


                        """],

                  [
                      ['Select file', 'tabular'],
                      ['Select way of showing series as', 'Multi'],
                      ['Select type of chart', 'Column'],
                      ['Select value for x-Axis', 'base-pair coverage'],
                      ['Select type of scale for x-Axis', 'linear'],
                      ['Select value for y-Axis', 'base-pair coverage-max, base-pair coverage-min'],
                      ['Select type of scale for y-Axis', 'linear']
                  ],
              [
                  '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample3Output + '" /><img  style="margin-right:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:right;padding-left:0px;" width="300" src="' + urlexample4Output + '" /></div>']
              ]
        }

        toolResult = 'The results are presented in an interactive chart.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example
                                          )

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

