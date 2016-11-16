from collections import OrderedDict, namedtuple

import gold.gsuite.GSuiteComposer as GSuiteComposer
from quick.extra.ProgressViewer import ProgressViewer
from quick.trackaccess.TrackGlobalSearchModule import TrackGlobalSearchModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

VocabularyElement = namedtuple('VocabularyElement', ('category', 'subCategory','sourceTool','sourceTable','toolAttr','toolVal'))

class TrackGlobalSearchTool(GeneralGuiTool):
    ERROR_HISTORY_TITLE_DOWNLOAD = 'GSuite - files that failed to download (select in "Fetch remote GSuite datasets" to retry)'
    ERROR_HISTORY_TITLE_PREPROCESS = 'GSuite - files that failed preprocessing (select in "Preprocess tracks in GSuite" to retry)'
    HISTORY_PROGRESS_TITLE = 'Progress'

    def __new__(cls, *args, **kwArgs):
        #cls.DOWNLOAD_PROTOCOL = None
        #cls.exception = None
        #cls.DB = DatabaseTrackAccessModule()
        #cls.VOCABULARY = []
        #cls.Rpositories = []
        #cls.SOURCE = {'EncodeTrackSearchTool': 'ENCODE',
        #              'EpigenomeTrackSearchTool': 'Roadmap Epigenomics',
        #              'CGAtlasTrackSearchTool': 'TCGA',
        #              'FANTOM5TrackSearchTool': 'FANTOM'}
        #
        #with open(os.path.join(HB_SOURCE_DATA_BASE_DIR, 'TrackTextSearch', 'Vocabulary.tsv'),'r') as f:
        #    lines = f.readlines()
        #
        #for line in lines:
        #    if line.startswith('#'):
        #        continue
        #    lineList = line.split('\t')
        #    category = lineList[0]
        #    subCategory = lineList[1]
        #    sourceTool = lineList[2]
        #    sourceTable = None
        #
        #    for k in cls.SOURCE.keys():
        #        if cls.SOURCE[k].upper() == lineList[2].upper():
        #            sourceTool = k
        #            sourceTable =  'file_' + sourceTool.split('Track')[0].lower()
        #            break
        #
        #    toolInput = lineList[-1].split(':')[1]
        #    toolAttr = toolInput.split('=')[0].strip()
        #    toolVal_text = toolInput.split('=')[1].strip()
        #    #if toolVal_text.find('*'):
        #    #    toolVal_text = '(' + toolVal_text.replace('*','.*') + ')'
        #    #    col_name = cls.DB.getAttributeNameFromReadableName(sourceTable,toolAttr)
        #    #    List = cls.DB._db.getREMatchingValues(sourceTable,col_name,toolVal_text)
        #    #    if len(List) > 0:
        #    #        toolVal = List[0]
        #    #    else:
        #    #        toolVal = None
        #    #else:
        #    #    toolVal = toolVal_text
        #    toolVal = toolVal_text
        #
        #    cls.VOCABULARY.append \
        #        (VocabularyElement(category,subCategory,sourceTool,sourceTable,toolAttr,toolVal))
        #
        #    cls.hits = []
        #    cls.sourceCounts = {}

        return GeneralGuiTool.__new__(cls, *args, **kwArgs)

    @staticmethod
    def getToolName():
        return 'Browse Catalog of Chromatin Tracks'

    @staticmethod
    def getInputBoxNames():
        #return ['Search Type:','Search:','Sub-Category:','Select Source:','URL:', '']
        return [#('Search Type:','searchType'),\
                ('<b>What to do?</b>','searchType'),\
                ('Category:','search'),\
                ('Sub-Category:','subCategory'),\
                ('Select Source:','source'),\
                ('Select File Type:','filetype'),\
                ('Download and preprocess? (temporary)', 'downloadAndPreprocess'),\
                ('Select genome (temporary):', 'genome')]

    #@classmethod
    #def getOptionsBoxSearchType(cls):
    #    #return OrderedDict([(str(t),False) for t in cls.VOCABULARY])
    #    return ['Categorized','Text']

    @classmethod
    def getOptionsBoxSearchType(cls):
        return ['Select 10 random tracks','Select all tracks','Categorized Search for Tracks']
    @classmethod
    def getOptionsBoxSearch(cls,prevChoices):
        #string = ''
        #for item in cls.VOCABULARY:
        #    string += item.category+','+item.subCategory+','+item.sourceTool+','+str(item.Dict)+'\n'
        #return string,5
        ##if prevChoices.searchType == 'Text':
        ##    return ''
        ###category_list = []
        ###for cat in cls.VOCABULARY:
        ###    if not cat.category in category_list:
        ###        category_list.append(cat.category)
        ###return category_list
        if prevChoices.searchType != 'Categorized Search for Tracks':
            return
        gsm = TrackGlobalSearchModule()
        return gsm.getCategories()

    #@classmethod
    #def getInfoForOptionsBoxSearch(cls, prevChoices):
    #    if prevChoices.searchType == 'Text':
    #        return 'Enter search keys and values separated by "&", e.g.\n'+\
    #    'Histone modifications=H2AK5ac & Open Chromatin=Dnase HSS'
    #    else:
    #        return

    @classmethod
    def getOptionsBoxSubCategory(cls, prevChoices):
        #if prevChoices.searchType == 'Text' or prevChoices.search == None:
        #    return
        ###return [ve.subCategory for ve in cls.VOCABULARY if ve.category == prevChoices.search]
        if prevChoices.searchType != 'Categorized Search for Tracks':
            return
        gsm = TrackGlobalSearchModule()
        return gsm.getSubCategories(prevChoices.search)

    @classmethod
    def getOptionsBoxSource(cls, prevChoices):
        ###cls.hits = []
        ###if prevChoices.search != None and prevChoices.subCategory != None:
        ###    cat = prevChoices.search
        ###    sub_cat = prevChoices.subCategory
        ###    for el in cls.VOCABULARY:
        ###        if cat.upper() == el.category.upper() and  sub_cat.upper() == el.subCategory.upper():
        ###            cls.hits.append(el)
        ###
        ####elif prevChoices.searchType == 'Text' and prevChoices.search.strip() != '':
        ####    search = prevChoices.search.split('&')
        ####    cls.exception = 'Search text must be in the correct form, e.g. "Histone modifications=H2AK5ac & Open Chromatin=Dnase HSS"'
        ####    for item in search:
        ####        if  re.match('(.*=.*)',item) == None:
        ####            continue
        ####        cls.exception = None
        ####        cat = item.split('=')[0].strip()
        ####        sub_cat = item.split('=')[1].strip()
        ####        for el in cls.VOCABULARY:
        ####            if cat.upper() == el.category.upper() and  sub_cat.upper() == el.subCategory.upper():
        ####                cls.hits.append(el)
        ###
        ###else:
        ###    return
        ###if len(cls.hits) == 0:
        ###    return
        ###
        ###cls.sourceCounts = dict.fromkeys(cls.SOURCE.keys(),0)
        ###for hit in cls.hits:
        ###    src = hit.sourceTool
        ###    #if hit.sourceTool in cls.SOURCE.keys():
        ###    cls.sourceCounts[hit.sourceTool] = len(cls.getRows(hit))
        ###
        ###cls.Rpositories = [cls.SOURCE[src]+ ' ['+str(cls.sourceCounts[src])+']' for src in cls.sourceCounts.keys() if cls.sourceCounts[src] > 0]
        ###
        ###sourceList = [cls.SOURCE[src]+ ' ['+str(cls.sourceCounts[src])+']' for src in cls.sourceCounts.keys() if cls.sourceCounts[src] > 0]
        ###sourceList.insert(0,'All')
        ###return sourceList
        ###
        ####return [str(hit) for hit in cls.hits]
        if prevChoices.searchType != 'Categorized Search for Tracks':
            return
        gsm = TrackGlobalSearchModule()
        hits = gsm.getItems(prevChoices.search,prevChoices.subCategory)
        sourceTupleList = gsm.getDataSources(hits)
        sourceList = []
        for src,count in sourceTupleList:
            sourceList.append(src+' ['+str(count)+']')

        sourceList.insert(0,'All')
        return sourceList

    @classmethod
    def getOptionsBoxFiletype(cls, prevChoices):
        if prevChoices.searchType != 'Categorized Search for Tracks':
            return
        gsm = TrackGlobalSearchModule()
        hits = gsm.getItems(prevChoices.search,prevChoices.subCategory)
        source = prevChoices.source.split('[')[0]
        result = gsm.getFileTypes(hits,source)
        return OrderedDict([(el,True) for el in result])

    @classmethod
    def getOptionsBoxDownloadAndPreprocess(cls, prevChoices):
        if prevChoices.searchType != 'Categorized Search for Tracks':
            return
        return ['No','Yes']

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        if prevChoices.downloadAndPreprocess == 'Yes':
            return '__genome__'

    @classmethod
    def getExtraHistElements(cls, choices):
        fileList = []

        if choices.downloadAndPreprocess == 'Yes':
            from quick.webtools.GeneralGuiTool import HistElement
            fileList += [HistElement(cls.ERROR_HISTORY_TITLE_DOWNLOAD, 'gsuite')]
            fileList += [HistElement(cls.ERROR_HISTORY_TITLE_PREPROCESS, 'gsuite')]
            fileList += [HistElement(cls.HISTORY_PROGRESS_TITLE, 'customhtml')]

            try:
                gSuite = cls._getGSuite(cls.hits)

                for track in gSuite.allTracks():
                    from gold.gsuite.GSuiteDownloader import getTitleAndSuffixWithCompressionSuffixesRemoved
                    title, suffix = getTitleAndSuffixWithCompressionSuffixesRemoved(track)
                    fileList.append( HistElement(title, suffix, hidden=True) )

            except:
                pass

        return fileList

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        #for hit in cls.hits:
        #    cols, colListString = cls.getColListString(hit.sourceTable)
        #    attribute_col_name = cls.DB.getAttributeNameFromReadableName(hit.sourceTable,hit.toolAttr)
        #    rows = cls.getRows(hit)
        #
            #for row in rows:
            #    outfile.write(hit.sourceTable+'\t'+attribute_col_name+'\t'+hit.toolVal+'\t'+row[0]+'\n')
        gsm = TrackGlobalSearchModule()
        if choices.searchType == 'Select all tracks':
            hits = gsm.getAllItems()
            remoteGSuite = gsm.getGSuite(hits,'All')
        elif choices.searchType == 'Select 10 random tracks':
            remoteGSuite = gsm.getGsuiteFromRandomRows(10)
        else:
            hits = gsm.getItems(choices.search,choices.subCategory)
            source = choices.source.split('[')[0]
            fileTypes = [x for x,selected in choices.filetype.iteritems() if selected]
            remoteGSuite = gsm.getGSuite(hits,source,fileTypes)
        ###remoteGSuite = cls._getGSuite(hits,choices.source.split('[')[0])
        ##outfile = open(galaxyFn,'w')
        ##outfile.write(str(hits))
        ##outfile.close()
        ##return

        if choices.downloadAndPreprocess == 'Yes':
            trackCount = remoteGSuite.numTracks()
            progressViewer = ProgressViewer([('Download tracks', trackCount),
                                             ('Preprocess tracks', trackCount)],
                                            cls.extraGalaxyFn[cls.HISTORY_PROGRESS_TITLE] )

            from gold.gsuite.GSuiteDownloader import GSuiteMultipleGalaxyFnDownloader
            from gold.gsuite.GSuitePreprocessor import GSuitePreprocessor

            gSuiteDownloader = GSuiteMultipleGalaxyFnDownloader()
            localGSuite, errorLocalGSuite = \
                gSuiteDownloader.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites\
                    (remoteGSuite, progressViewer, cls.extraGalaxyFn)
#           localGSuite, errorLocalGSuite = \
#                remoteGSuite.downloadAllRemoteTracksAndReturnOutputAndErrorGSuites(cls.extraGalaxyFn, progressViewer)
            localGSuite.setGenomeOfAllTracks(choices.genome)

            progressViewer.updateProgressObjectElementCount('Preprocess tracks', localGSuite.numTracks())
            gSuitePreprocessor = GSuitePreprocessor()
            preProcessedGSuite, errorPreProcessGSuite = \
                gSuitePreprocessor.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites\
                    (localGSuite, progressViewer)
            #preProcessedGSuite, errorPreProcessGSuite = localGSuite.preProcessAllLocalTracksAndReturnOutputAndErrorGSuites(progressViewer)

            GSuiteComposer.composeToFile(errorLocalGSuite, cls.extraGalaxyFn[cls.ERROR_HISTORY_TITLE_DOWNLOAD])
            GSuiteComposer.composeToFile(errorPreProcessGSuite, cls.extraGalaxyFn[cls.ERROR_HISTORY_TITLE_PREPROCESS])

            GSuiteComposer.composeToFile(preProcessedGSuite, galaxyFn)

        else:
            GSuiteComposer.composeToFile(remoteGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        #if choices[0] == 'Text' and choices[1].strip() == '':
        #    return 'You have to enter a search text'
        if cls.exception:
            return cls.exception

        if choices.searchType == 'Categorized Search for Tracks':
            if not choices.filetype in [None,'',[]] and len([x for x,selected in choices.filetype.iteritems() if selected]) == 0:
                return 'You have to select at least one file type'


            if choices.downloadAndPreprocess == 'Yes':
                errorStr = cls._checkGenome(choices.genome)
                if errorStr:
                    return errorStr

        return

    #@classmethod
    #def getRows(cls, hit):
    #
    #    cols, colListString = cls.getColListString(hit.sourceTable)
    #
    #    WHERE = ''
    #
    #    attribute_col_name = cls.DB.getAttributeNameFromReadableName(hit.sourceTable,hit.toolAttr)
    #    multi_val_rec = hit.toolVal
    #    if multi_val_rec.find('*') > -1:
    #        multi_val_rec = '(' + multi_val_rec.strip().replace('*','.*') + ')'
    #    else:
    #        multi_val_rec = '(.*' + multi_val_rec + '.*)'
    #    multi_val_list = cls.DB._db.getREMatchingValues(hit.sourceTable,cls.DB._db.correctColumNames([attribute_col_name])[0],multi_val_rec)
    #
    #    WHERE += attribute_col_name  + ' in ('
    #    for val in multi_val_list:
    #        WHERE += "'" + val + "', "
    #    if WHERE.endswith(', '):
    #        WHERE = WHERE.strip(', ')
    #    WHERE += ')'
    #
    #    query = "SELECT "+colListString+" FROM "+hit.sourceTable+" "
    #    query += "WHERE " + WHERE + "ORDER BY "+colListString+";"
    #
    #    rows = cls.DB._db.runQuery(query)
    #    if len(rows) == 0 or rows == None:
    #       return [('EMPTY Result for Query:\n' + query,)]
    #
    #    return rows
    #
    #@classmethod
    #def getColListString(cls,tablename):
    #    cols = cls.DB._db.correctColumNames\
    #    (cls.DB._db.getTableCols(tablename))
    #    colListString = ''
    #    try:
    #        cols.insert(0, cols.pop(cols.index('"url"')))
    #    except:
    #        cols.insert(0, cols.pop(cols.index('"_url"')))
    #
    #    for col in cols:
    #        colListString += col + ','
    #
    #    return cols,colListString.strip(',')
    #
    #@classmethod
    #def _getGSuite(cls, hits, source):
    #
    #    source = source.strip()
    #    sourceTool = 'None'
    #
    #    gSuite = GSuite()
    #
    #    for key, value in cls.SOURCE.items():
    #        if source == value:
    #            sourceTool = key
    #    ##return source+'--'+sourceTool
    #    for hit in hits:
    #        if source != 'All' and hit.sourceTool != sourceTool:
    #            continue
    #        cols, colListString = cls.getColListString(hit.sourceTable)
    #        attribute_col_name = cls.DB.getAttributeNameFromReadableName(hit.sourceTable,hit.toolAttr)
    #        rows = cls.getRows(hit)
    #
    #        colListString = colListString.replace(',','\t')
    #        colListString = colListString.replace('_','').lower()
    #        colListString = colListString.replace('"','')
    #        colListString = colListString.strip('\t')
    #        colList = colListString.split('\t')
    #
    #
    #
    #        #if len(cls.SELECTED_FILES_INDEXES)>0:
    #        #   arr = cls.SELECTED_FILES_INDEXES
    #        #else:
    #        #   arr = range(len(rows))
    #
    #        for count, row in enumerate( \
    #                cls._getSelectedRows(rows)):
    #            #row = rows[i]
    #            if row == None or len(row)<len(cols):
    #               continue
    #
    #            url = row[0].strip()
    #            if cls.DOWNLOAD_PROTOCOL != None:
    #                protocol = url.split(':')[0]
    #                url = url.replace(protocol+':',cls.DOWNLOAD_PROTOCOL+':')
    #
    #            from gold.gsuite.GSuiteTrack import urlparse
    #            parsedUrl = urlparse.urlparse(url)
    #
    #            sitename = parsedUrl.netloc
    #            filepath = parsedUrl.path
    #            query = parsedUrl.query
    #            #sitename = url.split(':')[1].strip('/').split('/')[0]
    #            ###filename = url.split('/')[-1]
    #            #filepath = url.split(sitename)[1]
    #            suffix = cls._getGSuiteTrackSuffix(url)
    #            uri = None
    #            if url.startswith('ftp:'):
    #                uri = FtpGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
    #            elif url.startswith('http:'):
    #                uri = HttpGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
    #            elif url.startswith('https:'):
    #                uri = HttpsGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
    #            elif url.startswith('rsync:'):
    #                uri = RsyncGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
    #
    #            attr_val_list = []
    #            for j in range(1,len(row)):
    #                if str(row[j]) == 'None':
    #                    continue
    #                attr_val_list.append((colList[j],str(row[j])))## some datatypes are not string, e.g. datetime
    #
    #            filename = url.split('/')[-1]
    #            gSuite.addTrack(GSuiteTrack(uri, title=str(count)+'_'+filename, doUnquote = True, attributes=OrderedDict(attr_val_list)))
    #
    #    return gSuite
    #
    #
    #@classmethod
    #def _getSelectedRows(cls, rows):
    #    for row in rows:
    #        yield row
    #
    #@classmethod
    #def _getGSuiteTrackSuffix(cls,url):
    #    return None
    #@staticmethod
    #def isRedirectTool():
    #    return True
    #
    #@classmethod
    #def getRedirectURL(cls, choices):
    #    '''Return OptionsBox5'''
    #    return choices[4]

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
        desc = 'This tool provides a categorized search functionality for '\
                'histone modifications and open chromatin in different external '\
                'repositories using the "Compile GSuite from external database" tool.'
        core.paragraph(desc)

        return str(core)# + cls.getPlot()


    @staticmethod
    def getOutputFormat(choices):
        return 'gsuite'

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
