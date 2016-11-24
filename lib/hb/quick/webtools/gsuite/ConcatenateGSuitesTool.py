from quick.webtools.GeneralGuiTool import GeneralGuiTool

# This is a template prototyping GUI that comes together with a corresponding
# web page.

class ConcatenateGSuitesTool(GeneralGuiTool):
    MAX_NUM_OF_GSUITES_TO_ORDER = 20

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Concatenate two GSuites"

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select GSuite files from history', 'gsuites'), \
                ('Specify order of GSuite files?', 'order')] +\
                [('Select GSuite number %s' % (i+1), 'selectGsuite%s' % i) for i \
                 in range(cls.MAX_NUM_OF_GSUITES_TO_ORDER)]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxGsuites(): # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__multihistory__', 'gsuite'

    @classmethod
    def getOptionsBoxOrder(cls, prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        numSeletedGSuites = sum(1 for tn in cls._getAllSelectedGsuiteGalaxyTNs(prevChoices))
        if numSeletedGSuites >= 2:
            return ['No', 'Yes']

    @staticmethod
    def _getAllSelectedGsuiteGalaxyTNs(prevChoices):
        return [x for x in prevChoices.gsuites.values() if x is not None]


    @classmethod
    def _getOptionsBoxForSelectGsuite(cls, prevChoices, index):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        if prevChoices.order == 'Yes':
            selectionList = []
            allSelectedGsuiteGalaxyTNs = cls._getAllSelectedGsuiteGalaxyTNs(prevChoices)

            for selectedGsuiteGalaxyTNs in allSelectedGsuiteGalaxyTNs:
                selectedHistElName = ExternalTrackManager.extractNameFromHistoryTN(selectedGsuiteGalaxyTNs)
                if not any(selectedHistElName in getattr(prevChoices, 'selectGsuite%s' % i) for i in xrange(index)):
                    selectionList.append(selectedHistElName)

            if selectionList:
                return selectionList

    @classmethod
    def setupSelectGSuiteMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_NUM_OF_GSUITES_TO_ORDER):
            setattr(cls, 'getOptionsBoxSelectGsuite%s' % i, partial(cls._getOptionsBoxForSelectGsuite, index=i))

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def _getSelectedGsuiteGalaxyTNsInOrder(cls, choices):
        from quick.application.ExternalTrackManager import ExternalTrackManager

        allSelectedGsuiteGalaxyTNs = cls._getAllSelectedGsuiteGalaxyTNs(choices)

        if choices.order == 'No':
            return allSelectedGsuiteGalaxyTNs
        else: #Yes
            nameToSelectedGalaxyTN = dict([(ExternalTrackManager.extractNameFromHistoryTN(galaxyTN), galaxyTN) \
                                           for galaxyTN in allSelectedGsuiteGalaxyTNs])
            selectedGsuiteNamesInOrder = [getattr(choices, 'selectGsuite%s' % i) \
                                          for i in range(len(allSelectedGsuiteGalaxyTNs))]
            return [nameToSelectedGalaxyTN[name] for name in selectedGsuiteNamesInOrder]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        from gold.gsuite.GSuiteEditor import concatenateGSuites
        from gold.gsuite.GSuiteComposer import composeToFile

        gSuiteList = [getGSuiteFromGalaxyTN(galaxyTn) for galaxyTn in \
                      cls._getSelectedGsuiteGalaxyTNsInOrder(choices)]

        concatenatedGSuite = concatenateGSuites(gSuiteList)
        composeToFile(concatenatedGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        if not choices.gsuites:
            return 'Please add at least two GSuite files to your history'

        allSelectedGsuiteGalaxyTNs = cls._getAllSelectedGsuiteGalaxyTNs(choices)
        numSeletedGSuites = len(allSelectedGsuiteGalaxyTNs)
        if numSeletedGSuites < 2:
            return 'Please select at least two GSuites'

        if choices.order == 'Yes' and numSeletedGSuites > cls.MAX_NUM_OF_GSUITES_TO_ORDER:
            return 'Ordering of GSuite files is only possible for up to %s ' % cls.MAX_NUM_OF_GSUITES_TO_ORDER +\
                   'selection. You have selected %s GSuite files' % numSeletedGSuites

        for selectedGsuiteGalaxyTN in allSelectedGsuiteGalaxyTNs:
            errorStr = cls._validateGSuiteFile(selectedGsuiteGalaxyTN)
            if errorStr:
                return errorStr

    #@staticmethod
    #def getSubToolClasses():
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
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'

ConcatenateGSuitesTool.setupSelectGSuiteMethods()
