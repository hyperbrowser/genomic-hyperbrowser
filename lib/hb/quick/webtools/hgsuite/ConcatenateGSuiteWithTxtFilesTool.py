from collections import OrderedDict

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager

class ConcatenateGSuiteWithTxtFilesTool(GeneralGuiTool):

    TITLE = 'title'
    NO_OPERATION_TEXT = '-- Select --'

    @classmethod
    def getToolName(cls):

        return "Update hGSuite metadata using information from TXT file"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select GSuite: ', 'gsuite'),
                ('Select key from hGSuite: ', 'keyFirst'),
                ('Select txt file: ', 'selFile'),
                ('Select key from file: ', 'keySecond')]

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxKeyFirst(cls, prevChoices):
        if prevChoices.gsuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return [cls.NO_OPERATION_TEXT] + [cls.TITLE] + gSuite.attributes

    @classmethod
    def getOptionsBoxSelFile(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('tsv', 'txt', 'tabular')

    @classmethod
    def getOptionsBoxKeySecond(cls, prevChoices):
        if prevChoices.selFile:
            path = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.selFile.split(':'))
            lNum = 0
            with open(path) as f:
                for line in f.readlines():
                    if lNum == 0:
                        return line.strip('\n').split('\t')
                    lNum += 1


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        keyFirst = choices.keyFirst.encode('utf-8')
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        keySecond = choices.keySecond.encode('utf-8')
        path = ExternalTrackManager.extractFnFromGalaxyTN(choices.selFile.split(':'))
        header = []

        extraMetadata = {}
        lNum = 0
        with open(path) as f:
            for line in f.readlines():
                if lNum == 0:
                    header = line.strip('\n').split('\t')
                    inx = int(header.index(keySecond))
                else:
                    ll = line.strip('\n').split('\t')
                    if not str(ll[inx]) in extraMetadata.keys():
                        extraMetadata[str(ll[inx])] = OrderedDict()
                    for i in range(0, inx):
                        extraMetadata[str(ll[inx])][str(header[i])] = ll[int(i)]

                    for i in range(inx+1, len(header)):
                        extraMetadata[str(ll[inx])][str(header[i])] = ll[int(i)]
                lNum += 1

        #print extraMetadata

        outputGSuite = GSuite()
        for track in gSuite.allTracks():

            if keyFirst == cls.TITLE:
                attr = track.title
            else:
                attr = track.getAttribute(keyFirst)
            existingAttr = track.attributes
            if attr in extraMetadata.keys():
                attrDict = cls.merge_two_dicts(existingAttr, extraMetadata[attr])

                gs = GSuiteTrack(track.uri,
                                 title=''.join(str(track.title)),
                                 genome=gSuite.genome,
                                 attributes=attrDict)

                outputGSuite.addTrack(gs)

        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def merge_two_dicts(cls, x, y):
        z = x.copy()  # start with x's keys and values
        z.update(y)  # modifies z with y's keys and values & returns None
        return z

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
        #return 'customhtml'
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
