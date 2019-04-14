from collections import OrderedDict
from functools import partial

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class ModifyMetadataInHGSuiteTool(GeneralGuiTool):

    MAX_NUM_OF_TRACKS = 250

    @classmethod
    def getToolName(cls):
        return "Modify metadata in hGSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select hGSuite', 'gsuite')] +\
                [('', 'metadataColumn%s' %i) for i in range((cls.MAX_NUM_OF_TRACKS))]

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')


    @classmethod
    def _getOptionsBoxMetadataColumn(cls, prevChoices, index):
        if prevChoices.gsuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            attr = gSuite.attributes
            if index < len(attr):
                #return str(index) + str(attr[index]) + str([a for a in attr])
                return str(attr[index])

    @classmethod
    def setupSelectGSuiteMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_TRACKS):
            setattr(cls, 'getOptionsBoxMetadataColumn%s' % i, partial(cls._getOptionsBoxMetadataColumn, index=i))

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        attr = gSuite.attributes

        outputGSuite = GSuite()
        for i, track in enumerate(gSuite.allTracks()):
            attrNew = OrderedDict()
            for index, at in enumerate(attr):
                if index < len(attr):
                    newAttrValue = getattr(choices, 'metadataColumn%s' % index)
                    attrNew[str(newAttrValue)] = str(track.getAttribute(at))

            cls._buildTrack(outputGSuite, track.title, gSuite.genome, track.uri, attrNew, track.trackType)

        # Creates the new GSuite
        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def _buildTrack(cls, outGSuite, trackTitle, genome, trackPath, attr, trackType):

        uri = trackPath
        gSuiteTrack = GSuiteTrack(uri)
        gs = GSuiteTrack(uri,
                         title=''.join(trackTitle),
                         genome=genome,
                         attributes=attr,
                         trackType=trackType)

        outGSuite.addTrack(gs)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.gsuite:
            return 'Select GSuite or hGSuite'

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if not gSuite.attributes:
            return 'There are not attributes in the gSuite'

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
    @classmethod
    def getOutputFormat(cls, choices):
        return 'gsuite'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
ModifyMetadataInHGSuiteTool.setupSelectGSuiteMethods()