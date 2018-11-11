from collections import OrderedDict
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteConstants
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
from quick.webtools.hgsuite.Legend import Legend
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from gold.track.TrackStructure import SingleTrackTS, TrackStructureV2, FlatTracksTS
from functools import partial
from proto.hyperbrowser.StaticFile import StaticImage

class CountDescriptiveStatisticForHGSuiteTool(GeneralGuiTool, GenomeMixin, UserBinMixin, DebugMixin):

    MAIN_OPTIONS = ['Select one value', 'Show results for each value', 'Aggregate across this dimension']
    OPTIONS_LIST = ['sum', 'average', 'max', 'min']
    COUNT = 'Count'
    MAX_NUM_OF_COLS_IN_GSUITE = 10
    MAX_NUM_OF_COLS = 10
    MAX_NUM_OF_STAT = 1
    INFO_1 = 'You have define levels of dimensions in your hGSuite'
    INFO_2 = 'You need to define levels of dimensions in your hGSuite. Either you use the tool ... to build the hGSuite with predefined dimensions or you will specify order of levels in this tool'
    PHRASE = '-- SELECT --'

    COUNTSTAT = 'Coverage (Counts of elements)'
    NORMALIZESTAT = 'Normalize (Coverege divided by sum of coverages)'
    OBSVSEXPECTEDSTAT = 'Compare of observed coverege values vs expected coverage values'

    SUMMARIZE = {'sum': 'sum', 'average': 'average', 'minimum': 'min', 'maximum': 'max', 'no': 'no', 'raw': 'raw'}
    STAT_LIST = {NORMALIZESTAT: 'Count/SumStat', OBSVSEXPECTEDSTAT: 'ObsVsExpStat', COUNTSTAT: 'CountStat'}

    @classmethod
    def getToolName(cls):
        return "Count descriptive statistic for hGSuite"

    @classmethod
    def getInputBoxNames(cls):

        return [
                   ('Select hGSuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
               [('Select statistic ',
                 'selectedStat%s' % i) for i \
                in range(cls.MAX_NUM_OF_STAT)] + \
               [('Information', 'groupDefined')] + \
               [('Do you want to specify groups', 'groupResponse')] + \
               [('', 'preselectedGroup')] + \
               [('Select the column which define the group at level %s' % (i + 2) + '', 'selectedColumn%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               [('Do you want to have preselected presenting options', 'preselectedDecision')] + \
               [('Select main option for the group at level %s' % (i + 1) + '', 'selectedMainOption%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               [('', 'selectedOption%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               cls.getInputBoxNamesForUserBinSelection() + \
               cls.getInputBoxNamesForDebug()
               # [('Do you want to summarize results within groups', 'summarizeResponse')] + \
               # [('Select summary operation for results', 'summarize')] + \
               # [('Do you treat two groups as the same', 'question')] + \
               # [('Do you want to do above summarize data for column %s' % (
               # i + 1) + ' from hGSuite (val1,val2;val3;val4 means val1 operation val2 and val3 operation val4)',
               #    'selectedColumnOption%s' % i) for i in
               #  range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               # [('Text %s' % (i + 1) + ' from hGSuite ',
               #                                    'selectedText%s' % i) for i in
               #  range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \



    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def _getOptionsBoxForSelectedStat(cls, prevChoices, index):
        if prevChoices.gsuite:
            if not any(cls.PHRASE in getattr(prevChoices, 'selectedStat%s' % i) for i in
                       xrange(index)):

                attrList = [getattr(prevChoices, 'selectedStat%s' % i) for i in xrange(index)]
                selectionList = [cls.PHRASE] + list(set(cls.STAT_LIST.keys()) - set(attrList))

                return selectionList

    @classmethod
    def setupSelectedStatMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_STAT):
            setattr(cls, 'getOptionsBoxSelectedStat%s' % i, partial(cls._getOptionsBoxForSelectedStat, index=i))


    @classmethod
    def getOptionsBoxGroupDefined(cls, prevChoices):
        #parse GSuite and get metadata about dimensions
        #dimensions  = ['genotype']
        statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
        if len(statList) > 0:
            dimensions = []
            if len(dimensions) > 0:
                return '__rawstr__', cls.INFO_1
            else:
                return '__rawstr__', cls.INFO_2

    @classmethod
    def getOptionsBoxGroupResponse(cls, prevChoices):
        if prevChoices.gsuite:
            if prevChoices.groupDefined != cls.INFO_1:
                statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
                if len(statList) > 0:
                    return ['no', 'yes']

    @classmethod
    def getOptionsBoxPreselectedGroup(cls, prevChoices):
        return '__rawstr__', 'Important: Preselected column which define the group at level 1 is always title.'
    #coremine

    @classmethod
    def getHowManyStatHaveBeenSelected(cls, prevChoices):
        statList = []
        for i in xrange(cls.MAX_NUM_OF_STAT):
            attr = getattr(prevChoices, 'selectedStat%s' % i)
            if cls.PHRASE in [attr]:
                pass
            elif str(attr) == 'None':
                pass
            else:
                statList.append(attr)
        return statList

    @classmethod
    def getHowManyColumnHaveBeenSelected(cls, prevChoices):
        statList = []
        for i in xrange(cls.MAX_NUM_OF_COLS):
            attr = getattr(prevChoices, 'selectedColumn%s' % i)
            if cls.PHRASE in [attr]:
                pass
            elif str(attr) == 'None':
                pass
            else:
                statList.append(attr)
        return statList

    @classmethod
    def _getOptionsBoxForSelectedColumn(cls, prevChoices, index):
        if prevChoices.gsuite:
            if prevChoices.groupResponse and prevChoices.groupResponse != 'no':
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
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedColumn%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumn, index=i))

    @classmethod
    def getOptionsBoxPreselectedDecision(cls, prevChoices):
        if prevChoices.gsuite:
            statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
            if len(statList) > 0:
                return ['no', 'yes']

    @classmethod
    def _getOptionsBoxForSelectedMainOption(cls, prevChoices, index):
        if prevChoices.gsuite:
            if prevChoices.preselectedDecision and prevChoices.preselectedDecision != 'no':
                if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumn%s' % i) for i in xrange(index)):
                    return cls.MAIN_OPTIONS

    @classmethod
    def setupSelectedMainOptionMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedMainOption%s' % i,
                    partial(cls._getOptionsBoxForSelectedMainOption, index=i))

    @classmethod
    def _getOptionsBoxForSelectedOption(cls, prevChoices, index):
        if prevChoices.gsuite:
                if prevChoices.preselectedDecision and prevChoices.preselectedDecision != 'no':
                    dfTF = any(cls.PHRASE in getattr(prevChoices, 'selectedColumn%s' % i) for i in xrange(index))
                    if not dfTF:
                        attr = []
                        for i in xrange(index + 1):
                            attr.append(getattr(prevChoices, 'selectedColumn%s' % i))
                            selOption = getattr(prevChoices, 'selectedMainOption%s' % i).encode('utf-8')

                        if cls.MAIN_OPTIONS[0] == selOption:
                            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                            if index == 0:
                                return list(set(gSuite.allTrackTitles()))
                            else:
                                j = index-1
                                selectedAttribute = getattr(prevChoices, 'selectedColumn%s' % j)
                                return list(set(gSuite.getAttributeValueList(selectedAttribute)))
                        elif cls.MAIN_OPTIONS[1] == selOption:
                          pass
                        else:
                            return cls.OPTIONS_LIST

    @classmethod
    def setupSelectedOptionMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_COLS):
            setattr(cls, 'getOptionsBoxSelectedOption%s' % i,
                    partial(cls._getOptionsBoxForSelectedOption, index=i))

    # @classmethod
    # def getOptionsBoxSummarizeResponse(cls, prevChoices):
    #     if prevChoices.gsuite:
    #         if prevChoices.groupResponse and prevChoices.groupResponse != 'no':
    #             statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
    #             columnList = cls.getHowManyColumnHaveBeenSelected(prevChoices)
    #             if len(statList) > 0:
    #                 if len(columnList) > 0:
    #                     return ['no', 'yes']
    #
    # @classmethod
    # def getOptionsBoxSummarize(cls, prevChoices):
    #     if prevChoices.gsuite:
    #         if prevChoices.summarizeResponse and prevChoices.summarizeResponse != 'no':
    #             statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
    #             columnList = cls.getHowManyColumnHaveBeenSelected(prevChoices)
    #             if len(statList) > 0:
    #                 if len(columnList) > 0:
    #                     tempDict = cls.SUMMARIZE.copy()
    #                     del tempDict['no']
    #                     return tempDict.keys()
    #

    #
    # @classmethod
    # def getOptionsBoxQuestion(cls, prevChoices):
    #     if prevChoices.gsuite:
    #         if prevChoices.summarizeResponse and prevChoices.summarizeResponse != 'no':
    #             statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
    #             columnList = cls.getHowManyColumnHaveBeenSelected(prevChoices)
    #             if len(statList) > 0:
    #                 if len(columnList) > 0:
    #                     return ['no', 'yes']
    #
    # @classmethod
    # def _getOptionsBoxForSelectedColumnOption(cls, prevChoices, index):
    #     if prevChoices.gsuite:
    #         if prevChoices.question and prevChoices.question != 'no':
    #             if prevChoices.summarize and prevChoices.summarize != 'no':
    #                 attr = []
    #                 for i in xrange(index + 1):
    #                     attr.append(getattr(prevChoices, 'selectedColumn%s' % i))
    #
    #                 if cls.PHRASE in attr or None in attr:
    #                     pass
    #                 else:
    #                     return ''
    #
    # @classmethod
    # def setupSelectedColumnOptionMethods(cls):
    #     from functools import partial
    #     for i in xrange(cls.MAX_NUM_OF_COLS):
    #         setattr(cls, 'getOptionsBoxSelectedColumnOption%s' % i, partial(cls._getOptionsBoxForSelectedColumnOption, index=i))
    #
    # @classmethod
    # def _getOptionsBoxForSelectedText(cls, prevChoices, index):
    #     if prevChoices.gsuite:
    #         if prevChoices.question and prevChoices.question != 'no':
    #             if prevChoices.summarize and prevChoices.summarize != 'no':
    #                 attr = []
    #                 inx = index
    #                 for i in xrange(index+1):
    #                     a = getattr(prevChoices, 'selectedColumn%s' % i)
    #                     if a != None:
    #                         attr.append(a)
    #
    #
    #                 if cls.PHRASE in attr or None in attr:
    #                     pass
    #                 else:
    #                     if prevChoices.gsuite:
    #                         gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
    #                         return [list(set(gsuite.getAttributeValueList(attr[-1])))]
    #
    #
    #
    # @classmethod
    # def setupSelectedTextMethods(cls):
    #     from functools import partial
    #     for i in xrange(cls.MAX_NUM_OF_COLS):
    #         setattr(cls, 'getOptionsBoxSelectedText%s' % i,
    #                 partial(cls._getOptionsBoxForSelectedText, index=i))

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        groupResponse = choices.groupResponse.encode('utf-8')
        preselectedDecision = choices.preselectedDecision.encode('utf-8')
        #summarize = choices.summarize.encode('utf-8')
        #summarizeResponse = choices.summarizeResponse.encode('utf-8')
        #it need to be covered by javascript now
        summarizeResponse = 'no'
        summarize = 'no'

        if preselectedDecision != 'no':
            mainOptionList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices, 'selectedMainOption%s', cls.MAX_NUM_OF_COLS_IN_GSUITE)
            optionList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices, 'selectedOption%s', cls.MAX_NUM_OF_COLS_IN_GSUITE)
            newOptionList = []
            for mNum, m in enumerate(mainOptionList):
                if m == cls.MAIN_OPTIONS[1]:
                    newOptionList.append('')
                else:
                    newOptionList.append(optionList[mNum])
            optionList = newOptionList
        else:
            mainOptionList = []
            optionList = []

        # print mainOptionList, '<br>'
        # print optionList, '<br>'

        colList = []
        if groupResponse != 'no':
            summarize = 'raw'
            colList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                      'selectedColumn%s',
                                                                                      cls.MAX_NUM_OF_COLS_IN_GSUITE)
            columnOptionsDict = {}

        # if summarize != 'no':
        #     colList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices, 'selectedColumn%s', cls.MAX_NUM_OF_COLS_IN_GSUITE)
        #     columnOptionsDict = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedColumnOptions(choices, 'selectedColumnOption%s',cls.MAX_NUM_OF_COLS_IN_GSUITE, colList)
        # else:
        #     colList = []
        #     columnOptionsDict = {}

        # print 'colList', colList, '<br>'
        # print 'columnOptionsDict', columnOptionsDict, '<br>'

        #asked Sveinung for help
        #regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        regSpec, binSpec = "__chrs__", "*"
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=gSuite.genome)
        statList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices, 'selectedStat%s', cls.MAX_NUM_OF_STAT)
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

                #if cls.SUMMARIZE[summarize] != 'no':
                groupKey = CountDescriptiveStatisticBetweenHGsuiteTool.changeOptions(columnOptionsDict, groupKey)

                #print '-groupKey-', groupKey, '<br>'
                if not groupKey in resultsDict[stat][cls.SUMMARIZE[summarize]].keys():
                    resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey] = []

                for gi in groupItem:

                    res = doAnalysis(sa, analysisBins, gi)
                    countPerTrack = res.getGlobalResult()['Result'].getResult()

                    if stat == cls.NORMALIZESTAT or stat == cls.OBSVSEXPECTEDSTAT:
                        sumBp[stat] += countPerTrack

                    #remove the opeation which happens before
                    # if cls.SUMMARIZE[summarize] == 'no':
                    #     resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey].append([gi.metadata['title'], gi.metadata['title'], countPerTrack])
                    # else:
                        #resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey].append(countPerTrack)
                    if cls.SUMMARIZE[summarize] == 'raw':
                        resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey].append([gi.metadata['title'], countPerTrack])


        #print 'resultsDict',resultsDict, '<br>'
        # print 'colList', colList, '<br>'
        # print 'summarize', summarize, '<br>'
        # print 'sumBp', sumBp, '<br>'

        extraJavaScriptCode = """
                $(document).ready(function(){
                    init();
                }) 
                """

        htmlCore = HtmlCore()
        htmlCore.begin(extraCssFns=['hb_base.css', 'hgsuite.css'], extraJavaScriptCode=extraJavaScriptCode)

        htmlCore.bigHeader('Results for descriptive statistic between hGSuite')
        htmlCore.header('Description')
        htmlCore.paragraph(
            'You can see results in two ways: table with results and plot. ')
        htmlCore.header('Interpretation of results')
        htmlCore.paragraph('Click on the following options for selected statistic to see detailed results. ')

        cls.writeResults(galaxyFn, resultsDict, htmlCore, colList, [], summarize, sumBp, mainOptionList, optionList)
        htmlCore.end()
        print htmlCore

    @classmethod
    def writeResults(cls, galaxyFn, resultsDict, htmlCore, firstColumnList, secondColumnList, summarize, sumBp, mainOptionList, optionList):

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
                            expectedDict[g] += float(sum(groupItem))/float(sumBp[statKey])


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
                    elif summarizeKey == 'raw':
                        cls.countSummarize(data, expectedOrderedDict, groupItem, groupKey, statKey,
                                           sumBp, summarizeKey)
                    else:
                        cls.countSummarize(data, expectedOrderedDict, groupItem, groupKey, statKey,
                                           sumBp, summarizeKey)


            if summarizeKey == 'no':
                header = ['Column 1', 'Column 2', 'Value']
                #dataToPresent, headerToPresent = CountDescriptiveStatisticBetweenHGsuiteTool.flatResults(header, data)
                dp = zip(*data)
            elif summarizeKey == 'raw':
                header = ['Title'] + firstColumnList + secondColumnList + [summarizeKey]
                dataToPresent = data
                #print 'dataToPresent', dataToPresent
                # headerToPresent = header
                dp = zip(*dataToPresent)
            else:
                header = firstColumnList + secondColumnList + [summarizeKey]
                dataToPresent = data
                #headerToPresent = header
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
            i=0
            for d in data:
                if i ==0:
                    wf.write('\t'.join([str('attribute')+str(dd) for dd in range(0, len(d)+1)]) + '\n')
                wf.write('-'.join([str(d[dd]) for dd in range(0, len(d)-1)]) + '\t' + '\t'.join([str(dd) for dd in d]) + '\n')
                i+=1

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

            htmlCore.divBegin(divId='resultsDesc-' + str(statKey), divClass='visible')
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
                cube.addSelectList(header[:len(header) - 1], optionData, data, divId, statNum, mainOptionList, optionList, option = 'raw'))
            htmlCore.divEnd()
            htmlCore.divEnd()

            statNum += 1

    @classmethod
    def countSummarize(cls, data, expectedOrderedDict, groupItem, groupKey, statKey, sumBp,
                       summarizeKey):

        if statKey == cls.OBSVSEXPECTEDSTAT:
            if summarizeKey == 'sum':
                data.append(list(groupKey) + [
                    (float(sum(groupItem)) / sumBp[statKey]) / expectedOrderedDict[groupKey]])
            elif summarizeKey == 'average':
                data.append(list(groupKey) + [
                    (float(sum(groupItem) / len(groupItem)) / sumBp[statKey]) /
                    expectedOrderedDict[groupKey]])
            elif summarizeKey == 'min':
                data.append(list(groupKey) + [
                    (float(min(groupItem)) / sumBp[statKey]) / expectedOrderedDict[groupKey]])
            elif summarizeKey == 'max':
                data.append(list(groupKey) + [
                    (float(max(groupItem)) / sumBp[statKey]) / expectedOrderedDict[groupKey]])
            elif summarizeKey == 'raw': #double check it
                for g in groupItem:
                    data.append(list(groupKey) + (float(g) / sumBp[statKey]) / expectedOrderedDict[groupKey])
        else:
            if summarizeKey == 'sum':
                data.append(list(groupKey) + [(float(sum(groupItem)) / sumBp[statKey])])
            elif summarizeKey == 'average':
                data.append(
                    list(groupKey) + [(float(sum(groupItem) / len(groupItem)) / sumBp[statKey])])
            elif summarizeKey == 'min':
                data.append(list(groupKey) + [(float(min(groupItem)) / sumBp[statKey])])
            elif summarizeKey == 'max':
                data.append(list(groupKey) + [(float(max(groupItem)) / sumBp[statKey])])
            elif summarizeKey == 'raw':
                for g in groupItem:
                    data.append(list(groupKey) + g)

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

        if not choices.gsuite:
            return 'Select hGSuite'

        if choices.gsuite:
            gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
            if not gsuite.isPreprocessed():
                return 'hGSuite need to preprocessed.'

        # if cls.PHRASE in getattr(choices, 'selectedStat%s' % 0):
        #     return 'Select statistic'



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

        toolDescription = "This tool count descriptive statistics for hGSuite."

        stepsToRunTool = ['Select first hGSuite',
                          'Select statistic',
                          'Summarize within groups (no, sum, minimum, maximum, average)',
                          'Select column which you would like to group',
                          'Do you want to do above summarize data for column from hGSuite'
                          ]

        urlexample1Output = StaticImage(['hgsuite', 'img',
                                      'CountDescriptiveStatisticForHGSuiteTool-img1.png']).getURL()
        urlexample2Output = StaticImage(['hgsuite', 'img',
                                      'CountDescriptiveStatisticForHGSuiteTool-img2.png']).getURL()

        urlexample3Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticForHGSuiteTool-img3.png']).getURL()
        urlexample4Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticForHGSuiteTool-img4.png']).getURL()

        urlexample5Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticForHGSuiteTool-img5.png']).getURL()
        urlexample6Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticForHGSuiteTool-img6.png']).getURL()


        example = OrderedDict({'Example 1 - summarize within groups: no': ['', ["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title     genotype
    hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	eta
    hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	eta
    hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	iota
    hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	iota
                """],
                 [
                     ['Select hGSuite', 'gsuite'],
                     ['Select statistic 1', 'Coverage'],
                     ['Summarize within groups', 'no'],
                 ],
                 [
                 '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample1Output + '" /><img  style="margin-right:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:right;padding-left:0px;" width="300" src="' + urlexample2Output + '" /></div>'
                  ]
                ]
                   ,'Example 2 - summarize within groups: maximum': ['', ["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title     mutation    genotype
    hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	CA  eta
    hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	GT	eta
    hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	CG	iota
    hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	GC	iota
    hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	CA	iota
    hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track6.bed	GT	iota
              """],
                                         [
                                             ['Select hGSuite', 'gsuite'],
                                             ['Select statistic 1','Coverage'],
                                             ['Summarize within groups', 'maximum'],
                                             ['Select group 1', 'genotype']
                                         ],
                                         [
                                             '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample3Output + '" /><img  style="margin-right:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:right;padding-left:0px;" width="300" src="' + urlexample4Output + '" /></div>']
                                         ]
            , 'Example 3 - summarize within groups: sum': ['', ["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title     mutation    genotype
    hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	CA  eta
    hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	GT	eta
    hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	CG	iota
    hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	GC	iota
    hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	CA	iota
    hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track6.bed	GT	iota
               """],
                 [
                     ['Select hGSuite', 'gsuite'],
                     ['Select statistic 1','Coverage'],
                     ['Summarize within groups','sum'],
                     ['Select group 1','genotype'],
                     ['Select group 2', 'mutation'],
                     ['Do you want summarize data within group 1 from hGSuite ', ''],
                     ['Do you want summarize data within group 2 from hGSuite ', 'CA,GT;CG,GC;'],
                 ],
                 [
                     '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample5Output + '" /><img  style="margin-right:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:right;padding-left:0px;" width="300" src="' + urlexample6Output + '" /></div>']
                 ]

                   })

        toolResult = '<p>The output of this tool is a page with visualizations. </p>' \
                     'Detailed information about results. You can <b>download raw file</b> with results <br>' \
                     '<b>Options for presenting results:</b> <br>' \
                     '- Transpose tables and plots - transpose table and plots <br>' \
                     '- Show all series as one in the plots - show all data as one series <br>' \
                     "- Remove zeros from plots - remove value 0 from plots"




        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example)


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
    def getInputBoxOrder(cls):

        data = ['selectedText%s' % i for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)]
        #dataText = ['selectedColumnOption%s' % i for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)]

        mainOption = ['selectedMainOption%s' % i for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)]
        option = ['selectedOption%s' % i for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)]
        optionFlatList = [item for sublist in zip(mainOption, option) for item in sublist]

        #flat_list = [item for sublist in zip(data, dataText) for item in sublist]

        bins = [x[1] for x in cls.getInputBoxNamesForUserBinSelection()]

        return ['gsuite'] + \
               ['selectedStat%s' % i for i in range(cls.MAX_NUM_OF_STAT)] + \
               ['preselectedGroup'] + \
               ['groupResponse'] + \
               ['groupDefined'] + \
               ['selectedColumn%s' % i for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + ['preselectedDecision'] + optionFlatList
               # ['summarizeResponse', 'summarize', 'question'] + flat_list #+ bins



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

CountDescriptiveStatisticForHGSuiteTool.setupSelectedStatMethods()
CountDescriptiveStatisticForHGSuiteTool.setupSelectedColumnMethods()
CountDescriptiveStatisticForHGSuiteTool.setupSelectedMainOptionMethods()
CountDescriptiveStatisticForHGSuiteTool.setupSelectedOptionMethods()
#CountDescriptiveStatisticForHGSuiteTool.setupSelectedColumnOptionMethods()
#CountDescriptiveStatisticForHGSuiteTool.setupSelectedTextMethods()