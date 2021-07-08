from proto.HtmlCore import HtmlCore
from proto.tools.GeneralGuiTool import GeneralGuiTool


class ProtoGuiTestTool6(GeneralGuiTool):
    MAX_ROWS_AND_COLS = 5
    SELECT_R_OPERATION = '-- No selection (or finished selecting) --'
    CLEAR_OPERATION_QUEUE = '-- Clear matrix operation queue --'

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Variable number of inputs and R: Test tool #6 for Galaxy ProTo GUI"

    @classmethod
    def getInputBoxNames(cls):
        """
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase and start with a non-capital letter
              (e.g. "firstKey")

        Optional method. Default return value if method is not defined: []
        """
        return [('Number of rows (2-{})'.format(cls.MAX_ROWS_AND_COLS), 'numRows'),
                ('Number of columns (2-{})'.format(cls.MAX_ROWS_AND_COLS), 'numCols')] +\
               [('Value in matrix element ({}, {})'.format(i, j), 'extra{}_{}'.format(i, j))
                for i in xrange(cls.MAX_ROWS_AND_COLS) for j in xrange(cls.MAX_ROWS_AND_COLS)] +\
               [('Matrix', 'matrix'),
                ('Select next R single matrix operation', 'operation'),
                ('Operation queue', 'queue'),
                ('Operation queue (Html)', 'queueHtml')]

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
    #        from proto.tools.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey',
    #                         last='secondKey')]
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    @classmethod
    def getOptionsBoxNumRows(cls):  # Alt: getOptionsBox1()
        """
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to
        other methods. These are lists of results, one for each input box
        (in the order specified by getInputBoxOrder()).

        Mandatory for the first key defined in getInputBoxNames(), if any.

        The input box is defined according to the following syntax:

        Check box:              False | True
        - Returns: bool

        Selection box:          ['choice1', 'choice2']
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
        return '2'

    @classmethod
    def getOptionsBoxNumCols(cls, prevChoices):  # Alt: getOptionsBox2()
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
        return '2'

    @classmethod
    def _getOptionBoxExtra(cls, prevChoices, i, j):
        if i < int(prevChoices.numRows) and j < int(prevChoices.numCols):
            return '0'

    @classmethod
    def setupExtraBoxMethods(cls):
        from functools import partial
        for i in xrange(cls.MAX_ROWS_AND_COLS):
            for j in xrange(cls.MAX_ROWS_AND_COLS):
                setattr(cls, 'getOptionsBoxExtra{}_{}'.format(i, j),
                        partial(cls._getOptionBoxExtra, i=i, j=j))

    @classmethod
    def getOptionsBoxMatrix(cls, prevChoices):
        return cls._getMatrixFromChoices(prevChoices)

    @classmethod
    def _getMatrixFromChoices(cls, prevChoices):
        import numpy as np
        allVals = np.array([float(_) for _ in cls._getExtraChoices(prevChoices)])
        matrix = allVals.reshape((int(prevChoices.numRows), int(prevChoices.numCols))).tolist()
        return matrix

    @classmethod
    def getOptionsBoxOperation(cls, prevChoices):
        return [cls.SELECT_R_OPERATION, 'crossprod', 't', 'solve', cls.CLEAR_OPERATION_QUEUE]

    @classmethod
    def getOptionsBoxQueue(cls, prevChoices):
        queue = prevChoices.queue
        operation = prevChoices.operation

        if operation == cls.CLEAR_OPERATION_QUEUE:
            ret = ''
        elif operation == cls.SELECT_R_OPERATION:
            ret = queue if queue is not None else ''
        else:
            ret = '|'.join([queue, operation]) if queue else operation

        return '__hidden__', ret

    @classmethod
    def getOptionsBoxQueueHtml(cls, prevChoices):
        queue = prevChoices.queue
        core = HtmlCore()

        core.smallHeader('Queue of R single matrix operations')
        if queue:
            for i, operation in enumerate(queue.split('|')):
                core.descriptionLine(str(i + 1), operation)
        else:
            core.paragraph('No matrix operations selected.')

        return '__rawstr__', unicode(core)

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     """
    #     If not None, defines the string content of an clickable info box
    #     beside the corresponding input box. HTML is allowed.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    @classmethod
    def getDemoSelections(cls):
        """
        Defines a set of demo inputs to the option boxes in the
        order defined by getOptionBoxNames and getOptionsBoxOrder.
        If not None, a Demo button appears in the interface. Clicking the
        button fills the option boxed with the defined demo values.

        Optional method. Default return value if method is not defined: None
        """
        return ['2', '2', '3', '4'] +\
               [''] * (cls.MAX_ROWS_AND_COLS - 2) +\
               ['1', '2'] +\
               [''] * (cls.MAX_ROWS_AND_COLS - 2) +\
               [''] * ((cls.MAX_ROWS_AND_COLS - 2) * cls.MAX_ROWS_AND_COLS) +\
               ['None', cls.SELECT_R_OPERATION, 'crossprod|solve|t', 'None']

    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     """
    #     Defines extra history elements to be created when clicking execute.
    #     This is defined by a list of HistElement objects, as in the
    #     following example:
    #
    #        from proto.tools.GeneralGuiTool import HistElement
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
        from proto.RSetup import r

        core = HtmlCore()

        try:
            mat = cls._getMatrixFromChoices(choices)
            for operation in choices.queue.split('|'):
                mat = r[operation](mat).tolist()
        except Exception, e:
            core.paragraph(str(e))
        else:
            core.smallHeader('Output matrix after all R single matrix operations have been '
                             'carried out:')
            core.tableHeader([])
            for rowNum in range(len(mat)):
                core.tableLine(mat[rowNum])
            core.tableFooter()

        return unicode(core)

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
        for optionsBox in ['numRows', 'numCols']:
            val = getattr(choices, optionsBox)
            try:
                num = int(val)
                if num < 2 or num > cls.MAX_ROWS_AND_COLS:
                    return '"{}" is not in interval [2, {}]: {}'.format(
                        optionsBox, cls.MAX_ROWS_AND_COLS, val)
            except:
                return '"{}" is not an integer: {}'.format(optionsBox, val)

        extraChoices = ProtoGuiTestTool6._getExtraChoices(choices)
        for x, val in enumerate(extraChoices):
            try:
                num = float(val)
            except:
                numCols = int(choices.numCols)
                i = x / numCols
                j = x % numCols
                return 'Value in matrix element ({}, {}) is not a float: {}'.format(i, j, val)

        if not choices.queue:
            return 'Please select at least one R matrix operation'

    @classmethod
    def _getExtraChoices(cls, choices):
        return [getattr(choices, 'extra{}_{}'.format(i, j)) \
                for i in xrange(int(choices.numRows))
                for j in xrange(int(choices.numCols))]

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

    @classmethod
    def isHistoryTool(cls):
        """
        Specifies if a History item should be created when the Execute button
        is clicked.

        Optional method. Default return value if method is not defined: True
        """
        return False

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
    #     """
    #     The title (name) of the main output history element.
    #
    #     Optional method. Default return value if method is not defined:
    #     the name of the tool.
    #     """
    #     return cls.getToolSelectionName()


ProtoGuiTestTool6.setupExtraBoxMethods()
