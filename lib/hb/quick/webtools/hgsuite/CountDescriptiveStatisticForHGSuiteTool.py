from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.statistic.CountStat import CountStat
from gold.track.Track import PlainTrack
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.SingleTSStat import SingleTSStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.CountDescriptiveStatisticBetweenHGsuiteTool import \
    CountDescriptiveStatisticBetweenHGsuiteTool
from quick.webtools.hgsuite.CountDescriptiveStatisticJS import Cube
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from gold.track.TrackStructure import SingleTrackTS, TrackStructureV2, FlatTracksTS

class CountDescriptiveStatisticForHGSuiteTool(GeneralGuiTool, GenomeMixin, UserBinMixin, DebugMixin):

    COUNT = 'Count'
    MAX_NUM_OF_COLS_IN_GSUITE = 10
    MAX_NUM_OF_COLS = 10
    PHRASE = '-- SELECT --'

    COUNTSTAT = 'Count (bps)'
    NORMALIZESTAT = 'Normalize (bps)'
    OBSVSEXPECTEDSTAT = 'Observed/expected'

    SUMMARIZE = {'no': 'no', 'sum': 'sum', 'average': 'avg', 'minimum': 'min', 'maximum': 'max'}
    STAT_LIST = {COUNTSTAT: 'CountStat', NORMALIZESTAT: 'Count/SumStat', OBSVSEXPECTEDSTAT: 'ObsVsExpStat'}

    @classmethod
    def getToolName(cls):
        return "Count descriptive statistic for hGSuite"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select gSuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
               [('Select statistic %s' % (i + 1) + '',
                 'selectedStat%s' % i) for i \
                in range(cls.MAX_NUM_OF_COLS)] + \
               [('Summarize within groups', 'summarize')] + \
               [('Select column %s' % (
               i + 1) + ' which you would like to group',
                 'selectedColumn%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               [('Do you want to do above summarize data for column %s' % (
               i + 1) + ' from gSuite ',
                 'selectedColumnOption%s' % i) for i in
                range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
                cls.getInputBoxNamesForUserBinSelection() + \
                cls.getInputBoxNamesForDebug()

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
                selectionList = [cls.PHRASE] + list(set(cls.STAT_LIST.keys()) - set(attrList))
            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedStatMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedStat%s' % i,
                    partial(cls._getOptionsBoxForSelectedStat, index=i))

    @classmethod
    def getOptionsBoxSummarize(cls, prevChoices):
        if prevChoices.gsuite:
            return cls.SUMMARIZE.keys()

    @classmethod
    def _getOptionsBoxForSelectedColumn(cls, prevChoices, index):
        if prevChoices.gsuite:
            selectionList = []

            if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumn%s' % i) for i in
                       xrange(index)):
                gSuiteTNFirst = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                selectionList += gSuiteTNFirst.attributes

                attrList = [getattr(prevChoices, 'selectedColumn%s' % i) for i in
                            xrange(index)]
                selectionList = [cls.PHRASE] + list(
                    set(selectionList) - set(attrList))

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedColumnMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedColumn%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumn, index=i))

    @classmethod
    def _getOptionsBoxForSelectedColumnOption(cls, prevChoices, index):
        if prevChoices.gsuite and prevChoices.summarize != 'no':
            selectionList = []

            if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumn%s' % i) for i in
                       xrange(index)):
                selectionList = ''

                return selectionList

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectedColumnOptionMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedColumnOption%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumnOption, index=i))


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        summarize = choices.summarize.encode('utf-8')

        if summarize != 'no':
            colList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices, 'selectedColumn%s', cls.MAX_NUM_OF_COLS_IN_GSUITE)
            columnOptionsDict = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedColumnOptions(choices, 'selectedColumnOption%s',cls.MAX_NUM_OF_COLS_IN_GSUITE, colList)

        else:
            colList = []
            columnOptionsDict = {}

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec,
                                                         genome=gSuite.genome)

        statList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices, 'selectedStat%s', cls.MAX_NUM_OF_COLS)
        selectedAnalysis = cls.addStat(choices, statList)

        gsuiteOutput = CountDescriptiveStatisticBetweenHGsuiteTool._getAttributes(gSuite, colList)

        whichGroups = cls.createGroups(gSuite, colList, gsuiteOutput)

        resultsDict = OrderedDict()

        sumBp = OrderedDict()
        for saNum, sa in enumerate(selectedAnalysis):
            stat = statList[saNum]
            if not stat in resultsDict.keys():
                resultsDict[stat] = OrderedDict()
            if not cls.SUMMARIZE[summarize] in resultsDict[stat].keys():
                resultsDict[stat][cls.SUMMARIZE[summarize]] = OrderedDict()

            if not stat in sumBp.keys():
                sumBp[stat] = 0
            for groupKey, groupItem in whichGroups.iteritems():

                if cls.SUMMARIZE[summarize] != 'no':
                    groupKey = CountDescriptiveStatisticBetweenHGsuiteTool.changeOptions(columnOptionsDict, groupKey)

                if not groupKey in resultsDict[stat][cls.SUMMARIZE[summarize]].keys():
                    resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey] = []

                for gi in groupItem:

                    res = doAnalysis(sa, analysisBins, gi)
                    countPerTrack = res.getGlobalResult()['Result'].getResult()

                    if stat == cls.NORMALIZESTAT or stat == cls.OBSVSEXPECTEDSTAT:
                        sumBp[stat] += countPerTrack

                    if cls.SUMMARIZE[choices.summarize] == 'no':
                        resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey].append([gi.metadata['title'], gi.metadata['title'], countPerTrack])
                    else:
                        resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey].append(countPerTrack)



        htmlCore = HtmlCore()
        htmlCore.begin(extraCssFns=['hb_base.css', 'hgsuite.css'])

        htmlCore.bigHeader('Results for descriptive statistic between hGSuite')
        htmlCore.header('Description')
        htmlCore.paragraph(
            'You can see results in two ways: table and plot... Click on the following table to see results for statistics. ')
        htmlCore.header('Interpretation of results')
        htmlCore.paragraph('Click here to see how to ...')

        cls.writeResults(galaxyFn, resultsDict, htmlCore, colList, [], summarize, sumBp)
        htmlCore.end()
        print htmlCore

    @classmethod
    def writeResults(cls, galaxyFn, resultsDict, htmlCore, firstColumnList, secondColumnList, summarize, sumBp):

        cube = Cube()
        statNum = 0

        expectedDict = OrderedDict()
        expectedOrderedDict = OrderedDict()
        for statKey, statItem in resultsDict.iteritems():

            if sumBp[statKey] == 0:
                sumBp[statKey] = 1

            if statKey == cls.OBSVSEXPECTEDSTAT:
                for summarizeKey, summarizeItem in statItem.iteritems():
                    for groupKey, groupItem in summarizeItem.iteritems():
                        for g in groupKey:
                            if not g in expectedDict.keys():
                                expectedDict[g] = 0
                            expectedDict[g] += float(eval('sum' + "(" + str(groupItem) + ")"))/sumBp[statKey]


                for summarizeKey, summarizeItem in statItem.iteritems():
                    for groupKey, groupItem in summarizeItem.iteritems():
                        for g in groupKey:
                            if not groupKey in expectedOrderedDict.keys():
                                expectedOrderedDict[groupKey] = 1
                            expectedOrderedDict[groupKey] *= expectedDict[g]

            data = []
            for summarizeKey, summarizeItem in statItem.iteritems():
                # print 'summarizeKey', summarizeKey
                # print 'summarizeItem', summarizeItem

                for groupKey, groupItem in summarizeItem.iteritems():
                    # print 'groupKey', list(groupKey)
                    # print 'groupItem', groupItem

                    if summarizeKey == 'no':
                        data += groupItem
                    else:
                        if statKey == cls.OBSVSEXPECTEDSTAT:
                            data.append(
                                list(groupKey) + [
                                    (float(eval(summarizeKey + "(" + str(groupItem) + ")")) / sumBp[
                                        statKey]) / expectedOrderedDict[groupKey]
                            ])
                        else:
                            data.append(
                                list(groupKey) + [
                                    (float(eval(summarizeKey + "(" + str(groupItem) + ")"))/sumBp[statKey])
                            ])


            if summarizeKey == 'no':
                header = ['Column 1', 'Column 2', 'Value']
                dataToPresent, headerToPresent = CountDescriptiveStatisticBetweenHGsuiteTool.flatResults(header, data)
                dp = zip(*data)
            else:
                header = firstColumnList + secondColumnList + [summarizeKey]
                dataToPresent = data
                headerToPresent = header
                dp = zip(*dataToPresent)

            optionData = []
            for z in range(0, len(dp) - 1):
                pl = []
                for d in dp[z]:
                    if not d in pl:
                        pl.append(d)
                optionData.append(pl)

            statKeyOrginal = str(statKey)
            statKey = statKey.replace(' ', '').replace('(', '').replace(')', '').replace('/', '')

            # sth is wrong with url to file!
            fileStat = GalaxyRunSpecificFile([statKey + '.tabular'], galaxyFn)
            fileStatPath = fileStat.getDiskPath(ensurePath=True)
            wf = open(fileStatPath, 'w')
            for d in data:
                wf.write('\t'.join([str(dd) for dd in d]) + '\n')

            divId = 'results' + str(statKey)

            jsCode = """
                        <script>
                        $(document).ready(function(){
                            $('#""" + 'showDetailed-' + str(statKey) + """').click(function (){
                                var el = $('#""" + 'detailed-' + str(statKey) + """');
                                if (el.attr('class') == "hidden") {
                                    el.removeClass("hidden").addClass("visible");
                                } else {
                                    el.removeClass("visible").addClass("hidden");
                                }
                                //console.log('el', el.attr('class'));
                            });
                            $('#""" + 'resultsHeader-' + str(statKey) + """').click(function ()
                            {
                                var children = $('#""" + 'results' + str(statKey) + """').children();
                                for (i = 0; i < children.length; i++)
                                {
                                  var el = children[i];
                                  if (el  == 'undefined')
                                  {
                                  }
                                  else
                                  {
                                      if (el.tagName == 'DIV' && el.id != 'resultsHeader-""" + str(statKey) + """')
                                      {
                                          if ($(el).attr('class') == "hidden") 
                                          {
                                            $(el).removeClass("hidden").addClass("visible");
                                          } 
                                          else 
                                          {
                                            $(el).removeClass("visible").addClass("hidden");
                                          }
                                      }
                                  }
                                }
                                
                            });
                        });
                        </script>
                        """

            htmlCore.divBegin(divId, 'resultsAll')
            htmlCore.line(jsCode)

            htmlCore.divBegin(divId='resultsHeader-' + str(statKey), divClass='resultsHeader')
            htmlCore.header('Results for: ' + str(statKeyOrginal))
            htmlCore.divEnd()

            htmlCore.divBegin(divId='resultsDesc-' + str(statKey), divClass='hidden')
            htmlCore.divBegin(divClass='resultsDescription')
            htmlCore.divBegin(divId='showDetailed-' + str(statKey), divClass='showDetailed')
            htmlCore.header('Detailed information about results')
            htmlCore.divEnd()
            htmlCore.divBegin(divId='detailed-' + str(statKey), divClass='hidden')
            htmlCore.divBegin(divClass='detailed')
            htmlCore.link('Download raw file: ' + statKey, fileStat.getURL())
            htmlCore.divEnd()
            htmlCore.divEnd()
            htmlCore.divEnd()
            htmlCore.line(
                cube.addSelectList(header[:len(header) - 1], optionData, data, divId, statNum))
            htmlCore.divEnd()
            htmlCore.divEnd()

            statNum += 1

    @classmethod
    def addStat(cls, choices, statList):
        selectedAnalysis = []
        for a in statList:
            if cls.STAT_LIST[a] == 'CountStat' or cls.STAT_LIST[a] == 'Count/SumStat' or cls.STAT_LIST[a] == 'ObsVsExpStat':
                analysisSpec = AnalysisSpec(SingleTSStat)
                analysisSpec.addParameter('rawStatistic', CountStat.__name__)
                selectedAnalysis.append(analysisSpec)
        return selectedAnalysis

    @classmethod
    def createGroups(cls, gSuite, colList, gsuiteOutput):

        whichGroups = OrderedDict()
        for wg in CountDescriptiveStatisticBetweenHGsuiteTool._getCombinations(gsuiteOutput, []):
            whichGroups[wg] = []

        for iTrackFromFirst, track in enumerate(gSuite.allTracks()):
            attrTuple = []
            CountDescriptiveStatisticBetweenHGsuiteTool.buildAttrTuple(attrTuple, colList, track)
            attrTuple = tuple(attrTuple)

            sts = SingleTrackTS(PlainTrack(track.trackName),
                          OrderedDict(title=track.title, genome=str(gSuite.genome)))
            whichGroups[attrTuple].append(sts)
        return whichGroups

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

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

CountDescriptiveStatisticForHGSuiteTool.setupSelectedColumnMethods()
CountDescriptiveStatisticForHGSuiteTool.setupSelectedStatMethods()
CountDescriptiveStatisticForHGSuiteTool.setupSelectedColumnOptionMethods()