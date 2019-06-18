import os

import shutil

from proto.CommonFunctions import extractNameFromDatasetInfo, extractFnFromDatasetInfo, \
    extractFileSuffixFromDatasetInfo, getLoadToGalaxyHistoryURL, getFileSuffix, stripFileSuffix
from proto.HtmlCore import HtmlCore
from proto.tools.GeneralGuiTool import GeneralGuiTool


class ProtoGuiTestTool3(GeneralGuiTool):
    SINGLE_HISTORY_TEXT = 'A single history element'
    MULTIPLE_HISTORY_TEXT = 'Several history elements'
    ONE_OR_MANY_SELECTION = [SINGLE_HISTORY_TEXT, MULTIPLE_HISTORY_TEXT]

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Inputs and outputs: Test tool #3 for Galaxy ProTo GUI"

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
        return [('Select one or several histories?', 'oneOrMany'),
                ('Select input histories', 'histories'),
                ('Select input history', 'history')]

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
    def getOptionsBoxOneOrMany(cls):  # Alt: getOptionsBox1()
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

        return cls.ONE_OR_MANY_SELECTION

    @classmethod
    def getOptionsBoxHistory(cls, prevChoices):  # Alt: getOptionsBox2()
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
        if prevChoices.oneOrMany == cls.SINGLE_HISTORY_TEXT:
            return '__history__',

    @classmethod
    def getOptionsBoxHistories(cls, prevChoices):
        if prevChoices.oneOrMany == cls.MULTIPLE_HISTORY_TEXT:
            return '__multihistory__',

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
    @classmethod
    def getExtraHistElements(cls, choices):
        """
        Defines extra history elements to be created when clicking execute.
        This is defined by a list of HistElement objects, as in the
        following example:

           from proto.tools.GeneralGuiTool import HistElement
           return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]

        It is good practice to use class constants for longer strings.

        In the execute() method, one typically needs to fetch the path to
        the dataset referred to by the extra history element. To fetch the
        path, use the dict cls.extraGalaxyFn with the defined history title
        as key, e.g. "cls.extraGalaxyFn[cls.HISTORY_TITLE]".

        Optional method. Default return value if method is not defined: None
        """
        if cls._numberOfHistoriesSelected(choices) > 1:
            from proto.tools.GeneralGuiTool import HistElement
            return [HistElement(name=name,
                                format='customhtml',
                                label=cls._createHistLabel(name)) for name in
                    cls._getNamesForSelectedHistories(choices)[1:]]

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
        for i, datasetInfo in enumerate(cls._getDatasetInfoForSelectedHistories(choices)):
            inFileName, outFileName = cls._getInputAndOutputFileNames(i, datasetInfo, galaxyFn)
            embeddedFile = cls._createEmbeddedFile(datasetInfo, inFileName, outFileName)
            htmlContent = cls._generateHtmlContent(datasetInfo, embeddedFile, inFileName)
            cls._writeHtmlContent(htmlContent, outFileName)

    @classmethod
    def _getInputAndOutputFileNames(cls, i, datasetInfo, galaxyFn):
        if i == 0:
            outFileName = galaxyFn
        else:
            datasetName = extractNameFromDatasetInfo(datasetInfo)
            outFileName = cls.extraGalaxyFn[datasetName]

        inFileName = extractFnFromDatasetInfo(datasetInfo)

        return inFileName, outFileName

    @classmethod
    def _createEmbeddedFile(cls, datasetInfo, inFileName, outFileName):
        from proto.StaticFile import GalaxyRunSpecificFile

        inFileSuffix = extractFileSuffixFromDatasetInfo(datasetInfo)
        inDatasetName = extractNameFromDatasetInfo(datasetInfo)
        if not inDatasetName.endswith('.' + inFileSuffix):
            inDatasetName = '.'.join([inDatasetName, inFileSuffix])

        embeddedBaseFileName = cls._cleanUpName(inDatasetName)

        embeddedFile = GalaxyRunSpecificFile(['embedded', embeddedBaseFileName], outFileName)
        shutil.copy(inFileName, embeddedFile.getDiskPath(ensurePath=True))

        return embeddedFile

    @classmethod
    def _generateHtmlContent(cls, datasetInfo, embeddedFile, inFileName):
        with open(inFileName) as inFile:
            import cgi

            core = HtmlCore()
            core.begin()

            core.header('File contents')
            core.fieldsetBegin('Ten first lines of file: ' +
                               extractNameFromDatasetInfo(datasetInfo))
            core.preformatted(''.join([cgi.escape(inFile.readline()).decode('utf-8', 'ignore')
                                       for _ in range(10)]))
            core.fieldsetEnd()

            core.header('Direct URL to file')
            embeddedBaseFileName = embeddedFile.getId()[-1]
            core.paragraph(embeddedFile.getLink(embeddedBaseFileName))

            core.header('Open file in Galaxy history')
            embeddedFileSuffix = getFileSuffix(embeddedBaseFileName)
            core.paragraph(embeddedFile.getLoadToHistoryLink
                           (embeddedBaseFileName, galaxyDataType=embeddedFileSuffix))

            core.end()

        return unicode(core)

    @classmethod
    def _writeHtmlContent(cls, htmlContent, outFileName):
        import io
        with io.open(outFileName, 'w', encoding='utf-8') as outFile:
            outFile.write(htmlContent)

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
        if cls._numberOfHistoriesSelected(choices) == 0:
            return "Please select at least one history element"

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

    @classmethod
    def getToolDescription(cls):
        """
        Specifies a help text in HTML that is displayed below the tool.

        Optional method. Default return value if method is not defined: ''
        """
        core = HtmlCore()
        core.paragraph('This test tool creates one output history element for each input '
                       'history element. The output element is a HTML page showing the first '
                       '10 lines of the corresponding file, as well as a link to the '
                       'embedded full file. The embedded file are stored together with the '
                       'history element on disk and is a copy of the original.')
        core.paragraph('Below is an example of a tool illustration.')
        core.paragraph('The example link at the bottom currently points to the Galaxy ProTo '
                       'GitHub page. It would typically point to a Galaxy example page, but does '
                       'not do so in this case, as Galaxy Pages currently are installation '
                       'dependent and cannot be distributed with the source code.')
        return str(core)

    @classmethod
    def getToolIllustration(cls):
        """
        Specifies an id used by StaticFile.py to reference an illustration
        file on disk. The id is a list of optional directory names followed
        by a filename. The base directory is STATIC_PATH as defined by
        Config.py. The full path is created from the base directory
        followed by the id.

        Optional method. Default return value if method is not defined: None
        """
        return ['logo', 'ELIXIR_NORWAY_logo_transparent.png']

    @classmethod
    def getFullExampleURL(cls):
        """
        Specifies an URL to an example page that describes the tool, for
        instance a Galaxy page.

        Optional method. Default return value if method is not defined: None
        """
        return "https://github.com/elixir-no-nels/proto"

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
        return 'customhtml'

    @classmethod
    def getOutputName(cls, choices=None):
        """
        The title (name) of the main output history element.

        Optional method. Default return value if method is not defined:
        the name of the tool.
        """
        if cls._numberOfHistoriesSelected(choices) > 0:
            print cls._numberOfHistoriesSelected(choices)
            if choices.oneOrMany == cls.MULTIPLE_HISTORY_TEXT:
                historyName = cls._getNamesForSelectedHistories(choices)[0]
            else:
                historyName = extractNameFromDatasetInfo(choices.history)
            return cls._createHistLabel(historyName)

    @classmethod
    def _numberOfHistoriesSelected(cls, choices):
        if choices.oneOrMany == cls.MULTIPLE_HISTORY_TEXT:
            return sum(1 for sel in choices.histories.values() if sel)
        else:
            if choices.history:
                return 1
            else:
                return 0

    @classmethod
    def _getNamesForSelectedHistories(cls, choices):
        return [extractNameFromDatasetInfo(datasetInfo) for datasetInfo in
                cls._getDatasetInfoForSelectedHistories(choices)]

    @classmethod
    def _getDatasetInfoForSelectedHistories(cls, choices):
        if choices.oneOrMany == cls.MULTIPLE_HISTORY_TEXT:
            return [val for val in choices.histories.values() if val]
        else:
            return [choices.history]

    @classmethod
    def _cleanUpName(cls, historyName):
        histNum, histLabel = historyName.split(' - ', 1)
        return '_'.join([histNum] + histLabel.lower().split(' '))

    @classmethod
    def _createHistLabel(cls, name):
        cleanupName = cls._cleanUpName(name)
        return 'Embedded file: ' + cleanupName
