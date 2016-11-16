from collections import OrderedDict, namedtuple

import gold.gsuite.GSuiteComposer as GSuiteComposer
import gold.gsuite.GSuiteUtils as GSuiteUtils
from gold.gsuite.GSuitePreprocessor import GSuitePreprocessor
from quick.extra.ProgressViewer import ProgressViewer
from quick.trackaccess.TrackGlobalSearchModule import TrackGlobalSearchModule
from quick.webtools.GeneralGuiTool import GeneralGuiTool

VocabularyElement = namedtuple('VocabularyElement', ('category', 'subCategory','sourceTool','sourceTable','toolAttr','toolVal'))

class TrackGlobalSearchTool(GeneralGuiTool):
    ERROR_HISTORY_TITLE_DOWNLOAD = 'GSuite - files that failed to download (select in "Fetch remote GSuite datasets" to retry)'
    ERROR_HISTORY_TITLE_PREPROCESS = 'GSuite - files that failed preprocessing (select in "Preprocess tracks in GSuite" to retry)'
    HISTORY_PROGRESS_TITLE = 'Progress'
    HISTORY_HIDDEN_TRACK_STORAGE = 'GSuite track storage'
    PRIMARY_GSUITE_TITLE = 'GSuite - downloaded files'
    REMOTE_GSUITE_TITLE = 'GSuite - remote files'

    def __new__(cls, *args, **kwArgs):
        cls.exception = None
        cls.useSqlite = True
        #cls.remoteGSuite = None

        return GeneralGuiTool.__new__(cls, *args, **kwArgs)

    @staticmethod
    def getToolName():
        return 'Create a GSuite from an integrated catalog of genomic datasets (track selection by data-type)'        

    @staticmethod
    def getInputBoxNames():
        #return ['Search Type:','Search:','Sub-Category:','Select Source:','URL:', '']
        return [#('Search Type:','searchType'),\
                ('', 'basicQuestionId'),\
                ('Select track category','search'),\
                ('Select track sub-category','subCategory'),\
                ('Select database:','source'),\
                ('<b>Transfer selection to advanced mode for further fine-tuning?</b>', 'transfer'),\
                ('Select File Type:','filetype'),\
                ('<h3>Select Data Type</h3>', 'dataType'),\
                ('<b>What to do?</b>','outputType'),\
                ('Download and preprocess? (temporary)', 'downloadAndPreprocess'),\
                ('Select genome (temporary):', 'genome'),\
                #('<b>Redirect URL</b>', 'url'),\
                #('<h3>Manually Select Among Matching Tracks</h3>','showResults'),\
                ('<h3>Matching Tracks</h3>','results')]

    #@classmethod
    #def getOptionsBoxSearchType(cls):
    #    #return OrderedDict([(str(t),False) for t in cls.VOCABULARY])
    #    return ['Categorized','Text']

    @classmethod
    def getOptionsBoxBasicQuestionId(cls):
        return '__hidden__', None

    @classmethod
    def getOptionsBoxSearch(cls, prevChoices):

        
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        return ['--Select--'] + gsm.getCategories()

    #@classmethod
    #def getInfoForOptionsBoxSearch(cls, prevChoices):
    #    if prevChoices.searchType == 'Text':
    #        return 'Enter search keys and values separated by "&", e.g.\n'+\
    #    'Histone modifications=H2AK5ac & Open Chromatin=Dnase HSS'
    #    else:
    #        return

    @classmethod
    def getOptionsBoxSubCategory(cls, prevChoices):

        if prevChoices.search == '--Select--':
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        return ['--Select--'] + gsm.getSubCategories(prevChoices.search)

    @classmethod
    def getOptionsBoxSource(cls, prevChoices):

        if prevChoices.subCategory in [None,'--Select--']:
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        items = gsm.getItems(prevChoices.search,prevChoices.subCategory)
        ##return [str(item) for item in items]
        
        sourceTupleList = gsm.getDataSources(items)
        sourceList = []
        for src,count in sourceTupleList:
            sourceList.append(src+'['+str(count)+']')
        
        sourceList.insert(0,'All Original Tracks')
        
        HBGsuite = GSuiteUtils.getSubtracksAsGSuite('hg19', ['Sample data', 'Chromatin catalog', prevChoices.search, prevChoices.subCategory])
        if HBGsuite.numTracks() > 0:
            sourceList.append('HyperBrowser['+str(HBGsuite.numTracks())+']')
        
        return sourceList

    @classmethod
    def getInfoForOptionsBoxSource(cls, prevChoices):
        return "The provided file types are: 'tsv','broadPeak','narrowPeak', and 'bed'."\
            " So any difference in the number of tracks between this source list and"\
            " the 'what to do?' list below, is due to the fact that some track"\
            " file types are not currently supported"
        
    @classmethod
    def getOptionsBoxTransfer(cls, prevChoices):
        if prevChoices.source in [None,'All Original Tracks'] or 'HyperBrowser' in prevChoices.source:
            return
        return ['No','Yes']
    
    @classmethod
    def getOptionsBoxDataType(cls, prevChoices):
        
        if not prevChoices.source or prevChoices.source.find('HyperBrowser') > -1 or prevChoices.transfer == 'Yes':
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        items = gsm.getItems(prevChoices.search, prevChoices.subCategory)
        source = prevChoices.source.split('[')[0]
        datatypes = gsm.getDataTypes(items,source)
        
        return OrderedDict([(dataType + ' ['+str(count)+']',True) for dataType,count in datatypes.iteritems()])
    
    @classmethod
    def getOptionsBoxFiletype(cls, prevChoices):
        #if prevChoices.searchType != 'Categorized Search for Tracks':
        #    return
        if not prevChoices.source or prevChoices.source.find('HyperBrowser') > -1 or prevChoices.transfer == 'Yes':
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        items = gsm.getItems(prevChoices.search, prevChoices.subCategory)
        source = prevChoices.source.split('[')[0]
        result = gsm.getFileTypes(items,source)
        
        filteredResult = []
        for el in result:
            if el.split('[')[0] in ['tsv','broadPeak','narrowPeak','bed']:
                filteredResult.append(el)    
        
        return OrderedDict([(el.split('[')[0],True) for el in filteredResult])
        #Skip showing the filetype count for now (problems, e.g. 'bam' and 'bai')
        #return OrderedDict([(el,True) for el in filteredResult])
        
        #return OrderedDict([(el,True) for el in result])

    @classmethod
    def getOptionsBoxOutputType(cls, prevChoices):
        #if prevChoices.source.find('HyperBrowser') > -1:
        #    return
        if not prevChoices.source or prevChoices.transfer == 'Yes' or prevChoices.source.find('HyperBrowser') == -1 and len([x for x,selected in prevChoices.filetype.iteritems() if selected]) == 0:
           return
        
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        source = prevChoices.source.split('[')[0]
        if prevChoices.source.find('HyperBrowser') > -1:
            fileTypes = []
        else:
            fileTypes = [x.split('[')[0] for x,selected in prevChoices.filetype.iteritems() if selected]    
        count = gsm.getGSuite(prevChoices.search,prevChoices.subCategory,source,fileTypes).numTracks()
                
        choicesList =  ['Select all tracks['+str(count)+']','Select tracks manually']
        ##if prevChoices.source.find('HyperBrowser') == -1:
        choicesList.extend(['Select 10 random tracks','Select 50 random tracks'])
        return choicesList

    @classmethod
    def getOptionsBoxDownloadAndPreprocess(cls, prevChoices):
        #if prevChoices.searchType != 'Categorized Search for Tracks':
        #    return
        #return '__hidden__','Yes'
        if not prevChoices.source or prevChoices.transfer == 'Yes':
            return
        return ['Yes','No']

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        #if prevChoices.source.find('HyperBrowser') > -1:
        #    return
        #if prevChoices.downloadAndPreprocess == 'Yes':
        
        #return '__genome__'
        return '__hidden__','hg19'

    #@classmethod
    #def getOptionsBoxShowResults(cls, prevChoices):
    #    if prevChoices.source.find('HyperBrowser') > -1:
    #        return
    #    if len([x for x,selected in prevChoices.filetype.iteritems() if selected]) == 0:
    #       return
    #    else:
    #       return ['No','Yes']

    @classmethod
    def getOptionsBoxResults(cls, prevChoices):
        #if prevChoices.source.find('HyperBrowser') > -1:
        #    return
        #if prevChoices.showResults in [None,'No']:
        #   return
        if not prevChoices.source or prevChoices.transfer == 'Yes' or prevChoices.outputType != 'Select tracks manually':
            return
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        if prevChoices.source.find('HyperBrowser') > -1:
            return gsm.getTrackFileList(prevChoices.search, prevChoices.subCategory, 'HyperBrowser')
        else:
            source = prevChoices.source.split('[')[0]
            allFileTypes = [x.split('[')[0] for x,selected in prevChoices.filetype.iteritems()]
            fileTypes = [x.split('[')[0] for x,selected in prevChoices.filetype.iteritems() if selected]
            
            ##Was made to speadup so that there will be no filetype comparisons,
            ##but deactivated for now since there is hardcoded filtering in
            ##prevChoices.fileType
            #if len(allFileTypes) == len(fileTypes):
            #    fileTypes = []
            
            return gsm.getTrackFileList(prevChoices.search, prevChoices.subCategory,source,fileTypes)
            
        #items = gsm.getItems(prevChoices.search, prevChoices.subCategory)
    
    #@classmethod
    #def getOptionsBoxUrl(cls, prevChoices):
    #    gsm = TrackGlobalSearchModule(cls.useSqlite)
    #    sourceTool,attr_val_dict = gsm.getSourceToolURLParams(prevChoices.search,\
    #                                                    prevChoices.subCategory,\
    #                                                    prevChoices.source.split('[')[0])
    #    #attr_val_dict = {}
    #    #i = 0
    #    #attr_val_dict['attributeList'+str(i)] = 'Table Name'
    #    #attr_val_dict['multiSelect'+str(i)] = 'Text Search'
    #    ##attr_val_dict['valueList'+str(i)] = hit.toolVal
    #    #attr_val_dict['multiValueReceiver'+str(i)] = 'wgEncodeBroadHistone.*H3k0?9ac.*'
    #    return cls.createGenericGuiToolURL('hb_track_source_test_tool',\
    #                                           sourceTool,attr_val_dict)

    @classmethod
    def getExtraHistElements(cls, choices):
        from gold.gsuite.GSuiteConstants import GSUITE_SUFFIX, GSUITE_STORAGE_SUFFIX
        fileList = []

        if choices.outputType and choices.downloadAndPreprocess == 'Yes' and choices.source.find('HyperBrowser') == -1 and choices.transfer != 'Yes':
            from quick.webtools.GeneralGuiTool import HistElement
            fileList.append(HistElement(cls.REMOTE_GSUITE_TITLE, GSUITE_SUFFIX))
            fileList += [HistElement(cls.ERROR_HISTORY_TITLE_DOWNLOAD, GSUITE_SUFFIX)]
            fileList.append(HistElement(cls.PRIMARY_GSUITE_TITLE, GSUITE_SUFFIX))
            fileList += [HistElement(cls.ERROR_HISTORY_TITLE_PREPROCESS, GSUITE_SUFFIX)]
            fileList += [HistElement(cls.HISTORY_PROGRESS_TITLE, 'customhtml')]


            #if choices.source.find('HyperBrowser') > -1:
            #    gSuite = GSuiteUtils.getSubtracksAsGSuite('hg19', ['Sample data', 'Chromatin catalog', choices.search, choices.subCategory])
            #    for track in gSuite.allTracks():
            #        #from gold.gsuite.GSuiteDownloader import getTitleAndSuffixWithCompressionSuffixesRemoved
            #        #title, suffix = getTitleAndSuffixWithCompressionSuffixesRemoved(track)
            #
            #        fileList.append( HistElement(track.title, 'HB', hidden=True) )
            #else:
            remoteGSuite = None
            #try:
            gsm = TrackGlobalSearchModule(cls.useSqlite)
            #items = gsm.getItems(choices.search,choices.subCategory)
            source = choices.source.split('[')[0]
            allFileTypes = [x.split('[')[0] for x,selected in choices.filetype.iteritems()]
            fileTypes = [x.split('[')[0] for x,selected in choices.filetype.iteritems() if selected]

            ##Was made to speadup so that there will be no filetype comparisons,
            ##but deactivated for now since there is hardcoded filtering in
            ##prevChoices.fileType
            #if len(allFileTypes) == len(fileTypes):
            #    fileTypes = []

            if choices.outputType.split('[')[0] == 'Select all tracks':
                remoteGSuite = gsm.getGSuite(choices.search,choices.subCategory,source,fileTypes)
            elif choices.outputType == 'Select tracks manually':
                remoteGSuite = gsm.getGSuite(choices.search,choices.subCategory,source,fileTypes,choices.results)
            elif choices.outputType == 'Select 10 random tracks':
                remoteGSuite = gsm.getRandomGSuite(choices.search,choices.subCategory,source,fileTypes,10)
            elif choices.outputType == 'Select 50 random tracks':
                remoteGSuite = gsm.getRandomGSuite(choices.search,choices.subCategory,source,fileTypes,50)
            else:
                return []

            #for track in remoteGSuite.allTracks():
            #    from gold.gsuite.GSuiteDownloader import getTitleAndSuffixWithCompressionSuffixesRemoved
            #    title, suffix = getTitleAndSuffixWithCompressionSuffixesRemoved(track)
            #
            #    fileList.append( HistElement(title, suffix, hidden=True) )

            fileList.append( HistElement(cls.HISTORY_HIDDEN_TRACK_STORAGE, GSUITE_STORAGE_SUFFIX, hidden=True))

            #
            #except:
            #    pass

        return fileList

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        if not choices.source:
            return
        source = choices.source.split('[')[0]
        fileTypes = []
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        
        if choices.source.find('HyperBrowser') == -1:
            #items = gsm.getItems(choices.search,choices.subCategory)
            allFileTypes = [x.split('[')[0] for x,selected in choices.filetype.iteritems()]
            fileTypes = [x.split('[')[0] for x,selected in choices.filetype.iteritems() if selected]

            ##Was made to speadup so that there will be no filetype comparisons,
            ##but deactivated for now since there is hardcoded filtering in
            ##prevChoices.fileType
            #if len(allFileTypes) == len(fileTypes):
            #    fileTypes = []

        if choices.outputType.split('[')[0] == 'Select all tracks':
            remoteGSuite = gsm.getGSuite(choices.search,choices.subCategory,source,fileTypes)
        elif choices.outputType == 'Select tracks manually':
            remoteGSuite = gsm.getGSuite(choices.search,choices.subCategory,source,fileTypes,choices.results)
        elif choices.outputType == 'Select 10 random tracks':#Not enabled for HB tracks
            remoteGSuite = gsm.getRandomGSuite(choices.search,choices.subCategory,source,fileTypes,10)
        elif choices.outputType == 'Select 50 random tracks':#Not enabled for HB tracks
            remoteGSuite = gsm.getRandomGSuite(choices.search,choices.subCategory,source,fileTypes,50)



        if choices.downloadAndPreprocess == 'Yes' and choices.source.find('HyperBrowser') == -1:
            trackCount = remoteGSuite.numTracks()
            progressViewer = ProgressViewer([('Download tracks', trackCount),
                                             ('Preprocess tracks', trackCount)],
                                            cls.extraGalaxyFn[cls.HISTORY_PROGRESS_TITLE] )

            #from gold.gsuite.GSuiteDownloader import GSuiteMultipleGalaxyFnDownloader
            #gSuiteDownloader = GSuiteMultipleGalaxyFnDownloader()
            #localGSuite, errorLocalGSuite = \
            #    gSuiteDownloader.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites\
            #        (remoteGSuite, progressViewer, cls.extraGalaxyFn)
            from gold.gsuite.GSuiteDownloader import GSuiteSingleGalaxyFnDownloader
            from gold.gsuite.GSuiteFunctions import writeGSuiteHiddenTrackStorageHtml
            gSuiteDownloader = GSuiteSingleGalaxyFnDownloader()
            hiddenStorageFn = cls.extraGalaxyFn[cls.HISTORY_HIDDEN_TRACK_STORAGE]
            localGSuite, errorLocalGSuite = \
                gSuiteDownloader.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites \
                    (remoteGSuite, progressViewer, hiddenStorageFn, [])
            writeGSuiteHiddenTrackStorageHtml(hiddenStorageFn)

            progressViewer.updateProgressObjectElementCount('Preprocess tracks', localGSuite.numTracks())
            gSuitePreprocessor = GSuitePreprocessor()
            preProcessedGSuite, errorPreProcessGSuite = \
                gSuitePreprocessor.visitAllGSuiteTracksAndReturnOutputAndErrorGSuites\
                    (localGSuite, progressViewer)
            #preProcessedGSuite, errorPreProcessGSuite = localGSuite.preProcessAllLocalTracksAndReturnOutputAndErrorGSuites(progressViewer)
            GSuiteComposer.composeToFile(remoteGSuite, cls.extraGalaxyFn[cls.REMOTE_GSUITE_TITLE])
            GSuiteComposer.composeToFile(localGSuite, cls.extraGalaxyFn[cls.PRIMARY_GSUITE_TITLE])
            GSuiteComposer.composeToFile(errorLocalGSuite, cls.extraGalaxyFn[cls.ERROR_HISTORY_TITLE_DOWNLOAD])
            GSuiteComposer.composeToFile(preProcessedGSuite, galaxyFn)
            GSuiteComposer.composeToFile(errorPreProcessGSuite, cls.extraGalaxyFn[cls.ERROR_HISTORY_TITLE_PREPROCESS])

        else:
            GSuiteComposer.composeToFile(remoteGSuite, galaxyFn)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        #if choices[0] == 'Text' and choices[1].strip() == '':
        #    return 'You have to enter a search text'
        if cls.exception:
            return cls.exception


        #if choices.outputType == 'Categorized Search for Tracks':
        if not choices.filetype in [None,'',[]] and len([x for x,selected in choices.filetype.iteritems() if selected]) == 0:
            return 'You have to select at least one file type'


            if choices.downloadAndPreprocess == 'Yes':
                errorStr = cls._checkGenome(choices.genome)
                if errorStr:
                    return errorStr

        return GeneralGuiTool._checkGenome(choices.genome)



    @classmethod
    def isRedirectTool(cls,choices):
        if choices.transfer == 'Yes':
            return True
    
    @classmethod
    def getRedirectURL(cls, choices):
        gsm = TrackGlobalSearchModule(cls.useSqlite)
        sourceTool,attr_val_dict = gsm.getSourceToolURLParams(choices.search,\
                                                        choices.subCategory,\
                                                        choices.source.split('[')[0])
        
        return cls.createGenericGuiToolURL('hb_track_source_test_tool',\
                                               sourceTool,attr_val_dict)
        #return choices.url
    
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
