import os
import sys
from StringIO import StringIO
from collections import OrderedDict

from config.Config import HB_SOURCE_CODE_BASE_DIR
from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.webtools.GeneralGuiTool import GeneralGuiTool
import pytest
import pytest_html_profiling


class PytestRunnerTool(GeneralGuiTool):
    TEST_FOLDER_PATH = os.path.join(HB_SOURCE_CODE_BASE_DIR, 'test')
    CSS_PATH = os.path.join(pytest_html_profiling.__path__[0], 'resources', 'readable.css')
    FOLDERS = 'folders'
    FILES = 'files'
    TESTS = 'tests'
    PATH_PREFIX = 'lib/hb'

    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Pytest runner tool"

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
        return [('Test targets: ', 'selectTestTarget'),
                ('Select test folders', 'selectTestFolders'),
                ('', 'collectTests'),
                ('Select test files', 'selectTestFiles'),('Select tests', 'selectTests'),
                ('', 'getErrors')]

    @classmethod
    def getOptionsBoxSelectTestTarget(cls):
        return [cls.FOLDERS, cls.FILES, cls.TESTS]

    @classmethod
    def getOptionsBoxSelectTests(cls, prevChoices):
        if not prevChoices.collectTests:
            return
        if prevChoices.selectTestTarget != cls.TESTS:
            return

        outputLines = prevChoices.collectTests.splitlines()
        tests = []
        for line in outputLines:
            if line.startswith('=='):
                break
            else:
                if line.startswith(cls.PATH_PREFIX):
                    tests.append(os.path.relpath(line, HB_SOURCE_CODE_BASE_DIR))
        tests.sort()

        return OrderedDict([(test, True) for test in tests])

    @classmethod
    def getOptionsBoxCollectTests(cls, prevChoices):
        if prevChoices.selectTestTarget != cls.TESTS:
            return

        os.environ['PY_IGNORE_IMPORTMISMATCH'] = '1'

        pytestArgs = [
            '--collect-only',
            '--quiet',
            cls.TEST_FOLDER_PATH
        ]

        out = cls.capture(pytest.main, pytestArgs)

        return '__hidden__',out

    @classmethod
    def getOptionsBoxGetErrors(cls, prevChoices):
        if not prevChoices.collectTests:
            return

        outputLines = prevChoices.collectTests.splitlines()
        errorSection = False
        errors = ''
        for line in outputLines:
            if line.startswith('=='):
                errorSection = True
            if errorSection:
                errors += line + '\n'
            elif not line.startswith(cls.PATH_PREFIX):
                errors += line + '\n'

        return errors, 30


    @classmethod
    def getOptionsBoxSelectTestFiles(cls, prevChoices):
        if prevChoices.selectTestTarget != cls.FILES:
            return

        testNames = []

        for path, subdirs, files in os.walk(cls.TEST_FOLDER_PATH):
            for name in files:
                if name.startswith('Test') and name.endswith('.py'):
                    testNames.append(os.path.join(os.path.relpath(path, HB_SOURCE_CODE_BASE_DIR), name))

        testNames.sort()

        return OrderedDict([(testName, True) for testName in testNames])

    @classmethod
    def getOptionsBoxSelectTestFolders(cls, prevChoices):
        if prevChoices.selectTestTarget != cls.FOLDERS:
            return

        folderNames = []

        for path, subdirs, files in os.walk(cls.TEST_FOLDER_PATH):
            if not path.endswith('__'):
                folderNames.append(os.path.relpath(path, HB_SOURCE_CODE_BASE_DIR))

        folderNames.sort()

        return OrderedDict([(folderName, True) for folderName in folderNames])

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
        testPaths = []

        if choices.selectTestTarget == cls.FOLDERS:
            chosenFolders = [folder for folder, checked in choices.selectTestFolders.items() if checked]
            testPaths = [os.path.join(HB_SOURCE_CODE_BASE_DIR, folder) for folder in chosenFolders]


        elif choices.selectTestTarget == cls.FILES:
            pass
        elif choices.selectTestTarget == cls.TESTS:
            pass

        report = GalaxyRunSpecificFile(['report.html'], galaxyFn)
        baseDir = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()

        pytestArgs = ["--html", report.getDiskPath(), "--html-profiling",
                     '--html-profile-dir', baseDir, '--html-call-graph',
                    "--css", cls.CSS_PATH]

        pytestArgs.extend(testPaths)
        print pytestArgs

        os.environ['PY_IGNORE_IMPORTMISMATCH'] = '1'
        pytestOutput = cls.capture(pytest.main, pytestArgs)

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.paragraph(pytestOutput)
        htmlCore.divider()
        htmlCore.link('Link to report', report.getURL())
        htmlCore.end()

        print htmlCore


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
        return None

    @classmethod
    def capture(cls, func, *args, **kwArgs):
        out = StringIO()
        old_stdout = sys.stdout
        sys.stdout = out
        func(*args, **kwArgs)
        sys.stdout = old_stdout
        return out.getvalue()

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
