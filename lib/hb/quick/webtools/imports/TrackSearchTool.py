import os,re,datetime

from quick.webtools.GeneralGuiTool import GeneralGuiTool
from collections import OrderedDict
from functools import partial

from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from gold.util.CustomExceptions import AbstractClassError
from gold.result.HtmlCore import HtmlCore

from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack, HttpGSuiteTrack, HttpsGSuiteTrack, FtpGSuiteTrack, RsyncGSuiteTrack, HbGSuiteTrack
import gold.gsuite.GSuiteComposer as GSuiteComposer
import gold.gsuite.GSuiteParser as GSuiteParser
# This is a template prototyping GUI that comes together with a corresponding
# web page.

class TrackSearchTool(GeneralGuiTool):
    # Other constants
    INDEX_TABLE = None
    SELECTED_ATTRIBUTES = []
    #RESULT_FILES_URLS = []
    #SELECTED_FILES_INDEXES = []
    TIME_STAMP = None
    OUTPUT_GENOME = 'hg19'

    exception = None

    def __new__(cls, *args, **kwArgs):
        cls.DOWNLOAD_PROTOCOL = cls._getDownloadProtocol()
        cls.TABLE_NAME = cls._getTableName()
        cls.DB = DatabaseTrackAccessModule(isSqlite = True)
        cls.ATTRIBUTES = cls._getClassAttributes(cls.DB)
        cls.ATTRIBUTES_ALL = cls._getAllClassAttributes(cls.DB)
        cls.ATTRIBUTES_DETAILS = cls._getClassAttributesDetails(cls.ATTRIBUTES_ALL, cls.DB)
        cls.ATTRIBUTE_VALUES_DETAILS = cls._getClassAttributeValuesDetails(cls.DB)
        cls.setupVariableBoxFunctions(cls.ATTRIBUTES)
        
        return GeneralGuiTool.__new__(cls, *args, **kwArgs)

    @classmethod
    def _getRepoInfo(cls):
        '''
        Should be overrided in each child tool.
        Returns a three items list:
        ['Title (will be in bold)','a URL to the repo','Text for the URL link']
        '''
        return None
    
    @classmethod
    def _getOutputGenome(cls):
        #TODO: Interface should be changed so that the genome of a specific track can be fetched
        return cls.OUTPUT_GENOME
    
    @classmethod
    def _getTableName(cls):
        raise AbstractClassError()

    @classmethod
    def _getDownloadProtocol(cls):
        return None
    
    @classmethod
    def _getGlobalSQLFilter(cls):
        '''Value of the 'WHERE' close for the whole tool. Useful in case of two tools querying data
           from the same table with different filters'''
        return None

    @classmethod
    def _getGSuiteTrackSuffix(cls,url):
        return None

    @classmethod
    def _unquoteTrackURL(cls):
        return True

    @classmethod
    def _getClassAttributes(cls, db):
        '''
        Returns only searchable columns from the database table. This must be specified
        in the tool child class.
        '''
        raise AbstractClassError()

    @classmethod
    def _getAllClassAttributes(cls, db):
        '''
        Returns all columns from the database table.
        '''
        attributes = []

        colList = db._db.getTableCols(cls.TABLE_NAME)
        for col in colList:
            attributes.append(col)
        return attributes

    @classmethod
    def _getClassAttributesDetails(cls, attributes, db):
        result = db.getAttributesDetails(cls.TABLE_NAME, attributes)
        Dict = {}
        for k in result.keys():
            Dict[k] = result[k][0]
        return Dict

    @classmethod
    def _getClassAttributeValuesDetails(cls,db):
        return db.getAttributeValuesDetails(cls.TABLE_NAME)



    @classmethod
    def _getAttributeNameFromReadableName(cls,rName):
        for k in cls.ATTRIBUTES_DETAILS.keys():
            if cls.ATTRIBUTES_DETAILS[k] == rName:
                return k
        return rName
    @classmethod
    def _getAttributeReadableNameFromName(cls,name):
        try:
            return cls.ATTRIBUTES_DETAILS[name.strip('"')].strip('_')
        except Exception as e:
            print name
            print cls.ATTRIBUTES_DETAILS
            raise e

    @classmethod
    def _getAttributeValueDetails(cls,attribute,val):
        try:
            return cls.ATTRIBUTE_VALUES_DETAILS[attribute,val]
        except Exception as e:
            '''In case that this attribute value has no associated record'''
            return val,val#'Error: '+str(e)

    @classmethod
    def _getAttributeValueNameFromReadableName(cls,rName):
        try:
            for name,val in cls.ATTRIBUTE_VALUES_DETAILS.keys():
                if rName == cls.ATTRIBUTE_VALUES_DETAILS[name,val][0]:
                    return name,val
            return rName,rName
        except:
            '''In case that this attribute value has no associated record'''
            return rName,rName
    
    @staticmethod
    def getToolName():
        raise AbstractClassError()

    @classmethod
    def getInputBoxNames(cls):
        attrBoxes = []
        for i in xrange(len(cls.ATTRIBUTES)):
            attrBoxes.append(('<hr>&#9658;Select metadata attribute to search by:',\
                 'attributeList%s' % i))
            attrBoxes.append(('Selection type:',\
                 'multiSelect%s' % i))
            attrBoxes.append(('Text to search for (wildcards supported: "?" for single character, "*" for any combination of multiple characters)',\
                 'multiValueReceiver%s' % i))
            attrBoxes.append((1*'&#160'+'Select value:',\
                 'valueList%s' % i))
            attrBoxes.append(('Range ' + cls.ATTRIBUTES[i],\
                 'valueRange%s' % i))



        return [#('Track source', 'source'), \
                ('','repoInfo'), \
                ('Search for tracks using metadata?', 'search'), \
                ('','staticInfo'),\
                ('HIDDEN_0','hidden'),\
                ('Session Id','sessionId'),
                #('Select an attribute:','attributes'),\
                #('Filter by dataType?', 'filterDataType'), \
                #('dataType', 'dataType'), \
                #('Filter by cell?', 'filterCell'), \
                #('cell', 'cell'), \
                #('Filter by antibody?', 'filterAntibody'), \
                #('antibody', 'antibody'), \
                #('Filter by type?', 'filterType'),\
                 ] +\
                 attrBoxes +\
                [#('HIDDEN_1','dbTemp'),\
                 #('<h3>Select File Types</h3>', 'filetype'),\
                 ('<h3>Select Data Type</h3>', 'dataType'),\
                 ('<h3>Limit selection of tracks?</h3>', 'presentResults'),\
                 ('<h3>Results</h3>','results'),\
                 ('<h3>Output Format</h3>','outFormat')]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    #@staticmethod
    #def getOptionsBoxSource(): # Alternatively: getOptionsBoxKey1()

    #    return ['-- Select track source --', 'ENCODE','EpiGenome']

    #@staticmethod
    #def getOptionsBoxSearch(prevChoices): # Alternatively: getOptionsBoxKey2()

    #    if prevChoices.source != '-- Select track source --':
    #        return ['-- Select search method --', 'Structured search']


    @classmethod
    def getOptionsBoxRepoInfo(cls):
        info = cls._getRepoInfo()
        if info is None:
            return
        return '__rawstr__', \
        '<div style="border:1px solid black; border-radius: 10px;'+\
        ' background-color: #FFF8C6; margin-left: 20px;'+\
        ' margin-right: 20px; padding-bottom: 8px; padding-left: 8px;'+\
        ' padding-right: 8px; padding-top: 8px;">'+\
        '<i class="icon-info-sign"></i><b>'+info[0]+'</b><br/>'+\
        '<a href="'+info[1]+'">'+info[2]+'</a>'+\
        '</div>'
    
    @classmethod
    def getOptionsBoxSearch(cls,prevChoices):
        colsList = [cls._getAttributeReadableNameFromName(name) for name in cls.ATTRIBUTES]
        colsList.sort()
        cols,colListString = cls.getColListString()
        count = cls.getALLRowsCount(colListString)
        return ['Yes','No, use all '+str(count)+' tracks in database']
    
    @classmethod
    def getOptionsBoxStaticInfo(cls,prevChoices):
        if not prevChoices.search == 'Yes':
            return
        return '__rawstr__', \
        '<div style="border:1px dashed black; border-radius: 10px;'+\
        ' background-color: #E5E4E2; margin-left: 20px;'+\
        ' margin-right: 20px; padding-bottom: 8px; padding-left: 8px;'+\
        ' padding-right: 8px; padding-top: 8px;">'+\
        'Please search for the tracks of interest using the attributes in'+\
        'the external database, as presented below. Note that the attribute'+\
        'names are defined by the external project and not unified in any way'+\
        'by the Genomic HyperBrowser project.'
    
    @classmethod
    def getOptionsBoxHidden(cls,prevChoices):
        return 

    @classmethod
    def getOptionsBoxSessionId(cls,prevChoices):
        if prevChoices.sessionId == None:
            cls.TIME_STAMP = str(datetime.datetime.now())
            #TrackFileImport.DB._db.createTableFromList('temp',['session_id','attr'])
        else:
            cls.TIME_STAMP = prevChoices.sessionId
        return '__hidden__',cls.TIME_STAMP


    #@staticmethod
    #def getOptionsBoxAttributes(prevChoices):
        #if not prevChoices.search == 'Structured search':
        #    return

    #    colsList = []
    #    for col in TrackSearchTool.ATTRIBUTES:
            #colsList.append((col,False))
    #        colsList.append(col)

        #return OrderedDict(colsList)
    #    colsList.insert(0,'--None--')
        #colsList.insert(1,'--All--')
    #    return colsList


    #@staticmethod
    #def getOptionsBoxDbTemp(prevChoices):
    #
    #    selected_attr = prevChoices.attributes
    #    if selected_attr in [None,'--None--'] :
    #       TrackSearchTool.DB._db.runQuery\
    #       ("delete from temp where session_id like '"+prevChoices.sessionId+"';")
    #       return
    #
    #    rows = TrackSearchTool.DB._db.runQuery\
    #    ("select attr from temp where session_id like '"+prevChoices.sessionId+"';")
    #    selected_attrs_db = [x[0] for x in rows]
    #    if selected_attr == '--All--':
    #       for x in TrackSearchTool.ATTRIBUTES:
    #          if not selected_attr in selected_attrs_db:
    #             TrackSearchTool.DB._db.insertRow\
    #             ('temp',{'session_id':prevChoices.sessionId,'attr':x})
    #    elif not selected_attr in selected_attrs_db:
    #       TrackSearchTool.DB._db.insertRow\
    #       ('temp',{'session_id':prevChoices.sessionId,'attr':selected_attr})
    #
    #
    #    return

    @classmethod
    def setupVariableBoxFunctions(cls, attributes):
        for i in xrange(len(attributes)):
            setattr(cls, 'getOptionsBoxAttributeList%s' % i,\
             partial(cls._getAttributeListBox, index=i))
            setattr(cls, 'getOptionsBoxMultiSelect%s' % i,\
             partial(cls._getMultiSelectBox, index=i))
            setattr(cls, 'getOptionsBoxMultiValueReceiver%s' % i,\
             partial(cls._getMultiValueReceiverBox, index=i))
            setattr(cls, 'getOptionsBoxValueList%s' % i,\
             partial(cls._getValueListBox, index=i))
            setattr(cls, 'getInfoForOptionsBoxValueList%s' % i,\
             partial(cls._getValueInfoBox, index=i))
            setattr(cls, 'getOptionsBoxValueRange%s' % i,\
             partial(cls._getValueRangeBox, index=i))

    @classmethod
    def _getValueRangeBox(cls, prevChoices, index):
        return
        #rows = cls.DB._db.runQuery\
        #("select attr from temp where session_id like '"+prevChoices.sessionId+"';")
        #selected_attrs = [x[0] for x in rows]
        #if not cls.ATTRIBUTES[index] in selected_attrs:
        #   return
        #if getattr(prevChoices, 'valueList%s' % index) == '--Range--':
        #   return ''

    @classmethod
    def _getAttributeListBox(cls, prevChoices, index):
        '''
        Getting the list of attributes, e.g. "cell" and "datatype" for ENCODE
        '''
        if index > 0 and getattr(prevChoices, 'valueList%s' % (index-1))\
         in [None,'--Select--','']:
            return
        
        if index > 0 and getattr(prevChoices, 'multiSelect%s' % (index-1)) in ['Multiple Selection','Text Search']:
            val = getattr(prevChoices, 'valueList%s' % (index-1))
            if len([x[0] for x in val.items() if x[1]]) == 0:
                return
                
        #if val == None:
        #   return
        colsList = [cls._getAttributeReadableNameFromName(name) for name in cls.ATTRIBUTES]
        colsList.sort()
        if index == 0:
            #cols,colListString = cls.getColListString()
            #count = cls.getALLRowsCount(colListString)
            colsList.insert(0,'--None--')
            if prevChoices.search != 'Yes':
                return #['--ALL['+str(count)+']--'] 
            else:
                return colsList
        for i in xrange(len(cls.ATTRIBUTES)):
            if i >= index:
               break
            val = getattr(prevChoices, 'attributeList%s' % i)
            if val in [None,'--None--']:
               continue
            elif val in colsList:
               colsList.remove(val)

            #   colsList.append(TrackSearchTool.ATTRIBUTES[i])
            #elif getattr(prevChoices, 'valueList%s' % i) == None:
            #   colsList.append(TrackSearchTool.ATTRIBUTES[i])
        colsList.sort()
        ##colsList.insert(0,'--None--')
        return colsList

    @classmethod
    def _getMultiSelectBox(cls, prevChoices, index):
        attribute = getattr(prevChoices, 'attributeList%s' % index)
        if attribute in [None,'--None--']:
            return
        else:
            return ['Single Selection','Multiple Selection','Text Search']
            #return OrderedDict([('Allow Multiple Selection ',False)])

    @classmethod
    def _getMultiValueReceiverBox(cls, prevChoices, index):
        '''
        Receiving a Regular-Expressions formula from a URL redirect tool
        ,so that the _getValueListBox() method read it and return the associated
        OrderedDict
        '''
        if not getattr(prevChoices, 'multiSelect%s' % index) == 'Text Search':
            return
        else:
            return ''

    @classmethod
    def _getValueListBox(cls, prevChoices, index):
        '''
        Getting the list of values for a selected attribute
        , e.g. "Melano" for the attribute "cell" for ENCODE
        '''
        #rows = TrackSearchTool.DB._db.runQuery\
        #("select attr from temp where session_id like '"+prevChoices.sessionId+"';")
        #selected_attrs = [x[0] for x in rows]
        attribute = getattr(prevChoices, 'attributeList%s' % index)
        if attribute in [None, '--None--']:
            return
        attribute_col_name = cls._getAttributeNameFromReadableName(attribute)

        multi_val_list = []
        multi_val_rec = getattr(prevChoices, 'multiValueReceiver%s' % index)
        if not multi_val_rec  in ['',None]:
            multi_val_list = cls.DB._db.getWildCardsMatchingValues(cls.TABLE_NAME,cls.DB._db.correctColumNames([attribute_col_name])[0],multi_val_rec)
            ##This commented-out section if for using regex instead of wild-cards
            ##if multi_val_rec.find('*') > -1:
            ##    multi_val_rec = '(' + multi_val_rec.strip().replace('*','.*') + ')'
            ##else:
            ##    multi_val_rec = '(.*' + multi_val_rec + '.*)'
            ##multi_val_list = cls.DB._db.getREMatchingValues(cls.TABLE_NAME,cls.DB._db.correctColumNames([attribute_col_name])[0],multi_val_rec)
            
            #multi_val_list.append(','.join([cls.TABLE_NAME,attribute_col_name,multi_val_rec]))
            #return [multi_val_rec]



        prevSelected = {}
        for i in xrange(len(cls.ATTRIBUTES)):
            '''
            Otherwise, will generate an exception. Because 'prevChoices'
            must be only the 'Previous' ones
            '''
            if i >= index:
               break
            attr = getattr(prevChoices, 'attributeList%s' % i)
            col = cls._getAttributeNameFromReadableName(attr)

            rep_val = getattr(prevChoices, 'valueList%s' % i)

            if type(rep_val) is list:
                if attr in [None,'--None--'] or rep_val in ['--Select--','--Range--',None,'']:
                    continue
                val = cls._getAttributeValueNameFromReadableName(rep_val)[1]
                prevSelected[col] = val

            elif type(rep_val) is OrderedDict:
                selected_vals = [x for x,selected in rep_val.iteritems() if selected]
                if attr in [None,'--None--'] or len(selected_vals) == 0:
                    continue
                vals = [cls._getAttributeValueNameFromReadableName(val)[1] for val in selected_vals]
                prevSelected[col] = vals##
            else:
                selected_vals = [x.strip() for x in rep_val.split('\n')]
                if attr in [None,'--None--'] or len(selected_vals) == 0:
                    continue
                vals = [cls._getAttributeValueNameFromReadableName(val)[1] for val in selected_vals]
                prevSelected[col] = vals##

        try:
            valsWithCount = cls.DB.getValueListWithCounts(cls.TABLE_NAME, attribute_col_name, prevSelected)
        except Exception as e:
            #raise e
            cls.exception = e
            return []#'Error: ' + str(e)

        rep_valuesList = []
        for t in valsWithCount:
            if t.val in [None,'']:
                continue
            rep_valuesList.append(cls._getAttributeValueDetails(attribute_col_name,t.val)[0])

        #######if len(rep_valuesList) == 0:
        #######    return
        #multi = [x for x,selected in getattr(prevChoices, 'multiSelect%s' % index).iteritems() if selected]
        if getattr(prevChoices, 'multiSelect%s' % index) == 'Text Search':
            if len(multi_val_list) > 0:
                multi_val_list = [cls._getAttributeValueDetails(attribute_col_name,x)[0] for x in multi_val_list]
                return_list = []
                for v in rep_valuesList:
                    if v in multi_val_list:
                        return_list.append((v,True))
                    else:
                        return_list.append((v,False))
                #return OrderedDict([(z,True) for z in multi_val_list]+[(cls.TABLE_NAME+','+attribute_col_name+','+multi_val_rec+','+str(len(multi_val_list)),True)]+return_list)
                #return OrderedDict([(x[0],True) for x in return_list if x[1] is True])
                return OrderedDict(return_list)
                ###string = ''
                ###for el in multi_val_list:
                ###    if el.strip() != '':
                ###        string += el+'\n'
                ###lineCount = 4
                ###if len(multi_val_list)< lineCount:
                ###    lineCount = len(multi_val_list)
                ###return string.strip('\n'),lineCount,True
                ##return multi_val_list
            else:
                ##return multi_val_list
                ##return OrderedDict([(x,False) for x in rep_valuesList])
                return
                #return OrderedDict([(cls.TABLE_NAME+','+attribute_col_name+','+multi_val_rec+','+str(len(multi_val_list)),False)]+[(x,False) for x in rep_valuesList])
            #return OrderedDict([(x,True) for x in rep_valuesList])
        elif getattr(prevChoices, 'multiSelect%s' % index) == 'Multiple Selection':
            return OrderedDict([(x,False) for x in rep_valuesList])
        else:

            return ['--Select--'] + rep_valuesList
            #[(a,b,cls.ATTRIBUTE_VALUES_DETAILS[(a,b)][0],cls.ATTRIBUTE_VALUES_DETAILS[(a,b)][1]) for a,b in cls.ATTRIBUTE_VALUES_DETAILS.keys()] +\




            #[x.val for x in valsWithCount if x.val is not None]

    #@classmethod
    #def getResetBoxes(cls):
    #    '''
    #    Returns a list of input boxes which if changed, they will reset the other input
    #    boxes (i.e. re-run their methods)
    #    '''
    #    List = []
    #    for i in xrange(len(cls.ATTRIBUTES)):
    #        List.append('multiValueReceiver%s' % i)
    #    return List

    @classmethod
    def _getValueInfoBox(cls, prevChoices, index):
        infoValues = ['Cancer Type']
        try:
            attr = getattr(prevChoices, 'attributeList%s' % index)
            if attr not in infoValues:
                return
            repr_val = getattr(prevChoices, 'valueList%s' % index)
            val = cls._getAttributeValueNameFromReadableName(repr_val)
            if val[0] == repr_val:
                return repr_val
            url = cls._getAttributeValueDetails(val[0],val[1])[1]
            return HtmlCore().link(attr+' "'+val[1].upper()+'" Details',url)
        except Exception as e:
            return #str(e)

    @classmethod
    def getOptionsBoxSessionId(cls, prevChoices):
        #return '1'
        if prevChoices.sessionId == None:
                 cls.TIME_STAMP = str(datetime.datetime.now())
        else:
                 cls.TIME_STAMP = prevChoices.sessionId

        return '__hidden__',cls.TIME_STAMP

    @classmethod
    def getOptionsBoxPresentResults(cls, prevChoices):
        if len(cls.ATTRIBUTES) > 1 and \
        getattr(prevChoices, 'attributeList0') in [None, '--None--']:
            return
        selected_attrs = 0
        for i in xrange(len(cls.ATTRIBUTES)):
            if not getattr(prevChoices, 'valueList%s' % i) in [None,'','--Select--']:
                #New requested by SG
                if getattr(prevChoices, 'multiSelect%s' % (i)) in ['Multiple Selection','Text Search']:
                    val = getattr(prevChoices, 'valueList%s' % (i))
                    if len([x[0] for x in val.items() if x[1]]) == 0:
                        continue
                selected_attrs+=1

        if selected_attrs == 0 or len([x for x,selected in prevChoices.dataType.iteritems() if selected]) == 0:
            return
        else:
            cols,colListString = cls.getColListString()
            count = len(cls._getValidRows(prevChoices, cls.getFilteredRows(prevChoices,colListString)))
            return ['Select all tracks['+str(count)+']','Select tracks manually']
            #'List search results','Download results as history elements']#,'Download and convert to GTrack']

    @classmethod
    def getOptionsBoxDataType(cls, prevChoices):
        selected_attrs = 0
        for i in xrange(len(cls.ATTRIBUTES)):
            if not getattr(prevChoices, 'valueList%s' % i) in [None,'','--Select--']:
                #New requested by SG
                if getattr(prevChoices, 'multiSelect%s' % (i)) in ['Multiple Selection','Text Search']:
                    val = getattr(prevChoices, 'valueList%s' % (i))
                    if len([x[0] for x in val.items() if x[1]]) == 0:
                        continue
                selected_attrs+=1
        
        if selected_attrs == 0:
            #and not getattr(prevChoices, 'attributeList0') in [None,'--None--']:
            return
        
        cols,colListString = cls.getColListString()
        rows = cls.getFilteredRows(prevChoices,colListString)
        
        #test#return OrderedDict([(str(row),True) for row in rows])
        
        if rows[0][0].find('EMPTY') > -1:
            cls.exception = rows[0]
            return []
        WHERE = cls.getSQLFilter(prevChoices,colListString)
        datatypes = cls.DB.getTableDataTypes(cls.TABLE_NAME,WHERE)
        
        return OrderedDict([(el[0] + ' ['+str(el[1])+']',True) for el in datatypes])
        
    # @classmethod
    # def getOptionsBoxFiletype(cls, prevChoices):
    #     selected_attrs = 0
    #     for i in xrange(len(cls.ATTRIBUTES)):
    #         if not getattr(prevChoices, 'valueList%s' % i) in [None,'','--Select--']:
    #             #New requested by SG
    #             if getattr(prevChoices, 'multiSelect%s' % (i)) in ['Multiple Selection','Text Search']:
    #                 val = getattr(prevChoices, 'valueList%s' % (i))
    #                 if len([x[0] for x in val.items() if x[1]]) == 0:
    #                     continue
    #             selected_attrs+=1
    # 
    #     #print 'ttt'+str(selected_attrs)
    #     if selected_attrs == 0:
    #         #and not getattr(prevChoices, 'attributeList0') in [None,'--None--']:
    #         return
    # 
    #     cols,colListString = cls.getColListString()
    #     rows = cls.getFilteredRows(prevChoices,colListString)
    #     
    #     #test#return OrderedDict([(str(row),True) for row in rows])
    #     
    #     if rows[0][0].find('EMPTY') > -1:
    #         cls.exception = rows[0]
    #         #print 'ttt2'+str(selected_attrs)
    #         return []
    #     
    #     fileExtList = cls.DB.getAllFileExtensions()
    #     fileTypes = []
    #     for ext in fileExtList:
    #         count = 0
    #         for row in rows:
    #             filename = row[0].strip().split('/')[-1]
    #             if '.*' in ext and re.match(ext.lower(), filename) or \
    #             filename.lower().endswith('.'+ext.lower()):
    #                 count += 1
    #         
    #         if count > 0:
    #             #Skip showing the filetype count for now (problems, e.g. 'bam' and 'bai')
    #             #fileTypes.extend([x+'['+str(count)+']' for x in cls.DB.getFileTypes(ext)])
    #             fileTypes.extend([x for x in cls.DB.getFileTypes(ext)])
    #     
    #     fileTypes = list(set(fileTypes))
    #     #print 'ttt'+str(selected_attrs)
    #     return OrderedDict([(el,True) for el in fileTypes])

    @classmethod
    def getOptionsBoxOutFormat(cls, prevChoices):
        if prevChoices.presentResults != None or (len(cls.ATTRIBUTES) > 1 and getattr(prevChoices, 'attributeList0') in [None,'--None--']):
           return ['gsuite','Html']
           #return '__hidden__','gsuite'


    @classmethod
    def getOptionsBoxResults(cls, prevChoices):
        if len(cls.ATTRIBUTES) > 1 and getattr(prevChoices, 'attributeList0') in [None,'--None--']:
            return
        if prevChoices.presentResults is None or 'Select all tracks' in prevChoices.presentResults:
           return
        cols,colListString = cls.getColListString()
        rows = cls._getValidRows(prevChoices, cls.getFilteredRows(prevChoices,colListString))
        #rows = cls.getRows(prevChoices,colListString)
        if len(rows) == 0:
            return
        elif rows[0][0].find('EMPTY') > -1:
            cls.exception = rows[0]
            return
        list_ = []
        for i, row in enumerate(rows):
            if row == None or len(row)<len(cols):
               continue

            #line = ''
            #for i in xrange(len(row)):
            #    line+= str(row[i])+'\t|'
            #line = line.strip('|')
            #cls.RESULT_FILES_URLS.append(row[0])#.replace('http://','ftp://'))
            filename = row[0].split('/')[-1]
            list_.append((str(i) + ' - ' + filename,True))

        #return OrderedDict([(x[0],False) for x in rows if x[0] != None])
        #if prevChoices.download == 'List search results':
        #    return [x[0] for x in List]
        #else:
        return OrderedDict(list_)


    #@staticmethod
    @classmethod
    def execute(cls,choices, galaxyFn=None, username=''):
        cols, colListString = cls.getColListString()

        if len(cls.ATTRIBUTES) > 1 and getattr(choices, 'attributeList0') in [None,'--None--']:
            #rows = cls.getAllRows(colListString)
            rows = cls._getValidRows(choices, cls.getAllRows(colListString))
        else:
            rows = cls._getValidRows(choices, cls.getFilteredRows(choices,colListString))
        
        
        if choices.outFormat == 'Html':
           cls.printHtml(choices,cols,rows,colListString,galaxyFn)
        else:
           cls.printGSuite(choices,cols,rows,colListString,galaxyFn)
           #cls.printText(choices,cols,rows,colListString,outFile)

    @classmethod
    def getColListString(cls):
        cols = cls.DB._db.correctColumNames\
        (cls.DB._db.getTableCols(cls.TABLE_NAME))
        colListString = ''


    #@classmethod
    #def getRowsCount(cls, colListString):
    @classmethod
    def getALLRowsCount(cls, colListString):
        return cls.getRowsCount(colListString)
    
    @classmethod
    def getAllRows(cls, colListString):
        return cls.getRows(colListString)
    
    @classmethod
    def getFilteredRows(cls, choices,colListString):
        WHERE = cls.getSQLFilter(choices,colListString)
        return cls.getRows(colListString,WHERE)
    
    @classmethod
    def getSQLFilter(cls, choices,colListString):
        
        WHERE = cls._getGlobalSQLFilter()
        if WHERE is not None:
            WHERE += ' AND '
        else:
            WHERE = ''

        for i in xrange(len(cls.ATTRIBUTES)):

            attr = getattr(choices, 'attributeList%s' % i)
            if attr in [None,'--None--']:
               continue
            
            col = cls._getAttributeNameFromReadableName(attr)
            col = cls.DB._db.correctColumNames([col])[0]

            rep_val = getattr(choices, 'valueList%s' % i)

            if getattr(choices, 'multiSelect%s' % i) in ['Multiple Selection','Text Search']:#type(rep_val) is OrderedDict:
                selected_vals = [x for x,selected in rep_val.iteritems() if selected]
                if len(selected_vals) == 0:
                    continue
                vals = [cls._getAttributeValueNameFromReadableName(val)[1] for val in selected_vals]
                WHERE += col  + ' in ('
                for val in vals:
                    WHERE += '"' + val + '", '
                if WHERE.endswith(', '):
                    WHERE = WHERE.strip(', ')
                WHERE += ') AND '
            elif getattr(choices, 'multiSelect%s' % i) == 'Single Selection':
                if rep_val in ['--Select--','--Range--',None,'']:
                    continue
                val = cls._getAttributeValueNameFromReadableName(rep_val)[1]
                WHERE += col  + " LIKE '" + val + "' AND "
            ###elif getattr(choices, 'multiSelect%s' % i) == 'Text Search':
            ###    '''Multi-line text'''
            ###    selected_vals = [x.strip() for x in rep_val.split('\n')]
            ###    if len(selected_vals) == 0:
            ###        continue
            ###    vals = [cls._getAttributeValueNameFromReadableName(val)[1] for val in selected_vals]
            ###    WHERE += col  + ' in ('
            ###    for val in vals:
            ###        WHERE += '"' + val + '", '
            ###    if WHERE.endswith(', '):
            ###        WHERE = WHERE.strip(', ')
            ###    WHERE += ') AND '

        if WHERE.endswith('AND '):
           WHERE = WHERE.rstrip('AND ')
        
        return WHERE
    
    @classmethod
    def getRowsCount(cls, colListString, WHERE = ''):
        
        g_WHERE = cls._getGlobalSQLFilter()
        if g_WHERE is not None:
            if WHERE == '':
                WHERE = g_WHERE
            else:
                WHERE += ' AND '+ g_WHERE
        
        query = "SELECT count(*) FROM "+cls.TABLE_NAME+" "
        if WHERE != '':
           query += "WHERE " + WHERE + "ORDER BY "+colListString+";"
        else:
           query += "ORDER BY "+colListString+";"
           
        rows = cls.DB._db.runQuery(query)
        if len(rows) == 0 or rows == None:
           return 0
        else:
            return rows[0][0]
        
    @classmethod
    def getRows(cls, colListString, WHERE = ''):
        
        g_WHERE = cls._getGlobalSQLFilter()
        if g_WHERE is not None:
            if WHERE == '':
                WHERE = g_WHERE
            else:
                WHERE += ' AND '+ g_WHERE
        
        query = "SELECT "+colListString+" FROM "+cls.TABLE_NAME+" "
        if WHERE != '':
           query += "WHERE " + WHERE + "ORDER BY "+colListString+";"
        else:
           query += "ORDER BY "+colListString+";"

        rows = cls.DB._db.runQuery(query)
        if len(rows) == 0 or rows == None:
           return [('EMPTY Result for Query:\n' + query,)]

        return rows

    # @classmethod
    # def _getValidRows(cls, choices, allRows):#With selected file-types
    #     rows = []
    #     if not choices.filetype in [None,'',[]]:
    #         print 'filetype'+str(choices.filetype)
    #         fileTypes = [x.split('[')[0] for x,selected in choices.filetype.iteritems() if selected]
    #         for row in allRows:
    #                 if cls._isValidRow(row,fileTypes):
    #                     rows.append(row)
    #     else:
    #         rows = allRows
    #     return rows
    @classmethod
    def _getValidRows(cls, choices, allRows):#With selected file-types
        rows = []
        if not choices.dataType in [None,'',[]]:
            print 'datatype'+str(choices.dataType)
            dataTypes = [x.split('[')[0].strip() for x,selected in choices.dataType.iteritems() if selected]
            for row in allRows:
                    datatype = row[1].strip()
                    if datatype in dataTypes:
                        rows.append(row)
        else:
            rows = allRows
        return rows

    @classmethod
    def _getSelectedRows(cls, choices, rows):

        if choices.results in [None,'',[]]:
            for row in rows:
                yield row
        else:
            rowDict = OrderedDict()
            for i, row in enumerate(rows):
                rowKey = str(i) + ' - ' + row[0].split('/')[-1]
                rowDict[rowKey] = row

            for key, selected in choices.results.iteritems():
                if selected:
                    yield rowDict[key]

    @classmethod
    def _isValidRow(cls,row,fileTypes):
        filename = row[0].strip().split('/')[-1]
        for ft in fileTypes:
            for ext in cls.DB.getFileExtensions(ft):
                if '.*' in ext and re.match(ext.lower(), filename) or \
                filename.lower().endswith('.'+ext.lower()):
                    return True
                
        return False
    

    @classmethod
    def printHtml(cls, choices, cols, rows, colListString, outFileName):

        #colListString = colListString.replace('_','').upper()
        #colListString = colListString.replace('"','')

        outFile = open(outFileName, 'w')

        core = HtmlCore()
        core.begin()

        headerList = [cls._getAttributeReadableNameFromName(x.strip()) for x in colListString.split(',')]
        for i,header in enumerate(headerList):
            if header.strip() in ['url','URL']:
                headerList[i] = 'Download Link'
                
        emptyCells = [0 for header in headerList]
        
        rowList = []
        for row in cls._getSelectedRows(choices, rows):
            if row == None or len(row)<len(cols):
               continue
            i = 0
            for i in range(len(row)):
                if row[i] is None or str(row[i]).strip() == '':
                    emptyCells[i] = emptyCells[i] + 1
            
            url = str(row[0])
            filename = url.split('/')[-1]
            link = HtmlCore().link(filename,url)
            row = list(row)
            row[0] = link
            rowList.append([str(x) for x in row])

        #if len(cls.SELECTED_FILES_INDEXES)>0:
        #   arr = cls.SELECTED_FILES_INDEXES
        #else:
        #   arr = range(len(rows))
        newHeaderList = []
        i = 0
        for i in range(len(headerList)):
            if emptyCells[i] < len(rowList):
                newHeaderList.append(headerList[i])
        
        core.tableHeader(newHeaderList,sortable = True)
        
        for row in rowList:
            #row = rows[i]
            tableLine = []
            i = 0
            for i in range(len(row)):
                if emptyCells[i] < len(rowList):
                    tableLine.append(row[i])
            
            core.tableLine(tableLine)

        
        
        core.tableFooter()
        core.end()
        outFile.write(str(core))

        outFile.close()

    @classmethod
    def printText(cls, choices,cols,rows,colListString,outFileName):
        outFile = open(outFileName, 'w')

        colListString = colListString.replace(',','\t')
        #colListString = colListString.replace(',','\t|')
        #colListString = colListString.replace('_','').upper()
        colListString = colListString.replace('_','').lower()
        colListString = colListString.replace('"','')
        colListString = colListString.strip('\t')
        #outFile.write('#'+colListString+'\n')
        outFile.write('###'+colListString+'\n')
        #outFile.write('#'+'-'*100+'\n')

        #if len(cls.SELECTED_FILES_INDEXES)>0:
        #   arr = cls.SELECTED_FILES_INDEXES
        #else:
        #   arr = range(len(rows))
        #for i in arr:
        for row in cls._getSelectedRows(choices, rows):
            #row = rows[i]
            if row == None or len(row)<len(cols):
               continue
            #filename = row[0].split('/')[-1]
            line = ''

            for i in xrange(len(row)):
                line+= str(row[i])+'\t'
            line = line.strip('\t')
            #outFile.write(row[1]+'\t|'+row[0]+newLine)
            outFile.write(line+'\n')
            #outFile.write('-'*100+'\n')

        outFile.close()

    @classmethod
    def printGSuite(cls, choices, cols, rows, colListString, outFileName):
        colListString = colListString.replace(',','\t')
        #colListString = colListString.replace('_','').lower()
        #colListString = colListString.replace('"','')
        colListString = colListString.strip('\t')
        colList = colListString.split('\t')

        gSuite = GSuite()

        #if len(cls.SELECTED_FILES_INDEXES)>0:
        #   arr = cls.SELECTED_FILES_INDEXES
        #else:
        #   arr = range(len(rows))

        for count, row in enumerate( \
                cls._getSelectedRows(choices, rows)):
            #row = rows[i]
            if row == None or len(row)<len(cols):
               continue

            url = row[0].strip()
            if cls.DOWNLOAD_PROTOCOL != None:
                protocol = url.split(':')[0]
                url = url.replace(protocol+':',cls.DOWNLOAD_PROTOCOL+':')

            from gold.gsuite.GSuiteTrack import urlparse
            parsedUrl = urlparse.urlparse(url)

            sitename = parsedUrl.netloc
            filepath = parsedUrl.path
            query = parsedUrl.query
            #sitename = url.split(':')[1].strip('/').split('/')[0]
            ###filename = url.split('/')[-1]
            #filepath = url.split(sitename)[1]
            suffix = cls._getGSuiteTrackSuffix(url)
            uri = None
            if url.startswith('ftp:'):
                uri = FtpGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
            elif url.startswith('http:'):
                uri = HttpGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
            elif url.startswith('https:'):
                uri = HttpsGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)
            elif url.startswith('rsync:'):
                uri = RsyncGSuiteTrack.generateURI(netloc=sitename, path=filepath, suffix = suffix, query=query)

            attr_val_list = []
            for j in range(1,len(row)):
                if str(row[j]).strip() in ['None','']:
                    continue
                colReadableName = cls._getAttributeReadableNameFromName(colList[j])
                ## some datatypes are not string, e.g. datetime, and some others contain non-printable characters, e.g. \x00
                import string
                value = filter(lambda x: x in string.printable, str(row[j]))
                attr_val_list.append((colReadableName,value))
                
            gSuite.addTrack(GSuiteTrack(uri, doUnquote = cls._unquoteTrackURL(),
                                        genome=cls._getOutputGenome(), attributes=OrderedDict(attr_val_list)))

        contents = GSuiteComposer.composeToFile(gSuite, outFileName)

    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''

        if not choices.dataType in [None,'',[]] and len([x for x,selected in choices.dataType.iteritems() if selected]) == 0:
            return 'You have to select at least one data type'

        if not choices.results in [None,'',[]] and len([x for x,selected in choices.results.iteritems() if selected]) == 0:
            return 'You have to select at least one result'

        if cls.exception:
            #raise cls.exception
            return str(cls.exception)

        try:# The list will be 'None' when the page is initially loaded
            if not (len(cls.ATTRIBUTES) > 1 and getattr(choices, 'attributeList0') in [None,'--None--']):
                #Return all rows in this case
                selected_attrs = 0
                for i in xrange(len(cls.ATTRIBUTES)):
                    if not getattr(choices, 'valueList%s' % i) in [None,'','--Select--']:
                        #New requested by SG
                        if getattr(choices, 'multiSelect%s' % (i)) == 'Multiple Selection':
                            val = getattr(choices, 'valueList%s' % (i))
                            if len([x[0] for x in val.items() if x[1]]) == 0:
                                continue
                        selected_attrs+=1
    
                if selected_attrs == 0:
                   return 'You have to select at least one attribute value filter'#+str(selected_attrs)+'--'+str(len(cls.ATTRIBUTES))
        except Exception as e:
            return str(e) + '--You have to select at least one attribute'



    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None

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
    #    return ['source','search','dataType','cell','antibody','type']
    #
    @staticmethod
    def getToolDescription():
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from quick.webtools.imports.TrackSourceTestTool import TrackSourceTestTool
        return TrackSourceTestTool.getToolDescription()
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
    @staticmethod
    def getFullExampleURL():
        from quick.webtools.imports.TrackSourceTestTool import TrackSourceTestTool
        return TrackSourceTestTool.getFullExampleURL()
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
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
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

        if choices.outFormat == 'Html':
            return 'customhtml'
            #return 'txt'    
        else:
            return 'gsuite'




#TrackSearchTool.DB._db.createTableFromList('temp',['attr'])