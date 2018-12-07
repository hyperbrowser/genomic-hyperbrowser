from proto.tools.GeneralGuiTool import GeneralGuiTool


class ToolTemplate(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        *Mandatory method*:
            Yes
        """
        return "Tool not yet in use"

    @classmethod
    def getInputBoxNames(cls):
        """
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of tuples of strings, where each tuple has
               two items: a header and a key.
            2) A simple list of strings denoting the headers for the input
               boxes in numerical order. [Deprecated]

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is the specified key (case 1).

        *Note*:
            the key has to be camelCase and start with a non-capital letter
            (e.g. "firstKey")
        *Note 2*:
            Case 2 above, which uses indexes, is deprecated and will not be
            discussed further in this documentation.
        *Mandatory method*:
            No
        *Default return value (if method is not defined)*:
            []
        """
        return [('First header', 'firstKey'),
                ('Second Header', 'secondKey')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     """
    #     Specifies the order in which the input boxes should be displayed,
    #     as a list. The input boxes are specified by index (starting with 1)
    #     or by key. If None, the order of the input boxes is in the order
    #     specified by :py:meth:`getInputBoxNames()`.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         None
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
    #     Example::
    #
    #        from proto.tools.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey',
    #                         last='secondKey')]
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         None
    #     """
    #     return None

    @classmethod
    def getOptionsBoxFirstKey(cls):  # Alt: getOptionsBox1()
        """
        For all the keys defined in :py:meth:`getInputBoxNames()`, the Galaxy
        ProTo parser looks for a class method named::

            getOptionsBox + key.capitalize()

        The Python object that is returned by such a method defines the type
        and contents of the corresponding input box in the GUI. The specific
        user selections are then provided to other methods in the prevChoices
        or choices parameters. This is a namedtuple object which can be
        accessed by key (recommended) or index (in the order specified by
        :py:meth:`getInputBoxOrder()`), e.g.::

            choices.firstKey
            choices[0]

        *Mandatory method*:
            Yes, for the first key defined in
            :py:meth:`getInputBoxNames()`, if any.

        Here follows an overview of the different GUI elements, together with
        an example of the Python syntax that needs to be returned by this to
        trigger the element, and the type of the user selection value present
        in choices/prevchoices:

        * *Check box*:
            * Syntax::

                False | True

            * Prevchoices/choices type::

                bool

        * *Selection box*:
            * Syntax::

                ['choice1', 'choice2']

            * Prevchoices/choices type::

                string

        * *Text area*:
            * Syntax::

                'textbox' | ('textbox', 1) | ('textbox', 1, False)

            * Tuple elements:

                1. contents:

                    the default value shown inside the text area

                2. height (default: 1):

                    the number of lines of the text box

                3. read only flag (default: False):

                    whether the text box will allow user input

            * Prevchoices/choices type::

                string

        * *Raw HTML code*:
            * Syntax::

                '__rawstr__', 'HTML code'

            * Note:

                This is mainly intended for read only usage. Even though more
                advanced hacks are possible, it is discouraged.

        * *Password field*:
            * Syntax::

                '__password__'

            * Prevchoices/choices type::

                string

        * *Genome selection box*:
            * Syntax::

                '__genome__'

            * Prevchoices/choices type::

                string

        * *History selection box*:
            * Syntax::

                ('__history__',) | ('__history__', 'bed', 'wig')

            * Note:

                Only history items of specified types are shown.

            * Prevchoices/choices type:

                colon-separated string denoting Galaxy dataset info, as
                described below.

        * *History check box list*:
            * Syntax::

                ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')

            * Note:

                Only history items of specified types are shown.

            * Prevchoices/choices type:

                OrderedDict with Galaxy dataset ids as key (the number YYYY
                as described below), and the associated Galaxy dataset info as
                the values, given that the history element is ticked off by the
                user. If not, the value is set to None. The Galaxy dataset info
                structure is described below.

        * *Hidden field*:
            * Syntax::

                ('__hidden__', 'Hidden value')

            * Prevchoices/choices type::

                string

        * *Table*:
            * Syntax::

                [['header1','header2'],
                 ['cell1_1','cell1_2'],
                 ['cell2_1','cell2_2']]

            * Prevchoices/choices type::

                None

        * *Check box list*:
            * Syntax:

                OrderedDict([('key1', True),
                             ('key2', False),
                             ('key3', False)])

            * Prevchoices/choices type:

                OrderedDict from key to selection status (bool).

        **Note about the "Galaxy dataset info" data structure**

        "Galaxy dataset info" is a list of strings coding information about a
        Galaxy history element and its associated dataset, typically used to
        provide info on the history element selected by the user as input to a
        ProTo tool.

        Structure::

            ['galaxy', fileFormat, path, name]

        Optionally encoded as a single string, delineated by colon::

            'galaxy:fileFormat:path:name'

        Where:
            * *'galaxy'* is used for assertions in the code
            * *fileFormat* (or suffix) contains the file format of the dataset,
              as encoded in the 'format' field of a Galaxy history element.
            * *path* (or file name/fn) is the disk path to the dataset file.
              Typically ends with 'XXX/dataset_YYYY.dat'. XXX and YYYY are
              numbers which are extracted and used as an unique id  of the
              dataset in the form [XXX, YYYY]
            * *name* is the title of the history element

        The different parts can be extracted using the functions
        :py:func:`proto.CommonFunctions.extractFileSuffixFromDatasetInfo()`,
        :py:func:`proto.CommonFunctions.extractFnFromDatasetInfo()`, and
        :py:func:`proto.CommonFunctions.extractNameFromDatasetInfo()`.
        """
        return ['testChoice1', 'testChoice2', '...']

    @classmethod
    def getOptionsBoxSecondKey(cls, prevChoices):  # Alt: getOptionsBox2()
        """
        See :py:meth:`getOptionsBoxFirstKey()`.

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by key (recommended)
        or index, e.g.::

            prevChoices.firstKey
            prevChoices[0]

        *Mandatory method*:
            Yes, for the subsequent keys (after the first key) defined in
            :py:meth:`getInputBoxNames()`, if any.
        """
        return ''

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     """
    #     If not None, defines the string content of an clickable info box
    #     beside the corresponding input box. HTML is allowed.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         None
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
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         None
    #     """
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     """
    #     Defines extra history elements to be created when clicking execute.
    #     This is defined by a list of
    #     :py:class:`proto.tools.GeneralGuiTool.HistElement` objects, as in the
    #     following example::
    #
    #        from proto.tools.GeneralGuiTool import HistElement
    #        return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]
    #
    #     It is good practice to use class constants for longer strings.
    #
    #     In the execute() method, one typically needs to fetch the path to
    #     the dataset referred to by the extra history element. To fetch the
    #     path, use the dict cls.extraGalaxyFn with the defined history title
    #     as key, e.g.::
    #
    #         cls.extraGalaxyFn[cls.HISTORY_TITLE]
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         None
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

        *Mandatory method*:
            Yes, unless :py:meth:`isRedirectTool()` returns True.
        """
        print 'Executing...'

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None, which enables
        the execute button.

        *Mandatory method*:
            No
        *Default return value (if method is not defined)*:
            None
        """
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     """
    #     Specifies a list of classes for subtools of the main tool. These
    #     subtools will be selectable from a selection box at the top of the
    #     page. The input boxes will change according to which subtool is
    #     selected.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         None
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
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         False
    #     """
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     """
    #     Specifies whether the tool should redirect to an URL when the Execute
    #     button is clicked.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         False
    #     """
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     """
    #     This method is called to return an URL if the isRedirectTool method
    #     returns True.
    #
    #     *Mandatory method*:
    #         Yes, if :py:meth:`isRedirectTool()` returns True.
    #     """
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     """
    #     Specifies if a History item should be created when the Execute button
    #     is clicked.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         True
    #     """
    #     return True
    #
    # @classmethod
    # def isDynamic(cls):
    #     """
    #     Specifies whether changing the content of textboxes causes the page
    #     to reload. Returning False stops the need for reloading the tool
    #     after each input, resulting in less lags for the user.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         True
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
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         []
    #     """
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     """
    #     Specifies a help text in HTML that is displayed below the tool.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         ''
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
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         None
    #     """
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     """
    #     Specifies an URL to an example page that describes the tool, for
    #     instance a Galaxy page.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         None
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
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         False
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
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         'html'
    #     """
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     """
    #     The title (name) of the main output history element.
    #
    #     *Mandatory method*:
    #         No
    #     *Default return value (if method is not defined)*:
    #         The name of the tool
    #     """
    #     return cls.getToolSelectionName()
