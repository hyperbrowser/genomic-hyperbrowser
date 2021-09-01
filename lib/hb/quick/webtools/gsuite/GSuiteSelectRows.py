from collections import OrderedDict

from gold.gsuite.GSuiteComposer import composeToFile
from gold.gsuite.GSuiteEditor import selectRowsFromGSuiteByTitle
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.util import CommonFunctionsForTools


class GSuiteSelectRows(GeneralGuiTool):
    exception = None

    INDEX_TITLE_DELIMITER = ': '

    @classmethod
    def getToolName(cls):
        return "Select subsets of tracks in a GSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select a GSuite file from history', 'history'),
                ('Row indices (e.g. 1-20 or 1,3,5,19-29. NB: Intervals are end inclusive)', 'rowIndices'),
                ('Select rows', 'selectRows'),
                ('', 'showVisualization')]

    @classmethod
    def getOptionsBoxHistory(cls):
        return '__history__', 'gsuite'

    @classmethod
    def getOptionsBoxRowIndices(cls, prevChoices):
        if prevChoices.history is None:
            return
        
        gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
        
        return '1-%i' % (gSuite.numTracks() + 1)
    
    @classmethod
    def getOptionsBoxSelectRows(cls, prevChoices):
        if prevChoices.history is None:
            return
        try:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
            rowIndicesStr = prevChoices.rowIndices

            if rowIndicesStr:
                selectedIndices = CommonFunctionsForTools.processIndicesString(rowIndicesStr)
            else:
                selectedIndices = xrange(len(gSuite))

            resDict = OrderedDict()
            for i, trackTitle in enumerate(gSuite.allTrackTitles()):
                selected = i in selectedIndices
                resDict[cls._addIndexToTitle(i, trackTitle)] = selected
            return resDict
        except Exception:
            pass
    
    @classmethod
    def getOptionsBoxShowVisualization(cls, prevChoices):
        return
#         if prevChoices.history == None:
#             return
#         else:
#             try:
#                 gSuite = getGSuiteFromGalaxyTN(prevChoices.history)
#                 rowIndicesStr = prevChoices.rowIndices
#                 if rowIndicesStr:
#                     selectedIndices = CommonFunctionsForTools.processIndicesString(rowIndicesStr)
#                     if selectedIndices:
#                         maxIndex = max(selectedIndices)
#                         if maxIndex > (gSuite.numTracks()-1):
#                             return 
#                         else:
#                             from quick.webtools.restricted.visualization.visualizationGraphs import \
#                                 visualizationGraphs, dataTransformer
#                             
#                             titleList = [tt for i, tt in enumerate(gSuite.allTrackTitles()) if i in selectedIndices]
#                             wholeList = gSuite.allTrackTitles()
#                             
#                             res=OrderedDict()
#                             for w in wholeList:
#                                 if w in titleList:
#                                     res[w]=1
#                                 else:
#                                     res[w]=0
#                             
#                             dT = dataTransformer(res)
#                             seriesName, categories, data = dT.changeDictIntoList()
#                              
#                             vg = visualizationGraphs()
#                             res = vg.drawBarChart(data, categories=categories, seriesName=['Tracks'],
#                                                   allowDecimals=False, maxY=1)
#                             
#                             return '__rawstr__', str(vg.visualizeResults(res))
#             except:
#                 pass

    @classmethod
    def _addIndexToTitle(cls, indx, title):
        return cls.INDEX_TITLE_DELIMITER.join([str(indx + 1), title])

    @classmethod
    def _removeIndexFromTitleName(cls, titleWithIndex):
        delimiterIndex = titleWithIndex.find(cls.INDEX_TITLE_DELIMITER)
        if delimiterIndex > -1:
            return titleWithIndex[(delimiterIndex + len(cls.INDEX_TITLE_DELIMITER)):]
        else:
            return titleWithIndex

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.history)

        titleList = [cls._removeIndexFromTitleName(title) for title, selected in choices.selectRows.iteritems() if selected]
        filteredGSuite = selectRowsFromGSuiteByTitle(gSuite, titleList)

        composeToFile(filteredGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        errorStr = GeneralGuiTool._checkGSuiteFile(choices.history)
        if errorStr:
            return errorStr
        
        gSuite = getGSuiteFromGalaxyTN(choices.history)
        if choices.rowIndices:
            try:
                selectedIndices = CommonFunctionsForTools.processIndicesString(choices.rowIndices)
                maxIndex = max(selectedIndices)
                if maxIndex >= len(gSuite):
                    return 'Selected row index %i is too high. GSuite contains %i tracks.' % (maxIndex, gSuite.numTracks())
            except:
                return 'Please enter valid indices string (e.g. 1-10, 12, 14)'

        if len(gSuite) == 0:
            return 'GSuite file contains no tracks'

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None

    @classmethod
    def isPublic(cls):
        return True

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

    @classmethod
    def getResetBoxes(cls):
        return ['history', 'rowIndices']
    
    @classmethod
    def getToolDescription(cls):
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()
        core.paragraph('This tool provides the option of filtering tracks in a GSuite file '
                       'generating as output a GSuite file with the same columns, but '
                       'with only a subset of tracks (rows) as selected by the user.')
        core.divider()
        core.paragraph('To filter a GSuite file, please follow these steps: ')
        core.orderedList(['Select the input GSuite file from history',
                          'Select the tracks that should be kept (described in the list '
                          'by its title, or by the whole uri if the title is not defined)',
                          'Click the "Execute" button'])

        cls._addGSuiteFileDescription(core,
                                      alwaysShowRequirements=True,
                                      alwaysShowOutputFile=True)

        return str(core)

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

    @classmethod
    def getOutputName(cls, choices):
        if choices.history:
            from quick.gsuite.GSuiteHbIntegration import getGSuiteHistoryOutputName
            return getGSuiteHistoryOutputName('same', ', subset of tracks', choices.history)
