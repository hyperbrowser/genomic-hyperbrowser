import ast
from collections import OrderedDict
from functools import partial

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from proto.HtmlCore import HtmlCore
from proto.tools.GeneralGuiTool import BoxGroup
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class GroupGSuiteTracks(GeneralGuiTool):
    KEEP_IN_GSUITE = "Keep in GSuite as disabled"
    REMOVE_FROM_GSUITE = "Remove from GSuite"
    MAX_NUM_OF_FILTERS = 5
    SELECT_CHOICE = ' --- Select --- '
    ADD_FILTER = 'Add a filter'
    NO_FILTER = 'No more filters'
    BASE_FILTER = 'Base filtering only'
    CASE_FILTER = 'Create a single group of tracks (case)'
    CASE_CONTROL_FILTER = 'Create two separate groups of tracks (case/control)'
    YES = 'Yes'
    NO = 'No'

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Group GSuite tracks based on metadata"

    @classmethod
    def getInputBoxNames(cls):
        attrBoxes = [('Select a GSuite of case-control tracks', 'gsuite'),
                     ('Which filtering operation do you want to carry out?', 'filterChoice')]

        for i in xrange(cls.MAX_NUM_OF_FILTERS):
            attrBoxes.extend([('Do you want to add a filter?', 'baseFilter%s' % i),
                ('Select metadata column', 'baseMetadataColumn%s' % i),
                ('Select values to be used', 'baseSelectValue%s' % i),
                ('', 'baseFilteredGSuiteTitles%s' % i)])

        attrBoxes.append(('Show base track table', 'showBaseTrackTable'))
        attrBoxes.append(('Tracks which have passed filters in this section', 'baseTrackTable'))

        for i in xrange(cls.MAX_NUM_OF_FILTERS):
            attrBoxes.extend([('Do you want to add a filter?', 'caseFilter%s' % i),
                ('Select metadata column', 'caseMetadataColumn%s' % i),
                ('Select values to be used', 'caseSelectValue%s' % i),
                ('', 'caseFilteredGSuiteTitles%s' % i)])

        attrBoxes.append(('Show case track table', 'showCaseTrackTable'))
        attrBoxes.append(('Tracks which have passed filters in this section', 'caseTrackTable'))

        for i in xrange(cls.MAX_NUM_OF_FILTERS):
            attrBoxes.extend([('Do you want to add a filter?', 'controlFilter%s' % i),
                ('Select metadata column', 'controlMetadataColumn%s' % i),
                ('Select values to be used', 'controlSelectValue%s' % i),
                ('', 'controlFilteredGSuiteTitles%s' % i)])

        attrBoxes.append(('Show control track table', 'showControlTrackTable'))
        attrBoxes.append(('Tracks which have passed filters in this section', 'controlTrackTable'))

        attrBoxes.extend([
            ('', 'divider'),
            ('Enter name of grouping (title of new metadata column)', 'groupName'),
            ('Enter value for of case group', 'caseGroupName'),
            ('Enter value for control group', 'controlGroupName'),
            ('Show tracks which have not passed base filters', 'showBaseFilteredOutTracks'),
            ('Tracks which have not passed base filters', 'baseFilteredOutTracks'),
            ('For tracks which have not passed base filters', 'baseNotSelectedTracks'),
            ('Show tracks which have not passed case/control filters', 'showCaseControlFilteredOutTracks'),
            ('Tracks which have not passed case/control filters', 'caseControlFilteredOutTracks'),
            ('For tracks that have passed base filters (if any) but have not pass case or control filters', 'caseControlNotSelectedTracks'),
            ])

        return attrBoxes

    @classmethod
    def setupExtraBoxMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_FILTERS):
            setattr(cls, 'getOptionsBoxBaseFilter%s' % i, partial(cls._getOptionsBoxBaseFilter, level=i))
            setattr(cls, 'getOptionsBoxBaseMetadataColumn%s' % i,
                    partial(cls._getOptionsBoxBaseMetadataColumn, level=i))
            setattr(cls, 'getOptionsBoxBaseSelectValue%s' % i, partial(cls._getOptionsBoxBaseSelectValue, level=i))
            setattr(cls, 'getOptionsBoxBaseFilteredGSuiteTitles%s' % i,
                    partial(cls._getOptionsBoxBaseFilteredGSuiteTitles, level=i))

        for i in xrange(cls.MAX_NUM_OF_FILTERS):
            setattr(cls, 'getOptionsBoxCaseFilter%s' % i, partial(cls._getOptionsBoxCaseFilter, level=i))
            setattr(cls, 'getOptionsBoxCaseMetadataColumn%s' % i,
                    partial(cls._getOptionsBoxCaseMetadataColumn, level=i))
            setattr(cls, 'getOptionsBoxCaseSelectValue%s' % i, partial(cls._getOptionsBoxCaseSelectValue, level=i))
            setattr(cls, 'getOptionsBoxCaseFilteredGSuiteTitles%s' % i, partial(cls._getOptionsBoxCaseFilteredGSuiteTitles, level=i))

        for i in xrange(cls.MAX_NUM_OF_FILTERS):
            setattr(cls, 'getOptionsBoxControlFilter%s' % i, partial(cls._getOptionsBoxControlFilter, level=i))
            setattr(cls, 'getOptionsBoxControlMetadataColumn%s' % i,
                    partial(cls._getOptionsBoxControlMetadataColumn, level=i))
            setattr(cls, 'getOptionsBoxControlSelectValue%s' % i, partial(cls._getOptionsBoxControlSelectValue, level=i))
            setattr(cls, 'getOptionsBoxControlFilteredGSuiteTitles%s' % i, partial(cls._getOptionsBoxControlFilteredGSuiteTitles, level=i))

    @classmethod
    def getOptionsBoxDivider(cls, prevChoices):
        return '__rawstr__', str(HtmlCore().divider())

    @classmethod
    def getOptionsBoxFilterChoice(cls, prevChoices):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        return [cls.BASE_FILTER, cls.CASE_FILTER, cls.CASE_CONTROL_FILTER]

    @classmethod
    def getOptionsBoxGsuite(cls):

        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def _getOptionsBoxShowTrackTable(cls, prevChoices):

        return [cls.NO, cls.YES]

    @classmethod
    def getOptionsBoxShowBaseTrackTable(cls, prevChoices):
        filteredTitles = cls._getFilteredTitles(prevChoices, 'baseFilteredGSuiteTitles')

        if not filteredTitles:
            return

        return cls._getOptionsBoxShowTrackTable(prevChoices)

    @classmethod
    def getOptionsBoxShowCaseTrackTable(cls, prevChoices):
        filteredTitles = cls._getFilteredTitles(prevChoices, 'caseFilteredGSuiteTitles')

        if not filteredTitles:
            return

        return cls._getOptionsBoxShowTrackTable(prevChoices)

    @classmethod
    def getOptionsBoxShowControlTrackTable(cls, prevChoices):
        filteredTitles = cls._getFilteredTitles(prevChoices, 'controlFilteredGSuiteTitles')

        if not filteredTitles:
            return

        return cls._getOptionsBoxShowTrackTable(prevChoices)

    @classmethod
    def getOptionsBoxShowBaseFilteredOutTracks(cls, prevChoices):
        filteredTitles = cls._getFilteredTitles(prevChoices, 'baseFilteredGSuiteTitles')

        if not filteredTitles:
            return

        return cls._getOptionsBoxShowTrackTable(prevChoices)

    @classmethod
    def getOptionsBoxShowCaseControlFilteredOutTracks(cls, prevChoices):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return
        
        if prevChoices.filterChoice == cls.BASE_FILTER:
            return

        if not (getattr(prevChoices,'caseFilteredGSuiteTitles0') or getattr(prevChoices, 'controlFilteredGSuiteTitles0')):
            return

        return cls._getOptionsBoxShowTrackTable(prevChoices)


    @classmethod
    def getOptionsBoxBaseFilteredOutTracks(cls, prevChoices):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        if prevChoices.showBaseFilteredOutTracks == cls.NO:
            return

        filteredTitles = cls._getValueOfLastInputBox(prevChoices, 'baseFilteredGSuiteTitles')

        if not filteredTitles:
            return

        gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)

        allTitles = gsuite.allTrackTitles()
        filteredOutTitles = [title for title in allTitles if title not in filteredTitles]

        trackTable = cls._getTrackTable(gsuite, filteredOutTitles, 'filteredOutTitles')

        return trackTable

    @classmethod
    def getOptionsBoxCaseControlFilteredOutTracks(cls, prevChoices):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        if prevChoices.filterChoice == cls.BASE_FILTER:
            return

        if prevChoices.showCaseControlFilteredOutTracks == cls.NO:
            return

        gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)

        filteredTitlesBase = cls._getValueOfLastInputBox(prevChoices, 'controlFilteredGSuiteTitles')
        if not filteredTitlesBase:
            filteredTitlesBase = gsuite.allTrackTitles()

        filteredTitlesCaseControl = cls._getValueOfLastInputBox(prevChoices, 'caseFilteredGSuiteTitles')
        if filteredTitlesCaseControl is None:
            filteredTitlesCaseControl = []

        if prevChoices.filterChoice == cls.CASE_CONTROL_FILTER:
            filteredTitlesControl = cls._getValueOfLastInputBox(prevChoices, 'controlFilteredGSuiteTitles')
            if filteredTitlesControl:
                filteredTitlesCaseControl += filteredTitlesControl

        if not filteredTitlesCaseControl:
            return

        filteredOutTitles = [title for title in filteredTitlesBase if title not in filteredTitlesCaseControl]

        trackTable = cls._getTrackTable(gsuite, filteredOutTitles, 'filteredOutTitlesCaseControl')

        return trackTable

    @classmethod
    def _getOptionsBoxFilter(cls, prevChoices, level, valueBoxName):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE or \
                (level > 0 and not cls._getSelectedValues(prevChoices, level-1, valueBoxName)):
            return

        return [cls.NO_FILTER, cls.ADD_FILTER]

    @classmethod
    def _getOptionsBoxMetadataColumn(cls, prevChoices, level, filterBoxName, valueBoxName,):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE or \
                (level > 0 and not cls._getSelectedValues(prevChoices, level - 1, valueBoxName)):
            return

        if getattr(prevChoices, (filterBoxName + '%s') % level) in [None, cls.NO_FILTER]:
            return

        gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)

        return gsuite.attributes

    @classmethod
    def _getOptionsBoxSelectValue(cls, prevChoices, level, filterBoxName, metadataBoxName, valueBoxName, filteredTitlesBoxName, isBase=False):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE or \
                (level > 0 and not cls._getSelectedValues(prevChoices, level-1, valueBoxName)):
            return

        if getattr(prevChoices, (filterBoxName + '%s') % level) in [None, cls.NO_FILTER]:
            return

        if getattr(prevChoices, (metadataBoxName + '%s') % level):
            gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            if level == 0:
                if isBase:
                    vals = sorted(list(set(gsuite.getAttributeValueList(getattr(prevChoices, (metadataBoxName + '%s') % level)))))
                else:
                    filteredTitles = cls._getValueOfLastInputBox(prevChoices, 'baseFilteredGSuiteTitles')

                    if not filteredTitles:
                        vals = sorted(list(set(gsuite.getAttributeValueList(
                            getattr(prevChoices, (metadataBoxName + '%s') % level)))))
                    else:
                        vals = cls._getFilteredValues(prevChoices, level, filteredTitlesBoxName,
                                                      metadataBoxName, lastTitles=filteredTitles)
            else:
                vals = cls._getFilteredValues(prevChoices, level, filteredTitlesBoxName, metadataBoxName)

            valsDict = OrderedDict([(val, False) for val in vals])

            return valsDict

    @classmethod
    def _getOptionsBoxFilteredGSuiteTitles(cls, prevChoices, level, metadataBoxName, valueBoxName, filteredTitlesBoxName, isBase=False):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE or not cls._getSelectedValues(
                prevChoices, level, valueBoxName):
            return

        gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)

        col = getattr(prevChoices, (metadataBoxName + '%s') % level)
        vals = cls._getSelectedValues(prevChoices, level, valueBoxName)

        lastTitles = None
        if level == 0:
            if not isBase:
                lastTitles = cls._getValueOfLastInputBox(prevChoices, 'baseFilteredGSuiteTitles')

            if not lastTitles:
                lastTitles = gsuite.allTrackTitles()
        else:
            lastTitles = getattr(prevChoices, (filteredTitlesBoxName + '%s') % (level - 1))
            if isinstance(lastTitles, unicode):
                lastTitles = ast.literal_eval(lastTitles)

        currentTrackTitles = []

        for title in lastTitles:
            track = gsuite.getTrackFromTitle(title)
            attrVal = track.getAttribute(col)
            if attrVal in vals:
                currentTrackTitles.append(title)

        return '__hidden__', currentTrackTitles

    @classmethod
    def _getTrackTableFromFilteredTitles(cls, prevChoices, filteredTitlesBoxName):
        filteredTitles = cls._getFilteredTitles(prevChoices, filteredTitlesBoxName)

        if not filteredTitles:
            return

        gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)

        return cls._getTrackTable(gsuite, filteredTitles, filteredTitlesBoxName)

    @classmethod
    def _getFilteredTitles(cls, prevChoices, filteredTitlesBoxName):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        filteredTitles = cls._getValueOfLastInputBox(prevChoices, filteredTitlesBoxName)
        if isinstance(filteredTitles, unicode):
            filteredTitles = ast.literal_eval(filteredTitles)

        return filteredTitles


    @classmethod
    def _getTrackTable(cls, gsuite, trackTitles, tableId):
        tableDict = {}
        attributeNames = gsuite.attributes
        for title in trackTitles:
            attributes = []
            track = gsuite.getTrackFromTitle(title)
            for attrName in attributeNames:
                val = track.getAttribute(attrName)
                attributes.append(val)

            tableDict[title] = attributes

        if not tableDict:
            return

        html = HtmlCore()
        html.tableFromDictionary(tableDict, columnNames=['track title'] + attributeNames,
                                 tableId=tableId, expandable=True)

        return '__rawstr__', unicode(html)

    @classmethod
    def _getValueOfLastInputBox(cls, prevChoices, inputBoxName):
        value = None
        for i in xrange(cls.MAX_NUM_OF_FILTERS):
            if not hasattr(prevChoices, (inputBoxName + '%s') % i) or not getattr(
                    prevChoices, (inputBoxName + '%s') % i):
                break
            value = getattr(prevChoices, (inputBoxName + '%s') % i)

        if isinstance(value, unicode):
            value = ast.literal_eval(value)

        return value

    @classmethod
    def _getOptionsBoxBaseFilter(cls, prevChoices, level):
        return cls._getOptionsBoxFilter(prevChoices, level, 'baseSelectValue')

    @classmethod
    def _getOptionsBoxBaseSelectValue(cls, prevChoices, level):
        return cls._getOptionsBoxSelectValue(prevChoices, level, 'baseFilter',
                                             'baseMetadataColumn', 'baseSelectValue',
                                             'baseFilteredGSuiteTitles', isBase=True)

    @classmethod
    def _getOptionsBoxBaseMetadataColumn(cls, prevChoices, level):
        return cls._getOptionsBoxMetadataColumn(prevChoices, level, 'baseFilter', 'baseSelectValue')


    @classmethod
    def _getOptionsBoxBaseFilteredGSuiteTitles(cls, prevChoices, level):
        return cls._getOptionsBoxFilteredGSuiteTitles(prevChoices, level, 'baseMetadataColumn', 'baseSelectValue',
                                             'baseFilteredGSuiteTitles', isBase=True)

    @classmethod
    def _getOptionsBoxCaseFilter(cls, prevChoices, level):
        if prevChoices.filterChoice == cls.BASE_FILTER:
            return
        return cls._getOptionsBoxFilter(prevChoices, level, 'caseSelectValue')

    @classmethod
    def _getOptionsBoxCaseSelectValue(cls, prevChoices, level):
        if prevChoices.filterChoice == cls.BASE_FILTER:
            return
        return cls._getOptionsBoxSelectValue(prevChoices, level, 'caseFilter',
                                             'caseMetadataColumn', 'caseSelectValue',
                                             'caseFilteredGSuiteTitles')

    @classmethod
    def _getOptionsBoxCaseMetadataColumn(cls, prevChoices, level):
        if prevChoices.filterChoice == cls.BASE_FILTER:
            return
        return cls._getOptionsBoxMetadataColumn(prevChoices, level, 'caseFilter',
                                                'caseSelectValue')

    @classmethod
    def _getOptionsBoxCaseFilteredGSuiteTitles(cls, prevChoices, level):
        if prevChoices.filterChoice == cls.BASE_FILTER:
            return
        return cls._getOptionsBoxFilteredGSuiteTitles(prevChoices, level, 'caseMetadataColumn',
                                                      'caseSelectValue',
                                                      'caseFilteredGSuiteTitles', isBase=False)

    @classmethod
    def _getOptionsBoxControlFilter(cls, prevChoices, level):
        if prevChoices.filterChoice != cls.CASE_CONTROL_FILTER:
            return
        return cls._getOptionsBoxFilter(prevChoices, level, 'controlSelectValue')

    @classmethod
    def _getOptionsBoxControlSelectValue(cls, prevChoices, level):
        if prevChoices.filterChoice != cls.CASE_CONTROL_FILTER:
            return
        return cls._getOptionsBoxSelectValue(prevChoices, level, 'controlFilter',
                                             'controlMetadataColumn', 'controlSelectValue',
                                             'controlFilteredGSuiteTitles')

    @classmethod
    def _getOptionsBoxControlMetadataColumn(cls, prevChoices, level):
        if prevChoices.filterChoice != cls.CASE_CONTROL_FILTER:
            return
        return cls._getOptionsBoxMetadataColumn(prevChoices, level, 'controlFilter',
                                                'controlSelectValue')

    @classmethod
    def _getOptionsBoxControlFilteredGSuiteTitles(cls, prevChoices, level):
        if prevChoices.filterChoice != cls.CASE_CONTROL_FILTER:
            return
        return cls._getOptionsBoxFilteredGSuiteTitles(prevChoices, level, 'controlMetadataColumn',
                                                      'controlSelectValue',
                                                      'controlFilteredGSuiteTitles', isBase=False)

    @classmethod
    def getOptionsBoxBaseTrackTable(cls, prevChoices):
        if prevChoices.showBaseTrackTable == cls.NO:
            return

        return cls._getTrackTableFromFilteredTitles(prevChoices, 'baseFilteredGSuiteTitles')

    @classmethod
    def getOptionsBoxCaseTrackTable(cls, prevChoices):
        if prevChoices.showCaseTrackTable == cls.NO:
            return

        return cls._getTrackTableFromFilteredTitles(prevChoices, 'caseFilteredGSuiteTitles')

    @classmethod
    def getOptionsBoxControlTrackTable(cls, prevChoices):
        if prevChoices.showControlTrackTable == cls.NO:
            return

        return cls._getTrackTableFromFilteredTitles(prevChoices, 'controlFilteredGSuiteTitles')

    @classmethod
    def getOptionsBoxBaseNotSelectedTracks(cls, prevChoices):
        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        if not getattr(prevChoices, 'baseFilteredGSuiteTitles0'):
            return

        if prevChoices.filterChoice == cls.BASE_FILTER:
            return [cls.REMOVE_FROM_GSUITE]
        else:
            return [cls.KEEP_IN_GSUITE, cls.REMOVE_FROM_GSUITE]

    @classmethod
    def getOptionsBoxCaseControlNotSelectedTracks(cls, prevChoices):
        if prevChoices.filterChoice == cls.BASE_FILTER:
            return

        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        if not (getattr(prevChoices,'caseFilteredGSuiteTitles0') or getattr(prevChoices, 'controlFilteredGSuiteTitles0')):
            return

        if getattr(prevChoices, 'baseFilter0') == cls.NO_FILTER or prevChoices.baseNotSelectedTracks == cls.REMOVE_FROM_GSUITE:
            return [cls.KEEP_IN_GSUITE, cls.REMOVE_FROM_GSUITE]

        if prevChoices.baseNotSelectedTracks == cls.KEEP_IN_GSUITE:
            return [cls.KEEP_IN_GSUITE]


    @classmethod
    def getOptionsBoxGroupName(cls, prevChoices):
        if prevChoices.filterChoice not in [cls.CASE_FILTER, cls.CASE_CONTROL_FILTER]:

            return

        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        filteredTitles = cls._getFilteredTitles(prevChoices, 'caseFilteredGSuiteTitles')

        if not filteredTitles:
            return

        return 'new group'



    @classmethod
    def getOptionsBoxCaseGroupName(cls, prevChoices):
        if prevChoices.filterChoice not in [cls.CASE_FILTER, cls.CASE_CONTROL_FILTER]:
            return

        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        filteredTitles = cls._getFilteredTitles(prevChoices, 'caseFilteredGSuiteTitles')

        if not filteredTitles:
            return

        return 'case'

    @classmethod
    def getOptionsBoxControlGroupName(cls, prevChoices):
        if prevChoices.filterChoice != cls.CASE_CONTROL_FILTER:
            return

        if not prevChoices.gsuite or prevChoices.gsuite == cls.SELECT_CHOICE:
            return

        filteredTitles = cls._getFilteredTitles(prevChoices, 'controlFilteredGSuiteTitles')

        if not filteredTitles:
            return

        return 'control'


    @classmethod
    def _getSelectedValues(cls, prevChoices, level, inputBoxName):
        valsDict = getattr(prevChoices, (inputBoxName + '%s') % level)
        if valsDict:
            vals = [val for val, checked in valsDict.items() if checked]

            return vals

    @classmethod
    def _getFilteredValues(cls, prevChoices, level, filteredTitlesBoxName, metadataBoxName, lastTitles=None):
        gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
        if not lastTitles:
            lastTitles = getattr(prevChoices, (filteredTitlesBoxName + '%s') % (level - 1))
            if isinstance(lastTitles, unicode):
                lastTitles = ast.literal_eval(lastTitles)

        gsuiteVals = set()
        currentCol = getattr(prevChoices, (metadataBoxName + '%s') % level)

        for title in lastTitles:
            track = gsuite.getTrackFromTitle(title)
            attrVal = track.getAttribute(currentCol)
            gsuiteVals.add(attrVal)

        return list(gsuiteVals)

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
    @classmethod
    def getInputBoxGroups(cls, choices=None):
        """
        Creates a visual separation of groups of consecutive option boxes
        from the rest (fieldset). Each such group has an associated label
        (string), which is shown to the user. To define groups of option
        boxes, return a list of BoxGroup namedtuples with the label, the key
        (or index) of the first and last options boxes (inclusive).

        Example:
           from quick.webtool.GeneralGuiTool import BoxGroup
           return [BoxGroup(label='A group of choices', first='firstKey',
                            last='secondKey')]

        Optional method. Default return value if method is not defined: None
        """

        if not choices.gsuite or choices.gsuite == cls.SELECT_CHOICE:
            return

        groups = []
        groups.append(BoxGroup(label='Base', first='baseFilter0', last='baseTrackTable'))
        if choices.filterChoice == cls.CASE_FILTER:
            groups.append(BoxGroup(label='Case', first='caseFilter0', last='caseFilter' + str(cls.MAX_NUM_OF_FILTERS-1)))
        elif choices.filterChoice == cls.CASE_CONTROL_FILTER:
            groups.append(BoxGroup(label='Case', first='caseFilter0', last='caseFilter' + str(cls.MAX_NUM_OF_FILTERS - 1)))
            groups.append(BoxGroup(label='Control', first='controlFilter0', last='controlFilter' + str(cls.MAX_NUM_OF_FILTERS-1)))

        if hasattr(choices, 'baseFilteredGSuiteTitles0') and getattr(choices, 'baseFilteredGSuiteTitles0') and choices.showBaseTrackTable == cls.YES:
            groups.append(BoxGroup(
                label='Table of tracks which have passed all base filters',
                first='baseTrackTable', last='baseTrackTable'))

        if hasattr(choices, 'caseFilteredGSuiteTitles0') and getattr(choices, 'caseFilteredGSuiteTitles0') and choices.showCaseTrackTable == cls.YES:
            groups.append(BoxGroup(
                label='Table of tracks which have passed all case filters',
                first='caseTrackTable', last='caseTrackTable'))

        if hasattr(choices, 'controlFilteredGSuiteTitles0') and getattr(choices, 'controlFilteredGSuiteTitles0') and choices.showControlTrackTable == cls.YES:
            groups.append(BoxGroup(
                label='Table of tracks which have passed all control filters',
                first='controlTrackTable', last='controlTrackTable'))

        if choices.filterChoice in [cls.CASE_FILTER, cls.CASE_CONTROL_FILTER] and hasattr(choices, 'caseFilteredGSuiteTitles0') and getattr(choices, 'caseFilteredGSuiteTitles0'):
            groups.append(BoxGroup(label='A new metadata column will be created to denote the new group(s) of tracks, with the following characteristics:',
                                   first='groupName', last='controlGroupName'))

        if hasattr(choices, 'baseFilteredGSuiteTitles0') and getattr(choices, 'baseFilteredGSuiteTitles0'):
            groups.append(BoxGroup(label='Management of tracks that have been filtered out by base filters:',
                                   first='baseFilteredOutTracks', last='baseNotSelectedTracks'))

        if choices.filterChoice in [cls.CASE_FILTER, cls.CASE_CONTROL_FILTER]:
            if (hasattr(choices, 'caseFilteredFSuiteTitles0') and getattr(choices, 'caseFilteredFSuiteTitles0')) or (hasattr(choices, 'controlFilteredFSuiteTitles0') and getattr(choices, 'controlFilteredFSuiteTitles0')):
                groups.append(BoxGroup(label='Management of tracks that have been filtered out by case/control filters:',
                                       first='caseControlFilteredOutTracks', last='caseControlNotSelectedTracks'))

        return groups


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        """
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than
        'html', the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional
        files can be put (cls, e.g. generated image files). choices is a list
        of selections made by web-user in each options box.

        Mandatory unless isRedirectTool() returns True.
        """
        print 'Executing...'
        newGSuite = GSuite()

        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        baseFilteredTitles = cls._getValueOfLastInputBox(choices, 'baseFilteredGSuiteTitles')
        if isinstance(baseFilteredTitles, unicode):
            baseFilteredTitles = ast.literal_eval(baseFilteredTitles)
        if choices.filterChoice == cls.BASE_FILTER:
            for title in baseFilteredTitles:
                track = gsuite.getTrackFromTitle(title)
                newGSuite.addTrack(track)

        else:
            caseFilteredTitles = cls._getValueOfLastInputBox(choices, 'caseFilteredGSuiteTitles')
            if isinstance(caseFilteredTitles, unicode):
                caseFilteredTitles = ast.literal_eval(caseFilteredTitles)
            for title in caseFilteredTitles:
                track = gsuite.getTrackFromTitle(title)
                track.setAttribute(choices.groupName, choices.caseGroupName)
                newGSuite.addTrack(track)

            filteredTitles = caseFilteredTitles

            if choices.filterChoice == cls.CASE_CONTROL_FILTER:
                controlFilteredTitles = cls._getValueOfLastInputBox(choices,
                                                                 'controlFilteredGSuiteTitles')
                if isinstance(controlFilteredTitles, unicode):
                    controlFilteredTitles = ast.literal_eval(controlFilteredTitles)
                for title in controlFilteredTitles:
                    track = gsuite.getTrackFromTitle(title)
                    track.setAttribute(choices.groupName, choices.controlGroupName)
                    newGSuite.addTrack(track)

                filteredTitles += controlFilteredTitles

            if choices.baseNotSelectedTracks == cls.KEEP_IN_GSUITE:
                for title in gsuite.allTrackTitles():
                    if title not in filteredTitles:
                        track = gsuite.getTrackFromTitle(title)
                        track.setAttribute(choices.groupName, 'disabled')
                        newGSuite.addTrack(track)
            elif choices.baseNotSelectedTracks == cls.REMOVE_FROM_GSUITE:
                if choices.caseControlNotSelectedTracks == cls.KEEP_IN_GSUITE:
                    for title in baseFilteredTitles:
                        if title not in filteredTitles:
                            track = gsuite.getTrackFromTitle(title)
                            track.setAttribute(choices.groupName, 'disabled')
                            newGSuite.addTrack(track)

        GSuiteComposer.composeToFile(newGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None, which enables
        the execute button.

        Optional method. Default return value if method is not defined: None
        """

        if not choices.gsuite or choices.gsuite == cls.SELECT_CHOICE:
            return 'Please select a GSuite'

        if choices.filterChoice == cls.BASE_FILTER:
            if getattr(choices, 'baseFilter0') == cls.NO_FILTER:
                return 'Please select at least one filter for the base filtering.'
        else:
            if getattr(choices, 'caseFilter0') == cls.NO_FILTER:
                return 'Please select at least one filter for the case filtering.'
            if choices.filterChoice == cls.CASE_CONTROL_FILTER:
                if getattr(choices, 'controlFilter0') == cls.NO_FILTER:
                    return 'Please select at least one filter for the control filtering.'

        inputBoxNames = [('baseFilter', 'baseSelectValue'), ('caseFilter', 'caseSelectValue'), ('controlFilter', 'controlSelectValue')]

        for filterInput, valueInput in inputBoxNames:
            lastIndex = None
            for i in xrange(cls.MAX_NUM_OF_FILTERS):
                if not hasattr(choices, (filterInput + '%s') % i) or not getattr(
                        choices, (filterInput + '%s') % i):
                    break
                filterValue = getattr(choices, (filterInput + '%s') % i)
                if filterValue and filterValue != cls.NO_FILTER:
                    lastIndex = i

            if lastIndex is not None:
                vals = cls._getSelectedValues(choices, lastIndex, valueInput)

                if not vals:
                    return 'Please finish the values selection'

        if choices.filterChoice == cls.CASE_CONTROL_FILTER:
            caseFilteredTitles = cls._getValueOfLastInputBox(choices, 'caseFilteredGSuiteTitles')
            controlFilteredTitles = cls._getValueOfLastInputBox(choices, 'controlFilteredGSuiteTitles')

            if not caseFilteredTitles or not controlFilteredTitles:
                return

            intersectTitles = set(caseFilteredTitles).intersection(set(controlFilteredTitles))
            if intersectTitles:
                return 'These tracks were found in both case and control groups: ' + ', '.join(intersectTitles) + '. Please make sure each track is only present in one of the groups.'


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
        """
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as well as admin
        users, as defined in the galaxy.ini file.

        Optional method. Default return value if method is not defined: False
        """
        return True

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
        """
        The format of the history element with the output of the tool. Note
        that if 'html' is returned, any print statements in the execute()
        method is printed to the output dataset. For text-based output
        (e.g. bed) the output dataset only contains text written to the
        galaxyFn file, while all print statements are redirected to the info
        field of the history item box.

        Note that for 'html' output, standard HTML header and footer code is
        added to the output dataset. If one wants to write the complete HTML
        page, use the restricted output format 'customhtml' instead.

        Optional method. Default return value if method is not defined:
        'html'
        """
        return 'gsuite'
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

GroupGSuiteTracks.setupExtraBoxMethods()

