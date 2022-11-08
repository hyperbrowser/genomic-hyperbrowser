from ast import literal_eval
from functools import partial

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteConstants import TITLE_COL
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.Legend import Legend


class AddAMetadataToGSuiteTool(GeneralGuiTool):
    MAX_NUM_OF_TRACKS = 100

    @classmethod
    def getToolName(cls):
        return "Add metadata column in hGSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select GSuite or hGSuite', 'gsuite'),
                ('Add data from file?', 'fileYesNo'),
                ('Select text file', 'selFile'),  #select a txt file that has track name and the corresponding metadata to add
                ('File info', 'filename'),
                ('Add metadata column', 'attrName'),
                ('', 'gsuiteTitles'),
                ('', 'gsuiteAttributeValues')] + \
               [('', 'selectAttribute%s' % i) for i
                in range((cls.MAX_NUM_OF_TRACKS * 2))]

    #     cls.getInputBoxNamesForGSuiteSelection() + \
    #     [('Select text file', 'selFile')
    #
    # ] + cls.getInputBoxNamesForbedfile()

    @classmethod
    def getOptionsBoxGsuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxFileYesNo(cls,prevChoices):
        return ["no","yes"]

    @classmethod
    def getOptionsBoxSelFile(cls, prevChoices):
        if prevChoices.fileYesNo == 'yes':
            return GeneralGuiTool.getHistorySelectionElement('tabular')


    @classmethod
    def getOptionsBoxFilename(cls, prevChoices):
        if prevChoices.fileYesNo == 'yes':
            if prevChoices.selFile:
                ll=cls.readFile(prevChoices.selFile)
                num=10
                if len(ll) >= num:
                    return ll[0:num]
                else:
                    return ll

    @classmethod
    def getOptionsBoxAttrName(cls, prevChoices):
        if prevChoices.fileYesNo == 'no':
            if prevChoices.gsuite:
                return ''

    @classmethod
    def readFile(cls, selFile2):
        allDataList = []
        with open(ExternalTrackManager.extractFnFromGalaxyTN(selFile2.split(':')), 'r') as f:
            for r in f:
                line = r.strip('\n').split('\t')
                if line != ['']:
                    allDataList.append([i for i in line])
        return allDataList

    @classmethod
    def getOptionsBoxGsuiteTitles(cls, prevChoices):
            if prevChoices.gsuite:
                gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
                return '__hidden__', gSuite.allTrackTitles()

        # if prevChoices.selFile:
        #     return None
            #gsuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            #file = readFile(prevChoices.filename)
            #return '__hidden__', gSuite.allTrackTitles()

    @classmethod
    def _getGsuiteTitles(cls, prevChoices):
        gsuiteTitles = prevChoices.gsuiteTitles
        if isinstance(gsuiteTitles, basestring):
            gsuiteTitles = literal_eval(gsuiteTitles)
        return gsuiteTitles

    @classmethod
    def getOptionsBoxGsuiteAttributeValues(cls, prevChoices):
        if prevChoices.gsuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            attrName = prevChoices.attrName
            if attrName != '':
                if gSuite.getCustomHeader(attrName):
                    return '__hidden__', [track.getAttribute(attrName) for track in gSuite.allTracks()]

    @classmethod
    def _getGsuiteAttributeValues(cls, prevChoices):
        gsuiteAttributeValues = prevChoices.gsuiteAttributeValues
        gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
        if gSuite.getCustomHeader(prevChoices.attrName):
            if isinstance(gsuiteAttributeValues, basestring):
                gsuiteAttributeValues = literal_eval(gsuiteAttributeValues)
            return gsuiteAttributeValues

    @classmethod
    def _getOptionsBoxLabel(cls, prevChoices, index):
        if not prevChoices.gsuite or not prevChoices.attrName:
            return

        gSuiteTitles = cls._getGsuiteTitles(prevChoices)
        if index < len(gSuiteTitles) * 2:
            return '__rawstr__', '<b>Add value for track nr. %s with title "%s":</b>' % (
            (index / 2) + 1, gSuiteTitles[index / 2])


    @classmethod
    def _getOptionsBoxForSelectAttribute(cls, prevChoices, index):
        if not prevChoices.gsuite or not prevChoices.attrName:
            return
        gSuiteTitles = cls._getGsuiteTitles(prevChoices)
        gSuiteAttributeValues = cls._getGsuiteAttributeValues(prevChoices)
        attrName = prevChoices.attrName
        if index < len(gSuiteTitles) * 2:
            if attrName == TITLE_COL:
                attrValue = gSuiteTitles[index / 2]
            else:
                if not gSuiteAttributeValues:
                    attrValue = '.' # ['' for t in gSuiteTitles[index / 2]]
                else:
                    attrValue = gSuiteAttributeValues[index / 2]
            return str(attrValue)

    @classmethod
    def setupSelectGSuiteMethods(cls):
        for i in xrange(cls.MAX_NUM_OF_TRACKS * 2):
            """setattr(cls, 'getOptionsBoxSelectAttribute%s' % i, partial(cls._getOptionsBoxLabel, index=i))
            setattr(cls, 'getOptionsBoxSelectAttribute%s' % i, partial(cls._getOptionsBoxForSelectAttribute, index=i))"""
            if (i % 2 == 0):
                setattr(cls, 'getOptionsBoxSelectAttribute%s' % i,
                        partial(cls._getOptionsBoxLabel, index=i))
            else:
                setattr(cls, 'getOptionsBoxSelectAttribute%s' % i,
                        partial(cls._getOptionsBoxForSelectAttribute, index=i))


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        outputGSuite = GSuite()
        if choices.fileYesNo == 'yes':
            #reads only tabular file from user and file should have the correct sample name
            ourFile = cls.readFile(choices.selFile)
            for i, track in enumerate(gSuite.allTracks()):  #loops through the tracks
                if i < cls.MAX_NUM_OF_TRACKS:
                    trackTitle = track.title.split(' - ', 1)[1]
                    indexOfTitle = [item[0] for item in ourFile].index(trackTitle)
                    for j in range(1, len(ourFile[0])):
                        attrName = ourFile[0][j]
                        newAttrValue = str(ourFile[indexOfTitle][j])
                        if newAttrValue == 'None':
                            newAttrValue = '.'
                        track.setAttribute(attrName.encode('utf-8'), newAttrValue.encode('utf-8'))

                    outputGSuite.addTrack(track)
            GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

        else:

            attrName = choices.attrName
            outputGSuite = GSuite()

            for i, track in enumerate(gSuite.allTracks()):
                if i < cls.MAX_NUM_OF_TRACKS:
                    newAttrValue = getattr(choices, 'selectAttribute%s' % ((i*2)+1))
                    if(attrName == TITLE_COL):
                        track.title = newAttrValue
                    else:
                        if newAttrValue == 'None' or newAttrValue == '':
                            newAttrValue = '.'
                        track.setAttribute(attrName.encode('utf-8'), newAttrValue.encode('utf-8'))
                outputGSuite.addTrack(track)

            #Creates the new GSuite
            GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.gsuite:
            return 'Select GSuite or hGSuite'

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        if choices.attrName:
            if choices.attrName in gSuite.attributes:
                return 'Attribute with that name has been already in the gsuite'

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
    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'This tool adds a metadata column for GSuite (hGSuite).'

        stepsToRunTool = ['Select GSuite (hGSuite)',
                          'Add metadata column or Select "yes" on the "Add data from file" option',
                          'Add value for track nr. 1 with title or Select your metadata from your history',
                          'Check the overview provided by the tool and execute']



        example = {'Example': ['', ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: hg19
        ###uri          	                                  title     T-cells B-cells
        hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	.
        hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	X
        hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	.
        hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.
        """],
            [
                ['Select GSuite (hGSuite)', 'gsuite'],
                ['Add metadata column ', 'Coverage'],
                ['Add value for track nr. 1 with title "track1.bed":', '100'],
                ['Add value for track nr. 2 with title "track2.bed":', 'None'],
                ['Add value for track nr. 3 with title "track3.bed":', '1500'],
                ['Add value for track nr. 4 with title "track4.bed":', '.'],
                ['Add value for track nr. 5 with title "track5.bed":', '1200'],

            ],
        ["""
        ##location: local
        ##file format: preprocessed
        ##track type: unknown
        ##genome: hg19
        ###uri          	                                  title     T-cells B-cells   Coverage
        hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	.       100
        hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	X       .
        hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.       1500
        hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	.       .
        hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.       1200
        """
                                ]
                               ]}

        toolResult = 'Metadata file must be uploaded to hyperbrowser, this can be done using the upload file tool). Ensure that this file is of tabular format. Ensure that the first column of the file has names matching the imputed bed files (including the .bed extension). Therefore if a bed file called my_bed_1.bed is in the GSuite, that same name is expected to be found in the first column of the file. Following columns will be the metadata associated to the bed files marked in the first column. The output of this tool is GSuite (hGsuite) with the extra metadata column.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example)

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
AddAMetadataToGSuiteTool.setupSelectGSuiteMethods()
