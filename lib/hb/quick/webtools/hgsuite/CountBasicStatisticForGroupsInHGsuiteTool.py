from collections import OrderedDict
from operator import itemgetter

from gold.track.TrackStructure import SingleTrackTS
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.statistic.CountElementStat import CountElementStat
from gold.statistic.CountStat import CountStat
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack
from gold.track.Track import PlainTrack
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.tools.GeneralGuiTool import HistElement
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.SingleTSStat import SingleTSStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.CountDescriptiveStatisticBetweenHGsuiteTool import \
    CountDescriptiveStatisticBetweenHGsuiteTool
from quick.webtools.hgsuite.CountDescriptiveStatisticForHGSuiteTool import \
    CountDescriptiveStatisticForHGSuiteTool
from quick.webtools.hgsuite.Legend import Legend
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
from quick.statistic.AvgSegLenStat import AvgSegLenStat

class CountBasicStatisticForGroupsInHGsuiteTool(GeneralGuiTool, GenomeMixin, DebugMixin, UserBinMixin):
    MAX_NUM_OF_COLS_IN_GSUITE = 10
    MAX_NUM_OF_COLS = 10
    MAX_NUM_OF_STAT = 1
    PHRASE = '-- SELECT --'

    NUMTRACK = 'Number of tracks'
    NUMELEMENTS = 'Number of elements'
    BPELEMENTS = 'Base-pair coverage'
    AVGLENGTHSEG = 'Average length of segments'

    STAT_LIST_NOT_PPREPROCESSED = {
        NUMTRACK: 'NumberOfTracks',
    }
    STAT_LIST = {
        NUMELEMENTS: 'NumElements',
        BPELEMENTS: 'BpCoverage',
        AVGLENGTHSEG: 'AvgLengthSeg'
    }

    @classmethod
    def getToolName(cls):
        return "Expand hGSuite with group summary statistics"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select hGSuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
               [('Select statistic %s' % (i + 1) + '',
                 'selectedStat%s' % i) for i \
                in range(cls.MAX_NUM_OF_STAT)] + \
               [('Select group %s' % (
                   i + 1) + '',
                 'selectedColumn%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def _getOptionsBoxForSelectedStat(cls, prevChoices, index):
        if prevChoices.gsuite:
            selectionList = []
            if not any(cls.PHRASE in getattr(prevChoices, 'selectedStat%s' % i) for i in
                       xrange(index)):
                attrList = [getattr(prevChoices, 'selectedStat%s' % i) for i in xrange(index)]

                gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                if gsuite.isPreprocessed():
                    selectionList = [cls.PHRASE] + list(set(cls.STAT_LIST_NOT_PPREPROCESSED.keys() + cls.STAT_LIST.keys()) - set(attrList))
                else:
                    selectionList = [cls.PHRASE] + list(set(cls.STAT_LIST_NOT_PPREPROCESSED.keys()) - set(attrList))
            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedStatMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_STAT):
            setattr(cls, 'getOptionsBoxSelectedStat%s' % i,
                    partial(cls._getOptionsBoxForSelectedStat, index=i))

    @classmethod
    def _getOptionsBoxForSelectedColumn(cls, prevChoices, index):
        if prevChoices.gsuite:
            statList = CountDescriptiveStatisticForHGSuiteTool.getHowManyStatHaveBeenSelected(prevChoices)
            if len(statList) > 0:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                dimensions = gSuite.getCustomHeader('levels')
                selectionList = []
                if str(dimensions) == 'None':
                    if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumn%s' % i) for i in
                               xrange(index)):
                        gSuiteTNFirst = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                        selectionList += gSuiteTNFirst.attributes

                        attrList = [getattr(prevChoices, 'selectedColumn%s' % i) for i in
                                    xrange(index)]
                        selectionList = [cls.PHRASE] + list(
                            set(selectionList) - set(attrList))
                else:
                    gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                    dimensions = gSuite.getCustomHeader('levels')
                    dimensions = dimensions.split(',')
                    attrList = [getattr(prevChoices, 'selectedColumn%s' % i) for i in
                                xrange(index)]
                    selectionList = [item for item in dimensions if item not in attrList]
                    cls.MAX_NUM_OF_COLS = len(dimensions)

                if selectionList:
                    return selectionList

    @classmethod
    def setupSelectedColumnMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedColumn%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumn, index=i))



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        attrNameList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                  'selectedColumn%s',
                                                                                  cls.MAX_NUM_OF_COLS_IN_GSUITE)

        statList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                   'selectedStat%s',
                                                                                   cls.MAX_NUM_OF_STAT)
        resDict = {}
        for stat in statList:
            resDict[stat] = OrderedDict()

        #count overview
        i = 0
        for iTrack in gSuite.allTracks():
            for stat in statList:
                tupleList = []
                if len(attrNameList) == 0:
                    tupleList = tuple(iTrack.title)
                else:
                    for attrName in attrNameList:
                        at = iTrack.getAttribute(attrName)
                        if at == None:
                            at = 'No group'
                        tupleList.append(at)
                    tupleList = tuple(tupleList)

                if not tupleList in resDict[stat].keys():
                    if stat == cls.NUMTRACK:
                        resDict[stat][tupleList] = 0
                    else:
                        resDict[stat][tupleList] = []

                if stat in cls.STAT_LIST.keys():
                    regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
                    analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec,
                                                                     genome=gSuite.genome)
                    analysisSpec = AnalysisSpec(SingleTSStat)

                    if cls.NUMELEMENTS == stat:
                        analysisSpec.addParameter('rawStatistic', CountStat.__name__)

                    if cls.BPELEMENTS == stat:
                        analysisSpec.addParameter('rawStatistic', CountElementStat.__name__)

                    if cls.AVGLENGTHSEG == stat:
                        analysisSpec.addParameter('rawStatistic', AvgSegLenStat.__name__)

                    sts = SingleTrackTS(PlainTrack(iTrack.trackName),
                                        OrderedDict(title=iTrack.title, genome=str(gSuite.genome)))

                    res = doAnalysis(analysisSpec, analysisBins, sts)


                    resDict[stat][tupleList].append(res.getGlobalResult()['Result'].getResult())

                if stat == cls.NUMTRACK:
                    resDict[stat][tupleList] += 1
            i+=1

        #exclude which will now have min-max
        notToExcludeFromResults = [cls.NUMTRACK]
        deleteElements = []

        group = []
        groupTuple =[]
        resDictExtra = OrderedDict()
        for rkey, rItem in resDict.iteritems():
            if rkey in notToExcludeFromResults:
                for kTemp, elTemp in resDict[rkey].iteritems():
                    v = ''.join(list(kTemp))
                    if not v in group:
                        group.append(v)
                        groupTuple.append(kTemp)
            else:
                deleteElements.append(rkey)
                if not [rkey+'-min'] in resDictExtra.keys():
                    resDictExtra[rkey+'-min'] = OrderedDict()
                if not [rkey + '-max'] in resDictExtra.keys():
                    resDictExtra[rkey+'-max'] = OrderedDict()
                if not [rkey+'-avg'] in resDictExtra.keys():
                    resDictExtra[rkey+'-avg'] = OrderedDict()
                for kTemp, elTemp in resDict[rkey].iteritems():
                    v = ''.join(list(kTemp))
                    if not v in group:
                        group.append(v)
                        groupTuple.append(kTemp)
                    if not kTemp in resDictExtra[rkey + '-min'].keys():
                        resDictExtra[rkey + '-min'][kTemp] = min(rItem[kTemp])
                    if not kTemp in resDictExtra[rkey + '-max'].keys():
                        resDictExtra[rkey + '-max'][kTemp] = max(rItem[kTemp])
                    if not kTemp in resDictExtra[rkey + '-avg'].keys():
                        resDictExtra[rkey + '-avg'][kTemp] = sum(rItem[kTemp])/len(rItem[kTemp])

        for de in deleteElements:
            del resDict[de]

        resDictMerged = cls.mergeTwodicts(resDict, resDictExtra)

        ########################################################################
        ###################### SUMMARIZE RESULTS ###############################
        ########################################################################
        #Overview table


        cls.createGSuiteWithExtraFields(attrNameList, gSuite, resDictMerged)
        core = cls.drawPlots(group, groupTuple, resDictMerged)

        print core

    @classmethod
    def createGSuiteWithExtraFields(cls, attrNameList, gSuite, resDictMerged):

        # add column for which we counted data
        for i, iTrack in enumerate(gSuite.allTracks()):
            for s in resDictMerged.keys():
                name = s.replace('-min','').replace('-max','').replace('-avg','')
                if not name in resDictMerged.keys():
                    resDictMerged[name] = OrderedDict()
                for sName in resDictMerged[s].keys():
                    if not tuple(sName) in resDictMerged[name].keys():
                       resDictMerged[name][tuple(sName)] = ''.join(list(sName))


        # build results
        outGSuite = GSuite()
        for i, iTrack in enumerate(gSuite.allTracks()):
            trackTitle = iTrack.title
            trackPath = iTrack.uri

            attr = OrderedDict()
            for a in gSuite.attributes:
                at = iTrack.getAttribute(a)
                if at == None:
                    at = 'No group'
                attr[str(a)] = str(at)

            tupleList = []
            if len(attrNameList) == 0:
                tupleList = tuple(trackTitle)
            else:
                for attrName in attrNameList:
                    at = iTrack.getAttribute(attrName)
                    if at == None:
                        at = 'No group'
                    tupleList.append(at)
                tupleList = tuple(tupleList)
            for s in resDictMerged.keys():
                attrChange = str(s)
                if attrChange in attr.keys():
                    attrChange = attrChange + str('-') + str(len(attr.keys()))

                attr[attrChange] = str(resDictMerged[s][tupleList])

            trackType = iTrack.trackType

            cls._buildTrack(outGSuite, trackTitle, gSuite.genome, trackPath, attr, trackType)
        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['overview gSuite'])

    @classmethod
    def drawPlots(cls, group, groupTuple, resDictMerged):
        dataForPlot = []
        seriesName = []
        categoriesForPlot = []
        rdmList = []
        for rdm in resDictMerged.keys():
            k = rdm.replace('-min', '').replace('-max', '').replace('-avg', '')
            if not k in rdmList:
                rdmList.append(k)
        titleText = []

        for k in rdmList:
            if cls.NUMTRACK == k:
                seriesName.append([k])
                data = []
                for g in groupTuple:
                    if group not in categoriesForPlot:
                        categoriesForPlot.append(group)
                    data.append(resDictMerged[k][g])
                dataForPlot.append(data)
            else:
                newK = []
                newD = []
                inxK = 0
                for r in sorted(resDictMerged.keys()):
                    if k in r:
                        newK.append(r.replace(k, ''))
                        data = []
                        for g in groupTuple:
                            if inxK == 0:
                                categoriesForPlot.append(group)
                            data.append(resDictMerged[r][g])
                        newD.append(data)
                        inxK = 1
                new = zip(newK, newD)
                new.sort()
                seriesName.append([str(x[0]) for x in new])
                dataForPlot.append([x[1] for x in new])
            titleText.append(k)

        vg = visualizationGraphs()
        core = HtmlCore()
        core.begin()
        core.paragraph('Summary results')
        core.divBegin()

        newdataForPlot = []
        newseriesName = []
        for eNum, e in enumerate(dataForPlot):
            d1=[]
            d2=[]
            for dNum, d in enumerate(e):
                try:
                    int(d[0])
                    newdataForPlot.append(dataForPlot[eNum][dNum])
                    newseriesName.append(seriesName[eNum][dNum])
                except:
                    pass

        plot = vg.drawColumnCharts([newdataForPlot],
                                   height=300,
                                   categories=categoriesForPlot,
                                   seriesName=[newseriesName],
                                   xAxisRotation=90,
                                   titleText=titleText)
        core.line(plot)
        core.divEnd()
        core.end()
        return core

    @classmethod
    def depth(cls, l):
        if isinstance(l, list):
            return 1 + max(cls.depth(item) for item in l)
        else:
            return 0

    @classmethod
    def mergeTwodicts(cls, x, y):
        z = x.copy()
        z.update(y)
        return z

    @classmethod
    def _buildTrack(cls, outGSuite, trackTitle, genome, trackPath, attr, trackType):

        uri = trackPath

        gs = GSuiteTrack(uri,
                         title=''.join(trackTitle),
                         genome=genome,
                         attributes=attr,
                         trackType=trackType)

        outGSuite.addTrack(gs)

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('overview gSuite', 'gsuite')]

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.gsuite:
            return 'Select hGSuite'

        if cls.PHRASE in getattr(choices, 'selectedStat%s' % 0):
            return 'Select at least 1 measure'


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

        toolDescription = "This tool provide overview of groups such as " + cls.NUMTRACK.lower() + ", " + cls.NUMELEMENTS.lower() + ", " + cls.BPELEMENTS.lower() + ", " + cls.AVGLENGTHSEG.lower() + " in hGSuite."

        stepsToRunTool = ['Select hGSuite',
                          'Select statistic',
                          'Select group'
                          ]

        example = {'Example 1': ['', ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: hg19
        ###uri          	                                  title     T-cells B-cells   group
        hb:/path/track1.bed	track1.bed	X	.       one
        hb:/path/track2.bed	track2.bed	.	X       one
        hb:/path/track3.bed	track3.bed	.	.       two
        hb:/path/track4.bed	track4.bed	X	.       .
        hb:/path/track5.bed	track5.bed	.	.       None
            """],
                  [
                      ['Select hGSuite', 'gsuite'],
                      ['Select statistic 1', 'Number of elements in track'],
                      ['Select group', 'group'],
              ],
              ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: hg19
        ###uri          	                                  title     T-cells B-cells   group    Number of elements in track   Number of elements in track-min	Number of elements in track-max
        hb:/path/track1.bed	track1.bed	X	.       one                 one                 100	       	               200
        hb:/path/track2.bed	track2.bed	.	X       one                 one          100	       	               200
        hb:/path/track3.bed	track3.bed	.	.       two                 two           300	       	               300
        hb:/path/track4.bed	track4.bed	X	.       .                   No group           500	       	               800
        hb:/path/track5.bed	track5.bed	.	.       .                   No group           500	                	   800
        """
               ]
              ]
        }

        toolResult = 'The output of this tool is a page with visualizations and hGsuite with extra columns.'

        notice = 'Different statistic are available for different type (primary, preprocessed) of hGSuites.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example,
                                          notice=notice)

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
CountBasicStatisticForGroupsInHGsuiteTool.setupSelectedColumnMethods()
CountBasicStatisticForGroupsInHGsuiteTool.setupSelectedStatMethods()
