from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
from proto.CommonFunctions import ensurePathExists
from proto.tools.GeneralGuiTool import HistElement
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from gold.gsuite.GSuiteConstants import TITLE_COL
import math

class ModifyMetadataAccordingToUserOperationsTool(GeneralGuiTool):

    OPER_BINNING = 'binning'
    OPER = 'user operation'

    @classmethod
    def getToolName(cls):
        return "Modify metadata according to user operations"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select gSuite', 'gsuite1'),
                ('Select type of operations', 'operation'),
                ('Select column', 'metadata1'),
                ('Number of bins (default 10)', 'binNum')]

    @classmethod
    def getOptionsBoxGsuite1(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxOperation(cls, prevChoices):
        return [cls.OPER, cls.OPER_BINNING]

    @classmethod
    def getOptionsBoxMetadata1(cls, prevChoices):
        if not prevChoices.gsuite1:
            return

        if not prevChoices.operation == cls.OPER_BINNING:
            return

        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite1)
        attributeList = gSuite.attributes
        #return [TITLE_COL] + attributeList
        return attributeList

    @classmethod
    def getOptionsBoxBinNum(cls, prevChoices):

        if not prevChoices.operation == cls.OPER_BINNING:
            return

        return '10'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        gsuiteName1 = choices.gsuite1
        gSuite1 = getGSuiteFromGalaxyTN(gsuiteName1)
        metaAtr1 = choices.metadata1
        binNum = float(choices.binNum)


        keys1 = gSuite1.getAttributeValueList(metaAtr1)
        values1 = gSuite1.allTrackTitles()

        allKeys = [float(k) for k in keys1]
        minK = min(allKeys)
        maxK = max(allKeys)

        t = zip(keys1, values1)
        dictAttr1 = dict()
        for x, y in t:

            norm = (float(x) - minK) / (maxK - minK)
            category = int(min(math.floor(binNum * norm), binNum-1))

            if (dictAttr1.has_key(y)):
                pass
            else:
                dictAttr1[y] = category

        outputGSuite = GSuite()

        for i, track in enumerate(gSuite1.allTracks()):
            track.setAttribute(metaAtr1 + '-categories', str(dictAttr1[track.trackName[-1]]))
            outputGSuite.addTrack(track)
        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)


    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    @classmethod
    def isPublic(cls):
        return True
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'gsuite'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
