from collections import OrderedDict

import math

from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from quick.webtools.plot.RainfallPlot import RP
from quick.webtools.hgsuite.Legend import Legend

## author: SK
## date : 12.10.2022

class GenerateRainfallPlotTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Generate rainfall plot"


    @classmethod
    def getInputBoxNames(cls):
        return [
            ('Select GSuite', 'gsuite'),
            ('Select type of plotting', 'multiPlot'),
            # ('Select scale for bps value', 'scale'),
            ('Select bin size (default: 1000000)', 'bps'),
            # ('Point overlap points on black', 'overlap')
        ]
        # """
        # Specifies a list of headers for the input boxes, and implicitly also
        # the number of input boxes to display on the page. The returned list
        # can have two syntaxes:
        #
        #     1) A list of strings denoting the headers for the input boxes in
        #        numerical order.
        #     2) A list of tuples of strings, where each tuple has
        #        two items: a header and a key.
        #
        # The contents of each input box must be defined by the function
        # getOptionsBoxK, where K is either a number in the range of 1 to the
        # number of boxes (case 1), or the specified key (case 2).
        #
        # Note: the key has to be camelCase and start with a non-capital letter
        #       (e.g. "firstKey")
        #
        # Optional method. Default return value if method is not defined: []
        # """
        # # return [('First header', 'firstKey'),
        # #         ('Second Header', 'secondKey')]

    @staticmethod
    def getOptionsBoxGsuite():
        return '__history__', 'gsuite'

    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single', 'Multi'] #, 'plotsSeeparately']

    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return '1000000'

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):

        if not choices.gsuite:
            return "Please select a GSuite from history"

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if gsuite.genome == 'unknown':
            return "Please select a genome while creating GSuite"

        return None

    @staticmethod
    def getToolDescription():

        l = Legend()

        toolDescription = 'The tool is used to generate a rainfall plot.<br> A rainfall plot is a scatter plot which is often used to illustrate genomic distance along the genomic position (y and x axis respectively)<br>These plots are often used to identify mutation hotspots along a reference genome. '

        stepsToRunTool = ['Select Gsuite file which contains one or more tracks.',
                          'Select the type of plotting',
                          'Enter teh bin size (default is 1000000)'
                          ]
        toolResult = 'The tool outputs the rainfall plot.'
        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          )
        #
        # htmlCore = HtmlCore()
        #
        # htmlCore.paragraph('The tool is used to generate a rainfall plot. <br>'
        #                    'A rainfall plot is a scatter plot which is often used to illustrate genomic distance <br>'
        #                    'along the genomic position (y and x axis respectively)<br>'
        #                    'These plots are often used to identify mutation hotspots along a reference genome.')
        #
        # htmlCore.divider()
        #
        # htmlCore.paragraph('The tool requires a GSuite file which contains one or more tracks.')
        # htmlCore.paragraph('The tool outputs the rainfall plot.')
        #
        #
        # return str(htmlCore)

    @staticmethod
    def isPublic():
        return True


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        #gsuite
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        #all boxes
        multiPlot = choices.multiPlot
        #scale = choices.scale
        #overlap = choices.overlap
        overlap = 'no'
        bps = int(choices.bps)

        rp = RP(gsuite)

        #get length of chromosomes and ordering
        chrItems = GenomeInfo.getStdChrLengthDict(gsuite.genome)
        chrOrder, chrLength = GenerateRainfallPlotTool.sortChrDict(chrItems)

        dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum, chrList = GenerateRainfallPlotTool.countMutations(
            gsuite, chrLength, bps)

        seriesType, newSeriesNameRes, newSeriesNameResOE, yAxisMultiVal = rp.getOptionsForPlot(elementOrder, gsuite.allTrackTitles())
        newResList, newResBinSizeList, newResBinSizeListSortedList = rp.generateBinSizeList(elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum)


        vg = visualizationGraphs()

        # print ("newResBinSizeListSortedList" + str(newResBinSizeListSortedList))
        # print ("</br>")
        # print ("Chromosoem length" + str(chrLength))
        # print ("</br>")
        # print ("newResList" + str(newResList))
        # print ("</br>")
        # print ("newSeriesNameRes" + str(newSeriesNameRes))
        # print ("</br>")
        # print ("newResBinSizeList" + str(newResBinSizeList))
        # print ("</br>")
        # print ("overlap" + str(overlap))
        # print ("</br>")
        # print ("seriesType" + str(seriesType))
        # print ("</br>")
        # print ("yAxisMultiVal" + str(yAxisMultiVal))
        # print ("</br>")
        # print (chrLength, newResList, newSeriesNameRes, newResBinSizeList, overlap, seriesType, yAxisMultiVal)
        # #print (yAxisMultiVal)


        res = ''
        if multiPlot == 'Single':
            res += GenerateRainfallPlotTool.drawSinglePlot(vg, newResBinSizeListSortedList, chrLength, newResList, newSeriesNameRes, newResBinSizeList, overlap, seriesType, yAxisMultiVal)
        elif multiPlot == "Multi":
            res += GenerateRainfallPlotTool.drawMultiPlot(newResList, newSeriesNameRes, newResBinSizeList, vg, seriesType, yAxisMultiVal)

        #plotsSeeparately

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line('Bin size: ' + str(bps))
        htmlCore.line(res)
        htmlCore.end()
        htmlCore.hideToggle(styleClass='debug')
        print htmlCore




    @classmethod
    def prepareUpdateButton(cls, newResList):
        listElAll = []
        for l in newResList:
            listElAll += [[ll[0], round(ll[1], 1)] for ll in l]

        epsilonTF = True

        if epsilonTF == False:

            z = []
            y = []
            for i in listElAll:
                if i not in z:
                    z.append(i)
                else:
                    y.append(i)
        else:
            pass


        return "<button id='up'> update </button> <script> var listElAll =  " + str(listElAll) + "; </script>"

    @classmethod
    def prepareDataForRP(cls, newResList, newSeriesNameRes, newResBinSizeList):

        #print newSeriesNameRes

        i = 0
        for nrNum in range(0, len(newResList)*2):

            newSeriesNameRes[nrNum]  = newSeriesNameRes[nrNum].replace('-- point', '')

            if i < len(newResList):
                #print "1"
                newSeriesNameRes[nrNum] = 'Rainfall plot of ' + newSeriesNameRes[nrNum]
            else:
                #print "2"
                newSeriesNameRes[nrNum] = 'Frequency of ' + newSeriesNameRes[nrNum]
            i+=1

            if i == len(newResList)-1:
                i==0

        data = newResList + newResBinSizeList
        #print newSeriesNameRes
        return data, newSeriesNameRes

    @classmethod
    def addJSForOverlap(cls):
        return """
                    <script>

                    function round(number, decimals)
                    {
                    return +(Math.round(number + "e+" + decimals) + "e-" + decimals);
                    }

                    function decNum(num)
                    {
                      return num.toString().length;
                    }


                    function arrayMinMax(arr) {
                      var len = arr.length,
                      maxX = -Infinity;
                      minX = Infinity;
                      maxY = -Infinity;
                      minY = Infinity;

                      maxArr = []

                      while (len--)
                      {
                        if (arr[len][0] < minX)
                        {
                          minX = arr[len][0];
                        }
                        if (arr[len][0] > maxX)
                        {
                          maxX = arr[len][0];
                        }

                        if (arr[len][1] < minY)
                        {
                          minY = arr[len][1];
                        }
                        if (arr[len][1] > maxY)
                        {
                          maxY = arr[len][1];
                        }



                      }

                      maxArr.push(minX);
                      maxArr.push(maxX);
                      maxArr.push(minY);
                      maxArr.push(maxY);

                      return maxArr;
                    }



                    $('#up').click(function () {

                        chart2  = $('#container2').highcharts();




                    var minX = 0;
                    var maxX = chart2.plotSizeX;
                    var minY = 0;
                    var maxY = chart2.plotSizeY * 0.7;



                    console.log(minX, minY, maxX, maxY);


                    decNumX = decNum(maxX);
                    decNumY = decNum(maxY);

                    minmaxArr = arrayMinMax(listElAll);

                    var minXval = minmaxArr[0];
                    var maxXval = minmaxArr[1];
                    var minYval = minmaxArr[2];
                    var maxYval = minmaxArr[3];

                    var xx=0;
                    var yy=0;
                    var listElAllNorm = [];

                    //to improve because 1 dot is 4 piksels - not 1, so it means that it will not find piksels which are partially
                    //covered, need to be fully covered

                    for (var elN =0; elN< listElAll.length; elN++)
                    {
                        //listElAllNorm.push([round((listElAll[elN][0] - minX) / (maxX - minX), decNumX-3), round((listElAll[elN][1] - minY) / (maxY - minY), decNumY-3)]);
                        xx = round((listElAll[elN][0] - minXval) / (maxXval - minXval), decNumX);
                        xx = xx * (maxX-minX) + minX;
                        yy = round((listElAll[elN][1] - minYval) / (maxYval - minYval), decNumY);
                        yy = yy * (maxY-minY) + minY;
                        listElAllNorm.push([xx, yy]);
                    }


                    //console.log(listElAllNorm);



                    var z = []
                    var yy = [] //unique elements
                    var index = 0
                    for (i in listElAllNorm)
                    {
                        //trick with changing list into string , because there is no simple method for array of arrays
                        //console.log(index, listElAllNorm[i], z, z.indexOf(listElAllNorm[i].toString()), yy);
                        if (z.indexOf(listElAllNorm[i].toString()) == -1)
                        {
                           z.push(listElAllNorm[i].toString());
                        }
                        else
                        {
                           yy.push(index);
                        }
                        index+=1;
                    }

                    //console.log(yy);


                    y = []
                    for (yEl in yy)
                    {
                        y.push(listElAll[yy[yEl]])
                    }



                    var seriesLength = chart2.series.length;
                    for(var i = seriesLength - 1; i > -1; i--)
                    {

                    if(chart2.series[i].name == 'overlap')
                       chart2.series[i].remove();
                    }

                    chart2.addSeries({
                        type: 'scatter',
                        name: 'overlap',
                        data: y.slice(0,y.length-1),
                        color: "#000000",
                        marker: { radius: 2, symbol: 'circle', },
                         yAxis: 0
                    });

                    //chart2.redraw();


                    //console.log(chart2);




                                })
                                </script>

                    """

    @classmethod
    def drawSinglePlot(cls, vg, newResBinSizeListSortedList, chrLength, newResList, newSeriesNameRes, newResBinSizeList,
                       overlap, seriesType, yAxisMultiVal):

        res = ''
        # line plot with sum of frequencies
        # res += vg.drawLineChart(
        #     [newResBinSizeListSortedList],
        #     seriesName=['sum per bin'],
        #     height=300,
        #     xAxisTitle='Genomic position',
        #     yAxisTitle='values',
        #     minY=0,
        #     plotLines=chrLength.values(),
        #     plotLinesName=chrLength.keys()
        # )
        #
        # res += '<div style="clear:both;"> </div>'

        data, newSeriesNameRes = GenerateRainfallPlotTool.prepareDataForRP(newResList, newSeriesNameRes,
                                                                           newResBinSizeList)
        #print str(newSeriesNameRes) + "<br>"



        if overlap == 'yes':
            res += GenerateRainfallPlotTool.prepareUpdateButton(newResList)

        # RP plot with frequency line
        res += vg.drawLineChartMultiYAxis(
            data,
            seriesName=newSeriesNameRes,
            seriesType=seriesType,
            height=400,  # newHeight + 0.3*newHeight,
            reversed=False,
            markerRadius=2,
            xAxisTitle='Genomic position',
            yAxisTitle=['Genomic distance', 'values'],
            yAxisMulti=yAxisMultiVal,
            minY=0,
            plotLines=chrLength.values(),
            plotLinesName=chrLength.keys()
        )

        if overlap == 'yes':
            res += GenerateRainfallPlotTool.addJSForOverlap()

        res += '<div style="clear:both;"> </div>'

        return res

    @classmethod
    def countForMultiPlot(cls, newResList, newSeriesNameRes, newResBinSizeList):

        for nrNum in range(0, len(newResList) * 2):
            if nrNum % 2 == 0:
                newSeriesNameRes[nrNum] = 'Frequency of ' + newSeriesNameRes[nrNum]
            else:
                newSeriesNameRes[nrNum] = 'Rainfall plot of ' + newSeriesNameRes[nrNum].replace('-- point', '')


        maxLength = -10000
        for nrNum in range(1, len(newResList)):
            if maxLength < newResList[nrNum][-1][0]:
                maxLength = newResList[nrNum][-1][0]

        #newSeriesNameRes[0] = newSeriesNameRes[0] + ' -- ' + str(len(newResList[0]))
        for nrNum in range(1, len(newResList)):
            for nrNum1 in range(0, len(newResList[nrNum])):
                newResList[nrNum][nrNum1][0] = newResList[nrNum][nrNum1][0] + maxLength * nrNum
            for nrNum1 in range(0, len(newResBinSizeList[nrNum])):
                newResBinSizeList[nrNum][nrNum1][0] = newResBinSizeList[nrNum][nrNum1][0] + maxLength * nrNum
            #newSeriesNameRes[nrNum] = newSeriesNameRes[nrNum] + ' -- ' + str(len(newResList[nrNum]))

        return newResList, newResBinSizeList, newSeriesNameRes

    @classmethod
    def drawMultiPlot(cls, newResList, newSeriesNameRes, newResBinSizeList, vg, seriesType, yAxisMultiVal):
        res = ''
        newResList, newResBinSizeList, newSeriesNameRes = GenerateRainfallPlotTool.countForMultiPlot(newResList,
                                                                                                     newSeriesNameRes,
                                                                                                     newResBinSizeList)
        #print newSeriesNameRes

        res += vg.drawLineChartMultiYAxis(
            newResList + newResBinSizeList,
            seriesName=newSeriesNameRes,
            seriesType=seriesType,
            height=500,
            reversed=False,
            markerRadius=1,
            label='<b>{series.name}: </b>{point.x}, {point.y} <br \>',
            xAxisTitle='Genomic position',
            yAxisTitle=['Genomic distance', 'Values'],
            yAxisMulti=yAxisMultiVal,
            minY=0,
            # plotLines=chrLength.values(),
            # plotLinesName=chrLength.keys()
        )

        res += '<div style="clear:both;"> </div>'
        return res


    @classmethod
    def countMutations(cls, gsuite, chrLength, bps):

        dataDict = OrderedDict()
        dataDictLine = OrderedDict()

        chrList = []

        elementOrder = []

        # parse the tracks
        for track in gsuite.allTrackTitles():

            # count one track
            gSuiteTrack = gsuite.getTrackFromTitle(track)
            trackName = track

            dataDict[trackName] = OrderedDict()
            dataDictLine[trackName] = OrderedDict()

            # read from file
            newDict = OrderedDict()
            with open(gSuiteTrack.path, 'r') as f:
                i = 0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el) >= 2:
                        try:
                            st = int(el[1])
                            if not el[0] in newDict:
                                newDict[el[0]] = []
                            if not el[0] in chrList:
                                chrList.append(el[0])
                            newDict[el[0]].append([el[0], st, int(el[2])])
                        except:
                            pass
                i += 1

            # sort file according to start position
            newDict2 = OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])

            j=0
            chr =''
            for key, it in newDict2.items():

                if j == 0:
                    chr = key
                    j+=1
                i = 0
                prevEnd = 0
                label = 0

                for el in it:
                    if len(el) >= 2:

                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:


                            if chr == key: #this is a condition which allow us to do not count the distance for the last an start points on the next chromosomes
                                if not label in dataDict[trackName]:
                                    dataDict[trackName][label] = OrderedDict()
                                    dataDict[trackName][label]['val'] = 0
                                    dataDict[trackName][label]['tot'] = 0

                                if start - prevEnd > 0:
                                    dataDict[trackName][label]['val'] += math.log(start - prevEnd, 10)
                                elif start - prevEnd == 0:
                                    dataDict[trackName][label]['val'] += start - prevEnd

                                dataDict[trackName][label]['tot'] += 1
                            else:
                                chr = key

                        label = int(el[1]) + int(chrLength[el[0]])

                        prevEnd = int(el[1])  # not anymore prevEnd
                        i += 1

            elementOrder.append(i)


        listResCopy = []
        for key0, it0 in dataDict.iteritems():
            listResPart = []
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        # if there is no need to have ordering
        # elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k], reverse=True)
        # then
        elementOrder = [k for k in range(0, len(elementOrder))]

        lengthOfLastChromosome = GenomeInfo.getChrLen(gsuite.genome, chrLength.keys()[-1])

        howManyIntervalsPerBin = int((chrLength.values()[-1] + lengthOfLastChromosome) / bps) + 1

        listOfBinSumPerTrack = []
        for interval in range(0, howManyIntervalsPerBin):
            listOfBin = (interval * bps, (interval + 1) * bps)
            listOfBinSumPerTrack.append(listOfBin)

            newResBinSizeListSum = {}

        listDataCountPerBin = []
        for el in listResCopy:
            data = filter(None, [filter(lambda l: t[0] <= int(l[0]) < t[1], el) for t in listOfBinSumPerTrack])
            listData = []
            for d in data:

                countD = int(d[0][0] / bps) * bps + bps / 2
                lenD = len(d)

                w = 0
                listData.append([countD, lenD])

                if not countD in newResBinSizeListSum.keys():
                    newResBinSizeListSum[countD] = lenD
                else:
                    newResBinSizeListSum[countD] += lenD

            listDataCountPerBin.append(listData)

        return dataDict, dataDictLine, elementOrder, listResCopy, listDataCountPerBin, newResBinSizeListSum, chrList

    @classmethod
    def sortChrDict(cls, chr):

        remeberString = []
        keysList = []
        for el in chr.keys():
            try:
                elC = int(el.replace('chr', ''))
                keysList.append(elC)
            except:
                remeberString.append(el.replace('chr', ''))

        sChr = sorted(keysList) + sorted(remeberString)

        chrDict = OrderedDict()
        chrLength = OrderedDict()
        val = 0
        for elChr in sChr:
            el = 'chr' + str(elChr)
            chrDict[el] = chr[el]
            chrLength[el] = val
            val += chr[el]

        return chrDict, chrLength


    # @classmethod
    # def getInputBoxOrder(cls):
    #     """
    #     Specifies the order in which the input boxes should be displayed,
    #     as a list. The input boxes are specified by index (starting with 1)
    #     or by key. If None, the order of the input boxes is in the order
    #     specified by getInputBoxNames().
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     """
    #     Creates a visual separation of groups of consecutive option boxes
    #     from the rest (fieldset). Each such group has an associated label
    #     (string), which is shown to the user. To define groups of option
    #     boxes, return a list of BoxGroup namedtuples with the label, the key
    #     (or index) of the first and last options boxes (inclusive).
    #
    #     Example:
    #        from quick.webtool.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey',
    #                         last='secondKey')]
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    @classmethod
    def getOptionsBoxFirstKey(cls):  # Alt: getOptionsBox1()
        """
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to
        other methods. These are lists of results, one for each input box
        (in the order specified by getInputBoxOrder()).

        Mandatory for the first key defined in getInputBoxNames(), if any.

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Raw HTML code:          '__rawstr__', 'HTML code'
        - This is mainly intended for read only usage. Even though more
          advanced hacks are possible, it is discouraged.

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) |
                                ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting Galaxy dataset info, as
            described below.

        History check box list: ('__multihistory__', ) |
                                ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with Galaxy dataset ids as key (the number YYYY
            as described below), and the associated Galaxy dataset info as the
            values, given that the history element is ticked off by the user.
            If not, the value is set to None. The Galaxy dataset info structure
            is described below.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'],
                                 ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False),
                                             ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).


        ###
        Note about the "Galaxy dataset info" data structure:
        ###

        "Galaxy dataset info" is a list of strings coding information about a
        Galaxy history element and its associated dataset, typically used to
        provide info on the history element selected by the user as input to a
        ProTo tool.

        Structure:
            ['galaxy', fileFormat, path, name]

        Optionally encoded as a single string, delineated by colon:

            'galaxy:fileFormat:path:name'

        Where:
            'galaxy' used for assertions in the code
            fileFormat (or suffix) contains the file format of the dataset, as
                encoded in the 'format' field of a Galaxy history element.
            path (or file name/fn) is the disk path to the dataset file.
                Typically ends with 'XXX/dataset_YYYY.dat'. XXX and YYYY are
                numbers which are extracted and used as an unique id  of the
                dataset in the form [XXX, YYYY]
            name is the title of the history element

        The different parts can be extracted using the functions
        extractFileSuffixFromDatasetInfo(), extractFnFromDatasetInfo(), and
        extractNameFromDatasetInfo() from the module CommonFunctions.py.
        """
        return ['testChoice1', 'testChoice2', '...']

    @classmethod
    def getOptionsBoxSecondKey(cls, prevChoices):  # Alt: getOptionsBox2()
        """
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).

        Mandatory for the subsequent keys (after the first key) defined in
        getInputBoxNames(), if any.
        """
        return ''

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     """
    #     If not None, defines the string content of an clickable info box
    #     beside the corresponding input box. HTML is allowed.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     """
    #     Defines a set of demo inputs to the option boxes in the
    #     order defined by getOptionBoxNames and getOptionsBoxOrder.
    #     If not None, a Demo button appears in the interface. Clicking the
    #     button fills the option boxed with the defined demo values.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     """
    #     Defines extra history elements to be created when clicking execute.
    #     This is defined by a list of HistElement objects, as in the
    #     following example:
    #
    #        from proto.GeneralGuiTool import HistElement
    #        return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]
    #
    #     It is good practice to use class constants for longer strings.
    #
    #     In the execute() method, one typically needs to fetch the path to
    #     the dataset referred to by the extra history element. To fetch the
    #     path, use the dict cls.extraGalaxyFn with the defined history title
    #     as key, e.g. "cls.extraGalaxyFn[cls.HISTORY_TITLE]".
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #     """
    #     Is called when execute-button is pushed by web-user. Should print
    #     output as HTML to standard out, which will be directed to a results
    #     page in Galaxy history. If getOutputFormat is anything else than
    #     'html', the output should be written to the file with path galaxyFn.
    #     If needed, StaticFile can be used to get a path where additional
    #     files can be put (cls, e.g. generated image files). choices is a list
    #     of selections made by web-user in each options box.
    #
    #     Mandatory unless isRedirectTool() returns True.
    #     """
    #     print 'Executing...'

    # @classmethod
    # def validateAndReturnErrors(cls, choices):
    #     """
    #     Should validate the selected input parameters. If the parameters are
    #     not valid, an error text explaining the problem should be returned.
    #     The GUI then shows this text to the user (if not empty) and greys
    #     out the execute button (even if the text is empty). If all
    #     parameters are valid, the method should return None, which enables
    #     the execute button.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

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
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     """
    #     The format of the history element with the output of the tool. Note
    #     that if 'html' is returned, any print statements in the execute()
    #     method is printed to the output dataset. For text-based output
    #     (e.g. bed) the output dataset only contains text written to the
    #     galaxyFn file, while all print statements are redirected to the info
    #     field of the history item box.
    #
    #     Note that for 'html' output, standard HTML header and footer code is
    #     added to the output dataset. If one wants to write the complete HTML
    #     page, use the restricted output format 'customhtml' instead.
    #
    #     Optional method. Default return value if method is not defined:
    #     'html'
    #     """
    #     return 'html'
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
