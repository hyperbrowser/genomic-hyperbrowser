from collections import OrderedDict

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteEditor import concatenateGSuitesAddingCategories
from gold.gsuite.GSuiteTrack import GSuiteTrack
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class GroupTestBM3ShuffleGroupsInGSuiteTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Group difference test - Shuffle group labels in GSuite (BM3)"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select a gsuite', 'gsuite'),
                ('Nr. of simulated sub-GSuites', 'nrSubGSuites'),
                ('Category name', 'catLbl')]


    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxNrSubGSuites(cls, prevChoices):
        return '100'

    @staticmethod
    def getOptionsBoxCatLbl(prevChoices):
        if prevChoices.gsuite:
            from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
            gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            return gsuite.attributes

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     return [HistElement('Simulated GSuite (BM3)', 'gsuite')]

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        nrSubGSuites = int(choices.nrSubGSuites)
        categoryVals = gsuite.getAttributeValueList(choices.catLbl)
        gsuiteList = []
        from random import shuffle
        for subGSuiteIndex in xrange(nrSubGSuites):
            shuffle(categoryVals)
            gsuiteList.append(cls._generateNewGSuite(gsuite, subGSuiteIndex, choices.catLbl, categoryVals, galaxyFn))

        catColName = "Sub-gsuite_index"
        counter = 0
        while catColName in gsuite.attributes:
            counter += 1
            catColName = "Sub-gsuite_index_{}".format(counter)
        newGSuite = concatenateGSuitesAddingCategories(gsuiteList, categoryColumnTitle=catColName,
                                                       categoryList=[str(x) for x in xrange(nrSubGSuites)])

        GSuiteComposer.composeToFile(newGSuite, galaxyFn)


    @classmethod
    def _generateNewGSuite(cls, gsuite, subGSuiteIndex, catLbl, categoryVals, galaxyFn):
        newTracks = []
        for track, newCategoryVal in zip(list(gsuite.allTracks()), categoryVals):
            extraFN = "simulated_" + track.title + "_" + str(subGSuiteIndex)
            newAttrs = OrderedDict([(x,y,) for x, y in track.attributes.items()])
            newAttrs[catLbl] = newCategoryVal
            gSuiteTrack = GSuiteTrack(track.uri, title=extraFN, genome=gsuite.genome, attributes=newAttrs)
            newTracks.append(gSuiteTrack)

        return GSuite(trackList=newTracks)


    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gsuite:
            return "Please select a GSuite"

        try:
            int(choices.nrSubGSuites)
        except:
            return "Nr. of sub-GSuites must be a valid integer."


    # @classmethod
    # def getSubToolClasses(cls):
    #     return None

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

    @classmethod
    def getOutputFormat(cls, choices):
        return 'gsuite'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
