from collections import OrderedDict

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from proto.CommonFunctions import ensurePathExists
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class DivideHgSuiteAccordingToColumnTool(GeneralGuiTool):

    DIVISION_BY_COLUMN = 'by column'
    DIVISION_BY_PHRASE = 'by phrase in data'
    TITLE = 'title'

    DIVISION = [DIVISION_BY_COLUMN, DIVISION_BY_PHRASE]


    @classmethod
    def getToolName(cls):
        return "Divide hgSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select gSuite', 'gSuite'),
                ('Select', 'division'),
                ('Select column', 'column'),
                ('Select phrases (use colon to provide more than one phrase)', 'param'),
                ('Add phrases separately', 'add')
                ]

    @classmethod
    def getOptionsBoxGSuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxDivision(cls, prevChoices):
        return cls.DIVISION

    @classmethod
    def getOptionsBoxColumn(cls, prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            if prevChoices.division.encode('utf-8') == cls.DIVISION_BY_COLUMN:
                return gSuite.attributes
            if prevChoices.division.encode('utf-8') == cls.DIVISION_BY_PHRASE:
                return [cls.TITLE] + gSuite.attributes
        return

    @classmethod
    def getOptionsBoxParam(cls, prevChoices):
        if prevChoices.gSuite and prevChoices.division == cls.DIVISION_BY_PHRASE:
            return ''

    @classmethod
    def getOptionsBoxAdd(cls, prevChoices):
        if prevChoices.gSuite and prevChoices.param and prevChoices.division == cls.DIVISION_BY_PHRASE:
            par = prevChoices.param.replace(' ', '').split(',')
            #
            # lenPar = 0
            # tf = False
            # for pNum, p in enumerate(par):
            #     if pNum == 0:
            #         lenPar = len(p)
            #     if lenPar == len(p):
            #         tf = True
            #     else:
            #         tf = False
            #
            # if tf == True:
            if len(par) >= 2:
                return ['yes', 'no']



    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        column = choices.column.encode('utf-8')

        trackList = {}
        if choices.division == cls.DIVISION_BY_COLUMN:
            for i, iTrack in enumerate(gSuite.allTracks()):
                attr = iTrack.getAttribute(column)
                if not attr in trackList.keys():
                    trackList[attr] = []
                trackList[attr].append(i)

        if choices.division == cls.DIVISION_BY_PHRASE:
            par = choices.param.replace(' ', '').split(',')

            if choices.add in ['yes', 'no']:
                add = choices.add
            else:
                add = 'no'

            if add == 'yes':
                trackList[('-'.join(par.encode('utf-8')))] = []
            else:
                for p in par:
                    trackList[p.encode('utf-8')] = []

            for i, iTrack in enumerate(gSuite.allTracks()):
                if column == cls.TITLE:
                    t = iTrack.title
                else:
                    t = iTrack.getAttribute(column)

                for p in par:
                    if p in t:
                        if add == 'yes':
                            trackList[('-'.join(par))].append(i)
                        else:
                            trackList[p].append(i)

            cls.buildNewGsuites(gSuite, trackList)

    @classmethod
    def buildNewGsuites(cls, gSuite, trackList):
        for tl in trackList.keys():

            outputGSuite = GSuite()
            url = cls.makeHistElement(galaxyExt='gsuite', title=str(tl))

            for t in trackList[tl]:
                track = gSuite.getTrackFromIndex(t)
                attributes = OrderedDict(
                    [(key, track.attributes[key]) for key in gSuite.attributes])
                gs = GSuiteTrack(track.uri, title=track.title, genome=gSuite.genome,
                                 attributes=attributes)

                outputGSuite.addTrack(gs)

            GSuiteComposer.composeToFile(outputGSuite, url)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

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
    #     return cls.getToolSelectionName()
    #     """
    #     The title (name) of the main output history element.
    #
    #     Optional method. Default return value if method is not defined:
    #     the name of the tool.
    #     """
