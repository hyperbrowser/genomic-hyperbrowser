from collections import OrderedDict, defaultdict

import itertools
from functools import partial

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteConstants
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.track.Track import PlainTrack
from proto.hyperbrowser.StaticFile import StaticImage
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.PairedTSStat import PairedTSStat
from quick.statistic.RawOverlapAllowSingleTrackOverlapsStat import \
    RawOverlapAllowSingleTrackOverlapsStat
from gold.track.TrackStructure import SingleTrackTS, TrackStructureV2, FlatTracksTS
from quick.statistic.StatFacades import ObservedVsExpectedStat
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import \
    SummarizedInteractionWithOtherTracksV2Stat
from quick.util import TrackReportCommon
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.CountDescriptiveStatisticJS import Cube
from quick.webtools.hgsuite.Legend import Legend
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS, processResult


class CountDescriptiveStatisticBetweenHGsuiteTool(GeneralGuiTool, GenomeMixin, UserBinMixin,
                                                  DebugMixin):
    MAIN_OPTIONS = ['Select one value', 'Show results for each value',
                    'Aggregate across this dimension']
    OPTIONS_LIST = ['sum', 'average', 'max', 'min']
    MAX_NUM_OF_COLS = 15
    MAX_NUM_OF_COLS_IN_GSUITE = 2
    MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED=MAX_NUM_OF_COLS_IN_GSUITE+2
    MERGED_SIGN = ' - '
    PHRASE = '-- SELECT --'
    STAT_LIST = {'Overlap': STAT_OVERLAP_COUNT_BPS, 'Forbes coefficient': 'Forbes coefficient'}
    FIRST_GSUITE = 'First GSuite'
    SECOND_GSUITE = 'Second GSuite'
    SUMMARIZE = {'no': 'no', 'sum': 'sum', 'average': 'avg', 'minimum': 'min', 'maximum': 'max', 'raw': 'raw'}
    TITLE = 'title'
    INFO_ALL = ''
    MAX_NUM_OF_STAT = 1
    INFO_1 = 'You have define levels of dimensions in your hGSuite so by defualt your groups and their hierarchy is specified.'
    INFO_2 = "You can define levels of dimensions in your hGSuite. Either you use the tool: 'Create hierarchy of GSuite' to build the hGSuite with predefined dimensions or you will specify order of levels in this tool"
    INFO_3 = "Information: There is always one preselected column. It defines group at the first level and it is represented by track's orginaltitle, if you do not have it then it is take column title."

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'

    @classmethod
    def getToolName(cls):
        return "Compute Pivot table for relations between hGSuites"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select first hGSuite', 'gsuite')] + \
               cls.getInputBoxNamesForGenomeSelection() + \
               [('Select column from first hGSuite', 'firstGSuiteColumn'),
                ('Select second hGSuite', 'secondGSuite'),
                ('Select column from second hGSuite', 'secondGSuiteColumn')] + \
               [('Select statistic %s' % (i + 1) + '', 'selectedStat%s' % i) for i in range(cls.MAX_NUM_OF_STAT)] + \
               [('Select overlap handling', 'intraOverlap')] + \
               [('Information', 'groupDefined')] + \
               [('Do you want to specify groups', 'groupResponse')] + \
               [('', 'preselectedGroup')] + \
               [('Select the column for first hGSuite which define the group at level %s' % (i + 2) + '',
                 'selectedColumnFirst%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)] + \
               [('Select the column for second hGSuite which define the group at level %s' % (i + 2) + '',
                 'selectedColumnSecond%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)] + \
               [('Do you want to have preselected presenting options for first hGSuite', 'preselectedDecision')] + \
               [('Select main option for first hGSuite for the group at level %s' % (i + 1) + '',
                 'selectedMainOptionFirst%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)] + \
               [('', 'selectedOptionFirst%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)] + \
               [('Select main option for second hGSuite for the group at level %s' % (i + 1) + '',
                 'selectedMainOptionSecond%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)] + \
               [('', 'selectedOptionSecond%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)] + \
               cls.getInputBoxNamesForUserBinSelection()
               # [('Summarize within groups', 'summarize')] + \
               # [('Select column from first hGSuite %s' % (
               # i + 1) + ' which you would like to treat as unique',
               #   'selectedFirstColumn%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               # [('Do you want to do above summarize data for column %s' % (
               # i + 1) + ' from first hGSuite ',
               #   'selectedFirstColumnOption%s' % i) for i in
               #  range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               # [('Select column from second hGSuite %s' % (
               # i + 1) + ' which you would like to treat as unique',
               #   'selectedSecondColumn%s' % i) for i in range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               # [('Do you want to do above summarize for column %s' % (
               # i + 1) + ' from second hGSuite ',
               #   'selectedSecondColumnOption%s' % i) for i in
               #  range(cls.MAX_NUM_OF_COLS_IN_GSUITE)] + \
               # cls.getInputBoxNamesForDebug()

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxFirstGSuiteColumn(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.gsuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return ['None'] + [cls.TITLE] + gSuiteTN.attributes

    @classmethod
    def getOptionsBoxSecondGSuite(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxSecondGSuiteColumn(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.secondGSuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
            return ['None'] + [cls.TITLE] + gSuiteTN.attributes

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
            setattr(cls, 'getOptionsBoxSelectedStat%s' % i,
                    partial(cls._getOptionsBoxForSelectedStat, index=i))

    @classmethod
    def getOptionsBoxIntraOverlap(cls, prevChoices):
        statList = cls._getSelectedOptions(prevChoices, 'selectedStat%s', cls.MAX_NUM_OF_STAT)
        for a in statList:
            if cls.STAT_LIST[a] == STAT_OVERLAP_COUNT_BPS:
                return [cls.MERGE_INTRA_OVERLAPS,
                        cls.ALLOW_MULTIPLE_OVERLAP]

    @classmethod
    def getOptionsBoxGroupDefined(cls, prevChoices):
        # parse GSuite and get metadata about dimensions
        statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
        if len(statList) > 0:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            dimensions = gSuite.getCustomHeader('levels')
            if str(dimensions) != 'None':
                cls.INFO_ALL = cls.INFO_1
                return '__rawstr__', cls.INFO_1
            else:
                cls.INFO_ALL = cls.INFO_2
                return '__rawstr__', cls.INFO_2

    @classmethod
    def getOptionsBoxGroupResponse(cls, prevChoices):
        if prevChoices.gsuite:
            if cls.INFO_ALL != cls.INFO_1:
                statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
                if len(statList) > 0:
                    return ['no', 'yes']

    @classmethod
    def getOptionsBoxPreselectedGroup(cls, prevChoices):
        return '__rawstr__', cls.INFO_3

    # coremine

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
    def _getOptionsBoxForSelectedColumnFirst(cls, prevChoices, index):
        if prevChoices.gsuite:
            selectionList = []
            statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
            if len(statList) > 0:
                if prevChoices.groupResponse:
                    if prevChoices.groupResponse != 'no':
                        if not any(cls.PHRASE in getattr(prevChoices,
                                                         'selectedColumnFirst%s' % i) for i in
                                   xrange(index)):
                            gSuiteTNFirst = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                            selectionList += gSuiteTNFirst.attributes

                            attrList = [getattr(prevChoices, 'selectedColumnFirst%s' % i) for i
                                        in
                                        xrange(index)]
                            selectionList = [cls.PHRASE] + list(
                                set(selectionList) - set(attrList))

                        if selectionList:
                            return selectionList
                else:
                    gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                    dimensions = gSuite.getCustomHeader('levels')
                    dimensions = dimensions.split(',')
                    attrList = [getattr(prevChoices, 'selectedColumnFirst%s' % i) for i in
                                xrange(index)]
                    selectionList = [item for item in dimensions if item not in attrList]
                    cls.MAX_NUM_OF_COLS = len(dimensions)
                    if selectionList:
                        return selectionList

    @classmethod
    def setupSelectedColumnMethodsFirst(cls):
        for i in xrange(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED):
            setattr(cls, 'getOptionsBoxSelectedColumnFirst%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumnFirst, index=i))

    @classmethod
    def _getOptionsBoxForSelectedColumnSecond(cls, prevChoices, index):
        if prevChoices.secondGSuite:
            selectionList = []
            statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
            if len(statList) > 0:
                if prevChoices.groupResponse:
                    if prevChoices.groupResponse != 'no':
                        if not any(cls.PHRASE in getattr(prevChoices,
                                                         'selectedColumnSecond%s' % i) for i in
                                   xrange(index)):
                            gSuiteTNFirst = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
                            selectionList += gSuiteTNFirst.attributes

                            attrList = [getattr(prevChoices, 'selectedColumnSecond%s' % i) for i
                                        in
                                        xrange(index)]
                            selectionList = [cls.PHRASE] + list(
                                set(selectionList) - set(attrList))

                        if selectionList:
                            return selectionList
                else:
                    gSuite = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
                    dimensions = gSuite.getCustomHeader('levels')
                    dimensions = dimensions.split(',')
                    attrList = [getattr(prevChoices, 'selectedColumnSecond%s' % i) for i in
                                xrange(index)]
                    selectionList = [item for item in dimensions if item not in attrList]
                    cls.MAX_NUM_OF_COLS = len(dimensions)
                    if selectionList:
                        return selectionList

    @classmethod
    def setupSelectedColumnMethodsSecond(cls):
        for i in xrange(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED):
            setattr(cls, 'getOptionsBoxSelectedColumnSecond%s' % i,
                    partial(cls._getOptionsBoxForSelectedColumnSecond, index=i))

    @classmethod
    def getOptionsBoxPreselectedDecision(cls, prevChoices):
        if prevChoices.gsuite:
            statList = cls.getHowManyStatHaveBeenSelected(prevChoices)
            if len(statList) > 0:
                return ['no', 'yes']

    @classmethod
    def _getOptionsBoxForSelectedMainOptionFirst(cls, prevChoices, index):
        if prevChoices.gsuite:
            # return cls.MAIN_OPTIONS
            if prevChoices.preselectedDecision:
                if prevChoices.preselectedDecision == 'no':
                    pass
                else:
                    if prevChoices.groupResponse and prevChoices.groupResponse != 'no':
                        if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumnFirst%s' % i)
                                   for i in xrange(index)):
                            return cls.MAIN_OPTIONS
                    else:
                        if int(index) <= cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED:
                            return cls.MAIN_OPTIONS

    @classmethod
    def setupSelectedMainOptionMethodsFirst(cls):
        for i in xrange(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED):
            setattr(cls, 'getOptionsBoxSelectedMainOptionFirst%s' % i,
                    partial(cls._getOptionsBoxForSelectedMainOptionFirst, index=i))

    @classmethod
    def _getOptionsBoxForSelectedOptionFirst(cls, prevChoices, index):
        if prevChoices.gsuite:
            if prevChoices.preselectedDecision and prevChoices.preselectedDecision != 'no':
                if prevChoices.groupResponse and prevChoices.groupResponse != 'no':
                    dfTF = any(
                        cls.PHRASE in getattr(prevChoices, 'selectedColumnFirst%s' % i) for i in
                        xrange(index))
                    if not dfTF:
                        attr = []
                        for i in xrange(index + 1):
                            attr.append(getattr(prevChoices, 'selectedColumnFirst%s' % i))
                            selOption = getattr(prevChoices,
                                                'selectedMainOptionFirst%s' % i).encode('utf-8')

                        if cls.MAIN_OPTIONS[0] == selOption:
                            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                            if index == 0:
                                #return list(set(gSuite.allTrackTitles()))
                                try:
                                    return list(set(gSuite.getAttributeValueList('orginaltitle')))
                                except:
                                    return list(set(gSuite.allTrackTitles()))
                            else:
                                j = index - 1
                                selectedAttribute = getattr(prevChoices,
                                                            'selectedColumnFirst%s' % j).encode(
                                    'utf-8')
                                return list(
                                    set(gSuite.getAttributeValueList(selectedAttribute)))
                        elif cls.MAIN_OPTIONS[1] == selOption:
                            pass
                        else:
                            return cls.OPTIONS_LIST
                else:
                    if index <= cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED:
                        attr = []
                        for i in xrange(index + 1):
                            attr.append(getattr(prevChoices, 'selectedColumnFirst%s' % i))
                            selOption = getattr(prevChoices,
                                                'selectedMainOptionFirst%s' % i).encode('utf-8')

                        if cls.MAIN_OPTIONS[0] == selOption:
                            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                            if index == 0:
                                #return list(set(gSuite.allTrackTitles()))
                                try:
                                    return list(set(gSuite.getAttributeValueList('orginaltitle')))
                                except:
                                    return list(set(gSuite.allTrackTitles()))
                            else:
                                j = index - 1
                                attrNone = getattr(prevChoices, 'selectedColumnFirst%s' % j)
                                if attrNone == 'None':
                                    return
                                else:
                                    selectedAttribute = attrNone.encode('utf-8')
                                return list(
                                    set(gSuite.getAttributeValueList(selectedAttribute)))
                        elif cls.MAIN_OPTIONS[1] == selOption:
                            pass
                        else:
                            return cls.OPTIONS_LIST

    @classmethod
    def setupSelectedOptionMethodsFirst(cls):
        for i in xrange(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED):
            setattr(cls, 'getOptionsBoxSelectedOptionFirst%s' % i,
                    partial(cls._getOptionsBoxForSelectedOptionFirst, index=i))

    @classmethod
    def _getOptionsBoxForSelectedMainOptionSecond(cls, prevChoices, index):
        if prevChoices.gsuite:
            # return cls.MAIN_OPTIONS
            if prevChoices.preselectedDecision:
                if prevChoices.preselectedDecision == 'no':
                    pass
                else:
                    if prevChoices.groupResponse and prevChoices.groupResponse != 'no':
                        if not any(cls.PHRASE in getattr(prevChoices, 'selectedColumnSecond%s' % i)
                                   for i in xrange(index)):
                            return cls.MAIN_OPTIONS
                    else:
                        if int(index) <= cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED:
                            return cls.MAIN_OPTIONS

    @classmethod
    def setupSelectedMainOptionMethodsSecond(cls):
        for i in xrange(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED):
            setattr(cls, 'getOptionsBoxSelectedMainOptionSecond%s' % i,
                    partial(cls._getOptionsBoxForSelectedMainOptionSecond, index=i))

    @classmethod
    def _getOptionsBoxForSelectedOptionSecond(cls, prevChoices, index):
        if prevChoices.secondGSuite:
            if prevChoices.preselectedDecision and prevChoices.preselectedDecision != 'no':
                if prevChoices.groupResponse and prevChoices.groupResponse != 'no':
                    dfTF = any(
                        cls.PHRASE in getattr(prevChoices, 'selectedColumnSecond%s' % i) for i in
                        xrange(index))
                    if not dfTF:
                        attr = []
                        for i in xrange(index + 1):
                            attr.append(getattr(prevChoices, 'selectedColumnSecond%s' % i))
                            selOption = getattr(prevChoices,
                                                'selectedMainOptionSecond%s' % i).encode('utf-8')

                        if cls.MAIN_OPTIONS[0] == selOption:
                            gSuite = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
                            if index == 0:
                                return list(set(gSuite.allTrackTitles()))
                            else:
                                j = index - 1
                                selectedAttribute = getattr(prevChoices,
                                                            'selectedColumnSecond%s' % j).encode(
                                    'utf-8')
                                return list(
                                    set(gSuite.getAttributeValueList(selectedAttribute)))
                        elif cls.MAIN_OPTIONS[1] == selOption:
                            pass
                        else:
                            return cls.OPTIONS_LIST
                else:
                    if index <= cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED:
                        attr = []
                        for i in xrange(index + 1):
                            attr.append(getattr(prevChoices, 'selectedColumnSecond%s' % i))
                            selOption = getattr(prevChoices,
                                                'selectedMainOptionSecond%s' % i).encode('utf-8')

                        if cls.MAIN_OPTIONS[0] == selOption:
                            gSuite = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
                            if index == 0:
                                return list(set(gSuite.allTrackTitles()))
                            else:
                                j = index - 1

                                attrNone = getattr(prevChoices, 'selectedColumnSecond%s' % j)
                                if attrNone == 'None':
                                    return
                                else:
                                    selectedAttribute = attrNone.encode('utf-8')

                                return list(
                                    set(gSuite.getAttributeValueList(selectedAttribute)))
                        elif cls.MAIN_OPTIONS[1] == selOption:
                            pass
                        else:
                            return cls.OPTIONS_LIST

    @classmethod
    def setupSelectedOptionMethodsSecond(cls):
        for i in xrange(cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED):
            setattr(cls, 'getOptionsBoxSelectedOptionSecond%s' % i,
                    partial(cls._getOptionsBoxForSelectedOptionSecond, index=i))

    # @classmethod
    # def getOptionsBoxSummarize(cls, prevChoices):
    #     if prevChoices.gsuite and prevChoices.secondGSuite:
    #
    #         statList = []
    #         for i in xrange(cls.MAX_NUM_OF_COLS):
    #             attr = getattr(prevChoices, 'selectedStat%s' % i)
    #             if cls.PHRASE in [attr]:
    #                 pass
    #             elif str(attr) == 'None':
    #                 pass
    #             else:
    #                 statList.append(attr)
    #         if len(statList) > 0:
    #             return cls.SUMMARIZE.keys()
    #
    # @classmethod
    # def _getOptionsBoxForSelectedFirstColumn(cls, prevChoices, index):
    #     if prevChoices.gsuite and prevChoices.secondGSuite and prevChoices.summarize != 'no':
    #         selectionList = []
    #         if (cls._getLenOfSelectedStat(prevChoices)):
    #             if not any(cls.PHRASE in getattr(prevChoices, 'selectedFirstColumn%s' % i) for i in
    #                        xrange(index)):
    #                 gSuiteTNFirst = getGSuiteFromGalaxyTN(prevChoices.gsuite)
    #                 selectionList += gSuiteTNFirst.attributes
    #
    #                 attrList = [getattr(prevChoices, 'selectedFirstColumn%s' % i) for i in
    #                             xrange(index)]
    #                 selectionList = [cls.PHRASE] + [cls.TITLE] + list(
    #                     set(selectionList) - set(attrList))
    #
    #             if selectionList:
    #                 return selectionList
    #
    # @classmethod
    # def setupSelectedFirstColumnMethods(cls):
    #     from functools import partial
    #     for i in xrange(cls.MAX_NUM_OF_COLS):
    #         setattr(cls, 'getOptionsBoxSelectedFirstColumn%s' % i,
    #                 partial(cls._getOptionsBoxForSelectedFirstColumn, index=i))
    #
    # @classmethod
    # def _getOptionsBoxForSelectedFirstColumnOption(cls, prevChoices, index):
    #     if prevChoices.gsuite and prevChoices.secondGSuite and prevChoices.summarize != 'no':
    #         selectionList = []
    #         if (cls._getLenOfSelectedStat(prevChoices)):
    #             if not any(cls.PHRASE in getattr(prevChoices, 'selectedFirstColumn%s' % i) for i in
    #                        xrange(index)):
    #                 selectionList = ''
    #
    #                 return selectionList
    #
    #             if selectionList:
    #                 return selectionList
    #
    # @classmethod
    # def setupSelectedFirstColumnOptionMethods(cls):
    #     from functools import partial
    #     for i in xrange(cls.MAX_NUM_OF_COLS):
    #         setattr(cls, 'getOptionsBoxSelectedFirstColumnOption%s' % i,
    #                 partial(cls._getOptionsBoxForSelectedFirstColumnOption, index=i))
    #
    # @classmethod
    # def _getOptionsBoxForSelectedSecondColumn(cls, prevChoices, index):
    #     if prevChoices.gsuite and prevChoices.secondGSuite and prevChoices.summarize != 'no':
    #         selectionList = []
    #         if (cls._getLenOfSelectedStat(prevChoices)):
    #             if not any(cls.PHRASE in getattr(prevChoices, 'selectedSecondColumn%s' % i) for i in
    #                        xrange(index)):
    #                 gSuiteTNSecond = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
    #                 selectionList += gSuiteTNSecond.attributes
    #
    #                 attrList = [getattr(prevChoices, 'selectedSecondColumn%s' % i) for i in
    #                             xrange(index)]
    #                 selectionList = [cls.PHRASE] + [cls.TITLE] + list(
    #                     set(selectionList) - set(attrList))
    #
    #             if selectionList:
    #                 return selectionList
    #
    # @classmethod
    # def setupSelectedSecondColumnMethods(cls):
    #     from functools import partial
    #     for i in xrange(cls.MAX_NUM_OF_COLS):
    #         setattr(cls, 'getOptionsBoxSelectedSecondColumn%s' % i,
    #                 partial(cls._getOptionsBoxForSelectedSecondColumn, index=i))
    #
    # @classmethod
    # def _getOptionsBoxForSelectedSecondColumnOption(cls, prevChoices, index):
    #     if prevChoices.gsuite and prevChoices.secondGSuite and prevChoices.summarize != 'no':
    #         if (cls._getLenOfSelectedStat(prevChoices)):
    #             selectionList = []
    #             if not any(cls.PHRASE in getattr(prevChoices, 'selectedSecondColumn%s' % i) for i in
    #                        xrange(index)):
    #                 selectionList = ''
    #
    #                 return selectionList
    #
    #             if selectionList:
    #                 return selectionList
    #
    # @classmethod
    # def setupSelectedSecondColumnOptionMethods(cls):
    #     from functools import partial
    #     for i in xrange(cls.MAX_NUM_OF_COLS):
    #         setattr(cls, 'getOptionsBoxSelectedSecondColumnOption%s' % i,
    #                 partial(cls._getOptionsBoxForSelectedSecondColumnOption, index=i))

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        # DebugMixin._setDebugModeIfSelected(choices)
        preselectedDecision = choices.preselectedDecision.encode('utf-8')
        groupResponse = choices.groupResponse.encode('utf-8')
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        secondGSuite = getGSuiteFromGalaxyTN(choices.secondGSuite)
        analysisBins, columnOptionsDict, firstColumnList, ifAnyElements, secondColumnList, statList, summarize, whichGroups = cls.prepareElements(
            choices)


        mainOptionList, optionList = cls.getPreselectedOptions(choices, preselectedDecision)

        # print 'mainOptionList', mainOptionList, '<br>'
        # print 'optionList', optionList, '<br>'
        #
        # print 'ifAnyElements', ifAnyElements, '<br>'
        # print 'which groups', whichGroups, '<br>'
        selectedAnalysis, statIndex = cls.addStat(choices, statList)

        resultsDict = cls.countStat(analysisBins, selectedAnalysis,
                                    statIndex, whichGroups, statList, summarize, columnOptionsDict, gSuite, secondGSuite)

        summarize = 'raw'

        # print 'resultsDict=', resultsDict, '<br>'
        # print 'galaxyFn=', galaxyFn, '<br>'
        # print 'firstColumnList=', firstColumnList, '<br>'
        # print 'secondColumnList=', secondColumnList, '<br>'
        # print 'summarize=', summarize, '<br>'


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
        htmlCore.paragraph(
            'Click on the following options for selected statistic to see detailed results. ')

        cls.writeResults(galaxyFn, resultsDict, htmlCore, firstColumnList, secondColumnList,
                         summarize, mainOptionList, optionList)
        htmlCore.end()
        print htmlCore

    @classmethod
    def getPreselectedOptions(cls, choices, preselectedDecision):

        if preselectedDecision != 'no':

            mainOptionList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(
                choices, 'selectedMainOptionFirst%s', cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)
            optionList = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                         'selectedOptionFirst%s',
                                                                                         cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)
            main1, main2, option1, option2 = cls.getAllOptions(mainOptionList, optionList)
            # print 'main1', main1, 'main2', main2, 'option1', option1, 'option2', option2

            mainOptionList1 = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(
                choices, 'selectedMainOptionSecond%s', cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)
            optionList1 = CountDescriptiveStatisticBetweenHGsuiteTool._getSelectedOptions(choices,
                                                                                          'selectedOptionSecond%s',
                                                                                          cls.MAX_NUM_OF_COLS_IN_GSUITE_PREDEFINED)
            main3, main4, option3, option4 = cls.getAllOptions(mainOptionList1, optionList1)
            # print 'main3', main3, 'main4', main4, 'option3', option3, 'option4', option4

            # optionList = ['44 - ung-bcl', 'tat', '43 - ung-aicda-bcl--AT']

            mainOptionList = option1 + option3 + option2 + option4
            optionList = main1 + main3 + main2 + main4

            # print 'mainOptionList', mainOptionList, '<br>'
            # print 'optionList', optionList, '<br>'

        else:
            mainOptionList = []
            optionList = []
        return mainOptionList, optionList

    @classmethod
    def getAllOptions(cls, mainOptionList, optionList):
        newOptionList = []
        newMainOptionList = []
        mNum = 0
        for m in mainOptionList:
            if m == cls.MAIN_OPTIONS[1]:
                newMainOptionList.append(-2)
                newOptionList.append('')
            elif m == cls.MAIN_OPTIONS[0]:
                newMainOptionList.append(1)
                newOptionList.append(optionList[mNum])
                mNum += 1
            elif m == cls.MAIN_OPTIONS[2]:
                newMainOptionList.append(-1)
                newOptionList.append(optionList[mNum])
                mNum += 1
        return newOptionList[1:len(newOptionList)], [newOptionList[0]], newMainOptionList[1:len(
            newMainOptionList)], [newMainOptionList[0]]

    @classmethod
    def prepareElements(cls, choices):
        firstGSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        firstGSuiteColumn = choices.firstGSuiteColumn.encode('utf-8')
        secondGSuite = getGSuiteFromGalaxyTN(choices.secondGSuite)
        secondGSuiteColumn = choices.secondGSuiteColumn.encode('utf-8')
        summarize = 'no'
        # summarize = choices.summarize.encode('utf-8')
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec,
                                                         genome=firstGSuite.genome)
        # print firstGSuite, '<br>'
        # print firstGSuiteColumn, '<br>'
        # print secondGSuite, '<br>'
        # print secondGSuiteColumn, '<br>'
        statList = cls._getSelectedOptions(choices, 'selectedStat%s', cls.MAX_NUM_OF_STAT)
        # if summarize != 'no':
        #     firstColumnList = cls._getSelectedOptions(choices, 'selectedFirstColumn%s',
        #                                               cls.MAX_NUM_OF_COLS_IN_GSUITE)
        #     columnOptionsDict = cls._getSelectedColumnOptions(choices,
        #                                                       'selectedFirstColumnOption%s',
        #                                                       cls.MAX_NUM_OF_COLS_IN_GSUITE,
        #                                                       firstColumnList)
        #     secondColumnList = cls._getSelectedOptions(choices, 'selectedSecondColumn%s',
        #                                                cls.MAX_NUM_OF_COLS_IN_GSUITE)
        #     columnOptionsDict = cls._getSelectedColumnOptions(choices,
        #                                                       'selectedSecondColumnOption%s',
        #                                                       cls.MAX_NUM_OF_COLS_IN_GSUITE,
        #                                                       secondColumnList, columnOptionsDict,
        #                                                       st=len(firstColumnList))
        #
        # else:
        firstColumnList = cls._getSelectedOptions(choices, 'selectedColumnFirst%s', cls.MAX_NUM_OF_COLS_IN_GSUITE)
        secondColumnList = cls._getSelectedOptions(choices, 'selectedColumnSecond%s', cls.MAX_NUM_OF_COLS_IN_GSUITE)
        columnOptionsDict = {}
        # print statList, '<br>'
        # print 'firstColumnList', firstColumnList, '<br>'
        # print 'secondColumnList', secondColumnList, '<br>'
        # print 'columnOptionsDict', columnOptionsDict, '<br>'
        # As many unique columns from: firstColumnList and secondColumnList as many outputGSuites
        firstOutput = cls._getAttributes(firstGSuite, firstColumnList)
        # print 'firstOutput', firstOutput, '<br>'
        secondOutput = cls._getAttributes(secondGSuite, secondColumnList)
        # print 'secondOutput', secondOutput, '<br>'
        whichGroups, ifAnyElements = cls.createGroups(firstColumnList, firstGSuite, firstOutput,
                                                      secondColumnList,
                                                      secondGSuite, secondOutput,
                                                      firstGSuiteColumn,
                                                      secondGSuiteColumn)
        return analysisBins, columnOptionsDict, firstColumnList, ifAnyElements, secondColumnList, statList, summarize, whichGroups

    @classmethod
    def _getLenOfSelectedStat(cls, prevChoices):
        statList = []
        for i in xrange(cls.MAX_NUM_OF_COLS):
            attr = getattr(prevChoices, 'selectedStat%s' % i)
            if cls.PHRASE in [attr]:
                pass
            elif str(attr) == 'None':
                pass
            else:
                statList.append(attr)
        if len(statList) >0:
            return True
        else:
            return False

    @classmethod
    def writeResults(cls, galaxyFn, resultsDict, htmlCore, firstColumnList, secondColumnList,
                     summarize, mainOptionList, optionList):

        # print '--- resultsDictFinal --- ', resultsDict
        # print 'firstColumnList, secondColumnList', firstColumnList, secondColumnList

        cube = Cube()
        statNum = 0
        for statKey, statItem in resultsDict.iteritems():

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
                        for g in groupItem:
                            data.append(list(groupKey) + g)
                    else:
                        # print '1--', summarizeKey + "(" + str(groupItem) + ")", len(groupItem), '<br>'
                        # print '2--', list(groupKey), '<br>'
                        if len(groupItem) == 0:
                            # print '4--', list(groupKey) + [0], '<br>'
                            data.append(list(groupKey) + [0])
                        else:
                            if summarizeKey == 'sum':
                                data.append(list(groupKey) + [sum(groupItem)])
                            elif summarizeKey == 'avg':
                                data.append(list(groupKey) + [sum(groupItem)/len(groupItem)])
                            elif summarizeKey == 'min':
                                data.append(list(groupKey) + [min(groupItem)])
                            elif summarizeKey == 'max':
                                data.append(list(groupKey) + [max(groupItem)])
                            # print '5--', list(groupKey), '<br>'


            # print 'data=', data

            if summarizeKey == 'no':
                header = ['Column 1', 'Column 2', 'Value']
                #dataToPresent, headerToPresent = cls.flatResults(header, data)
                dp = zip(*data)
            elif summarizeKey == 'raw':
                header = firstColumnList + secondColumnList + ['Title (first GSuite)'] + ['Title (second GSuite)'] + [summarizeKey]
                dataToPresent = data
                dp = zip(*dataToPresent)
            else:
                header = firstColumnList + secondColumnList + [summarizeKey]
                dataToPresent = data
                headerToPresent = header
                dp = zip(*dataToPresent)

            # print 'header[:len(header) - 1]', header[:len(header) - 1], '<br>'

            optionData = []
            for z in range(0, len(dp) - 1):
                pl = []
                for d in dp[z]:
                    if not d in pl:
                        pl.append(d)
                optionData.append(pl)

            # operations = [-2 for i in range(0, elNum-3)] + [-1,-1, -2]
            # data = cls.summarizeTable(statItem, operations)

            # print 'header', header
            # print 'data', data
            # print 'headerToPresent', headerToPresent
            # print 'dataToPresent', dataToPresent
            # print 'optionData', optionData

            statKeyOrginal = str(statKey)
            statKey = statKey.replace(' ', '').replace('(', '').replace(')', '').replace('/', '')

            # sth is wrong with url to file!
            fileStat = GalaxyRunSpecificFile([statKey + '.tabular'], galaxyFn)
            fileStatPath = fileStat.getDiskPath(ensurePath=True)
            wf = open(fileStatPath, 'w')
            i = 0
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
                            //console.log('el', el.attr('class'));
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
                                      if (el.tagName == 'DIV' && el.id != 'resultsHeader-""" + str(
                statKey) + """')
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
    def flatResults(cls, header, data):
        res = OrderedDict()
        if len(header) == 3:
            for d in data:
                if not d[0] in res.keys():
                    res[d[0]] = OrderedDict()
                    if not d[1] in res[d[0]].keys():
                        res[d[0]][d[1]] = 0
                    res[d[0]][d[1]] = d[2]


            header = ['Tracks'] + res[res.keys()[0]].keys()
            resTab = []
            for k1 in res.keys():
                resTabPart = [k1]
                for k2 in res[res.keys()[0]].keys():
                    if k2 in res[k1]:
                        resTabPart.append(res[k1][k2])
                    else:
                        resTabPart.append(0)
                resTab.append(resTabPart)

            # print 'resTab, header', resTab, header


            return resTab, header

    @classmethod
    def addStat(cls, choices, statList):
        selectedAnalysis = []
        for a in statList:
            if cls.STAT_LIST[a] == STAT_OVERLAP_COUNT_BPS:
                statIndex = TrackReportCommon.STAT_LIST_INDEX[cls.STAT_LIST[a]]
                if choices.intraOverlap == CountDescriptiveStatisticBetweenHGsuiteTool.MERGE_INTRA_OVERLAPS:
                    analysisSpec = AnalysisSpec(PairedTSStat)
                    analysisSpec.addParameter('pairedTsRawStatistic', RawOverlapStat.__name__)
                else:
                    analysisSpec = AnalysisSpec(PairedTSStat)
                    analysisSpec.addParameter('pairedTsRawStatistic',
                                              RawOverlapAllowSingleTrackOverlapsStat.__name__)
                selectedAnalysis.append(analysisSpec)
            if cls.STAT_LIST[a] == 'Forbes coefficient':
                statIndex = 10
                analysisSpec = AnalysisSpec(SummarizedInteractionWithOtherTracksV2Stat)
                analysisSpec.addParameter('pairwiseStatistic', 'ObservedVsExpectedStat')
                analysisSpec.addParameter('reverse', 'No')
                analysisSpec.addParameter("summaryFunc", 'raw')
                selectedAnalysis.append(analysisSpec)

        return selectedAnalysis, statIndex

    # print summarizeTable([['ata', '1 - 243-2--eta-.bed--TG', 863], ['ata', '1 - 243-2--eta-.bed--TA', 781]], [-1, -1, -2])
    # [[1644]]
    @classmethod
    def summarizeTable(cls, flat, operations):
        for i, op in reversed(list(enumerate(operations))):
            if op >= 0:
                flat = [x[:i] + x[i + 1:] for x in flat if x[i] == op]
            elif op == -1:
                flat = [x[:i] + x[i + 1:] for x in flat]
                d = defaultdict(int)
                for x in flat:
                    d[tuple(x[:-1])] += x[-1]
                flat = [list(x) + [d[x]] for x in d]
        return flat

    @classmethod
    def countStat(cls, analysisBins, selectedAnalysis, statIndex, whichGroups, statList, summarize,
                  columnOptionsDict, gSuite, secondGSuite):
        resultsDict = OrderedDict()

        orgnalTitleAll = {}
        orgnalTitleAllCount = 0
        orgnalTitleAllSecond = {}
        orgnalTitleAllCountSecond = 0
        try:
            for x in gSuite.allTracks():
                orgnalTitleAll[x.title] = x.getAttribute('orginaltitle')
            orgnalTitleAllCount = 1
        except:
            pass
        try:
            for x in secondGSuite.allTracks():
                orgnalTitleAllSecond[x.title] = x.getAttribute('orginaltitle')
            orgnalTitleAllCountSecond = 1
        except:
            pass

        # print 'analysisBins', analysisBins, '<br>'
        # print 'selectedAnalysis', selectedAnalysis, '<br>'
        # print 'statIndex', statIndex, '<br>'
        # print 'whichGroups', whichGroups, '<br>'
        # print 'statList', statList, '<br>'
        # print 'summarize', summarize, '<br>', '<br>', '<br>'

        summarize = 'raw'
        for saNum, sa in enumerate(selectedAnalysis):
            stat = statList[saNum]

            if not stat in resultsDict.keys():
                resultsDict[stat] = OrderedDict()
            if not cls.SUMMARIZE[summarize] in resultsDict[stat].keys():
                resultsDict[stat][cls.SUMMARIZE[summarize]] = OrderedDict()
            for groupKey, groupItem in whichGroups.iteritems():
                groupKey = cls.changeOptions(columnOptionsDict, groupKey)
                if not groupKey in resultsDict[stat][cls.SUMMARIZE[summarize]].keys():
                    resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey] = []

                for gi in groupItem:
                    result = doAnalysis(sa, analysisBins, gi)
                    res = result.getGlobalResult()['Result']
                    allResults = res.getResult()
                    queryTrackTitle = res.getTrackStructure()['query'].metadata['title']
                    refTrackTitle = res.getTrackStructure()['reference'].metadata['title']
                    if stat == 'Forbes coefficient':
                        resVal = float(allResults[0])
                    else:
                        resVal = int(allResults['Both'])

                    # if cls.SUMMARIZE[summarize] == 'raw':
                    #     resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey].append(
                    #         [queryTrackTitle, refTrackTitle, resVal])

                    if cls.SUMMARIZE[summarize] == 'raw':
                        title = res.getTrackStructure()['query'].metadata['title']
                        if orgnalTitleAllCount == 1:
                            orginalTitle = orgnalTitleAll[title]
                        else:
                            orginalTitle = title
                        titleSecond = res.getTrackStructure()['reference'].metadata['title']
                        if orgnalTitleAllCountSecond == 1:
                            orginalTitleSecond = orgnalTitleAllSecond[title]
                        else:
                            orginalTitleSecond = titleSecond
                        resultsDict[stat][cls.SUMMARIZE[summarize]][groupKey].append(
                            [orginalTitle, orginalTitleSecond, resVal])


        return resultsDict

    @classmethod
    def _replacementForTupleAtPosition(cls, tup, ix, val):
        return tup[:ix] + (val,) + tup[ix + 1:]

    @classmethod
    def changeOptions(cls, columnOptionsDict, groupKey):

        # print 'columnOptionsDict', columnOptionsDict, '<br>'
        for kCo, itCo in columnOptionsDict.iteritems():
            changeElement = False
            # print 'kCo', kCo, 'itCo', itCo, '<br>'
            for itCoOp in itCo:
                if not changeElement:
                    if groupKey[int(kCo)] in itCoOp:
                        # print 'itCoOp', itCoOp, 'groupKey[int(kCo)]', groupKey[int(kCo)], '<br>'
                        if itCoOp.index(groupKey[int(kCo)]) != 0:
                            # print 'groupKey, int(kCo), itCoOp[0]', groupKey, int(kCo), itCoOp[0], '<br>'
                            groupKey = cls._replacementForTupleAtPosition(groupKey, int(kCo),
                                                                          itCoOp[0])
                            # print 'gr', groupKey, '<br>'
                            changeElement = True
        return groupKey

    @classmethod
    def createGroups(cls, firstColumnList, firstGSuite, firstOutput, secondColumnList,
                     secondGSuite, secondOutput, firstGSuiteColumn, secondGSuiteColumn):

        # print firstColumnList, firstGSuite, firstOutput, secondColumnList,
        # print secondGSuite, secondOutput, firstGSuiteColumn, secondGSuiteColumn

        whichGroups = OrderedDict()
        # print firstOutput, secondOutput
        for wg in cls._getCombinations(firstOutput, secondOutput):
            whichGroups[wg] = []

        # print 'Count for groups: ', whichGroups

        ifAnyElements = False
        for iTrackFromFirst, trackFromFirst in enumerate(firstGSuite.allTracks()):
            for iTrackFromSecond, trackFromSecond in enumerate(secondGSuite.allTracks()):

                # print 'firstGSuiteColumn', firstGSuiteColumn, '<br>'
                # print 'secondGSuiteColumn', secondGSuiteColumn, '<br>'


                if firstGSuiteColumn == 'title':
                    attr1 = trackFromFirst.title
                elif firstGSuiteColumn == 'None':
                    attr1 = 'None'
                else:
                    attr1 = trackFromFirst.getAttribute(firstGSuiteColumn.encode('utf-8'))


                if secondGSuiteColumn == 'title':
                    attr2 = trackFromSecond.title
                elif secondGSuiteColumn == 'None':
                    attr2 = 'None'
                else:
                    attr2 = trackFromSecond.getAttribute(secondGSuiteColumn.encode('utf-8'))

                # print 'attr', attr1, attr2, firstGSuiteColumn, secondGSuiteColumn, '<br>'

                if attr1 == attr2:
                    attrTuple = []
                    cls.buildAttrTuple(attrTuple, firstColumnList, trackFromFirst)
                    cls.buildAttrTuple(attrTuple, secondColumnList, trackFromSecond)
                    attrTuple = tuple(attrTuple)

                    # print 'attrTuple', attrTuple, '<br>'
                    # print '[trackFromFirst, trackFromSecond]', [trackFromFirst.trackName,trackFromSecond.trackName], '<br>', '<br>'
                    realTS = TrackStructureV2()
                    realTS["query"] = SingleTrackTS(PlainTrack(trackFromFirst.trackName),
                                                    OrderedDict(title=trackFromFirst.title,
                                                                genome=str(firstGSuite.genome)))
                    realTS["reference"] = SingleTrackTS(PlainTrack(trackFromSecond.trackName),
                                                        OrderedDict(title=trackFromSecond.title,
                                                                    genome=str(
                                                                        firstGSuite.genome)))
                    whichGroups[attrTuple].append(realTS)
                    ifAnyElements = True

        return whichGroups, ifAnyElements

    @classmethod
    def buildAttrTuple(cls, attrTuple, firstColumnList, trackFromFirst):
        for attrName in firstColumnList:
            if attrName == cls.TITLE:
                at = trackFromFirst.title
            else:
                at = trackFromFirst.getAttribute(attrName)
            attrTuple.append(at)
        return attrTuple

    @classmethod
    def _getAttributes(cls, firstGSuite, firstColumnList):
        if len(firstColumnList) > 0:
            firstOutput = []
            for fCol in firstColumnList:
                if fCol == cls.TITLE:
                    at = firstGSuite.allTrackTitles()
                else:
                    at = firstGSuite.getAttributeValueList(fCol)
                listOfUniqueElements = list(set(at))
                firstOutput.append(listOfUniqueElements)
            return firstOutput
        return None

    @classmethod
    def _getCombinations(cls, firstOutput, secondOutput):
        listOfLists = []
        if firstOutput != None:
            listOfLists = firstOutput
        if secondOutput != None:
            listOfLists += secondOutput
        listOfListsCombinations = itertools.product(*listOfLists)
        return listOfListsCombinations

    @classmethod
    def _getSelectedColumnOptions(cls, choices, division, num, columnList, columnOptionsList={},
                                  st=0):
        cols = []
        for i in range(0, num):
            cols.append(getattr(choices, division % i))
        return cls._getDatafromSelectedStatOption(cols, columnList, columnOptionsList, st)

    @classmethod
    def _getDatafromSelectedStatOption(cls, cols, columnList, selColumn, st):
        if len(cols) >= 1:
            for numC, c in enumerate(cols):
                if c != None:
                    c = c.encode('utf-8')
                    if c != cls.PHRASE and c != '':
                        if not str(numC + st) in selColumn.keys():
                            selColumn[str(numC + st)] = []
                        for el in c.split(';'):
                            selColumn[str(numC + st)].append(el.split(','))
        return selColumn

    @classmethod
    def _getSelectedOptions(cls, choices, division, num):
        cols = []
        for i in range(0, num):
            cols.append(getattr(choices, division % i))
        return cls._getDatafromSelectedStat(cols)

    @classmethod
    def _getDatafromSelectedStat(cls, cols):
        selectedCols = []
        if len(cols) >= 1:
            for c in cols:
                if c != None:
                    c = c.encode('utf-8')
                    if c != cls.PHRASE and c != '':
                        selectedCols.append(c)
        return selectedCols

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gsuite and not choices.secondGSuite:
            return 'Select first and second hGSuite'

        if not choices.gsuite:
            return 'Select first hGSuite'

        if not choices.secondGSuite:
            return 'Select second hGSuite'

        if choices.gsuite and choices.secondGSuite:
            gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
            if not gsuite.isPreprocessed():
                return 'First hGSuite need to preprocessed.'
            secondGSuite = getGSuiteFromGalaxyTN(choices.secondGSuite)
            if not secondGSuite.isPreprocessed():
                return 'Second hGSuite need to preprocessed.'


        if cls.PHRASE in getattr(choices, 'selectedStat%s' % 0):
            return 'Select at least 1 statistic'

        if choices.gsuite and choices.secondGSuite:
            firstGSuite = getGSuiteFromGalaxyTN(choices.gsuite)
            secondGSuite = getGSuiteFromGalaxyTN(choices.secondGSuite)

            if firstGSuite.genome == secondGSuite.genome:
                pass
            else:
                return 'Genomes from both hGSuites are not the same.'

        analysisBins, columnOptionsDict, firstColumnList, ifAnyElements, secondColumnList, statList, summarize, whichGroups = cls.prepareElements(choices)
        if ifAnyElements == False:
            return 'No common values in columns for both hGSuites.'



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

        toolDescription = "This tool count descriptive statistics for relations between hGSuites."

        stepsToRunTool = ['Select first hGSuite',
                          'Select column from first hGSuite',
                          'Select second hGSuite',
                          'Select column from second hGSuite',
                          'Select statistic',
                          'Summarize within groups (no, sum, minimum, maximum, average)',
                          'Select column from first hGSuite which you would like to treat as unique',
                          'Do you want to do above summarize data for column from first hGSuite',
                          'Select column from second hGSuite which you would like to treat as unique',
                          'Do you want to do above summarize data for column from second hGSuite'
                          ]

        urlexample1Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticBetweenHGSuitesTool-img1.png']).getURL()
        urlexample2Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticBetweenHGSuitesTool-img2.png']).getURL()

        urlexample3Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticBetweenHGSuitesTool-img3.png']).getURL()
        urlexample4Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticBetweenHGSuitesTool-img4.png']).getURL()

        urlexample5Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticBetweenHGSuitesTool-img5.png']).getURL()
        urlexample6Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticBetweenHGSuitesTool-img6.png']).getURL()
        urlexample7Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticBetweenHGSuitesTool-img7.png']).getURL()
        urlexample8Output = StaticImage(['hgsuite', 'img',
                                         'CountDescriptiveStatisticBetweenHGSuitesTool-img8.png']).getURL()

        example = OrderedDict(
            {'Example 1 - summarize within groups: no': ['',
        ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: mm10
        ###uri          	                                  title     mutation	genotype	dir_level_1	dir_level_2
        hb:/external/gsuite/c2/c298599af8b0d539/track1.bed      track1.bed    CA        eta	            C       	    A
        hb:/external/gsuite/c2/c298599af8b0d539/track2.bed      track2.bed    GT        eta	            G       	    T
        hb:/external/gsuite/c2/c298599af8b0d539/track3.bed      track3.bed    CG        iota  	            C       	    G
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track4.bed    GC        iota  	            G       	    C
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track5.bed    CA        iota  	            C       	    A
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track6.bed    GT        iota  	            G       	    T
        """,
        """
         ##location: local				
        ##file format: preprocessed				
        ##track type: points				
        ##genome: mm10				
        ###uri          	                                  title     dir_level_1	dir_level_2	dir_level_3
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aca	aca	A	C	A
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acc	acc	A	C	C
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acg	acg	A	C	G
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/act	act	A	C	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aga	aga	A	G	A
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agc	agc	A	G	C
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agg	agg	A	G	G
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agt	agt	A	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aca	tgt	T	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acc	ggt	G	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acg	cgt	C	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/ata	ata	A	T	A
         """
         ],
         [
             ['Select first hGSuite','gsuite'],
             ['Select column from first hGSuite','dir_level_1'],
             ['Select second hGSuite','gsuite'],
             ['Select column from second hGSuite','dir_level_2'],
             ['Select statistic 1', 'Coverage'],
             ['Select overlap handling', 'Merge any overlapping points/segments within the same track'],
             ['Summarize within groups', 'no']

         ],
         [
             '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample1Output + '" /><img  style="margin-right:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:right;padding-left:0px;" width="300" src="' + urlexample2Output + '" /></div>']
         ],
        'Example 2 - summarize within groups: sum (with unique column and summarize data)': ['',
         ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: mm10
        ###uri          	                                  title     mutation	genotype	dir_level_1	dir_level_2
        hb:/external/gsuite/c2/c298599af8b0d539/track1.bed      track1.bed    CA        eta	            C       	    A
        hb:/external/gsuite/c2/c298599af8b0d539/track2.bed      track2.bed    GT        eta	            G       	    T
        hb:/external/gsuite/c2/c298599af8b0d539/track3.bed      track3.bed    CG        iota  	            C       	    G
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track4.bed    GC        iota  	            G       	    C
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track5.bed    CA        iota  	            C       	    A
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track6.bed    GT        iota  	            G       	    T
        """,
        """
        ##location: local				
        ##file format: preprocessed				
        ##track type: points				
        ##genome: mm10				
        ###uri          	                                  title     dir_level_1	dir_level_2	dir_level_3
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aca	aca	A	C	A
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acc	acc	A	C	C
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acg	acg	A	C	G
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/act	act	A	C	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aga	aga	A	G	A
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agc	agc	A	G	C
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agg	agg	A	G	G
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agt	agt	A	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aca	tgt	T	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acc	ggt	G	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acg	cgt	C	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/ata	ata	A	T	A
         """
        ],
        [
            ['Select first hGSuite', 'gsuite'],
            ['Select column from first hGSuite','dir_level_1'],
            ['Select second hGSuite', 'gsuite'],
            ['Select column from second hGSuite', 'dir_level_2'],
            ['Select statistic 1', 'Coverage'],
            ['Select overlap handling', 'Merge any overlapping points/segments within the same track'],
            ['Summarize within groups', 'sum'],
            ['Select column from first hGSuite 1 which you would like to treat as unique', 'title'],
            ['Select column from first hGSuite 2 which you would like to treat as unique', 'mutation'],
            ['Do you want to do above summarize data for column 1 from first hGSuite', ''],
            ['Do you want to do above summarize data for column 2 from first hGSuite', 'CA,GT;CG,GC;CT,GA;TA,AT;TC,AG;TG,AC'],
             [
                 'Select column from second hGSuite 1 which you would like to treat as unique',
                 ''],
             [
                 'Do you want to do above summarize for column 1 from second hGSuite',
                 ''],
        ],
         [
             '<div style = "margin: 0px auto;" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample3Output + '" /><img  style="margin-right:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:right;padding-left:0px;" width="300" src="' + urlexample4Output + '" /></div>']
         ],
        'Example 3 - summarize within groups: sum (with unique columns and summarize data)': ['',
         ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: mm10
        ###uri          	                                  title     mutation	genotype	dir_level_1	dir_level_2
        hb:/external/gsuite/c2/c298599af8b0d539/track1.bed      track1.bed    CA        eta	            C       	    A
        hb:/external/gsuite/c2/c298599af8b0d539/track2.bed      track2.bed    GT        eta	            G       	    T
        hb:/external/gsuite/c2/c298599af8b0d539/track3.bed      track3.bed    CG        iota  	            C       	    G
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track4.bed    GC        iota  	            G       	    C
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track5.bed    CA        iota  	            C       	    A
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed      track6.bed    GT        iota  	            G       	    T
        """,
        """
        ##location: local				
        ##file format: preprocessed				
        ##track type: points				
        ##genome: mm10				
        ###uri          	                                  title     dir_level_1	dir_level_2	dir_level_3
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aca	aca	A	C	A
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acc	acc	A	C	C
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acg	acg	A	C	G
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/act	act	A	C	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aga	aga	A	G	A
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agc	agc	A	G	C
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agg	agg	A	G	G
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/agt	agt	A	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/aca	tgt	T	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acc	ggt	G	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/acg	cgt	C	G	T
        hb:/external/dianadom_sandbox/c7/c79967e1aa4e6024/ata	ata	A	T	A
         """
        ],
        [
            ['Select first hGSuite', 'gsuite'],
            ['Select column from first hGSuite','dir_level_1'],
            ['Select second hGSuite', 'gsuite'],
            ['Select column from second hGSuite', 'dir_level_2'],
            ['Select statistic 1', 'Coverage'],
            ['Select overlap handling', 'Merge any overlapping points/segments within the same track'],
            ['Summarize within groups', 'sum'],
            ['Select column from first hGSuite 1 which you would like to treat as unique', 'title'],
            ['Select column from first hGSuite 2 which you would like to treat as unique', 'mutation'],
            ['Do you want to do above summarize data for column 1 from first hGSuite', ''],
            ['Do you want to do above summarize data for column 2 from first hGSuite', 'CA,GT;CG,GC;CT,GA;TA,AT;TC,AG;TG,AC'],
            ['Select column from second hGSuite 1 which you would like to treat as unique','title'],
            ['Select column from second hGSuite 2 which you would like to treat as unique',''],
            ['Do you want to do above summarize for column 1 from second hGSuite',
                 'aca,tgt;acc,ggt;acg,cgt;act,agt;ata,tat;tct,aga;gct,agc;cct,agg'],
             [
                 'Do you want to do above summarize for column 2 from second hGSuite',
                 '']

        ],
         [
             '<div style = "margin: 0px auto 20px auto;clear:both;width:100%" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample5Output + '" /><img  style="margin-right:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:right;padding-left:0px;" width="300" src="' + urlexample6Output + '" /></div><div style = "margin: 0px auto 20px auto;clear:both;width:100%" ><img style="margin-left:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:left;padding-left:0px;" width="300" src="' + urlexample7Output + '" /><img  style="margin-right:30px;border-radius: 15px;border: 1px dotted #3d70b2;float:right;padding-left:0px;" width="300" src="' + urlexample8Output + '" /></div>']
         ]

        })

        toolResult = '<p>The output of this tool is a page with visualizations.</p>' \
                     'Detailed information about results gives possibility to <b>download raw file</b> with results <br>' \
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
    @classmethod
    def isDebugMode(cls):
        return True

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


CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedStatMethods()
# CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedFirstColumnMethods()
# CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedFirstColumnOptionMethods()
# CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedSecondColumnMethods()
# CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedSecondColumnOptionMethods()
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedColumnMethodsFirst()
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedColumnMethodsSecond()
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedMainOptionMethodsFirst()
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedOptionMethodsFirst()
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedMainOptionMethodsSecond()
CountDescriptiveStatisticBetweenHGsuiteTool.setupSelectedOptionMethodsSecond()