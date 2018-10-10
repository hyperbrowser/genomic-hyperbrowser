from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.trackfind.TrackFindModule import TrackFindModule
from functools import partial
from collections import OrderedDict


class TrackFindClientTool(GeneralGuiTool):
    MAX_NUM_OF_EXTRA_BOXES = 20
    SELECT_CHOICE = '--- Select ---'
    SINGLE_SELECTION = 'Single selection'
    MULTIPLE_SELECTION = 'Multiple selection'
    TEXT_SEARCH = 'Text search'

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



        for i in xrange(cls.MAX_NUM_OF_EXTRA_BOXES):
            attrBoxes.append(('Select attribute:', \
                              'attributeList%s' % i))
            attrBoxes.append(('Selection type:', \
                              'selectionType%s' % i))
            attrBoxes.append(('Text to search for', \
                             'textSearch%s' % i))
            attrBoxes.append(('Select value:', \
                         'valueList%s' % i))
            #attrBoxes.append(('Range ' + cls.ATTRIBUTES[i], \
              #                'valueRange%s' % i))


        return attrBoxes

    @classmethod
    def setupExtraBoxMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_EXTRA_BOXES):
            setattr(cls, 'getOptionsBoxAttributeList%s' % i, \
                    partial(cls._getAttributeListBox, index=i))
            setattr(cls, 'getOptionsBoxValueList%s' % i, \
                    partial(cls._getValueListBox, index=i))
            setattr(cls, 'getOptionsBoxSelectionType%s' % i, \
                    partial(cls._getSelectionTypeBox, index=i))
            setattr(cls, 'getOptionsBoxTextSearch%s' % i, \
                    partial(cls._getTextSearchBox, index=i))

    @classmethod
    def _getAttributeListBox(cls, prevChoices, index):
        if index == 0 and getattr(prevChoices, 'selectRepository') in [None, cls.SELECT_CHOICE, '']:
            return

        if index > 0 and getattr(prevChoices, 'valueList%s' % (index-1))\
         in [None, cls.SELECT_CHOICE, '']:
            return

        tfm = TrackFindModule()
        attributes = tfm.getAttributesForRepository(prevChoices.selectRepository)

        for i in xrange(index):
            prevAttr = getattr(prevChoices, 'attributeList%s' % i)

            if prevAttr in attributes:
                attributes.remove(prevAttr)

        attributes.sort()
        attributes.insert(0, cls.SELECT_CHOICE)

        return attributes

    @classmethod
    def _getValueListBox(cls, prevChoices, index):
        if index > 0 and getattr(prevChoices, 'valueList%s' % (index - 1)) \
                in [None, cls.SELECT_CHOICE, '']:
            return

        selectedAttribute = getattr(prevChoices, 'attributeList%s' % index)
        if selectedAttribute in [None, cls.SELECT_CHOICE, '']:
            return

        tfm = TrackFindModule()
        filteredValues = []
        if getattr(prevChoices, 'selectionType%s' % index) == cls.TEXT_SEARCH:
            searchTerm = getattr(prevChoices, 'textSearch%s' % index)
            if searchTerm:
                filteredValues = tfm.getAttributeValues(prevChoices.selectRepository, selectedAttribute, searchTerm)

        values = tfm.getAttributeValues(prevChoices.selectRepository, selectedAttribute)
        values.sort()

        if getattr(prevChoices, 'selectionType%s' % index) == cls.SINGLE_SELECTION:
            values.insert(0, cls.SELECT_CHOICE)
            return values
        elif getattr(prevChoices, 'selectionType%s' % index) == cls.MULTIPLE_SELECTION:
            return OrderedDict([(value, False) for value in values])
        elif getattr(prevChoices, 'selectionType%s' % index) == cls.TEXT_SEARCH:
            valuesDict = OrderedDict()
            for value in values:
                print value + '\n'
                if value in filteredValues:
                    valuesDict[value] = True
                else:
                    valuesDict[value] = False
            return valuesDict

        return values

    @classmethod
    def _getSelectionTypeBox(cls, prevChoices, index):
        attribute = getattr(prevChoices, 'attributeList%s' % index)
        if attribute in [None, cls.SELECT_CHOICE, '']:
            return
        else:
            return [cls.SINGLE_SELECTION, cls.MULTIPLE_SELECTION, cls.TEXT_SEARCH]


    @classmethod
    def getOptionsBoxSelectRepository(cls):
        tfm = TrackFindModule()
        repos = tfm.getRepositories()
        repos.sort()
        repos.insert(0, cls.SELECT_CHOICE)

        return repos

    @classmethod
    def _getTextSearchBox(cls, prevChoices, index):
        attribute = getattr(prevChoices, 'selectionType%s' % index)
        if attribute == cls.TEXT_SEARCH:
            return ''
        else:
            return


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

        chosenOptions = {}
        for i in xrange(cls.MAX_NUM_OF_EXTRA_BOXES):
            attr = getattr(choices, 'attributeList%s' % i)
            val = getattr(choices, 'valueList%s' % i)

            if attr == cls.SELECT_CHOICE or val == cls.SELECT_CHOICE:
                break

            if type(val) is OrderedDict:
                chosenOptions[attr] = [option for option, checked in val.items() if checked]
            else:
                chosenOptions[attr] = val

        tfm = TrackFindModule()
        data = tfm.getData(choices.selectRepository, chosenOptions)

        print 'You chose ' + str(chosenOptions)
        print
        print data

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
    @classmethod
    def getResetBoxes(cls):
        """
        Specifies a list of input boxes which resets the subsequent stored
        choices previously made. The input boxes are specified by index
        (starting with 1) or by key.

        Optional method. Default return value if method is not defined: True
        """

        textSearchBoxes = []
        for i in xrange(cls.MAX_NUM_OF_EXTRA_BOXES):
            textSearchBoxes.append('textSearch%s' % i)
            return textSearchBoxes

        return []

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
    #     return 'gsuite'

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