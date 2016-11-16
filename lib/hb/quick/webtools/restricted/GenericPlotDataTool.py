from collections import OrderedDict

from gold.gsuite.GSuiteConstants import TITLE_COL
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class GenericPlotDataTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Generate plot"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select GSuite','gSuite'),
                ('Show series on', 'plotSeries'),
                ('Select type of plot', 'plotType'),
                ('Select value for x-Axis', 'columnX'),
                ('Select value for y-Axis', 'columnY')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @classmethod
    def getOptionsBoxPlotSeries(cls, prevChoices): 
        return ['Single', 'Multi']
    
    @classmethod
    def getOptionsBoxPlotType(cls, prevChoices):
        if prevChoices.plotSeries == 'Single': 
            return ['Column', 'Scatter', 'Heatmap']
        else:
            return ['Column', 'Scatter']
    
    
    @classmethod
    def getOptionsBoxColumnX(cls, prevChoices): # Alternatively: getOptionsBox2()
        if not prevChoices.gSuite:
            return
        
        gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
        attributeList = gSuite.attributes
        
        return ['Iterate'] + [TITLE_COL] + attributeList
    
    @classmethod
    def getOptionsBoxColumnY(cls, prevChoices): # Alternatively: getOptionsBox2()
        if not prevChoices.gSuite:
            return
        
        gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
        attribute = gSuite.attributesType()
        
        att=OrderedDict()
        for key, it in attribute.iteritems():
            if it == True:
                att[key] = False
        
        return att
    
    
    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getInputBoxGroups(choices=None):
    #    '''
    #    Creates a visual separation of groups of consecutive option boxes from the rest (fieldset).
    #    Each such group has an associated label (string), which is shown to the user. To define
    #    groups of option boxes, return a list of BoxGroup namedtuples with the label, the key 
    #    (or index) of the first and last options boxes (inclusive).
    #
    #    Example:
    #        from quick.webtool.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey', last='secondKey')]
    #    '''
    #    return None


#     @staticmethod
#     def getOptionsBoxFirstKey(): # Alternatively: getOptionsBox1()
#         '''
#         Defines the type and contents of the input box. User selections are
#         returned to the tools in the prevChoices and choices attributes to other
#         methods. These are lists of results, one for each input box (in the
#         order specified by getInputBoxOrder()).
# 
#         The input box is defined according to the following syntax:
# 
#         Selection box:          ['choice1','choice2']
#         - Returns: string
# 
#         Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
#         - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
#         - The contents is the default value shown inside the text area
#         - Returns: string
# 
#         Raw HTML code:          '__rawstr__', 'HTML code'
#         - This is mainly intended for read only usage. Even though more advanced
#           hacks are possible, it is discouraged.
# 
#         Password field:         '__password__'
#         - Returns: string
# 
#         Genome selection box:   '__genome__'
#         - Returns: string
# 
#         Track selection box:    '__track__'
#         - Requires genome selection box.
#         - Returns: colon-separated string denoting track name
# 
#         History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
#         - Only history items of specified types are shown.
#         - Returns: colon-separated string denoting galaxy track name, as
#                    specified in ExternalTrackManager.py.
# 
#         History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
#         - Only history items of specified types are shown.
#         - Returns: OrderedDict with galaxy id as key and galaxy track name
#                    as value if checked, else None.
# 
#         Hidden field:           ('__hidden__', 'Hidden value')
#         - Returns: string
# 
#         Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
#         - Returns: None
# 
#         Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
#         - Returns: OrderedDict from key to selection status (bool).
#         '''
#         return ['testChoice1', 'testChoice2', '...']



    #@staticmethod
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
    #
    #@classmethod
    #def getExtraHistElements(cls, choices):
    #    return None

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        gSuite = choices.gSuite
        plotType = choices.plotType
        columnX = choices.columnX
        columnY = choices.columnY
        plotSeries = choices.plotSeries
        
        gSuite = getGSuiteFromGalaxyTN(gSuite)
        attributeList = gSuite.attributes
        attributeList = [TITLE_COL] + attributeList
        
        seriesName=[]
             
        sortedCat=None
        categories=None
        if columnX == TITLE_COL:
            categories = gSuite.allTrackTitles()
        elif columnX == 'Iterate':
            categories = None
        else:
            if columnX in columnY.keys():
                categoriesBefore = [float(v) for v in gSuite.getAttributeValueList(columnX)]
                sortedCat = sorted(range(len(categoriesBefore)), key=lambda k: categoriesBefore[k])
                categories=[]
                for n in sortedCat:
                    categories.append(categoriesBefore[n])
            else:
                categories = gSuite.getAttributeValueList(columnX)
                
        
        data=[]
        for key, it in columnY.iteritems():
            if it == 'True':
                dataPart=[]
                seriesName.append(key)
                dataPart = []
                for x in gSuite.getAttributeValueList(key):
                    try:
                        dataPart.append(float(x))
                    except:
                        # need to support None in heatmap
                        if plotType == 'Heatmap':
                            dataPart.append(0)
                        else:
                            dataPart.append(x)
                if sortedCat!=None:
                    dataPartTemp=[]
                    for n in sortedCat:
                        dataPartTemp.append(dataPart[n])
                    dataPart = dataPartTemp
                data.append(dataPart)
                
        
        label=''
        if len(seriesName)!=0:
            label = '<b>{series.name}</b>: {point.x} {point.y}'
        else:
            label = '{point.x} {point.y}'
        
        vg = visualizationGraphs()
        
#         'Column', 'Scatter', 'Heatmap'
        
        res=''
        if plotSeries == 'Single':
            if plotType == 'Scatter':
                res += vg.drawScatterChart(
                     data,
                     categories = categories,
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = str(columnX),
                     height = 500,
                     seriesName = seriesName,
                     label = label,
#                      titleText = 'Plot',
                     )
            if plotType == 'Column':
                res += vg.drawColumnChart(
                     data,
                     categories = categories,
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = str(columnX),
                     height = 500,
                     seriesName = seriesName,
                     label = label,
#                      titleText = 'Plot',
                     )
            if plotType == 'Heatmap':
                res += vg.drawHeatmapSmallChart(
                     data,
                     categories = categories,
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = str(columnX),
                     height = 500,
                     seriesName = seriesName,
                     label = label,
#                      titleText = 'Plot',
                     )
        elif plotSeries == 'Multi':
            if plotType == 'Scatter':
                for nrD in range(0, len(data)):
                    res += vg.drawScatterChart(
                         data[nrD],
                         categories = categories,
                         xAxisRotation = 90,
                         marginTop = 30,
                         xAxisTitle = str(columnX),
                         height = 500,
                         seriesName = [seriesName[nrD]],
                         label = label,
    #                      titleText = 'Plot',
                         )
            if plotType == 'Column':
                res += vg.drawColumnCharts(
                     data,
                     categories = [categories for x in range(0, len(data))],
                     xAxisRotation = 90,
                     marginTop = 30,
                     xAxisTitle = str(columnX),
                     height = 500,
                     seriesName = [[seriesName[elD]] for elD in range(0, len(data))],
                     label = label,
#                      titleText = 'Plot',
                     )                     
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin(divId='results-page')
        htmlCore.divBegin(divClass='results-section')
        
        htmlCore.line(res)
        
        htmlCore.divEnd()
        htmlCore.divEnd()
        htmlCore.end()
        
        print htmlCore
        
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        return None

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
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
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
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    '''
    #    Specifies a help text in HTML that is displayed below the tool.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by AutoConfig.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    #@staticmethod
    #def getFullExampleURL():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether the debug mode is turned on.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'
