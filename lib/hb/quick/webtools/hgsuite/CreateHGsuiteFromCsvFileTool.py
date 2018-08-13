from quick.webtools.GeneralGuiTool import GeneralGuiTool, HistElement
from quick.webtools.hgsuite.HGsuiteClass import HGsuite
import quick.gsuite.GuiBasedTsFactory as factory
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.gsuite import GSuiteStatUtils
from collections import OrderedDict
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.webtools.hgsuite.Legend import Legend

class CreateHGsuiteFromCsvFileTool(GeneralGuiTool):


    @classmethod
    def getToolName(cls):

        return "Combain metadata"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select hGSuite', 'gSuite'),
                ('See columns', 'possibleColumns'),
                ('Select columns numbers which you want to combain (e.g. 1,2, 4-6)', 'selectedColumns')
                ]

    @classmethod
    def getOptionsBoxGSuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxPossibleColumns(cls, prevChoices):

        #for reading only from gSuite
        if prevChoices.gSuite:
            gSuiteTN = getGSuiteFromGalaxyTN(prevChoices.gSuite)

            tableElements = [['Column number', 'Column name']]
            i=1
            for attr in gSuiteTN.attributes:
                tableElements.append([i, attr])
                i+=1
            return tableElements

    @classmethod
    def getOptionsBoxSelectedColumns(cls, prevChoices):
        if prevChoices.gSuite:
            return ''

    @classmethod
    def validateAndReturnErrors(cls, choices):
        hGSuite = HGsuite()

        if not choices.gSuite:
            return 'Select gSuite'

        if choices.gSuite:
            if choices.selectedColumns != '':
                selCol = hGSuite.parseColumnResponse(choices.selectedColumns)
                if len(selCol) > 15:
                    return 'Limited number of column is 15. You selected: ' + str(len(selCol)) + ' columns.'

        return


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        #selectedFile = choices.selectedFile
        selectedColumns = choices.selectedColumns
        gSuite = choices.gSuite

        hGSuite = HGsuite()
        # get selected columns as a list with numbers: starting from 0
        selCol = hGSuite.parseColumnResponse(selectedColumns)
        #get the column with new atributes

        gSuiteTN = getGSuiteFromGalaxyTN(gSuite)



        #dataFromFile, header, message = hGSuite.parseCvsFileBasedOnColumsNumber(selectedFile, selCol)
        dataFromFile, header, message = hGSuite.parseGSuiteFileBasedOnColumsNumber(gSuiteTN, selCol)

        extraGalaxyElement = cls.extraGalaxyFn['hGSuite']

        #refTS = factory.getFlatTracksTS(gSuiteTN.genome, gSuite)
        #iteration through refTS did not support the proper order of tracks


        if len(header) == 1:
            results = OrderedDict()
            i=0
            for tr in gSuiteTN.allTrackTitles():
                results[tr] = dataFromFile[i]
                i+=1

            GSuiteStatUtils.addResultsToInputGSuite(gSuiteTN, results, header, extraGalaxyElement)
        else:
            for h in header:
                results = OrderedDict()
                i = 0
                for tr in gSuiteTN.allTrackTitles():
                    results[tr] = dataFromFile[h][i]
                    i += 1
                GSuiteStatUtils.addResultsToInputGSuite(gSuiteTN, results, [h],
                                                        extraGalaxyElement)
                results.clear()

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.paragraph('HGsuite with new category is in the history.')
        htmlCore.paragraph(message)
        htmlCore.end()

        print htmlCore

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('hGSuite', 'gsuite')]

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if not choices.gSuite:
            return 'Select gSuite'

    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'

    @classmethod
    def isPublic(cls):
        return True

    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'This tool combain metadata of hGSuite.'

        stepsToRunTool = ['Select hGSuite',
                          'Select columns numbers which you want to combain (e.g. 1,2, 4-6)']

        example = {'Example':['',["""
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
                   [['Select hGSuite', 'gsuite'],
                    ['Select columns numbers which you want to combain (e.g. 1,2, 4-6) ', '1,2']],
   ["""
    ##location: local
    ##file format: preprocessed
    ##track type: unknown
    ##genome: hg19
    ###uri          	                                  title    t-cells  t-cells-b-cells  b-cells
    hb:/external/gsuite/c2/c298599af8b0d539/track1.bed	track1.bed	X	t-cells	      .
    hb:/external/gsuite/c2/c298599af8b0d539/track2.bed	track2.bed	.	b-cells	      X
    hb:/external/gsuite/c2/c298599af8b0d539/track3.bed	track3.bed	.	.	      .
    hb:/external/gsuite/c2/c298599af8b0d539/track4.bed	track4.bed	X	t-cells	      .
    hb:/external/gsuite/c2/c298599af8b0d539/track5.bed	track5.bed	.	.	      .
    """
   ]
                ]}

        toolResult = 'The output of this tool is hGsuite with extra columns, which have combained data.'



        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example)
