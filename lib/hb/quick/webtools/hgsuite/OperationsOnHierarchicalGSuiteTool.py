from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
import os, subprocess
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from proto.CommonFunctions import ensurePathExists
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from tempfile import NamedTemporaryFile


class OperationsOnHierarchicalGSuiteTool(GeneralGuiTool, GenomeMixin):

    TITLE = 'title'

    @classmethod
    def getToolName(cls):
        return "Operations on hierarchical gSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select first GSuite', 'gsuite')] + \
                    cls.getInputBoxNamesForGenomeSelection() + \
                [('Select column from first gSuite', 'firstGSuiteColumn'),
                ('Select second GSuite', 'secondGSuite'),
                ('Select column from second gSuite', 'secondGSuiteColumn'),
                ('Select operations', 'operations')
        ]

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxFirstGSuiteColumn(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.gsuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return ['None'] + [cls.TITLE] + gSuiteTN.attributes

    @classmethod
    def getOptionsBoxSecondGSuite(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxSecondGSuiteColumn(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.secondGSuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.secondGSuite)
            return ['None'] + [cls.TITLE] + gSuiteTN.attributes

    @classmethod
    def getOptionsBoxOperations(cls, prevChoices):  # Alt: getOptionsBox2()
        return ['intersection']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        firstGSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        firstGSuiteColumn = choices.firstGSuiteColumn.encode('utf-8')
        secondGSuite = getGSuiteFromGalaxyTN(choices.secondGSuite)
        secondGSuiteColumn = choices.secondGSuiteColumn.encode('utf-8')
        oper = choices.operations.encode('utf-8')

        outputGSuite = GSuite()
        trackNum = 0
        for iTrackFromFirst, trackFromFirst in enumerate(firstGSuite.allTracks()):
            for iTrackFromSecond, trackFromSecond in enumerate(secondGSuite.allTracks()):

                if firstGSuiteColumn == 'title':
                    attr1 = trackFromFirst.title
                else:
                    attr1 = trackFromFirst.getAttribute(firstGSuiteColumn)

                if secondGSuiteColumn == 'title':
                    attr2 = trackFromSecond.title
                else:
                    attr2 = trackFromSecond.getAttribute(secondGSuiteColumn)

                # print 'attr1', attr1
                # print 'attr2', attr2

                if attr1 == attr2:

                    track1 = trackFromFirst.path
                    track2 = trackFromSecond.path

                    tmpFile1 = NamedTemporaryFile()
                    tmpFile2 = NamedTemporaryFile()
                    tmpFn1 = cls.writeToTempFile(tmpFile1, track1)
                    tmpFn2 = cls.writeToTempFile(tmpFile2, track2)

                    # print 'old1', track1
                    # print 'new1', tmpFn1
                    #
                    # print 'old2', track2
                    # print 'new2', tmpFn2

                    if oper == "intersection":
                        # print """ bedtools intersect -a """ + str(track1) + """ -b  """ + str(
                        #     track2)

                        command = """ bedtools intersect -a """ + str(tmpFn1) + """ -b  """ + str(
                            tmpFn2)
                        # print command
                    else:
                        print

                    process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

                    results, errors = process.communicate()

                    ttNew = trackFromFirst.title + str(trackNum)
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                        extraFileName=ttNew,
                                                        suffix='bed')
                    gSuiteTrack = GSuiteTrack(uri)
                    outFn = gSuiteTrack.path
                    ensurePathExists(outFn)

                    # print 'errors', errors
                    # print 'results', results, 'end results'

                    wr = open(outFn, 'w')
                    wr.write(results)
                    wr.close()

                    gs = GSuiteTrack(uri, title=ttNew, genome=firstGSuite.genome)

                    outputGSuite.addTrack(gs)

                    trackNum += 1

        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def writeToTempFile(cls, tmpFile1, track1):
        tmpFn1 = tmpFile1.name
        f = open(track1, 'r')
        text = f.read()
        f.close()
        fw = open(tmpFn1, 'w')
        fw.write(text)
        fw.close()

        return tmpFn1

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
