import time
from collections import OrderedDict
from collections import defaultdict
from copy import copy
from functools import partial
from ast import literal_eval

import gold.gsuite.GSuiteComposer as GSuiteComposer
import quick.gsuite.GSuiteUtils as GSuiteUtils
from gold.gsuite.GSuite import GSuite
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.trackfind.TrackFindModule import TrackFindModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

import logging
log = logging.getLogger( __name__ )


class TrackFindClientTool(GeneralGuiTool):
    MAX_NUM_OF_LEVELS = 7
    MAX_NUM_OF_SUB_LEVELS = 5
    SELECT_CHOICE = '--- Select ---'
    SINGLE_SELECTION = 'Single selection'
    MULTIPLE_SELECTION = 'Multiple selection'
    TEXT_SEARCH = 'Text search'
    ALL_TRACKS = 'Keep all tracks'
    RANDOM_10_TRACKS = 'Select 10 random tracks'
    RANDOM_50_TRACKS = 'Select 50 random tracks'
    MANUAL_TRACK_SELECT = 'Select tracks manually'

    CELL_TISSUE_PATH = ['samples', 'sample_type', 'summary']
    EXPERIMENT_TYPE_PATH = ['experiments', 'technique', 'term_label']
    GENOME_ASSEMBLY_PATH = ['tracks', 'assembly_name']
    TARGET_PATH = ['experiments', 'target', 'summary']
    FILE_FORMAT_PATH = ['tracks', 'file_format', 'term_label']
    TYPE_OF_DATA_PATH = ['tracks', 'type_of_condensed_data']
    PHENOTYPE_PATH = ['samples', 'phenotype', 'term_label']
    GEOMETRIC_TRACK_TYPE_PATH = ['tracks', 'geometric_track_type']
    LONG_LABEL_PATH = ['tracks', 'label_long']

    CELL_TISSUE_ATTR = '->'.join(CELL_TISSUE_PATH)
    GENOME_ASSEMBLY_ATTR = '->'.join(GENOME_ASSEMBLY_PATH[1:])
    TARGET_ATTR = '->'.join(TARGET_PATH)
    FILE_FORMAT_ATTR = '->'.join(FILE_FORMAT_PATH[1:])
    TYPE_OF_DATA_ATTR = '->'.join(TYPE_OF_DATA_PATH[1:])
    LONG_LABEL_ATTR = '->'.join(LONG_LABEL_PATH[1:])
    PHENOTYPE_ATTR = '->'.join(PHENOTYPE_PATH)
    GEOMETRIC_TRACK_TYPE_ATTR = '->'.join(GEOMETRIC_TRACK_TYPE_PATH[1:])
    
    TABLE_ATTRIBUTES = [CELL_TISSUE_PATH, GENOME_ASSEMBLY_PATH, TARGET_PATH, FILE_FORMAT_PATH,
                        TYPE_OF_DATA_PATH, LONG_LABEL_PATH, PHENOTYPE_PATH, GEOMETRIC_TRACK_TYPE_PATH]

    FILE_URL_PATH = ['tracks', 'file_url']
    LABEL_SHORT_PATH = ['tracks', 'label_short']
    ASSEMBLY_NAME_PATH = ['tracks', 'assembly_name']

    GSUITE_REQUIRED_ATTRS = [FILE_URL_PATH, LABEL_SHORT_PATH, ASSEMBLY_NAME_PATH]

    YES = 'Yes'
    NO = 'No'

    ATTRIBUTE_SHORTCUTS = OrderedDict([('* Cell/Tissue type', CELL_TISSUE_PATH),
                          ('* Experiment type', EXPERIMENT_TYPE_PATH),
                          ('* Genome assembly', GENOME_ASSEMBLY_PATH),
                          ('* Target', TARGET_PATH),
                          ('* File format', FILE_FORMAT_PATH),
                          ('* Type of condensed data', TYPE_OF_DATA_PATH),
                          ('* Phenotype', PHENOTYPE_PATH),
                          ('* Geometric track type', GEOMETRIC_TRACK_TYPE_PATH)])

    TRACK_TABLE_LIMIT = 50

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
        attrBoxes.append(('', 'categories'))

        selectAttributeStr = 'Select attribute: '
        for i in xrange(cls.MAX_NUM_OF_LEVELS):
            attrBoxes.append(('', 'divider%s' % i))
            for j in xrange(cls.MAX_NUM_OF_SUB_LEVELS):
                if j == 0:
                    attrBoxes.append((selectAttributeStr, 'subAttributeList%s_%s' % (i,j)))
                else:
                    attrBoxes.append(((len(selectAttributeStr) + 6)*'&nbsp;' + (j*'&emsp;') + '|_',
                                      'subAttributeList%s_%s' % (i, j)))
            attrBoxes.append(('Selection type:', 'selectionType%s' % i))
            attrBoxes.append(('Text to search for', 'textSearch%s' % i))
            attrBoxes.append(('Select value:', 'valueList%s' % i))
            attrBoxes.append(('Select value:', 'valueCheckbox%s' % i))
        attrBoxes.append(('', 'gsuite'))
        attrBoxes.append(('', 'gsuiteHash'))
        attrBoxes.append(('Select type of condensed data', 'dataTypes'))
        attrBoxes.append(('Select tracks', 'selectTracks'))
        attrBoxes.append(('Select tracks manually', 'selectTracksManually'))
        attrBoxes.append(('', 'selectRandomTracks'))
        attrBoxes.append(('By default, only the first ' + str(cls.TRACK_TABLE_LIMIT) +
                          ' tracks are displayed. Do you want to display all?', 'displayAllTracks'))
        attrBoxes.append(('Found tracks: ', 'trackList'))
        attrBoxes.append(('Include non-standard attributes in the result GSuite', 'extraAttributes'))

        return attrBoxes

    @classmethod
    def setupExtraBoxMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_LEVELS):
            setattr(cls, 'getOptionsBoxValueList%s' % i, partial(cls._getValueListBox, level=i))
            setattr(cls, 'getOptionsBoxValueCheckbox%s' % i, partial(cls._getValueCheckboxBox, level=i))
            setattr(cls, 'getOptionsBoxDivider%s' % i, partial(cls._getDivider, level=i))
            setattr(cls, 'getOptionsBoxTextSearch%s' % i, partial(cls._getTextSearchBox, level=i))
            for j in xrange(cls.MAX_NUM_OF_SUB_LEVELS):
                setattr(cls, 'getOptionsBoxSubAttributeList%s_%s' % (i,j),
                        partial(cls._getSubAttributeListBox, level=i, index=j))
            setattr(cls, 'getOptionsBoxSelectionType%s' % i,
                    partial(cls._getSelectionTypeBox, level=i))

    @classmethod
    def _getDivider(cls, prevChoices, level):
        if not cls.getChoice(prevChoices, 'selectRepository'):
            return

        if level > 0 and not cls.getChosenValues(prevChoices, level - 1):
            return

        return '__rawstr__', str(HtmlCore().divider())

    @classmethod
    def getOptionsBoxSelectRepository(cls):
        tfm = TrackFindModule()
        repos = tfm.getRepositories()
        reposAndHubs = []
        for repo in repos:
            hubs = tfm.getHubs(repo)
            for hub in hubs:
                reposAndHubs.append(repo + ' - ' + hub)

        reposAndHubs.sort()
        reposAndHubs.insert(0, cls.SELECT_CHOICE)

        return reposAndHubs

    @classmethod
    def getOptionsBoxCategories(cls, prevChoices):
        if not cls.getChoice(prevChoices, 'selectRepository'):
            return

        tfm = TrackFindModule()
        categories = tfm.getCategoriesForRepository(prevChoices.selectRepository)
        categories.sort()
        return '__hidden__', categories

    @classmethod
    def _getSubAttributeListBox(cls, prevChoices, level, index):
        if not cls.getChoice(prevChoices, 'selectRepository'):
            return

        if level > 0 and not cls.getChoice(prevChoices, 'subAttributeList', level - 1, 0):
            return
        if index > 0 and not cls.getChoice(prevChoices, 'subAttributeList', level, index - 1):
            return

        if index == 0:
            if level > 0:
                vals = cls.getChosenValues(prevChoices, level-1)
                if not vals:
                    return
                if type(vals) is OrderedDict:
                    if True not in vals.values():
                        return
            attributes = copy(prevChoices.categories)
            # add shortcuts to most used attributes
            for shortcut in cls.ATTRIBUTE_SHORTCUTS:
                attributes.insert(0, shortcut)
        else:
            attributes = cls.getSubattributes(prevChoices, level, index)
            if cls.isBottomLevel(attributes):
                return

            attributes.sort()

        attributes.insert(0, cls.SELECT_CHOICE)

        return attributes

    @classmethod
    def _getSelectionTypeBox(cls, prevChoices, level):
        if not cls.getChoice(prevChoices, 'selectRepository'):
            return

        if not cls.getChoice(prevChoices, 'subAttributeList', level, 0):
            return

        attributes = cls.getSubattributes(prevChoices, level)

        if cls.isBottomLevel(attributes):
            return [cls.SINGLE_SELECTION, cls.MULTIPLE_SELECTION, cls.TEXT_SEARCH]

    @classmethod
    def _getTextSearchBox(cls, prevChoices, level):
        attribute = cls.getChoice(prevChoices, 'selectionType', level)
        if attribute == cls.TEXT_SEARCH:
            return ''
        else:
            return '__hidden__', ''

    @classmethod
    def _getValueListBox(cls, prevChoices, level):
        if level > 0 and not cls.getChosenValues(prevChoices, level-1):
            return

        selectionType = cls.getChoice(prevChoices, 'selectionType', level)
        if selectionType != cls.SINGLE_SELECTION:
            return

        values = cls.getValues(prevChoices, level)
        values.insert(0, cls.SELECT_CHOICE)

        return values

    @classmethod
    def _getValueCheckboxBox(cls, prevChoices, level):
        if level > 0 and not cls.getChosenValues(prevChoices, level-1):
            return

        selectionType = cls.getChoice(prevChoices, 'selectionType', level)
        if selectionType not in [cls.MULTIPLE_SELECTION, cls.TEXT_SEARCH]:
            return

        values = cls.getValues(prevChoices, level)

        if selectionType == cls.MULTIPLE_SELECTION:
            return OrderedDict([(value, False) for value in values])
        else:
            searchTerm = cls.getChoice(prevChoices, 'textSearch', level)
            if not searchTerm:
                return OrderedDict([(value, True) for value in values])

            tfm = TrackFindModule()
            subattributePath = cls.getSubattributePath(prevChoices, level)
            filteredValues = tfm.getAttributeValues(prevChoices.selectRepository,
                                                    subattributePath, searchTerm=searchTerm)

            valuesDict = OrderedDict()
            for value in values:
                if value in filteredValues:
                    valuesDict[value] = True
                else:
                    valuesDict[value] = False
            return valuesDict

    @classmethod
    def getOptionsBoxGsuite(cls, prevChoices):
        chosenOptions = cls.getPreviousChoices(prevChoices)

        if not chosenOptions:
            return

        tfm = TrackFindModule()
        gsuite = tfm.getGSuite(prevChoices.selectRepository, chosenOptions, attrFilter=cls.TABLE_ATTRIBUTES +cls.GSUITE_REQUIRED_ATTRS )

        return '__hidden__', gsuite

    @classmethod
    def getOptionsBoxGsuiteHash(cls, prevChoices):
        gsuite = prevChoices.gsuite
        if gsuite:
            gsuiteHash = hash(tuple(sorted(hash(track.uri) for track in gsuite.allTracks())))
        else:
            gsuiteHash = ''

        return '__hidden__', gsuiteHash

    @classmethod
    def getOptionsBoxDataTypes(cls, prevChoices):
        if not prevChoices.gsuite:
            return

        if not cls.isSelectionComplete(prevChoices):
            return

        dataTypes = defaultdict(int)
        gsuite = cls.getGSuite(prevChoices)

        for track in gsuite.allTracks():
            attr = track.getAttribute(cls.TYPE_OF_DATA_ATTR)
            if attr:
                dataTypes[attr] += 1

        dataTypes = OrderedDict(sorted(dataTypes.items()))

        dataTypesOutput = OrderedDict()
        for dataType, count in dataTypes.iteritems():
            dataTypesOutput[dataType + ' [' + str(count) + ' files found]'] = True

        return dataTypesOutput

    @classmethod
    def getOptionsBoxSelectTracks(cls, prevChoices):
        if not prevChoices.gsuite:
            return

        chosenDataTypes = cls.getChosenDataTypes(prevChoices)
        if not chosenDataTypes:
            return

        return [cls.ALL_TRACKS, cls.RANDOM_10_TRACKS, cls.RANDOM_50_TRACKS, cls.MANUAL_TRACK_SELECT]

    @classmethod
    def getOptionsBoxSelectTracksManually(cls, prevChoices):
        if prevChoices.selectTracks != cls.MANUAL_TRACK_SELECT:
            return

        chosenDataTypes = cls.getChosenDataTypes(prevChoices)
        if not chosenDataTypes:
            return

        trackTitles = []
        gsuite = cls.getGSuite(prevChoices)

        for track in gsuite.allTracks():
            dataType = track.getAttribute(cls.TYPE_OF_DATA_ATTR)

            if dataType not in chosenDataTypes:
                continue

            if prevChoices.selectTracks == cls.MANUAL_TRACK_SELECT:
                trackTitles.append(track.title)

        return OrderedDict([(title, True) for title in trackTitles])

    @classmethod
    def getOptionsBoxSelectRandomTracks(cls, prevChoices):
        if prevChoices.selectTracks not in (cls.RANDOM_10_TRACKS, cls.RANDOM_50_TRACKS):
            return

        chosenDataTypes = cls.getChosenDataTypes(prevChoices)
        if not chosenDataTypes:
            return

        gsuite = cls.getGSuite(prevChoices)

        filteredGsuite = GSuite()
        for track in gsuite.allTracks():
            dataType = track.getAttribute(cls.TYPE_OF_DATA_ATTR)

            if dataType not in chosenDataTypes:
                continue

            filteredGsuite.addTrack(track)

        if prevChoices.selectTracks == cls.RANDOM_10_TRACKS:
            randomTracks = GSuiteUtils.getRandomTracks(filteredGsuite, 10, seed=time.time())
        else:
            randomTracks = GSuiteUtils.getRandomTracks(filteredGsuite, 50, seed=time.time())

        return '__hidden__', [track.title for track in randomTracks]

    @classmethod
    def getOptionsBoxDisplayAllTracks(cls, prevChoices):
        chosenDataTypes = cls.getChosenDataTypes(prevChoices)
        if not chosenDataTypes:
            return

        selectedTracks = cls.getSelectedTracks(prevChoices)

        gsuite = cls.getGSuite(prevChoices)
        numTracks = gsuite.numTracks()
        if numTracks < cls.TRACK_TABLE_LIMIT:
            return

        counter = 0
        for track in gsuite.allTracks():
            if counter > cls.TRACK_TABLE_LIMIT:
                break
            title = track.title

            dataType = track.getAttribute(cls.TYPE_OF_DATA_ATTR)

            if selectedTracks is not None and title not in selectedTracks:
                continue
            if dataType and dataType not in chosenDataTypes:
                continue

            counter += 1

        if counter < cls.TRACK_TABLE_LIMIT:
            return

        return [cls.NO, cls.YES]

    @classmethod
    def getOptionsBoxTrackList(cls, prevChoices):
        chosenDataTypes = cls.getChosenDataTypes(prevChoices)
        if not chosenDataTypes:
            return

        selectedTracks = cls.getSelectedTracks(prevChoices)
        gsuite = cls.getGSuite(prevChoices)

        tableDict = {}
        counter = 0
        for track in gsuite.allTracks():
            if counter == cls.TRACK_TABLE_LIMIT and prevChoices.displayAllTracks != cls.YES:
                break
            title = track.getAttribute(cls.LONG_LABEL_ATTR)
            attributes = []
            dataType = track.getAttribute(cls.TYPE_OF_DATA_ATTR)

            if dataType and dataType not in chosenDataTypes:
                continue
            if selectedTracks is not None and title not in selectedTracks:
                continue

            attributes.append(track.getAttribute(cls.GENOME_ASSEMBLY_ATTR))
            attributes.append(track.getAttribute(cls.PHENOTYPE_ATTR))
            attributes.append(track.getAttribute(cls.CELL_TISSUE_ATTR))
            attributes.append(track.getAttribute(cls.TARGET_ATTR))
            attributes.append(dataType)
            attributes.append(track.getAttribute(cls.GEOMETRIC_TRACK_TYPE_ATTR))
            attributes.append(track.getAttribute(cls.FILE_FORMAT_ATTR))
            tableDict[title] = attributes

            counter += 1

        if not tableDict:
            return

        html = HtmlCore()
        html.tableFromDictionary(tableDict,
                                 columnNames=['Track title', 'Genome build', 'Phenotype',  'Cell/tissue type',
                                              'Target', 'Type of condensed data', 'Geometric track type', 'File format'],
                                 tableId='t1', expandable=True)

        return '__rawstr__', unicode(html)

    @classmethod
    def getOptionsBoxExtraAttributes(cls, prevChoices):
        if not prevChoices.gsuite:
            return

        chosenDataTypes = cls.getChosenDataTypes(prevChoices)
        if not chosenDataTypes:
            return

        return [cls.NO, cls.YES]

    @classmethod
    def getSubattributes(cls, prevChoices, level, index=None):
        subattributePath = cls.getSubattributePath(prevChoices, level, index=index)

        tfm = TrackFindModule()
        attributes = tfm.getSubLevelAttributesForRepository(prevChoices.selectRepository,
                                                            subattributePath)

        return attributes

    @classmethod
    def getSubattributePath(cls, prevChoices, level, inQueryForm=False, index=None):
        prevSubattributes = []
        if index:
            maxIndex = index
        else:
            maxIndex = cls.MAX_NUM_OF_SUB_LEVELS
        for i in range(maxIndex):
            if hasattr(prevChoices, 'subAttributeList%s_%s' % (level, i)):
                attr = cls.getChoice(prevChoices, 'subAttributeList', level, i)
                if not attr or attr == cls.SELECT_CHOICE:
                    break

                if attr.startswith('* '):
                    prevSubattributes = cls.ATTRIBUTE_SHORTCUTS[attr]
                    break

                else:
                    prevSubattributes.append(attr)

        if not prevSubattributes:
            return

        if inQueryForm:
            prevSubattributes = cls.convertAttributesToQueryForm(prevSubattributes)
        subattributePath = ('->'.join(prevSubattributes))

        return subattributePath

    @classmethod
    def getValues(cls, prevChoices, level):
        subattributePath = cls.getSubattributePath(prevChoices, level)

        tfm = TrackFindModule()
        if level == 0:
            values = tfm.getAttributeValues(prevChoices.selectRepository, subattributePath)
        else:
            chosenOptions = cls.getPreviousChoices(prevChoices, level)
            values = tfm.getAttributeValues(prevChoices.selectRepository, subattributePath,
                                            attrValueMap=chosenOptions)

        values.sort()

        return values

    @classmethod
    def convertAttributesToQueryForm(cls, subattrList):
        convertedSubattrs = [subattrList[0] + '.content']
        for subattr in subattrList[1:]:
            convertedSubattrs.append("'{}'".format(subattr))

        return convertedSubattrs

    @classmethod
    def getPreviousChoices(cls, prevChoices, maxLevel=MAX_NUM_OF_LEVELS, inQueryForm=True):
        chosenOptions = {}
        for level in range(maxLevel):
            path = cls.getSubattributePath(prevChoices, level, inQueryForm=inQueryForm)
            if not path:
                break

            val = cls.getChosenValues(prevChoices, level)
            if not val:
                break
            if type(val) is OrderedDict:
                options = [option for option, checked in val.items() if checked]
                if options:
                    chosenOptions[path] = options
            else:
                chosenOptions[path] = val

        return chosenOptions

    @classmethod
    def getChosenDataTypes(cls, prevChoices):
        dataTypes = prevChoices.dataTypes
        if not dataTypes:
            return

        chosenDataTypes = [option.split(' [')[0] for option, checked in
                           dataTypes.items() if checked]

        return chosenDataTypes

    @classmethod
    def getGSuite(cls, prevChoices, includeExtraAttributes=False):
        if not includeExtraAttributes:
            gsuite = prevChoices.gsuite

        else:
            tfm = TrackFindModule()
            chosenOptions = cls.getPreviousChoices(prevChoices)
            gsuite = tfm.getGSuite(prevChoices.selectRepository, chosenOptions,
                                   includeExtraAttributes=True)

        return gsuite

    @classmethod
    def getChoice(cls, prevChoices, optionBoxName, level=None, index=None):
        if level is not None:
            if index is not None:
                val = getattr(prevChoices, optionBoxName + '%s_%s' % (level, index))
            else:
                val = getattr(prevChoices, optionBoxName + '%s' % level)

        else:
            val = getattr(prevChoices, optionBoxName)

        if val in [None, cls.SELECT_CHOICE, '']:
            return None

        return val
    
    @classmethod
    def isBottomLevel(cls, attributes):
        if not attributes:
            return True

    @classmethod
    def getSelectedTracks(cls, prevChoices):
        if prevChoices.selectTracks not in (cls.MANUAL_TRACK_SELECT, cls.RANDOM_10_TRACKS, cls.RANDOM_50_TRACKS):
            return None

        selectedTracks = None
        if prevChoices.selectTracks == cls.MANUAL_TRACK_SELECT:
            selectedTracks = [track for track, checked in prevChoices.selectTracksManually.items() if checked]
        elif prevChoices.selectTracks in (cls.RANDOM_10_TRACKS, cls.RANDOM_50_TRACKS):
            selectedTracks = prevChoices.selectRandomTracks
            if type(selectedTracks) is not list:
                selectedTracks = literal_eval(prevChoices.selectRandomTracks)

        return selectedTracks

    @classmethod
    def getChosenValues(cls, prevChoices, level):
        val = None
        if hasattr(prevChoices, 'selectionType%s' % level):
            selectionType = cls.getChoice(prevChoices, 'selectionType', level)
            if selectionType == cls.SINGLE_SELECTION:
                val = cls.getChoice(prevChoices, 'valueList', level)
            else:
                val = cls.getChoice(prevChoices, 'valueCheckbox', level)

        return val

    @classmethod
    def isSelectionComplete(cls, choices):
        lastLevel = 0
        for level in range(cls.MAX_NUM_OF_LEVELS):
            path = cls.getSubattributePath(choices, level, inQueryForm=False)
            if not path:
                lastLevel = level
                break

        if hasattr(choices, 'subAttributeList%s_%s' % (lastLevel, 0))\
                and getattr(choices, 'subAttributeList%s_%s' % (lastLevel, 0)):
            if getattr(choices, 'subAttributeList%s_%s' % (lastLevel, 0)) != cls.SELECT_CHOICE:
                return False
        else:
            return False

        return True

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

        if choices.extraAttributes == cls.YES:
            extraAttrs = True
        else:
            extraAttrs = False

        tfm = TrackFindModule()
        chosenOptions = cls.getPreviousChoices(choices)
        gsuite = tfm.getGSuite(choices.selectRepository, chosenOptions, includeExtraAttributes=extraAttrs)

        newGSuite = GSuite()
        chosenDataTypes = cls.getChosenDataTypes(choices)
        selectedTracks = cls.getSelectedTracks(choices)
        for track in gsuite.allTracks():
            dataType = track.getAttribute(cls.TYPE_OF_DATA_ATTR)

            if selectedTracks is not None and track.title not in selectedTracks:
                continue
            if dataType not in chosenDataTypes:
                continue

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
        chosenDataTypes = cls.getChosenDataTypes(choices)
        if not chosenDataTypes:
            return 'Please complete attributes and values selection'

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
        boxes.append('selectRepository')
        boxes.append('gsuiteHash')
        for i in xrange(cls.MAX_NUM_OF_LEVELS):
            boxes.append('textSearch%s' % i)
            boxes.append('subAttributeList%s_0' % i)

        return boxes

    @classmethod
    def getToolDescription(cls):
        """
        Specifies a help text in HTML that is displayed below the tool.

        Optional method. Default return value if method is not defined: ''
        """

        trackFindLink = str(HtmlCore().link('TrackFind', 'https://trackfind.elixir.no',
                                            popup=True))
        fairTracksLink = str(HtmlCore().link('FAIRtracks', 'https://fairtracks.github.io',
                                             popup=True))

        core = HtmlCore()
        core.paragraph(
            'This tool is a client for the ' + trackFindLink + ' service. After selecting a '
            'repository of genomic tracks, it is possible to select one or several attributes. '
            'The hierarchy of the attributes follows the hierarchy of the data according to the '
            'FAIRtracks standard. It is possible to select one or several values for each '
            'attribute.')
        core.paragraph(
            'After at least one value is selected, the tool shows a table with tracks that match '
            'the selected criteria. As more attributes and values are selected, the list of '
            'tracks will be increasingly more filtered. When the list of tracks is suitable, the '
            'tracks can be exported by clicking on the "Execute" button. The tracks will then be '
            'exported as GSuite file. ')
        core.divider()
        core.paragraph('More information about the FAIRtracks standard can be found here: '
                       + fairTracksLink)

        return str(core)

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
    #
    #     group = []
    #     return [
    #             BoxGroup(label='A group of choices', first='subAttributeList0_0',
    #                      last='valueCheckbox0',
    #                      ), BoxGroup(label='A group of choices', first='subAttributeList1_0',
    #                      last='valueCheckbox1')
    #             ]
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
    #     return ['Blueprint - Blueprint', 'experiments', 'technique', 'term_id', 'None', 'None', 'None', cls.SINGLE_SELECTION, ('__hidden__', ''), 'http://purl.obolibrary.org/obo/OBI_0000748', 'None']
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
