import re
from collections import namedtuple

from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

VocabularyElement = namedtuple('VocabularyElement', ('category', 'subCategory','sourceTool','sourceTable','toolAttr','toolVal'))
class TrackGlobalSearchTool(GeneralGuiTool):

    def __new__(cls, *args, **kwArgs):
        cls.exception = None
        cls.DB = DatabaseTrackAccessModule()
        cls.VOCABULARY = []
        cls.Rpositories = []
        cls.SOURCE = {'EncodeTrackSearchTool':'ENCODE','EpigenomeTrackSearchTool':'Roadmap Epigenomics','CGAtlasTrackSearchTool':'TCGA','FANTOM5TrackSearchTool':'FANTOM'}
        with open('/hyperbrowser/src/hb_core_developer/trunk/quick/webtools/imports/TrackTextSearch/Vocabulary.tsv','r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('#'):
                continue
            lineList = line.split('\t')
            category = lineList[0]
            subCategory = lineList[1]
            sourceTool = lineList[2]
            sourceTable = None
            for k in cls.SOURCE.keys():
                if cls.SOURCE[k].upper() == lineList[2].upper():
                    sourceTool = k
                    sourceTable =  'file_' + sourceTool.split('Track')[0].lower()
                    break

            toolInput = lineList[-1].split(':')[1]
            toolAttr = toolInput.split('=')[0].strip()
            toolVal_text = toolInput.split('=')[1].strip()
            #if toolVal_text.find('*'):
            #    toolVal_text = '(' + toolVal_text.replace('*','.*') + ')'
            #    col_name = cls.DB.getAttributeNameFromReadableName(sourceTable,toolAttr)
            #    List = cls.DB._db.getREMatchingValues(sourceTable,col_name,toolVal_text)
            #    if len(List) > 0:
            #        toolVal = List[0]
            #    else:
            #        toolVal = None
            #else:
            #    toolVal = toolVal_text
            toolVal = toolVal_text

            cls.VOCABULARY.append\
            (VocabularyElement(category,subCategory,sourceTool,sourceTable,toolAttr,toolVal))

            cls.hits = []
            cls.sourceCounts = {}

        return GeneralGuiTool.__new__(cls, *args, **kwArgs)

    @staticmethod
    def getToolName():
        return 'Browse catalog of chromatin tracks'

    @staticmethod
    def getInputBoxNames():
        return ['Search Type:','Search:','Sub-Category:','Select Source:','URL:', '']

    @classmethod
    def getOptionsBox1(cls):
        #return OrderedDict([(str(t),False) for t in cls.VOCABULARY])
        return ['Categorized','Text']

    @classmethod
    def getOptionsBox2(cls, prevChoices):
        #string = ''
        #for item in cls.VOCABULARY:
        #    string += item.category+','+item.subCategory+','+item.sourceTool+','+str(item.Dict)+'\n'
        #return string,5
        if prevChoices[0] == 'Text':
            return ''
        category_list = []
        for cat in cls.VOCABULARY:
            if not cat.category in category_list:
                category_list.append(cat.category)
        return category_list

    @classmethod
    def getInfoForOptionsBox2(cls, prevChoices):
        if prevChoices[0] == 'Text':
            return 'Enter search keys and values separated by "&", e.g.\n'+\
        'Histone modifications=H2AK5ac & Open Chromatin=Dnase HSS'
        else:
            return

    @classmethod
    def getOptionsBox3(cls, prevChoices):
        if prevChoices[0] == 'Text' or prevChoices[1] == None:
            return
        return [ve.subCategory for ve in cls.VOCABULARY if ve.category == prevChoices[1]]

    @classmethod
    def getOptionsBox4(cls, prevChoices):
        cls.hits = []
        if prevChoices[0] != 'Text' and prevChoices[1] != None and prevChoices[2] != None:
            cat = prevChoices[1]
            sub_cat = prevChoices[2]
            for el in cls.VOCABULARY:
                if cat.upper() == el.category.upper() and  sub_cat.upper() == el.subCategory.upper():
                    cls.hits.append(el)

        elif prevChoices[0] == 'Text' and prevChoices[1].strip() != '':
            search = prevChoices[1].split('&')
            cls.exception = 'Search text must be in the correct form, e.g. "Histone modifications=H2AK5ac & Open Chromatin=Dnase HSS"'
            for item in search:
                if  re.match('(.*=.*)',item) == None:
                    continue
                cls.exception = None
                cat = item.split('=')[0].strip()
                sub_cat = item.split('=')[1].strip()
                for el in cls.VOCABULARY:
                    if cat.upper() == el.category.upper() and  sub_cat.upper() == el.subCategory.upper():
                        cls.hits.append(el)

        else:
            return
        if len(cls.hits) == 0:
            return

        cls.sourceCounts = dict.fromkeys(cls.SOURCE.keys(),0)
        for hit in cls.hits:
            src = hit.sourceTool
            if hit.sourceTool in cls.SOURCE.keys():
                cls.sourceCounts[hit.sourceTool] += 1
    
        cls.Rpositories = [cls.SOURCE[src]+ ' ['+str(cls.sourceCounts[src])+']' for src in cls.sourceCounts.keys() if cls.sourceCounts[src] > 0]    
        return [cls.SOURCE[src]+ ' ['+str(cls.sourceCounts[src])+']' for src in cls.sourceCounts.keys() if cls.sourceCounts[src] > 0]
        
        #return [str(hit) for hit in cls.hits]
    

    @classmethod
    def getOptionsBox5(cls, prevChoices):

        if prevChoices[3] == None:
            return
        try:

            sourceText = prevChoices[3].split('[')[0].strip()
            source = ''
            for k,v in cls.SOURCE.items():
                if sourceText == v:
                    source = k
                    break

            hits = [x for x in cls.hits if x.sourceTool == source]

            i = 0
            attr_val_dict = {}
            for hit in hits:
                attr_val_dict['attributeList'+str(i)] = hit.toolAttr
                attr_val_dict['multiSelect'+str(i)] = 'Text Search'
                #attr_val_dict['valueList'+str(i)] = hit.toolVal
                attr_val_dict['multiValueReceiver'+str(i)] = hit.toolVal
                i +=1

            return '__hidden__',cls.createGenericGuiToolURL('hb_track_source_test_tool',\
                                               source,attr_val_dict)
            #return cls.createGenericGuiToolURL('hb_track_source_test_tool',\
            #                                   'EpigenomeTrackSearchTool', \
            #                                   {'attributeList0':'Study','multiSelect0':'Yes','valueList0':'UCSC','attributeList1':'Experiment'}\
            #)
            ##OrderedDict([('BI',True),('UCSD',True),('UCSF-UBC',False),('UW',False)])
        except Exception as e:
            #raise
            return 'Error:'+str(e)

    def getOptionsBox6(cls, prevChoices):
        return ['']

    @classmethod
    def getInfoForOptionsBox6(cls, prevChoices):
        return cls.getPlot()
        #import quick.webtools.restricted.visualization.visualizationPlots as vp
        #plot = vp.addJSlibs()
        #plot = plot + vp.useThemePlot()
        #plot = plot + vp.addJSlibsExport()
        #
        #try:
        #    #Required
        #    #dataX =  [[10, 20, 30], [2, 10, 20], [2, 100, 20]]
        #    dataX =  [[20], [10]]
        #    '''More information about the template are in quick.webtools.restricted.visualization.visualizationPlots'''
        #    #Additional
        #    #categories = ['cat1', 'cat2', 'cat3']
        #    categories = ['Data Repositories']
        #    yAxisTitle = 'yAxisTitle'
        #    seriesName = []
        #    seriesType=[]
        #    for item in cls.Rpositories:
        #        seriesName.append(str(item))
        #        seriesType.append('column')
        #    #seriesName=[str(cls.Rpositories[0]), str(cls.Rpositories[1]), str(cls.Rpositories[2])]
        #    shared=False
        #    titleText = 'titleText'
        #    #legend =True
        #    legend =False
        #    xAxisRotation=270
        #
        #    stacked=True
        #
        #    plot = plot + vp.drawChart(dataX, type='column', categories=categories, yAxisTitle =yAxisTitle,minWidth = 600, legend =legend, xAxisRotation=xAxisRotation, seriesType=seriesType, seriesName=seriesName, shared=shared, titleText=titleText, stacked = stacked)
        #    return plot
        #except Exception as e:   
        #    return str(cls.Rpositories)
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        #f = open(galaxyFn,'w')
        #f.write('---')
        #f.close()
        return

    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices[0] == 'Text' and choices[1].strip() == '':
            return 'You have to enter a search text'
        elif cls.exception:
            return cls.exception
        return

    @staticmethod
    def isRedirectTool():
        return True

    @classmethod
    def getRedirectURL(cls, choices):
        '''Return OptionsBox5'''
        return choices[4]

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
        desc = 'This tool provides a categorized and text search functionality for '\
                'histone modifications and open chromatin in different external '\
                'repositories using the "Compile GSuite from external database" tool.'
        core.paragraph(desc)

        return str(core)# + cls.getPlot()   
    
    @classmethod
    def getPlot(cls):
        import quick.webtools.restricted.visualization.visualizationPlots as vp
        plot = vp.addJSlibs()
        plot = plot + vp.useThemePlot()
        plot = plot + vp.addJSlibsExport()
        
        try:
            #Required
            #dataX =  [[10, 20, 30], [2, 10, 20], [2, 100, 20]]
            dataX =  [[20], [10]]
            '''More information about the template are in quick.webtools.restricted.visualization.visualizationPlots'''
            #Additional
            #categories = ['cat1', 'cat2', 'cat3']
            categories = ['Data Repositories']
            yAxisTitle = 'yAxisTitle'
            seriesName = []
            seriesType=[]
            for item in cls.Rpositories:
                seriesName.append(str(item))
                seriesType.append('column')
            #seriesName=[str(cls.Rpositories[0]), str(cls.Rpositories[1]), str(cls.Rpositories[2])]
            shared=False
            titleText = 'titleText'
            #legend =True
            legend =False
            xAxisRotation=-90
        
            stacked=True
        
            plot = plot + vp.drawChart(dataX, type='column', categories=categories, yAxisTitle =yAxisTitle,minWidth = 600, legend =legend, xAxisRotation=xAxisRotation, seriesType=seriesType, seriesName=seriesName, shared=shared, titleText=titleText, stacked = stacked)
            return plot
        except Exception as e:   
            return str(e)+'\n'+str(cls.Rpositories)
    @staticmethod
    def getFullExampleURL():
        return 'https://hyperbrowser.uio.no/nar/u/hb-superuser/p/browse-catalog-of-chromatin-tracks'
