from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.track.Track import Track
from gold.util import CommonConstants
from gold.util.RandomUtil import random
from quick.gsuite import GSuiteStatUtils
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.GSuiteVsGSuiteWrapperStat import GSuiteVsGSuiteWrapperStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool, GeneralGuiToolMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.application.GalaxyInterface import GalaxyInterface
from urllib import quote

class CountNullModelForRandomizedGSuiteTool(GeneralGuiTool, UserBinMixin, GenomeMixin):
    ALLOW_UNKNOWN_GENOME = False

    @classmethod
    def getToolName(cls):
        return "Count null model for randomized gSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select orginal gSuite', 'orgGsuite'),
                ('Select column from orginal gSuite', 'orgCol'),
                ('Second randomized gSuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
                [('Second column from randomized gSuite', 'randCol')] + \
                cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxOrgGsuite(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxOrgCol(cls, prevChoices):
        if prevChoices.orgGsuite:
            first = getGSuiteFromGalaxyTN(prevChoices.orgGsuite)
            attributeList = ['title'] + first.attributes
            return attributeList
        else:
            return

    @classmethod
    def getOptionsBoxGsuite(cls, prevChoices):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxRandCol(cls, prevChoices):
        if prevChoices.gsuite:
            first = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            attributeList = ['title'] + first.attributes
            return attributeList
        else:
            return

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        orgGsuite = choices.orgGsuite
        randGsuite = choices.gsuite
        orgCol = choices.orgCol
        randCol = choices.randCol

        orginalgSuite = getGSuiteFromGalaxyTN(orgGsuite)
        randomGsuite = getGSuiteFromGalaxyTN(randGsuite)

        if randCol == 'title':
            randAttributesList = randomGsuite.allTrackTitles()
        else:
            randAttributesList = randomGsuite.getAttributeValueList(randCol)

        randAttributesListNotDuplicates = list(set(randAttributesList))
        numRandAttributesList = len(list(set(randAttributesListNotDuplicates)))

        if orgCol == 'title':
            orgAttributesList = orginalgSuite.allTrackTitles()
        else:
            orgAttributesList = orginalgSuite.getAttributeValueList(orgCol)

        orgAttributesListNotDuplicates = list(set(orgAttributesList) - set(randAttributesList))
        numOrgAttributesListNotDuplicates = len(orgAttributesListNotDuplicates)

        randOrginalTracks = random.sample(xrange(numOrgAttributesListNotDuplicates), numRandAttributesList)

        print randOrginalTracks

        oTr = 0
        rTr = 0
        for oTrack1 in orginalgSuite.allTracks():
            if oTr in randOrginalTracks:

                #first analysis
                #one random track from gsuite1 - T1
                #second random track from gsuite - T2

                oTrackName1 = oTrack1.trackName
                oTrack2 = orginalgSuite.getTrackFromTitle(randAttributesListNotDuplicates[rTr])

                regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
                analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=orginalgSuite.genome)





                resultsObj = doAnalysis(analysisSpec, analysisBins, queryTrackList + refTrackList)
                results = resultsObj.getGlobalResult()

                print results



                rTr += 1
            oTr += 1



        #check random number of tracks




    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     return False
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
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
