from gold.gsuite import GSuiteConstants
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from collections import OrderedDict

# Author: Diana Domanska


'''
Input:
1 - Track
2 - GSuite file

Calculation:
Calculate overlaps in segments among track and other tracks
Vizualization: heatmap, column and line plots


Output:
hmtl file

'''

colorMaps = {
       'BlueYellowRedBlack': [[0, '#3060cf'], [0.5, '#fffbbc'], [0.9, '#c4463a'], [1, '#000000']],
       'WhiteGrayBlack' : [[0, '#ffffff'], [0.5, '#cccccc'], [0.9, '#4a525a'], [1.0, '#000000']],
       'GreenOrangeBlue' : [[0, '#c2ecb5'], [0.5, '#ff6600'], [1.0, '#31698a']],
       'GrayPinkBlack': [[0, '#cdc5bf'], [0.5, '#ffe4e1'], [0.9, '#fa5d68'], [1, '#000000']],
       'YellowVioletRed' : [[0, '#ffffc1'], [0.5, '#9304ec'], [1.0, '#c4463a']]
    }

class SegmentsOverlapVisualizationHeatmapTool(GeneralGuiTool, UserBinMixin,
                                              GenomeMixin):

    ALLOW_UNKNOWN_GENOME = False
    ALLOW_GENOME_OVERRIDE = False
    
    exception = None

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    TRACK_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS, GSuiteConstants.VALUED_SEGMENTS] #points?

    @staticmethod
    def getToolName():
        return "Generate a heatmap based on overlap of segments from a query track with reference tracks in a GSuite"

    @classmethod
    def getInputBoxNames(cls):

        return [('Basic user mode', 'isBasic'), ('Select track','targetTrack'), \
                ('Select GSuite file from history', 'gsuite'), \
                ('Select metadata from GSuite', 'selectColumns')] +\
                cls.getInputBoxNamesForGenomeSelection() +\
                [
                ('Select a color map:', 'colorMapSelectList')
                ] + cls.getInputBoxNamesForUserBinSelection()

    @staticmethod
    def getOptionsBoxIsBasic(): # Alternatively: getOptionsBox1()
        return False
    
#     @staticmethod
#     def getOptionsBoxTargetTrackGenome():
#         return GeneralGuiTool.GENOME_SELECT_ELEMENT

    @staticmethod
    def getOptionsBoxTargetTrack(prevChoices): # refTrack
        return GeneralGuiTool.getHistorySelectionElement('bed', 'gtrack')

    @staticmethod 
    def getOptionsBoxGsuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxSelectColumns(cls, prevChoices):
        from gold.gsuite.GSuiteConstants import TITLE_COL
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

        if prevChoices.gsuite == None:
            return
        try:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gsuite)
        except:
            return

        cols = []
        if gSuite.hasCustomTitles():
            cols.append(TITLE_COL)
        cols += gSuite.attributes

        return cols

    @staticmethod
    def getOptionsBoxColorMapSelectList(prevChoices): # Alternatively: getOptionsBox1()
        return colorMaps.keys()

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        genome = choices.genome
         

        from quick.multitrack.MultiTrackCommon import getGSuiteDataFromGalaxyTN
        trackTitles, refTrackNameList, genome = getGSuiteDataFromGalaxyTN(choices.gsuite)
        
        queryTrackName = ExternalTrackManager.extractFnFromGalaxyTN(choices.targetTrack)
        if choices.isBasic:
            suffix = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices.targetTrack, False)
            regSpec = suffix
            binSpec = queryTrackName
        else:
            regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        
        #targetTrack = choices.targetTrack.split(':')
        #targetTrackTitle = targetTrack[-1]
        #print targetTrackTitle
        #
        #binSpec = targetTrackTitle
        #Phenotype and disease associations:Assorted experiments:Virus integration, HPV specific, Kraus and Schmitz, including 50kb flanks

        from gold.gsuite.GSuiteConstants import TITLE_COL
        from gold.gsuite.GSuite import GSuite
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        from gold.gsuite.GSuiteEditor import selectColumnsFromGSuite
        staticFile=[]
        
        results = []
        for refTrack in refTrackNameList:
            analysisDef = '-> ProportionCountStat'
            res = GalaxyInterface.runManual([refTrack], analysisDef, regSpec, binSpec, genome, username=username, galaxyFn=galaxyFn, printRunDescription=False, printResults=False, printProgress=False)
            segCoverageProp = [res[seg]['Result'] for seg in res.getAllRegionKeys()]
            results.append(segCoverageProp)
            
            regFileNamer = GalaxyRunSpecificFile(refTrack, galaxyFn)
            staticFile.append([regFileNamer.getLink('Download bed-file'), regFileNamer.getLoadToHistoryLink('Download bed-file to History')])

        refGSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        if TITLE_COL == choices.selectColumns:
            selected = trackTitles
        else:
            selected = refGSuite.getAttributeValueList(choices.selectColumns)

        yAxisNameOverMouse=[]
        for x in range(0, len(selected)):
            if selected[x] == None:
                yAxisNameOverMouse.append(str(trackTitles[x]) + ' --- ' + 'None')
            else:
                if TITLE_COL == choices.selectColumns:
                    yAxisNameOverMouse.append(selected[x].replace('\'', '').replace('"', ''))
                else:
                    yAxisNameOverMouse.append(str(trackTitles[x]) + ' --- ' + '<b>' + str(selected[x].replace('\'', '').replace('"', '')))


        #startEnd - order in res
        startEndInterval = []
        startEnd = []
        i=0
        

        extraX=[]
        rowLabel = []
        for ch in res.getAllRegionKeys():
            rowLabel.append(str(ch.chr) + ":" + str(ch.start) + "-" + str(ch.end) + str(' (Pos)' if ch.strand else ' (Neg)'))
            if not i==0 and not i==len(res.getAllRegionKeys())-1:
                start = ch.start
                if start-end > 0:
                    startEnd.append(start-end)
                else:
                    startEnd.append('null')
                    extraX.append("""{ color: 'orange', width: 5, value: '""" + str(i-0.5) + """' }""")
                startEndInterval.append(ch.end - ch.start)
            else:
                startEndInterval.append(ch.end - ch.start)
            end = ch.end
            i+=1

        extraXAxis='plotLines: [ '
        extraXAxis = extraXAxis + ",".join(extraX)
        extraXAxis = extraXAxis + """ ],  """

        #rowLabel = res.getAllRegionKeys()
        #rowLabel = [str(x) for x in rowLabel]
        

        import quick.webtools.restricted.visualization.visualizationPlots as vp

        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin(divId='results-page')
        htmlCore.divBegin(divClass='results-section')
        htmlCore.divBegin('plotDiv')
        htmlCore.line(vp.addJSlibs())
        htmlCore.line(vp.useThemePlot())
        htmlCore.line(vp.addJSlibsExport())
        htmlCore.line(vp.axaddJSlibsOverMouseAxisisPopup())
        #vp.addGuideline(htmlCore)
        htmlCore.line(vp._addGuidelineV1())

        htmlCore.line(vp.addJSlibsHeatmap())
        
        
        hm, heatmapPlotNumber, heatmapPlot = vp.drawHeatMap(
                                                results,
                                                colorMaps[choices.colorMapSelectList],
                                                label='this.series.xAxis.categories[this.point.x] + ' + "'<br >'" + ' + yAxisNameOverMouse[this.point.y] + ' + "'<br>Overlap proportion: <b>'" + ' + this.point.value + ' + "'</b>'",
                                                yAxisTitle= 'Reference tracks',
                                                categories=rowLabel,
                                                tickInterval=1,
                                                plotNumber=3,
                                                interaction=True,
                                                otherPlotNumber=1,
                                                titleText='Overlap with reference tracks for each local region',
                                                otherPlotData=[startEnd, startEndInterval],
                                                overMouseAxisX=True,
                                                overMouseAxisY=True,
                                                yAxisNameOverMouse=yAxisNameOverMouse,
                                                overMouseLabelY=" + 'Track: '" + ' + this.value + ' + "' '" + ' + yAxisNameOverMouse[this.value] + ',
                                                overMouseLabelX = ' + this.value.substring(0, 20) +',
                                                extrOp = staticFile
                                                )
        htmlCore.line(hm)
        htmlCore.line(vp.drawChartInteractionWithHeatmap(
            [startEndInterval, startEnd],
            tickInterval=1,
            type='line',
            categories=[rowLabel, rowLabel],
            seriesType=['line', 'column'],
            minWidth=300,
            height=500,
            lineWidth=3,
            titleText=['Lengths of segments (local regions)','Gaps between consecutive segments'],
            label=['<b>Length: </b>{point.y}<br/>', '<b>Gap length: </b>{point.y}<br/>'],
            subtitleText=['',''],
            yAxisTitle=['Lengths','Gap lengths'],
            seriesName=['Lengths','Gap lengths'],
            xAxisRotation=90,
            legend=False,
            extraXAxis=extraXAxis,
            heatmapPlot=heatmapPlot,
            heatmapPlotNumber=heatmapPlotNumber,
            overMouseAxisX=True,
            overMouseLabelX = ' + this.value.substring(0, 20) +'
            ))
        htmlCore.divEnd()
        htmlCore.divEnd()
        htmlCore.divEnd()
        htmlCore.end()

        htmlCore.hideToggle(styleClass='debug')

        print htmlCore

        #create tmp file
        #import tempfile,os
        #tmp = tempfile.NamedTemporaryFile(delete = False, suffix='.png')
        #plt.savefig(tmp.name)
        #os.rename(tmp.name,galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
            
        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        errorString = cls._validateGenome(choices)
        if errorString:
            return errorString
        
        errorString = GeneralGuiTool._checkTrack(choices, 'targetTrack', 'genome')
        if errorString:
            return errorString


        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements \
            (gsuite,
             cls.GSUITE_ALLOWED_FILE_FORMATS,
             cls.GSUITE_ALLOWED_LOCATIONS,
             cls.GSUITE_ALLOWED_TRACK_TYPES,
             cls.GSUITE_DISALLOWED_GENOMES)
        
        if errorString:
            return errorString

        errorString = GeneralGuiTool._checkGSuiteTrackListSize(gsuite)
        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString
        
        #check track
#         errorString = GeneralGuiTool._checkTrack(choices, 'targetTrack', 'targetTrackGenome')
#         if errorString:
#             return errorString
# 
#         genome, tn, tf = GeneralGuiTool._getBasicTrackFormat(choices, 'targetTrack', 'targetTrackGenome')
#         errorString = ''
#         from os import linesep
#         if tf not in SegmentsOverlapVisualizationHeatmapTool.TRACK_ALLOWED_TRACK_TYPES:
#             errorString += '%s is not a supported track type for this tool. Supported track types are ' %tf
#             errorString += str(SegmentsOverlapVisualizationHeatmapTool.TRACK_ALLOWED_TRACK_TYPES) + linesep
#             return errorString
# 
# 
#         if choices.gsuite is not None:
# 
#             targetTrackGenome = choices.targetTrackGenome
#             errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
#             if errorString:
#                 return errorString
# 
#             refGSuite = getGSuiteFromGalaxyTN(choices.refTrackCollection)
# 
#             #check genome
#             errorString = GeneralGuiTool._checkGenomeEquality(targetTrackGenome, refGSuite.genome)
#             if errorString:
#                 return errorString
# 
#             errorString = GeneralGuiTool._checkGSuiteRequirements \
#               (refGSuite,
#                SegmentsOverlapVisualizationHeatmapTool.GSUITE_ALLOWED_FILE_FORMATS,
#                SegmentsOverlapVisualizationHeatmapTool.GSUITE_ALLOWED_LOCATIONS,
#                SegmentsOverlapVisualizationHeatmapTool.GSUITE_ALLOWED_TRACK_TYPES,
#                SegmentsOverlapVisualizationHeatmapTool.GSUITE_DISALLOWED_GENOMES)
#             if errorString:
#                 return errorString
# 
#             #number of tracks
# 
#             errorString = GeneralGuiTool._checkGSuiteTrackListSize(refGSuite, maxSize=50)
#             if errorString:
#                 return errorString
#         else:
#             return None


    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore

        core = HtmlCore()

        core.paragraph('This tool computes the proportions of overlap between the segments '
                       'of a query track against each track in a collection of reference tracks '
                       'described in a GSuite file. The overlap proportions are output in an '
                       'interactive heatmap, where each cell is colored according to the '
                       'overlap between each query segment (column) with each reference '
                       'track (row).')

        core.divider()
        core.paragraph('To carry out the analysis, please follow these steps:')
        core.orderedList(['Select a genome build. Both the query track and the reference tracks'
                          'need to use the same genome build.',
                          'Select a query track from the HyperBrowser repository',
                          'Select a reference track collection as a GSuite file from history',
                          'Select the color map, going from no overlap to full overlap.',
                          'Click "Execute"'])

        core.divider()
        core.smallHeader('Requirements for query track')
        core.descriptionLine('Track types', ', '.join(cls.TRACK_ALLOWED_TRACK_TYPES), emphasize=True)


        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)
        #
        #htmlCore.divBegin(divId ='toolDesc')
        #htmlCore.descriptionLine('Tool description',
        #                         """This tool computes the proportions between overlaped segments.
        #                         Output are three plots: overlap with reference tracks for each local region,
        #                         lenghts of segments (local regions) and gaps between consecutive
        #                         segments. """)
        #htmlCore.divEnd()
        #
        #htmlCore.divBegin(divId ='toolExample')
        #htmlCore.line('<b>Example</b>')
        #htmlCore.line('<b>Input:</b>')
        #htmlCore.line('Genome build: Human Feb. 2009 (GRCh37/hg19) (hg19)')
        #htmlCore.line('Select track: Phenotype_and_disease_associations:Assorted_experiments:Virus_integration,_HPV_specific,_Kraus_et_al')
        #htmlCore.line('Select GSuite file from history: Genes and gene subsets:Genes')
        #htmlCore.line('Select a color map')
        #htmlCore.line('<b>Output:</b>')
        #htmlCore.line('Plots')
        #
        #htmlCore.divEnd()
        #
        #return htmlCore

    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None

    # @staticmethod
    # def getFullExampleURL():
    #     return 'u/hb-superuser/p/visualize-overlap-between-query-segments-and-reference-tracks-by-heatmap'

    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices=None):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'
