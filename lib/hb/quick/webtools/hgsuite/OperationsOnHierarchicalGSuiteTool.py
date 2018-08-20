from collections import OrderedDict

from proto.StaticFile import StaticImage
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
import os, subprocess
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from proto.CommonFunctions import ensurePathExists
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from quick.webtools.hgsuite.Legend import Legend
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from tempfile import NamedTemporaryFile


class OperationsOnHierarchicalGSuiteTool(GeneralGuiTool, GenomeMixin):

    TITLE = 'title'

    @classmethod
    def getToolName(cls):
        return "Operations on hGSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select first hGSuite', 'gsuite')] + \
                    cls.getInputBoxNamesForGenomeSelection() + \
                [('Select column from first hGSuite', 'firstGSuiteColumn'),
                ('Select second hGSuite', 'secondGSuite'),
                ('Select column from second hGSuite', 'secondGSuiteColumn'),
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
        return ['intersection', 'subtract']

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

                # print 'attr1', attr1, '<br>'
                # print 'attr2', attr2, '<br>'

                ttNew = trackFromFirst.title + str(trackNum)

                attrDict = OrderedDict()
                attrDict['oldTrackName1'] = str(trackFromFirst.title)
                attrDict['oldTrackName2'] = str(trackFromSecond.title)

                for attrName in firstGSuite.attributes:
                    attrDict[attrName] = trackFromFirst.getAttribute(attrName)

                for attrName in secondGSuite.attributes:
                    attrDict[attrName] = trackFromSecond.getAttribute(attrName)

                if attr1 == attr2:

                    track1 = trackFromFirst.path
                    track2 = trackFromSecond.path

                    # print 'track1', track1, '<br>'
                    # print 'track2', track2, '<br>'

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
                    elif oper == "subtract":
                        command = """ bedtools subtract -a """ + str(tmpFn1) + """ -b  """ + str(
                            tmpFn2)
                    else:
                        print

                    process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)

                    results, errors = process.communicate()


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

                    gs = GSuiteTrack(uri, title=ttNew, genome=firstGSuite.genome, attributes=attrDict)

                    outputGSuite.addTrack(gs)

                    trackNum += 1

        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def writeToTempFile(cls, tmpFile1, track1):
        print tmpFile1, track1, '<br>'
        tmpFn1 = tmpFile1.name
        print tmpFn1, '<br>'
        f = open(track1, 'r')
        text = f.read()
        f.close()
        fw = open(tmpFn1, 'w')
        fw.write(text)
        fw.close()

        return tmpFn1

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gsuite or not choices.secondGSuite:
            return 'Select first and second hGSuite'

        if choices.gsuite and choices.secondGSuite:
            gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
            secondGSuite = getGSuiteFromGalaxyTN(choices.gsuite)
            if gsuite.isPreprocessed() or secondGSuite.isPreprocessed():
                return 'hGSuites need to be primary. If you have preprocess hGSuite, then use tool: Convert GSuite tracks from preprocessed to primary.'


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


    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'The tool allow to proceed operations: intersection or subtract between hGSuites'

        stepsToRunTool = ['Select first GSuite',
                          'Select column from first hGSuite',
                          'Select second hGSuite',
                          'Select column from second hGSuite',
                          'Select operations (intersection, subtract)'
                          ]

        example = {'Example': ['', ["""
        ##file format: primary					
        ##track type: unknown					
        ##genome: mm10					
        ###uri	title	mutation	genotype	dir_level_1	dir_level_2
        galaxy:/path;bed	track1.bed	CA	eta	C	A
        galaxy:/path;bed	track2.bed	GT	eta	G	T
        galaxy:/path;bed	track5.bed	CG	iota	C	G
        galaxy:/path;bed	track6.bed	GC	iota	G	C
        galaxy:/path;bed	track3.bed	CA	iota	C	A
        galaxy:/path;bed	track4.bed	GT	iota	G	T
                        """,
                    """
        ##location: local				
        ##file format: primary				
        ##track type: unknown				
        ##genome: mm10				
        ###uri	title	dir_level_1	dir_level_2	dir_level_3
        galaxy:/path;point.bed	aca	A	C	A
        galaxy:/path;point.bed	acc	A	C	C
        galaxy:/path;point.bed	acg	A	C	G
        galaxy:/path;point.bed	act	A	C	T
        galaxy:/path;point.bed	aga	A	G	A
        galaxy:/path;point.bed	agc	A	G	C
        galaxy:/path;point.bed	agg	A	G	G
        galaxy:/path;point.bed	agt	A	G	T
                """],
              [
                ['Select first GSuite','gsuite'],
                ['Select column from first hGSuite','dir_level_1'],
                ['Select second hGSuite','gsuite'],
                ['Select column from second hGSuite','dir_level_2'],
                ['Select operations (intersection, subtract)','intersection']

              ],
              [
                 """
         ##location: local
        ##file format: primary
        ##track type: unknown
        ##genome: mm10
        ###uri	title	oldTrackName1	oldTrackName2	mutation	genotype	dir_level_1	dir_level_2	dir_level_3	dir_level_4
        galaxy:/29ee58bc6a49908e/track1.bed0;bed	track1.bed0	track1.bed	aca	CA	eta	C	A	C	A
        galaxy:/29ee58bc6a49908e/track1.bed1;bed	track1.bed1	track1.bed	acc	CA	eta	C	A	C	C
        galaxy:/29ee58bc6a49908e/track1.bed2;bed	track1.bed2	track1.bed	acg	CA	eta	C	A	C	G
        galaxy:/29ee58bc6a49908e/track1.bed3;bed	track1.bed3	track1.bed	act	CA	eta	C	A	C	T
        galaxy:/29ee58bc6a49908e/track2.bed4;bed	track2.bed4	track2.bed	aga	GT	eta	G	A	G	A
        galaxy:/29ee58bc6a49908e/track2.bed5;bed	track2.bed5	track2.bed	agc	GT	eta	G	A	G	C
        galaxy:/29ee58bc6a49908e/track2.bed6;bed	track2.bed6	track2.bed	agg	GT	eta	G	A	G	G
        galaxy:/29ee58bc6a49908e/track2.bed7;bed	track2.bed7	track2.bed	agt	GT	eta	G	A	G	T
        galaxy:/29ee58bc6a49908e/track5.bed8;bed	track5.bed8	track5.bed	aca	CG	iota	C	A	C	A
        galaxy:/29ee58bc6a49908e/track5.bed9;bed	track5.bed9	track5.bed	acc	CG	iota	C	A	C	C
        galaxy:/29ee58bc6a49908e/track5.bed10;bed	track5.bed10	track5.bed	acg	CG	iota	C	A	C	G
        galaxy:/29ee58bc6a49908e/track5.bed11;bed	track5.bed11	track5.bed	act	CG	iota	C	A	C	T
        galaxy:/29ee58bc6a49908e/track6.bed12;bed	track6.bed12	track6.bed	aga	GC	iota	G	A	G	A
        galaxy:/29ee58bc6a49908e/track6.bed13;bed	track6.bed13	track6.bed	agc	GC	iota	G	A	G	C
        galaxy:/29ee58bc6a49908e/track6.bed14;bed	track6.bed14	track6.bed	agg	GC	iota	G	A	G	G
        galaxy:/29ee58bc6a49908e/track6.bed15;bed	track6.bed15	track6.bed	agt	GC	iota	G	A	G	T
        galaxy:/29ee58bc6a49908e/track3.bed16;bed	track3.bed16	track3.bed	aca	CA	iota	C	A	C	A
        galaxy:/29ee58bc6a49908e/track3.bed17;bed	track3.bed17	track3.bed	acc	CA	iota	C	A	C	C
        galaxy:/29ee58bc6a49908e/track3.bed18;bed	track3.bed18	track3.bed	acg	CA	iota	C	A	C	G
        galaxy:/29ee58bc6a49908e/track3.bed19;bed	track3.bed19	track3.bed	act	CA	iota	C	A	C	T
        galaxy:/29ee58bc6a49908e/track4.bed20;bed	track4.bed20	track4.bed	aga	GT	iota	G	A	G	A
        galaxy:/29ee58bc6a49908e/track4.bed21;bed	track4.bed21	track4.bed	agc	GT	iota	G	A	G	C
        galaxy:/29ee58bc6a49908e/track4.bed22;bed	track4.bed22	track4.bed	agg	GT	iota	G	A	G	G
        galaxy:/29ee58bc6a49908e/track4.bed23;bed	track4.bed23	track4.bed	agt	GT	iota	G	A	G	T
                 """
              ]
              ]
        }

        toolResult = 'The output of this tool is a hGsuite with extra columns.'

        notice = "If you want to use hGSuite for the futher analysis then remeber to preprocess it using tool: Preprocess a GSuite for analysis"

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example,
                                          notice=notice
                                          )

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
