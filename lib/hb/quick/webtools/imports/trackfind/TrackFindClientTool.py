from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.trackfind.TrackFindModule import TrackFindModule
from functools import partial
from collections import OrderedDict
from proto.hyperbrowser.HtmlCore import HtmlCore
import operator
import gold.gsuite.GSuiteComposer as GSuiteComposer
from collections import defaultdict
from gold.gsuite.GSuite import GSuite
import quick.gsuite.GSuiteUtils as GSuiteUtils


class TrackFindClientTool(GeneralGuiTool):
    MAX_NUM_OF_EXTRA_BOXES = 10
    MAX_NUM_OF_SUB_LEVELS = 5
    SELECT_CHOICE = '--- Select ---'
    SINGLE_SELECTION = 'Single selection'
    MULTIPLE_SELECTION = 'Multiple selection'
    TEXT_SEARCH = 'Text search'
    ALL_TRACKS = 'Keep all tracks'
    RANDOM_10_TRACKS = 'Select 10 random tracks'
    RANDOM_50_TRACKS = 'Select 50 random tracks'
    MANUAL_TRACK_SELECT = 'Select tracks manually'
    
    TYPE_OF_DATA_ATTR = 'type->datatype_term'
    GENOME_ASSEMBLY_ATTR = 'genome_assembly'
    CELL_TISSUE_ATTR = 'sample->type->sample_type_term'
    TARGET_ATTR = 'experiment->target'
    FILE_FORMAT_ATTR = 'type->fileformat_term'
    

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "TrackFind client"


    @classmethod
    def getInputBoxNames(cls):
        attrBoxes = []
        attrBoxes.append(('Select repository: ', 'selectRepository'))

        selectAttributeStr = 'Select attribute: '
        for i in xrange(cls.MAX_NUM_OF_EXTRA_BOXES):
            attrBoxes.append((('', 'divider%s' % i)))
            for j in xrange(cls.MAX_NUM_OF_SUB_LEVELS):
                if j == 0:
                    attrBoxes.append((selectAttributeStr, \
                              'subAttributeList%s_%s' % (i,j)))
                else:
                    attrBoxes.append(((len(selectAttributeStr) + 6)*'&nbsp;' + (j*'&emsp;') + '|_', \
                                      'subAttributeList%s_%s' % (i, j)))
            attrBoxes.append(('Selection type:', \
                              'selectionType%s' % i))
            attrBoxes.append(('Text to search for', \
                              'textSearch%s' % i))
            attrBoxes.append(('Select value:', \
                              'valueList%s' % i))
            attrBoxes.append(('Select value:', \
                              'valueCheckbox%s' % i))
        attrBoxes.append(('Select type of data', 'dataTypes'))
        attrBoxes.append(('Select tracks', 'selectTracks'))
        attrBoxes.append(('Select tracks manually', 'selectTracksManually'))
        attrBoxes.append(('Found tracks: ', 'trackList'))


        return attrBoxes

    @classmethod
    def setupExtraBoxMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_EXTRA_BOXES):
            setattr(cls, 'getOptionsBoxValueList%s' % i, \
                    partial(cls._getValueListBox, index=i))
            setattr(cls, 'getOptionsBoxValueCheckbox%s' % i, \
                    partial(cls._getValueCheckboxBox, index=i))
            setattr(cls, 'getOptionsBoxDivider%s' % i, partial(cls._getDivider, index=i))
            setattr(cls, 'getOptionsBoxTextSearch%s' % i, \
                    partial(cls._getTextSearchBox, index=i))
            for j in xrange(cls.MAX_NUM_OF_SUB_LEVELS):
                setattr(cls, 'getOptionsBoxSubAttributeList%s_%s' % (i,j), \
                        partial(cls._getSubAttributeListBox, level=i, index=j))
            setattr(cls, 'getOptionsBoxSelectionType%s' % i, \
                    partial(cls._getSelectionTypeBox, index=i))

    @classmethod
    def getOptionsBoxSelectRepository(cls):
        tfm = TrackFindModule()
        hubs = tfm.getRepositories()
        repos = []
        for hub in hubs:
            repos.append(hub['repository'] + ' - ' + hub['hub'])

        repos.sort()
        repos.insert(0, cls.SELECT_CHOICE)

        return repos

    @classmethod
    def _getDivider(cls, prevChoices, index):
        if prevChoices.selectRepository in [None, cls.SELECT_CHOICE, '']:
            return

        if index > 0 and getattr(prevChoices, 'valueList%s' % (index - 1)) \
                in [None, cls.SELECT_CHOICE, '']:
            return

        return '__rawstr__', str(HtmlCore().divider())



    @classmethod
    def _getSubAttributeListBox(cls, prevChoices, level, index):
        if level == 0 and prevChoices.selectRepository in [None, cls.SELECT_CHOICE, '']:
            return

        if index > 0 and getattr(prevChoices, 'subAttributeList%s_%s' % (level, index-1)) in [None, cls.SELECT_CHOICE, '']:
            return
        if level > 0 and getattr(prevChoices, 'subAttributeList%s_%s' % (level-1, 0)) in [None, cls.SELECT_CHOICE, '']:
            return
        if index == 0 and level > 0:
            prev = getattr(prevChoices, 'valueList%s' % (level - 1))
            if prev in [None, cls.SELECT_CHOICE, '']:
                return
            elif type(prev) is OrderedDict:
                if True not in prev.values():
                    return

        subattributePath = ''
        if index == 0:
            tfm = TrackFindModule()
            attributes = tfm.getTopLevelAttributesForRepository(prevChoices.selectRepository)

        else:
            attributes, subattributePath = cls.getSubattributes(prevChoices, level, index)
            if cls.isBottomLevel(attributes):
                return

        #filter out previously chosen attributes
        prevChoicesList = []
        if level > 0:
            for l in xrange(level):
                subattributes = []
                for i in xrange(cls.MAX_NUM_OF_SUB_LEVELS):
                    attr = getattr(prevChoices, 'subAttributeList%s_%s' % (l, i))
                    if attr is None or attr == '':
                        break
                    subattributes.append(attr)
                path = ('->'.join(subattributes))
                prevChoicesList.append(path)

        currentChoicesMap = {}
        for attr in attributes:
            if subattributePath:
                currentChoicesMap[subattributePath + '->' + attr] = attr
            else:
                currentChoicesMap[attr] = attr

        for choice in currentChoicesMap.keys():
            if choice in prevChoicesList:
                attributes.remove(currentChoicesMap[choice])
                currentChoicesMap.pop(choice)

        if not attributes:
            return

        #filter out attributes that have no subattributes left
        tfm = TrackFindModule()
        attributesInRepo = tfm.getAttributesForRepository(prevChoices.selectRepository)

        for prevChoice in prevChoicesList:
            if prevChoice in attributesInRepo:
                attributesInRepo.remove(prevChoice)

        for choice in currentChoicesMap.keys():
            found = False
            for repoAttr in attributesInRepo:
                if repoAttr.startswith(choice + '->') or repoAttr == choice:
                    found = True
                    break
            if not found:
                attributes.remove(currentChoicesMap[choice])

        if not attributes:
            return

        attributes.sort()
        attributes.insert(0, cls.SELECT_CHOICE)

        return attributes

    @classmethod
    def _getValueListBox(cls, prevChoices, index):
        if index > 0 and getattr(prevChoices, 'valueList%s' % (index - 1)) \
                in [None, cls.SELECT_CHOICE, '']:
            return

        selectionType = getattr(prevChoices, 'selectionType%s' % index)
        if selectionType != cls.SINGLE_SELECTION:
            return

        values = cls.getValues(prevChoices, index)[0]

        values.insert(0, cls.SELECT_CHOICE)
        return values

    @classmethod
    def _getValueCheckboxBox(cls, prevChoices, index):
        if index > 0 and getattr(prevChoices, 'valueList%s' % (index - 1)) \
                in [None, cls.SELECT_CHOICE, '']:
            return
        selectionType = getattr(prevChoices, 'selectionType%s' % index)
        if selectionType not in [cls.MULTIPLE_SELECTION, cls.TEXT_SEARCH]:
            return

        values, subattributePath = cls.getValues(prevChoices, index)

        if getattr(prevChoices, 'selectionType%s' % index) == cls.MULTIPLE_SELECTION:
            return OrderedDict([(value, False) for value in values])
        else:
            searchTerm = getattr(prevChoices, 'textSearch%s' % index)
            if not searchTerm:
                return
            tfm = TrackFindModule()
            filteredValues = tfm.getAttributeValues(prevChoices.selectRepository,
                                                    subattributePath, searchTerm)

            valuesDict = OrderedDict()
            for value in values:
                if value in filteredValues:
                    valuesDict[value] = True
                else:
                    valuesDict[value] = False
            return valuesDict


    @classmethod
    def getValues(cls, prevChoices, index):
        prevSubattributes = []
        for i in xrange(cls.MAX_NUM_OF_SUB_LEVELS):
            attr = getattr(prevChoices, 'subAttributeList%s_%s' % (index, i))
            if attr is None:
                break

            prevSubattributes.append(attr)

        subattributePath = ('->'.join(prevSubattributes))

        tfm = TrackFindModule()
        if index == 0:
            values = tfm.getAttributeValues(prevChoices.selectRepository, subattributePath)
        else:
            chosenOptions = cls.getPreviousChoices(prevChoices, index)
            jsonData = tfm.getJsonData(prevChoices.selectRepository, chosenOptions)

            values = set()
            for jsonItem in jsonData:
                try:
                    value = reduce(operator.getitem, prevSubattributes, jsonItem)
                except (KeyError, TypeError):
                    continue
                if value:
                    values.add(value)

        values = list(values)
        values.sort()

        return values, subattributePath


    @classmethod
    def _getSelectionTypeBox(cls, prevChoices, index):
        if prevChoices.selectRepository in [None, cls.SELECT_CHOICE, '']:
            return

        if getattr(prevChoices, 'subAttributeList%s_%s' % (index, 0)) in [None, cls.SELECT_CHOICE, '']:
            return

        attributes = cls.getSubattributes(prevChoices, index, cls.MAX_NUM_OF_SUB_LEVELS)[0]

        if cls.isBottomLevel(attributes):
            return [cls.SINGLE_SELECTION, cls.MULTIPLE_SELECTION, cls.TEXT_SEARCH]

    @classmethod
    def _getTextSearchBox(cls, prevChoices, index):
        attribute = getattr(prevChoices, 'selectionType%s' % index)
        if attribute == cls.TEXT_SEARCH:
            return ''
        else:
            return '__hidden__', ''


    @classmethod
    def getGsuite(cls, prevChoices):
        chosenOptions = cls.getPreviousChoices(prevChoices, cls.MAX_NUM_OF_EXTRA_BOXES)

        if not chosenOptions:
            return

        tfm = TrackFindModule()
        gsuite = tfm.getGSuite(prevChoices.selectRepository, chosenOptions)

        return gsuite

    @classmethod
    def getOptionsBoxTrackList(cls, prevChoices):
        chosenDataTypes = cls.getChosenDataTypes(prevChoices)
        if not chosenDataTypes:
            return

        selectedTracks = cls.getSelectedTracks(prevChoices)
        gsuite = cls.getGsuite(prevChoices)

        tableDict = {}
        for track in gsuite.allTracks():
            title = track.title
            attributes = []
            dataType = track.getAttribute(cls.TYPE_OF_DATA_ATTR)

            if dataType not in chosenDataTypes:
                continue
            if selectedTracks is not None and title not in selectedTracks:
                continue

            attributes.append(dataType)
            attributes.append(track.getAttribute(cls.CELL_TISSUE_ATTR))
            attributes.append(track.getAttribute(cls.TARGET_ATTR))
            attributes.append(track.getAttribute(cls.GENOME_ASSEMBLY_ATTR))
            attributes.append(track.getAttribute(cls.FILE_FORMAT_ATTR))
            tableDict[title] = attributes

        if not tableDict:
            return

        html = HtmlCore()
        html.tableFromDictionary(tableDict, columnNames=['Sample name', 'Type of data', 'Cell/tissue type', 'Target', 'Genome build', 'File format'],  \
                                 tableId='t1', expandable=True)

        return '__rawstr__', unicode(html)

    @classmethod
    def getOptionsBoxDataTypes(cls, prevChoices):
        chosenOptions = cls.getPreviousChoices(prevChoices, cls.MAX_NUM_OF_EXTRA_BOXES)

        if not chosenOptions:
            return

        dataTypes = defaultdict(int)

        gsuite = cls.getGsuite(prevChoices)

        for track in gsuite.allTracks():
            attr = track.getAttribute(cls.TYPE_OF_DATA_ATTR)
            if attr:
                dataTypes[attr] += 1

        if not dataTypes:
            return []

        dataTypes = OrderedDict(sorted(dataTypes.items()))

        dataTypesOutput = OrderedDict()
        for dataType, count in dataTypes.iteritems():
            dataTypesOutput[dataType + ' [' + str(count) + ' files found]'] = True

        return dataTypesOutput

    @classmethod
    def getOptionsBoxSelectTracks(cls, prevChoices):
        chosenOptions = cls.getPreviousChoices(prevChoices, cls.MAX_NUM_OF_EXTRA_BOXES)

        if not chosenOptions:
            return

        return [cls.ALL_TRACKS, cls.RANDOM_10_TRACKS, cls.RANDOM_50_TRACKS, cls.MANUAL_TRACK_SELECT]

    @classmethod
    def getOptionsBoxSelectTracksManually(cls, prevChoices):
        if not prevChoices.selectTracks == cls.MANUAL_TRACK_SELECT:
            return

        chosenDataTypes = cls.getChosenDataTypes(prevChoices)
        if not chosenDataTypes:
            return

        trackTitles = []

        gsuite = cls.getGsuite(prevChoices)

        for track in gsuite.allTracks():
            dataType = track.getAttribute(cls.TYPE_OF_DATA_ATTR)

            if dataType not in chosenDataTypes:
                continue

            trackTitles.append(track.title)

        return OrderedDict([(title, True) for title in trackTitles])


    @classmethod
    def getSubattributes(cls, prevChoices, level, index):
        prevSubattributes = []
        for i in xrange(index):
            attr = getattr(prevChoices, 'subAttributeList%s_%s' % (level, i))
            if attr is None or attr == cls.SELECT_CHOICE:
                break

            prevSubattributes.append(attr)

        tfm = TrackFindModule()
        subattributePath = ('->'.join(prevSubattributes))

        attributes = tfm.getSubLevelAttributesForRepository(prevChoices.selectRepository,
                                                            subattributePath)

        return attributes, subattributePath

    @classmethod
    def getPreviousChoices(cls, prevChoices, level):
        chosenOptions = {}
        for i in xrange(level):
            val = getattr(prevChoices, 'valueList%s' % i)
            if val in [None, cls.SELECT_CHOICE, '']:
                break

            subattributes = []
            for j in xrange(cls.MAX_NUM_OF_SUB_LEVELS):
                attr = getattr(prevChoices, 'subAttributeList%s_%s' % (i, j))
                if attr in [None, cls.SELECT_CHOICE, '']:
                    break
                subattributes.append("'{}'".format(attr))
            path = ('->'.join(subattributes))

            if type(val) is OrderedDict:
                chosenOptions[path] = [option for option, checked in val.items() if checked]
            else:
                chosenOptions[path] = val

        return chosenOptions

    @classmethod
    def getChosenDataTypes(cls, prevChoices):
        chosenOptions = cls.getPreviousChoices(prevChoices, cls.MAX_NUM_OF_EXTRA_BOXES)

        if not chosenOptions:
            return

        dataTypes = prevChoices.dataTypes
        if not dataTypes:
            return

        chosenDataTypes = [option.split(' [')[0] for option, checked in
                           prevChoices.dataTypes.items() if checked]

        return chosenDataTypes

    
    @classmethod
    def isBottomLevel(cls, attributes):
        if not attributes:
            return True

    @classmethod
    def getSelectedTracks(cls, prevChoices):
        if prevChoices.selectTracks != cls.MANUAL_TRACK_SELECT:
            return None
        selectedTracks = [track for track, checked in prevChoices.selectTracksManually.items()
                              if checked]

        return selectedTracks


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

        chosenDataTypes = cls.getChosenDataTypes(choices)
        if not chosenDataTypes:
            return

        selectedTracks = cls.getSelectedTracks(choices)

        newGSuite = GSuite()
        gsuite = cls.getGsuite(choices)

        for track in gsuite.allTracks():
            dataType = track.getAttribute(cls.TYPE_OF_DATA_ATTR)

            if not dataType in chosenDataTypes:
                continue
            if selectedTracks is not None and track.title not in selectedTracks:
                continue

            newGSuite.addTrack(track)

        if choices.selectTracks == cls.RANDOM_10_TRACKS:
            newGSuite = GSuiteUtils.getRandomGSuite(newGSuite, 10)
        elif choices.selectTracks == cls.RANDOM_50_TRACKS:
            newGSuite = GSuiteUtils.getRandomGSuite(newGSuite, 50)

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
    @classmethod
    def getResetBoxes(cls):
        """
        Specifies a list of input boxes which resets the subsequent stored
        choices previously made. The input boxes are specified by index
        (starting with 1) or by key.

        Optional method. Default return value if method is not defined: True
        """

        boxes = []
        #boxes.append('selectRepository')
        for i in xrange(cls.MAX_NUM_OF_EXTRA_BOXES):
            boxes.append('textSearch%s' % i)

        return boxes

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

    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
    #     """
    #     The title (name) of the main output history element.
    #
    #     Optional method. Default return value if method is not defined:
    #     the name of the tool.
    #     """

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

TrackFindClientTool.setupExtraBoxMethods()