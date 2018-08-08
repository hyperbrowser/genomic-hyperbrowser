from quick.webtools.GeneralGuiTool import GeneralGuiTool, HistElement
from quick.webtools.hgsuite.HGsuiteClass import HGsuite
import quick.gsuite.GuiBasedTsFactory as factory
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.gsuite import GSuiteStatUtils
from collections import OrderedDict
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.webtools.assemblygap.Legend import Legend

class CreateHGsuiteFromCsvFileTool(GeneralGuiTool):


    @classmethod
    def getToolName(cls):

        return "Combain metadata for hGSuite"

    @classmethod
    def getInputBoxNames(cls):

        return [('Select hGSuite:', 'gSuite'),
                ('Select columns', 'possibleColumns'),
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
    def getOutputFormat(cls, choices):
        return 'customhtml'


    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'This tool combain metadata of hGSuite.'

        stepsToRunTool = ['Select hGSuite',
                          'Select columns',
                          'Select columns numbers which you want to combain (e.g. 1,2, 4-6)']

        toolResult = 'The output of this tool is hGsuite with extra columns, which have combained data.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult)
