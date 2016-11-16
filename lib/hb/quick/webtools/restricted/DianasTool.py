import copy
import itertools
import math
import urllib2
from collections import OrderedDict

from gold.application.HBAPI import GlobalBinSource, PlainTrack
from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite import GSuiteConstants
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
from gold.track.Track import Track
from gold.util.CommonFunctions import strWithStdFormatting
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import UserBinSource
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.MaxElementValueStat import MaxElementValueStat
from quick.statistic.RawOverlapToSelfStat import RawOverlapToSelfStat
from quick.statistic.RipleysKStat import RipleysKStat
from quick.statistic.SumTrackPointsStat import SumTrackPointsStat
from quick.util.CommonFunctions import ensurePathExists
from quick.util.GenomeInfo import GenomeInfo
from quick.util.StaticFile import GalaxyRunSpecificFile
from quick.util.TrackReportCommon import STAT_OVERLAP_COUNT_BPS,\
    STAT_OVERLAP_RATIO, STAT_FACTOR_OBSERVED_VS_EXPECTED, processRawResults,\
    STAT_COVERAGE_RATIO_VS_REF_TRACK, STAT_COVERAGE_RATIO_VS_QUERY_TRACK,\
    STAT_LIST_INDEX
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool, GeneralGuiTool, HistElement
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs


# This is a template prototyping GUI that comes together with a corresponding
# web page.

####
##
##

class DianasTool(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Diana's tool"
    
    @staticmethod
    def getSubToolClasses():
        return [GenerateRipleysK, GenerateTwoLevelOverlapPreferenceStat, DivideBedFileForChosenPhrase,\
                KseniagSuite, gSuiteName, divideGSuite, removeStringFromGSuite, VisTrackFrequency, \
                VisTrackFrequencyBetweenTwoTracks, gSuiteInverse, showGSuiteResultsInTable, \
                divideBedFile, divideBedFileV2, removeFromBedFile, GenerateRipleysKForEachChromosomeSeparately, \
                rainfallPlots, makeRainfallPlots, rainfallPlotsGSuite, miRNAPrecursors, rankingTFtracks, rankingTFtracks2, mRNATool, \
                divideBedFileTool, driverGeneIdentification, rankingTFtracks3, \
                geneExpressionV4, geneExpressionCutOff, geneExpressionCutOffTrack, geneExpressionHist, \
                geneExpressionMaxValue, kmerGSuite, rainfallBuildNewFile]

#geneExpression, geneExpressionV2, geneExpressionV3, 




class geneExpressionMaxValue(GeneralGuiTool, UserBinMixin):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Gene expression heatmap with option"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select target track collection GSuite','gSuiteFirst')
                ] + UserBinMixin.getUserBinInputBoxNames()


    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

  
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        
        analysis = AnalysisSpec(MaxElementValueStat)
        
        resultsList=[]
        trackList=[]
        
        globalRes=[]
        
        i=0
        
        avgTrack=[]
        
        for x in targetGSuite.allTracks():
            analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, x.genome)
            results = doAnalysis(analysis, analysisBins,  [PlainTrack(x.trackName)])
             
            tn=x.trackName
            globRes=results.getGlobalResult()
            globalRes.append([i, urllib2.unquote(tn[-1]), float(globRes['Result'])])
            trackList.append(urllib2.unquote(tn[-1]))
             
            resultsListPart=[]
            resultsListPartToSum=[]
            for el in results.getAllValuesForResDictKey('Result'):
                if el is None:
                    el=0
                else:
#                     el=float(el)
                    if el ==0:
                        el=0
                    else:
                        el1=float(el)
                        el=math.log(float(el),10)
                resultsListPart.append(el)
                resultsListPartToSum.append(el1)
            
          
            avgTrack.append([urllib2.unquote(tn[-1]), sum(resultsListPartToSum) / float(len(resultsListPartToSum))])
             
            resultsList.append(resultsListPart)
            
            
             
            if i==0:  
                categories = []
                for el in results.getAllRegionKeys():
                    categories.append(str(el))
            i+=1
            
                
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        
        htmlCore.header("")
        htmlCore.divBegin('resultsDiv')
#         htmlCore.tableHeader(['Number', 'Track name', 'Max value'], sortable=True, tableId='resultsTable')
        htmlCore.tableHeader(['Track name', 'Avg(from max) value'], sortable=True, tableId='resultsTable')
#         for line in globalRes:
#             htmlCore.tableLine(line)
        for line in avgTrack:
            htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()
        
        
        vg = visualizationGraphs()
        res = vg.drawHeatmapLargeChart(resultsList,
                                       categories=categories,
                                       categoriesY=trackList,
                                       xAxisRotation=90,
                                       xAxisTitle='',
                                       yAxisTitle='log10 scale',
                                       )
        
        htmlCore.line(res)
        htmlCore.end()    
            
        print htmlCore    
        
            
            #resultDict = results.getGlobalResult()
        
    @staticmethod
    def _getGenome(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.genome

    @staticmethod
    def _getTrackName1(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.allTracks().next().trackName

    @staticmethod
    def _getTrackName2(choices):
        return None

    @classmethod
    def getToolDescription(cls):
        return ''
  
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
    

class rainfallBuildNewFile(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Filter columns in bed files (rainfall paper filtering)"

    @staticmethod
    def getInputBoxNames():
        return [('Select genome', 'genome'),
                ('Select tracks','bedFile'),
                ('Select column which should have chromosome number (from 0)','chrNum'),
                ('Select the rest column (,)','column'),
                ('Select option','option'),
                ('Select column for option','optionVal')
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxBedFile(prevChoices):
        return ('__multihistory__', 'tabular')  
    
    @staticmethod
    def getOptionsBoxChrNum(prevChoices):            
        return ''
    
    @staticmethod
    def getOptionsBoxColumn(prevChoices):            
        return ''
    
    @staticmethod
    def getOptionsBoxOption(prevChoices):            
        return ['single mutations in two columns']
    
    
    @staticmethod
    def getOptionsBoxOptionVal(prevChoices):            
        return ''
    
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        
        bedFiles = choices.bedFile
        chrNum = int(choices.chrNum)
        column = choices.column
        column = column.replace(' ','')
        column = column.split(',')
        option = choices.option
        optionVal=choices.optionVal
        optionVal = optionVal.replace(' ','')
        optionVal = optionVal.split(',')
        
        
        mutList=['CA','CG','CT','TA','TC', 'TG']
        mutListReverse=['GT','GC','GA','AT','AG','AC']
        
        mut=[]
        for elN in range(0, len(mutList)):
            mut.append([mutList[elN], mutListReverse[elN]])
            
        
        for key, bedFile in bedFiles.items():
            #print bedfile
            
            outGSuite = GSuite()
                    
            inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(bedFile.split(':')), 'r')  
            with inputFile as f:
                data=[x.strip('\n') for x in f.readlines()]
            f.closed
            inputFile.close()
            
            name = bedFile.split(':')
            name = urllib2.unquote(name[-1])
            
            #maxelementvaluestat
            
            for m in mut:
                
                print galaxyFn
                
                trackName=str(name)+'-'+str(m[0])
                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=trackName,
                                                suffix='bed')
    
                gSuiteTrack = GSuiteTrack(uri)
                outFn = gSuiteTrack.path
                ensurePathExists(outFn)

                
                headerFirst = 'track name="' + str(name) + '" description="' + str(m[0]) + '" priority=1'
                #outputFile =  open(cls.makeHistElement(galaxyExt='bed',title=str(name)+'-'+str(m[0]), label=str(name)+'-'+str(m[0])), 'w')
                with open(outFn, 'w') as outputFile:
                    outputFile.write(headerFirst + '\n')
                    for d in data:
                        row = d.split('\t')
                        if option == 'single mutations in two columns':
                            if len(row[int(optionVal[0])]) == 1 and len(row[int(optionVal[1])]) == 1:
                                stM1 = list(m[0])
                                stM2 = list(m[1])
                                if ( row[int(optionVal[0])] ==stM1[0] and row[int(optionVal[1])] == stM1[1] ) or ( row[int(optionVal[0])] ==stM2[0] and row[int(optionVal[1])] == stM2[1]):
                                    line =''    
                                    for c in column:
                                        line += str(row[int(c)]) + '\t'
                                    outputFile.write('chr'+str(row[chrNum]) + '\t' + line + '\n')
                        
                    outputFile.close()
                    
                outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

            GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['Gsuite paper'])
            
        
        print 'GSuiteComposer - done'


    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('Gsuite paper', 'gsuite')]
        

class kmerGSuite(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "k-mer build 3-level gsuite"

    @staticmethod
    def getInputBoxNames():
        return [ ('Select genome', 'genome'),
                ('Select GSuite', 'gSuite'),
                ]
        
    
    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'
    
    @staticmethod
    def getOptionsBoxGSuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        
        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.gSuite.split(':')), 'r') as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        genome = choices.genome
        
        
        header='##location: local\n##file format: primary\n##track type: unknown\n###uri\ttitle\tdir_level_2\tdir_level_3\tdir_level_4\n####genome=mm9\n'
        
        output=''
        for d in range(0, len(data)):
            if d < 4:
                pass
            elif d == 4:
                output += header 
            else:
                newData = data[d].split("\t")
                
                kmer = list(newData[1])
                j=0
                for elKmer in kmer:
                    if j==1:
                        newData.append(str(genome)+'-'+str(elKmer.upper()))
                    else:
                        newData.append(elKmer.upper())
                    j+=1
                
                output += '\t'.join(newData)
                
                output +='\n'
        
        open(galaxyFn,'w').write(output) 
        
        print 'GSuite - done'


    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'gsuite'


class geneExpressionCutOff(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression - select cutoff value for gSuite"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select genome', 'genome'),
                ('Select GSuite', 'gSuite'),
                ('Select cutoff value', 'cutoff')
                ]
        
    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'
    
    @staticmethod
    def getOptionsBoxGSuite(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @staticmethod
    def getOptionsBoxCutoff(prevChoices):
        return ''
    
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        
        gSuiteName = choices.gSuite
        cutoff = choices.cutoff
        dataDict={}
        
        gSuite = getGSuiteFromGalaxyTN(gSuiteName)
            #parse the tracks!
        for track in gSuite.allTrackTitles():
            gSuiteTrack = gSuite.getTrackFromTitle(track)
            trackName = track
            
            if not trackName in dataDict:
                dataDict[trackName]=[]#dictOfTissue
            with open(gSuiteTrack.path, 'r') as f:
                for x in f.readlines(): 
                    el = x.strip('\n').split('\t')
                    
                    geneNameCuttOffVal =  el[3].split('---')
                    geneName  = geneNameCuttOffVal[0]
                    cuttOffVale  = geneNameCuttOffVal[1]
                    
                    
                    if float(cuttOffVale) >= float(cutoff):
                       
                        x= x.replace('---','\t')
                        el2=x.strip('\n').split('\t')
                        
                        x = str(el2[0]) + '\t' + str(int(el2[1])) + '\t' + str(int(el2[2]))+  '\t' + str(float(el2[4])) + '\t' + str(el2[3]) +'\n'
                        dataDict[trackName].append(x)
                        
           
                    
        outGSuite = GSuite()
        for trackName, it0 in dataDict.items():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=trackName,
                                                suffix='gtrack')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)
            
            header='##Track type: valued segments\n###seqid\tstart\tend\tvalue\tgene\n####genome=hg19\n'
            
            print str(trackName) + '-' + str(len(it0))
            with open(outFn, 'w') as outFile: 
                outFile.write(header)
                for el in it0:
                    outFile.write(str(el))
 
            print 'done with' + str(trackName)
 
            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['GE gsuite with cutoff value'])

        print 'GSuiteComposer - done'


    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('GE gsuite with cutoff value', 'gsuite')]

class geneExpressionCutOffTrack(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression - select cutoff value for track"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select genome', 'genome'),
                ('Select track', 'track'),
                ('Select cutoff value', 'cutoff')
                ]
        
    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'
    
    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxCutoff(prevChoices):
        return ''
    
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        
        trackName = choices.track
        cutoff = choices.cutoff
        
        wholeFile={}
        
        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(trackName.split(':')), 'r') as f:
            for x in f.readlines():
                if i > 0:
                    lVal = x.strip('\n').split('\t')
                    
                    if float(lVal[5]) >= float(cutoff):
                        if not lVal[0] in wholeFile:
                            wholeFile[lVal[0]]={}
                        if not lVal[4] in wholeFile[lVal[0]]:
                            wholeFile[lVal[0]][lVal[4]]={}
                            wholeFile[lVal[0]][lVal[4]]['start']=[]
                            wholeFile[lVal[0]][lVal[4]]['end']=[]
                
                        wholeFile[lVal[0]][lVal[4]]['start'].append(int(lVal[1]))
                        wholeFile[lVal[0]][lVal[4]]['end'].append(int(lVal[2]))
                    
                i+=1
        
        
        outputFile =  open(cls.makeHistElement(galaxyExt='bed',title=str('File with cutoff ' + str(cutoff))), 'w')
        
        output=''
        for key0, it0 in wholeFile.items():
            minV=0
            maxV=0
            for key1, it1 in it0.items():
                minV = int(min(it1['start']))-1
                maxV = max(it1['end'])
                output += 'chr'+str(key0) + '\t' + str(minV) + '\t' + str(maxV) + '\t' + str(key1) + '\n'
                            
        
        outputFile.write(output) 
        outputFile.close()
                
        
        print 'Track cut - done'


    @staticmethod
    def validateAndReturnErrors(choices):
        return None
    
    @staticmethod
    def getOutputFormat(choices):
        return 'bed'

class geneExpressionHist(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression histogram"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select annotatations', 'annotations'),
                ('Select tissue type', 'type'),
                ('Select RNA-Seq Data', 'rnaSeqData'),
                ('Select reference', 'reference'),
                ('Select breaks for clustering', 'breaks'),
                ('Select max value for clustering', 'maxVal')
                ]
    @staticmethod
    def getOptionsBoxAnnotations():
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    # @classmethod
    # def asDict(cls, vector):
    #     """Convert an RPy2 ListVector to a Python dict"""
    #     from rpy2 import robjects
    #     import types
    #     result = {}
    #     for i, name in enumerate(vector.names):
    #         if isinstance(vector[i], robjects.ListVector):
    #             result[name] = as_dict(vector[i])
    #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    #             result[name] = vector[i][0]
    #         else:
    #             result[name] = vector[i]
    #     return result

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxBreaks(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxMaxVal(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        type = choices.type
        rnaSeqData = choices.rnaSeqData
        breaks = choices.breaks
        maxVal = choices.maxVal
        reference = choices.reference

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5


        annotationDict = {}

        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
            for x in f.readlines():
                if i > 0:
                    el = x.strip('\n').split('\t')
                    if not el[nrType] in annotationDict:
                        annotationDict[el[nrType]]=[]
                    if not el[0] in annotationDict[el[nrType]]:
                        annotationDict[el[nrType]].append(el[0])
                i+=1
        i=0

        print 'done annotationDict'

        i=0
        rnaSeqDataDict={}
        with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
            for x in f.readlines():
                if i == 2:
                    el = x.strip('\n').split('\t')
                    header=[]
                    for elN in range(2, len(el)):
                        header.append(el[elN])
                        rnaSeqDataDict[el[elN]]={}
                if i > 2:
                    el = x.strip('\n').split('\t')
                    for elN in range(2, len(el)):
                        if el[elN]!='0':
                            if not el[0] in rnaSeqDataDict[header[elN-2]]:
                                rnaSeqDataDict[header[elN-2]][el[0]]=10
                            rnaSeqDataDict[header[elN-2]][el[0]] = float(el[elN])
                i+=1

        print 'done rnaSeqDataDict'

        #print rnaSeqDataDict


        finalResults={}
        for key0, it0 in annotationDict.iteritems():
            if key0 not in finalResults:
                finalResults[key0]={}
            for it00 in it0:
                if it00 in rnaSeqDataDict.keys():
                    for key1, it1 in rnaSeqDataDict[it00].iteritems():
                        if not key1 in finalResults[key0]:
                            finalResults[key0][key1]={}
                            finalResults[key0][key1]['num']=0
                            finalResults[key0][key1]['div']=0
                        finalResults[key0][key1]['num'] += float(it1)
                        finalResults[key0][key1]['div'] += 1.0

        # print finalResults



        vg = visualizationGraphs()


        print finalResults

        outputFile = open(cls.makeHistElement(galaxyExt='tabular', title='List of tissue'), 'w')
        res=''
        for tissue in  finalResults.keys():
            if finalResults[tissue]:
                res += str(tissue) + '\n'
        outputFile.write(res)
        outputFile.close()

        print 'done finalResults'

        i=0
        geneList=[]
        with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
            for x in f.readlines():

                if i > 4:

                    el = x.strip('\n').split(' ')
                    geneID = el[1].replace('"', '').replace(';','')
                    elNewDiv = x.strip('\n').split('\t')


                    if elNewDiv[2] == 'transcript':
                        geneList.append(geneID)

                i+=1


        print 'gene len' + str(len(geneList))




        tissueDict={}
        for tissue, it0 in finalResults.iteritems():
            if len(it0)!=0:
                if not tissue in tissueDict:
                    tissueDict[tissue]={}
                for gene, it1 in it0.iteritems():
                    if gene in geneList:
                        if not gene in tissueDict[tissue]:
                            tissueDict[tissue][gene]=0
                        tissueDict[tissue][gene]=float(it1['num']/it1['div'])

                tissueDict[tissue] = OrderedDict(sorted(tissueDict[tissue].items(), key=lambda t: t[1], reverse=True))

                outputFile = open(cls.makeHistElement(galaxyExt='html', title=str(tissue)), 'w')

                vg.countFromStart()

                res = vg.drawColumnChart(
                    tissueDict[tissue].values(),
                    xAxisRotation=90,
                    categories=tissueDict[tissue].keys(),
                    showInLegend=False,
                    titleText=str(tissue),
                    yAxisTitle='linear scale',
                    height=400,
                    addTable=True,
                    #extraScriptButton=[OrderedDict({'Use linear scale':'linear','Use log10 scale':'logarithmic'}), 'yAxisType']
                    )

                res += vg.drawColumnChart(
                    [math.log10(v) for v in tissueDict[tissue].values()],
                    xAxisRotation=90,
                    categories=tissueDict[tissue].keys(),
                    showInLegend=False,
                    titleText=str(tissue),
                    yAxisTitle='log10 scale',
                    height=400,
                    addTable=True,
                    #extraScriptButton=[OrderedDict({'Use linear scale':'linear','Use log10 scale':'logarithmic'}), 'yAxisType']
                    )



                outputFile.write(res)
                outputFile.close()

        htmlCore = HtmlCore()
        htmlCore.begin()

        htmlCore.line('Done')

        htmlCore.end()


        print htmlCore



    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @staticmethod
    def getOutputFormat(choices):
        return 'customhtml'

class geneExpression(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select genome', 'genome'),
                ('Select annotatations', 'annotations'),
                ('Select RNA-Seq Data', 'rnaSeqData'),
                #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
                ('Select reference', 'reference'),
                ('Select cutoff value', 'cutOff'),
                ('Select tissue type', 'type')
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxAnnotations(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def asDict(cls, vector):
    #     """Convert an RPy2 ListVector to a Python dict"""
    #     from rpy2 import robjects
    #     import types
    #     result = {}
    #     for i, name in enumerate(vector.names):
    #         if isinstance(vector[i], robjects.ListVector):
    #             result[name] = as_dict(vector[i])
    #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    #             result[name] = vector[i][0]
    #         else:
    #             result[name] = vector[i]
    #     return result

    # @staticmethod
    # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    #
    #     htmlCore = HtmlCore()
    #     htmlCore.begin()
    #
    #     vg = visualizationGraphs()
    #     rnaSeqDataPlot=[]
    #     i=0
    #     if prevChoices.rnaSeqData:
    #
    #
    #
    #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    #         data = f.readlines()
    #         colLen = data[2]
    #         colLen = len(colLen.strip('\n').split('\t'))
    #
    #         col = [w for w in range(2, colLen)]
    #
    #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    #
    #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    #         # #     for x in f.readlines():
    #         # #         if i > 2:
    #         # #             el = x.strip('\n').split('\t')
    #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    #         # #         i+=1
    #         #
    #         # #
    #
    #
    #
    #         #count histoggram
    #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    #         simpleHist = r(rCode)(dd)
    #         simpleHistDict = geneExpression.asDict(simpleHist)
    #
    #
    #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    #                                 xAxisRotation=90,
    #                                 categories=list(simpleHistDict['breaks']),
    #                                 showInLegend=False,
    #                                 histogram=True,
    #                                 height=400
    #                                 )
    #         htmlCore.line(res)
    #
    #     htmlCore.end()
    #
    #     return '', str(res)


    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxCutOff(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        rnaSeqData = choices.rnaSeqData
        reference = choices.reference

        cutoff = choices.cutOff
        type = choices.type

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5


        annotationDict = {}

        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
            for x in f.readlines():
                if i > 0:
                    el = x.strip('\n').split('\t')
                    if not el[nrType] in annotationDict:
                        annotationDict[el[nrType]]=[]
                    if not el[0] in annotationDict[el[nrType]]:
                        annotationDict[el[nrType]].append(el[0])
                i+=1
        i=0

        rnaSeqDataDict={}
        with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
            for x in f.readlines():
                if i == 2:
                    el = x.strip('\n').split('\t')
                    header=[]
                    for elN in range(2, len(el)):
                        header.append(el[elN])
                        rnaSeqDataDict[el[elN]]=[]
                if i > 2:
                    el = x.strip('\n').split('\t')
                    for elN in range(2, len(el)):
                        if el[elN] >= cutoff:
                            if not el[0] in rnaSeqDataDict[header[elN-2]]:
                                rnaSeqDataDict[header[elN-2]].append(el[0])
                i+=1

        rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
        rnaSeqDataDictList = list(set(rnaSeqDataDictList))

        i=0
        filesReferenceDict={}
        referenceDict={}

        header=[]
        with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
            for x in f.readlines():

                if i > 4:

                    el = x.strip('\n').split(' ')
                    geneID = el[1].replace('"', '').replace(';','')

                    elNewDiv = x.strip('\n').split('\t')

                    j=0
                    xNew=[]
                    for elND in elNewDiv:
                        if j==0:
                            xNew.append('chr' + str(elNewDiv[0]))
                        else:
                            xNew.append(elND)
                        j+=1



                    if elNewDiv[2] == 'transcript':
                        if geneID in rnaSeqDataDictList:
                            if not geneID in referenceDict:
                                referenceDict[geneID] = []
                            referenceDict[geneID].append(i)

                            if i not in filesReferenceDict:
                                filesReferenceDict[i]=[]
                            filesReferenceDict[i].append('\t'.join(xNew))

                    # print referenceDict
                    # print '\n' + '<br \>'
                else:
                    header.append(x)
                i+=1

        # print '\n' + '<br \>'
        # print '\n' + '<br \>'
        # print referenceDict

        #build files and then gSuite

        outGSuite = GSuite()
        for trackName, it0 in annotationDict.items():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=trackName,
                                                suffix='gff')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)


            with open(outFn, 'w') as outFile:
                outFile.write(''.join(header))

                for it00 in it0:
                    if it00 in rnaSeqDataDict:
                        for it1 in rnaSeqDataDict[it00]:
                            if it1 in referenceDict.keys():
                                for it2 in referenceDict[it1]:
                                    outFile.write(filesReferenceDict[it2][0] + '\n')

            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])

        # trackNameList = [ 'tissue', 'blood']
        #
        # for trackName in trackNameList:
        #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
        #     gSuiteTrack = GSuiteTrack(uri)
        #     outFn = gSuiteTrack.path
        #     ensurePathExists(outFn)
        #     line = ['chr1', '10', '200']
        #     with open(outFn, 'w') as outFile:
        #         outFile.write('\t'.join(line) + '\n')
        #
        #
        #
        #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
        #     #from quick.util.CommonFunctions import ensurePathExists
        #
        #     #ensurePathExists(fn)
        #
        #
        #
        #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
        #
        #     trackType = 'segments'
        #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
        #
        #
        #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
        #
        # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])

    # @staticmethod
    # def getOutputFormat(choices):
    #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]

    # @staticmethod
    # def getToolName():
    #     return "Gene expression"
    #
    # @staticmethod
    # def getInputBoxNames():
    #     return [
    #             ('Select genome', 'genome'),
    #             ('Select annotatations', 'annotations'),
    #             ('Select RNA-Seq Data', 'rnaSeqData'),
    #             #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
    #             ('Select reference', 'reference'),
    #             ('Select cutoff value', 'cutOff'),
    #             ('Select tissue type', 'type')
    #             ]
    #
    # @staticmethod
    # def getOptionsBoxGenome():
    #     return '__genome__'
    #
    # @staticmethod
    # def getOptionsBoxAnnotations(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxRnaSeqData(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # # @classmethod
    # # def asDict(cls, vector):
    # #     """Convert an RPy2 ListVector to a Python dict"""
    # #     from rpy2 import robjects
    # #     import types
    # #     result = {}
    # #     for i, name in enumerate(vector.names):
    # #         if isinstance(vector[i], robjects.ListVector):
    # #             result[name] = as_dict(vector[i])
    # #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    # #             result[name] = vector[i][0]
    # #         else:
    # #             result[name] = vector[i]
    # #     return result
    #
    # # @staticmethod
    # # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    # #
    # #     htmlCore = HtmlCore()
    # #     htmlCore.begin()
    # #
    # #     vg = visualizationGraphs()
    # #     rnaSeqDataPlot=[]
    # #     i=0
    # #     if prevChoices.rnaSeqData:
    # #
    # #
    # #
    # #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    # #         data = f.readlines()
    # #         colLen = data[2]
    # #         colLen = len(colLen.strip('\n').split('\t'))
    # #
    # #         col = [w for w in range(2, colLen)]
    # #
    # #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    # #
    # #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    # #         # #     for x in f.readlines():
    # #         # #         if i > 2:
    # #         # #             el = x.strip('\n').split('\t')
    # #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    # #         # #         i+=1
    # #         #
    # #         # #
    # #
    # #
    # #
    # #         #count histoggram
    # #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    # #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    # #         simpleHist = r(rCode)(dd)
    # #         simpleHistDict = geneExpression.asDict(simpleHist)
    # #
    # #
    # #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    # #                                 xAxisRotation=90,
    # #                                 categories=list(simpleHistDict['breaks']),
    # #                                 showInLegend=False,
    # #                                 histogram=True,
    # #                                 height=400
    # #                                 )
    # #         htmlCore.line(res)
    # #
    # #     htmlCore.end()
    # #
    # #     return '', str(res)
    #
    #
    # @staticmethod
    # def getOptionsBoxReference(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxCutOff(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxType(prevChoices):
    #     return ['SMTS', 'SMTSD']

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #
    #     annotation = choices.annotations
    #     rnaSeqData = choices.rnaSeqData
    #     reference = choices.reference
    #
    #     cutoff = choices.cutOff
    #     type = choices.type
    #
    #     if type == 'SMTSD':
    #         nrType = 6
    #     if type == 'SMTS':
    #         nrType = 5
    #
    #
    #     cutoffDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(cutoff.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             el = x.strip('\n').split('\t')
    #             cutoffDict[el[0]] = el[1]
    #
    #
    #     print cutoffDict
    #
    #     annotationDict = {}
    #     i=0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i > 0:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[nrType] in annotationDict:
    #                     annotationDict[el[nrType]]=[]
    #                 if not el[0] in annotationDict[el[nrType]]:
    #                     annotationDict[el[nrType]].append(el[0])
    #             i+=1
    #     i=0
    #
    #     print annotationDict
    #
    #     rnaSeqDataDictList=[]
    #     rnaSeqDataDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i == 2:
    #                 el = x.strip('\n').split('\t')
    #                 header=[]
    #                 for elN in range(2, len(el)):
    #                     header.append(el[elN])
    #                     rnaSeqDataDict[el[elN]]={}
    #                     # for key1 in annotationDict.keys():
    #                     #     rnaSeqDataDict[el[elN]][key1]=[]
    #             if i > 2:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[0] in rnaSeqDataDictList:
    #                     rnaSeqDataDictList.append(el[0])
    #                 for elN in range(2, len(el)):
    #                     for key1, it1 in annotationDict.iteritems():
    #                         for it11 in it1:
    #                             if it11 == header[elN-2]:
    #                                 if key1 not in rnaSeqDataDict[header[elN-2]]:
    #                                     rnaSeqDataDict[header[elN-2]][key1]=[]
    #                                 #if key1 in cutoffDict.keys() and el[elN] >= cutoffDict[key1]:
    #                                 rnaSeqDataDict[header[elN-2]][key1].append(el[0])
    #
    #             i+=1
    #
    #     #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
    #     #rnaSeqDataDictList = list(set(rnaSeqDataDictList))
    #
    #
    #     i=0
    #     filesReferenceDict={}
    #     referenceDict={}
    #
    #     header=[]
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
    #         for x in f.readlines():
    #
    #             if i > 4:
    #
    #                 el = x.strip('\n').split(' ')
    #                 geneID = el[1].replace('"', '').replace(';','')
    #
    #                 elNewDiv = x.strip('\n').split('\t')
    #
    #                 j=0
    #                 xNew=[]
    #                 for elND in elNewDiv:
    #                     if j==0:
    #                         xNew.append('chr' + str(elNewDiv[0]))
    #                     else:
    #                         xNew.append(elND)
    #                     j+=1
    #
    #
    #                 if geneID in rnaSeqDataDictList:
    #                     if not geneID in referenceDict:
    #                         referenceDict[geneID] = []
    #                     referenceDict[geneID].append(i)
    #
    #                     if i not in filesReferenceDict:
    #                         filesReferenceDict[i]=[]
    #                     filesReferenceDict[i].append('\t'.join(xNew))
    #
    #                 # print referenceDict
    #                 # print '\n' + '<br \>'
    #             else:
    #                 header.append(x)
    #             i+=1
    #
    #     # print '\n' + '<br \>'
    #     # print '\n' + '<br \>'
    #     # print referenceDict
    #
    #     #build files and then gSuite
    #
    #     outGSuite = GSuite()
    #     for trackName, it0 in annotationDict.items():
    #         uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
    #                                             extraFileName=trackName,
    #                                             suffix='gff')
    #         gSuiteTrack = GSuiteTrack(uri)
    #         outFn = gSuiteTrack.path
    #         ensurePathExists(outFn)
    #
    #
    #         with open(outFn, 'w') as outFile:
    #             outFile.write(''.join(header))
    #
    #             for it00 in it0:
    #                 if it00 in rnaSeqDataDict:
    #                     for it1 in rnaSeqDataDict[it00][trackName]:
    #                         for it2 in referenceDict[it1]:
    #                             outFile.write(filesReferenceDict[it2][0] + '\n')
    #
    #         outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))
    #
    #     GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])
    #
    #     # trackNameList = [ 'tissue', 'blood']
    #     #
    #     # for trackName in trackNameList:
    #     #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
    #     #     gSuiteTrack = GSuiteTrack(uri)
    #     #     outFn = gSuiteTrack.path
    #     #     ensurePathExists(outFn)
    #     #     line = ['chr1', '10', '200']
    #     #     with open(outFn, 'w') as outFile:
    #     #         outFile.write('\t'.join(line) + '\n')
    #     #
    #     #
    #     #
    #     #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
    #     #     #from quick.util.CommonFunctions import ensurePathExists
    #     #
    #     #     #ensurePathExists(fn)
    #     #
    #     #
    #     #
    #     #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
    #     #
    #     #     trackType = 'segments'
    #     #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
    #     #
    #     #
    #     #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
    #     #
    #     # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])
    #
    # # @staticmethod
    # # def getOutputFormat(choices):
    # #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]




class geneExpressionV2(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression per tissue"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select genome', 'genome'),
                ('Select annotatations', 'annotations'),
                ('Select RNA-Seq Data', 'rnaSeqData'),
                #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
                ('Select reference', 'reference'),
                ('Select file with tissue', 'fileTypeTissue'),
                ('List of possible tissue', 'typeTissue'),
                ('Select cutoff value', 'cutOff'),
                ('Select tissue type', 'type')
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxAnnotations(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxFileTypeTissue(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxTypeTissue(prevChoices):
        listAnswer=[]
        if prevChoices.fileTypeTissue:
            fileTissue = prevChoices.fileTypeTissue
            #listAnswer.append(fileTissue)
            with open(ExternalTrackManager.extractFnFromGalaxyTN(fileTissue.split(':')), 'r') as f:
                for x in f.readlines():
                    tissueName  = x.replace('\t','').replace('\n','')
                    listAnswer.append(tissueName)
        return listAnswer


    @staticmethod
    def getOptionsBoxCutOff(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        rnaSeqData = choices.rnaSeqData
        reference = choices.reference
        typeTissue = choices.typeTissue
        cutoff = choices.cutOff
        type = choices.type

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5


        annotationDict = {} #tissue -> list of samID

        print typeTissue

        #typeTissue = 'Brain - Cortex'

        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
            for x in f.readlines():
                if i > 0:
                    el = x.strip('\n').split('\t')
                    if el[nrType] == typeTissue:
                        if not el[nrType] in annotationDict:
                            annotationDict[el[nrType]]=[]
                        if not el[0] in annotationDict[el[nrType]]:
                            annotationDict[el[nrType]].append(el[0])
                i+=1
        i=0

        print 'annotationDict - done'


        rnaSeqDataDict={}
        with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
            for x in f.readlines():
                if i%1000==0:
                    print i
                if i == 2:
                    el = x.strip('\n').split('\t')
                    header=[]
                    for elN in range(2, len(el)):
                        header.append(el[elN])
                        #rnaSeqDataDict[el[elN]]=[]
                if i > 2:
                    el = x.strip('\n').split('\t')
                    for elN in range(2, len(el)):
                        if el[elN] >= cutoff:
                            if header[elN-2] in annotationDict[typeTissue]:
                                if not header[elN-2] in rnaSeqDataDict:
                                    rnaSeqDataDict[header[elN-2]]=[]
                                if not el[0] in rnaSeqDataDict[header[elN-2]]:
                                    rnaSeqDataDict[header[elN-2]].append(el[0])
                i+=1

        print 'rnaSeqDataDict - done'

        rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
        rnaSeqDataDictList = list(set(rnaSeqDataDictList))

        print 'rnaSeqDataDictList - done'

        i=0
        filesReferenceDict={}
        referenceDict={}

        header=[]
        with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
            for x in f.readlines():
                if i%10000==0:
                    print i
                if i > 4:

                    el = x.strip('\n').split(' ')
                    geneID = el[1].replace('"', '').replace(';','')

                    elNewDiv = x.strip('\n').split('\t')

                    j=0
                    xNew=[]
                    for elND in elNewDiv:
                        if j==0:
                            xNew.append('chr' + str(elNewDiv[0]))
                        else:
                            xNew.append(elND)
                        j+=1


                    if geneID in rnaSeqDataDictList:
                        if elNewDiv[2] == 'transcript':
                            if geneID in rnaSeqDataDictList:
                                if not geneID in referenceDict:
                                    referenceDict[geneID] = []
                                referenceDict[geneID].append(i)

                                if i not in filesReferenceDict:
                                    filesReferenceDict[i]=[]
                                filesReferenceDict[i].append('\t'.join(xNew))

                    # print referenceDict
                    # print '\n' + '<br \>'
                else:
                    header.append(x)
                i+=1

        # print '\n' + '<br \>'
        # print '\n' + '<br \>'
        # print referenceDict

        print 'reference - done'

        #build files and then gSuite

        outGSuite = GSuite()
        for trackName, it0 in annotationDict.items():
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=trackName,
                                                suffix='gff')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            print str(trackName) + '-' + str(len(it0))
            with open(outFn, 'w') as outFile:
                outFile.write(''.join(header))

                for it00 in it0:
                    if it00 in rnaSeqDataDict:
                        for it1 in rnaSeqDataDict[it00]:
                            if it1 in referenceDict.keys():
                                for it2 in referenceDict[it1]:
                                    outFile.write(filesReferenceDict[it2][0] + '\n')

            print 'done with' + str(trackName)
            annotationDict[trackName]=[]


            outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])

        print 'GSuiteComposer - done'


    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]

    # @staticmethod
    # def getToolName():
    #     return "Gene expression"
    #
    # @staticmethod
    # def getInputBoxNames():
    #     return [
    #             ('Select genome', 'genome'),
    #             ('Select annotatations', 'annotations'),
    #             ('Select RNA-Seq Data', 'rnaSeqData'),
    #             #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
    #             ('Select reference', 'reference'),
    #             ('Select cutoff value', 'cutOff'),
    #             ('Select tissue type', 'type')
    #             ]
    #
    # @staticmethod
    # def getOptionsBoxGenome():
    #     return '__genome__'
    #
    # @staticmethod
    # def getOptionsBoxAnnotations(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxRnaSeqData(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # # @classmethod
    # # def asDict(cls, vector):
    # #     """Convert an RPy2 ListVector to a Python dict"""
    # #     from rpy2 import robjects
    # #     import types
    # #     result = {}
    # #     for i, name in enumerate(vector.names):
    # #         if isinstance(vector[i], robjects.ListVector):
    # #             result[name] = as_dict(vector[i])
    # #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    # #             result[name] = vector[i][0]
    # #         else:
    # #             result[name] = vector[i]
    # #     return result
    #
    # # @staticmethod
    # # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    # #
    # #     htmlCore = HtmlCore()
    # #     htmlCore.begin()
    # #
    # #     vg = visualizationGraphs()
    # #     rnaSeqDataPlot=[]
    # #     i=0
    # #     if prevChoices.rnaSeqData:
    # #
    # #
    # #
    # #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    # #         data = f.readlines()
    # #         colLen = data[2]
    # #         colLen = len(colLen.strip('\n').split('\t'))
    # #
    # #         col = [w for w in range(2, colLen)]
    # #
    # #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    # #
    # #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    # #         # #     for x in f.readlines():
    # #         # #         if i > 2:
    # #         # #             el = x.strip('\n').split('\t')
    # #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    # #         # #         i+=1
    # #         #
    # #         # #
    # #
    # #
    # #
    # #         #count histoggram
    # #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    # #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    # #         simpleHist = r(rCode)(dd)
    # #         simpleHistDict = geneExpression.asDict(simpleHist)
    # #
    # #
    # #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    # #                                 xAxisRotation=90,
    # #                                 categories=list(simpleHistDict['breaks']),
    # #                                 showInLegend=False,
    # #                                 histogram=True,
    # #                                 height=400
    # #                                 )
    # #         htmlCore.line(res)
    # #
    # #     htmlCore.end()
    # #
    # #     return '', str(res)
    #
    #
    # @staticmethod
    # def getOptionsBoxReference(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxCutOff(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxType(prevChoices):
    #     return ['SMTS', 'SMTSD']

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #
    #     annotation = choices.annotations
    #     rnaSeqData = choices.rnaSeqData
    #     reference = choices.reference
    #
    #     cutoff = choices.cutOff
    #     type = choices.type
    #
    #     if type == 'SMTSD':
    #         nrType = 6
    #     if type == 'SMTS':
    #         nrType = 5
    #
    #
    #     cutoffDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(cutoff.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             el = x.strip('\n').split('\t')
    #             cutoffDict[el[0]] = el[1]
    #
    #
    #     print cutoffDict
    #
    #     annotationDict = {}
    #     i=0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i > 0:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[nrType] in annotationDict:
    #                     annotationDict[el[nrType]]=[]
    #                 if not el[0] in annotationDict[el[nrType]]:
    #                     annotationDict[el[nrType]].append(el[0])
    #             i+=1
    #     i=0
    #
    #     print annotationDict
    #
    #     rnaSeqDataDictList=[]
    #     rnaSeqDataDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i == 2:
    #                 el = x.strip('\n').split('\t')
    #                 header=[]
    #                 for elN in range(2, len(el)):
    #                     header.append(el[elN])
    #                     rnaSeqDataDict[el[elN]]={}
    #                     # for key1 in annotationDict.keys():
    #                     #     rnaSeqDataDict[el[elN]][key1]=[]
    #             if i > 2:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[0] in rnaSeqDataDictList:
    #                     rnaSeqDataDictList.append(el[0])
    #                 for elN in range(2, len(el)):
    #                     for key1, it1 in annotationDict.iteritems():
    #                         for it11 in it1:
    #                             if it11 == header[elN-2]:
    #                                 if key1 not in rnaSeqDataDict[header[elN-2]]:
    #                                     rnaSeqDataDict[header[elN-2]][key1]=[]
    #                                 #if key1 in cutoffDict.keys() and el[elN] >= cutoffDict[key1]:
    #                                 rnaSeqDataDict[header[elN-2]][key1].append(el[0])
    #
    #             i+=1
    #
    #     #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
    #     #rnaSeqDataDictList = list(set(rnaSeqDataDictList))
    #
    #
    #     i=0
    #     filesReferenceDict={}
    #     referenceDict={}
    #
    #     header=[]
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
    #         for x in f.readlines():
    #
    #             if i > 4:
    #
    #                 el = x.strip('\n').split(' ')
    #                 geneID = el[1].replace('"', '').replace(';','')
    #
    #                 elNewDiv = x.strip('\n').split('\t')
    #
    #                 j=0
    #                 xNew=[]
    #                 for elND in elNewDiv:
    #                     if j==0:
    #                         xNew.append('chr' + str(elNewDiv[0]))
    #                     else:
    #                         xNew.append(elND)
    #                     j+=1
    #
    #
    #                 if geneID in rnaSeqDataDictList:
    #                     if not geneID in referenceDict:
    #                         referenceDict[geneID] = []
    #                     referenceDict[geneID].append(i)
    #
    #                     if i not in filesReferenceDict:
    #                         filesReferenceDict[i]=[]
    #                     filesReferenceDict[i].append('\t'.join(xNew))
    #
    #                 # print referenceDict
    #                 # print '\n' + '<br \>'
    #             else:
    #                 header.append(x)
    #             i+=1
    #
    #     # print '\n' + '<br \>'
    #     # print '\n' + '<br \>'
    #     # print referenceDict
    #
    #     #build files and then gSuite
    #
    #     outGSuite = GSuite()
    #     for trackName, it0 in annotationDict.items():
    #         uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
    #                                             extraFileName=trackName,
    #                                             suffix='gff')
    #         gSuiteTrack = GSuiteTrack(uri)
    #         outFn = gSuiteTrack.path
    #         ensurePathExists(outFn)
    #
    #
    #         with open(outFn, 'w') as outFile:
    #             outFile.write(''.join(header))
    #
    #             for it00 in it0:
    #                 if it00 in rnaSeqDataDict:
    #                     for it1 in rnaSeqDataDict[it00][trackName]:
    #                         for it2 in referenceDict[it1]:
    #                             outFile.write(filesReferenceDict[it2][0] + '\n')
    #
    #         outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))
    #
    #     GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])
    #
    #     # trackNameList = [ 'tissue', 'blood']
    #     #
    #     # for trackName in trackNameList:
    #     #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
    #     #     gSuiteTrack = GSuiteTrack(uri)
    #     #     outFn = gSuiteTrack.path
    #     #     ensurePathExists(outFn)
    #     #     line = ['chr1', '10', '200']
    #     #     with open(outFn, 'w') as outFile:
    #     #         outFile.write('\t'.join(line) + '\n')
    #     #
    #     #
    #     #
    #     #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
    #     #     #from quick.util.CommonFunctions import ensurePathExists
    #     #
    #     #     #ensurePathExists(fn)
    #     #
    #     #
    #     #
    #     #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
    #     #
    #     #     trackType = 'segments'
    #     #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
    #     #
    #     #
    #     #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
    #     #
    #     # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])
    #
    # # @staticmethod
    # # def getOutputFormat(choices):
    # #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]




class geneExpressionV3(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression per tissue (new)"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select genome', 'genome'),
                ('Select annotatations', 'annotations'),
                ('Select RNA-Seq Data', 'rnaSeqData'),
                #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
                ('Select reference', 'reference'),
                ('Select file with tissue', 'fileTypeTissue'),
                ('List of possible tissue', 'typeTissue'),
                ('Select cutoff value', 'cutOff'),
                ('Select tissue type', 'type')
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxAnnotations(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxFileTypeTissue(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxTypeTissue(prevChoices):
        listAnswer=OrderedDict()
        if prevChoices.fileTypeTissue:
            fileTissue = prevChoices.fileTypeTissue
            #listAnswer.append(fileTissue)
            with open(ExternalTrackManager.extractFnFromGalaxyTN(fileTissue.split(':')), 'r') as f:
                for x in f.readlines():
                    tissueName  = x.replace('\t','').replace('\n','')
                    if not tissueName in listAnswer:
                        listAnswer[tissueName] = False
        return listAnswer


    @staticmethod
    def getOptionsBoxCutOff(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        rnaSeqData = choices.rnaSeqData
        reference = choices.reference
        typeTissueList = choices.typeTissue
        cutoff = choices.cutOff
        type = choices.type

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5

        #typeTissue = 'Brain - Cortex'


        outGSuite = GSuite()

        for typeTissue, ans in typeTissueList.items():

            if ans == 'True':

                print typeTissue

                annotationDict = {} #tissue -> list of samID
                annotationDict.clear()

                i=0
                with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i > 0:
                            el = x.strip('\n').split('\t')
                            if el[nrType] == typeTissue:
                                if not el[nrType] in annotationDict:
                                    annotationDict[el[nrType]]=[]
                                if not el[0] in annotationDict[el[nrType]]:
                                    annotationDict[el[nrType]].append(el[0])
                        i+=1
                i=0

                print 'annotationDict - done'


                rnaSeqDataDict={}
                rnaSeqDataDict.clear()

                with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i%1000==0:
                            print i
                        if i == 2:
                            el = x.strip('\n').split('\t')
                            header=[]
                            for elN in range(2, len(el)):
                                header.append(el[elN])
                                #rnaSeqDataDict[el[elN]]=[]
                        if i > 2:
                            el = x.strip('\n').split('\t')
                            for elN in range(2, len(el)):
                                if header[elN-2] in annotationDict[typeTissue]:
                                    if el[elN] >= cutoff:
                                        if not header[elN-2] in rnaSeqDataDict:
                                            rnaSeqDataDict[header[elN-2]]=[]
                                        if not el[0] in rnaSeqDataDict[header[elN-2]]:
                                            rnaSeqDataDict[header[elN-2]].append(el[0])
                        i+=1



                print 'rnaSeqDataDict - done'



                rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
                rnaSeqDataDictList = list(set(rnaSeqDataDictList))

                print rnaSeqDataDictList

                print 'rnaSeqDataDictList - done'

                i=0
                filesReferenceDict={}
                filesReferenceDict.clear()
                # referenceDict={}
                # referenceDict.clear()

                header=[]
                with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i%10000==0:
                            print i
                        if i > 4:

                            el = x.strip('\n').split(' ')
                            geneID = el[1].replace('"', '').replace(';','')

                            elNewDiv = x.strip('\n').split('\t')

                            j=0
                            xNew=[]
                            for elND in elNewDiv:
                                if j==0:
                                    xNew.append('chr' + str(elNewDiv[0]))
                                else:
                                    xNew.append(elND)
                                j+=1


                            if geneID in rnaSeqDataDictList:
                                if elNewDiv[2] == 'transcript':
                                    # if not geneID in referenceDict:
                                    #     referenceDict[geneID] = []
                                    # referenceDict[geneID].append(i)

                                    if i not in filesReferenceDict:
                                        filesReferenceDict[i]=[]
                                    filesReferenceDict[i].append('\t'.join(xNew))

                            # print referenceDict
                        else:
                            header.append(x)
                        i+=1

                # print '\n' + '<br \>'
                # print '\n' + '<br \>'

                print 'reference - done'

                #build files and then gSuite


                for trackName, it0 in annotationDict.items():
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                        extraFileName=trackName,
                                                        suffix='gff')
                    gSuiteTrack = GSuiteTrack(uri)
                    outFn = gSuiteTrack.path
                    ensurePathExists(outFn)

                    print str(trackName) + '-' + str(len(it0))
                    with open(outFn, 'w') as outFile:
                        outFile.write(''.join(header))

                        for el in filesReferenceDict:
                            outFile.write(filesReferenceDict[el][0] + '\n')

                    print 'done with' + str(trackName)
                    annotationDict[trackName]=[]


                    outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])

        print 'GSuiteComposer - done'


    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]

    # @staticmethod
    # def getToolName():
    #     return "Gene expression"
    #
    # @staticmethod
    # def getInputBoxNames():
    #     return [
    #             ('Select genome', 'genome'),
    #             ('Select annotatations', 'annotations'),
    #             ('Select RNA-Seq Data', 'rnaSeqData'),
    #             #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
    #             ('Select reference', 'reference'),
    #             ('Select cutoff value', 'cutOff'),
    #             ('Select tissue type', 'type')
    #             ]
    #
    # @staticmethod
    # def getOptionsBoxGenome():
    #     return '__genome__'
    #
    # @staticmethod
    # def getOptionsBoxAnnotations(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxRnaSeqData(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # # @classmethod
    # # def asDict(cls, vector):
    # #     """Convert an RPy2 ListVector to a Python dict"""
    # #     from rpy2 import robjects
    # #     import types
    # #     result = {}
    # #     for i, name in enumerate(vector.names):
    # #         if isinstance(vector[i], robjects.ListVector):
    # #             result[name] = as_dict(vector[i])
    # #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    # #             result[name] = vector[i][0]
    # #         else:
    # #             result[name] = vector[i]
    # #     return result
    #
    # # @staticmethod
    # # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    # #
    # #     htmlCore = HtmlCore()
    # #     htmlCore.begin()
    # #
    # #     vg = visualizationGraphs()
    # #     rnaSeqDataPlot=[]
    # #     i=0
    # #     if prevChoices.rnaSeqData:
    # #
    # #
    # #
    # #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    # #         data = f.readlines()
    # #         colLen = data[2]
    # #         colLen = len(colLen.strip('\n').split('\t'))
    # #
    # #         col = [w for w in range(2, colLen)]
    # #
    # #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    # #
    # #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    # #         # #     for x in f.readlines():
    # #         # #         if i > 2:
    # #         # #             el = x.strip('\n').split('\t')
    # #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    # #         # #         i+=1
    # #         #
    # #         # #
    # #
    # #
    # #
    # #         #count histoggram
    # #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    # #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    # #         simpleHist = r(rCode)(dd)
    # #         simpleHistDict = geneExpression.asDict(simpleHist)
    # #
    # #
    # #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    # #                                 xAxisRotation=90,
    # #                                 categories=list(simpleHistDict['breaks']),
    # #                                 showInLegend=False,
    # #                                 histogram=True,
    # #                                 height=400
    # #                                 )
    # #         htmlCore.line(res)
    # #
    # #     htmlCore.end()
    # #
    # #     return '', str(res)
    #
    #
    # @staticmethod
    # def getOptionsBoxReference(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxCutOff(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxType(prevChoices):
    #     return ['SMTS', 'SMTSD']

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #
    #     annotation = choices.annotations
    #     rnaSeqData = choices.rnaSeqData
    #     reference = choices.reference
    #
    #     cutoff = choices.cutOff
    #     type = choices.type
    #
    #     if type == 'SMTSD':
    #         nrType = 6
    #     if type == 'SMTS':
    #         nrType = 5
    #
    #
    #     cutoffDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(cutoff.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             el = x.strip('\n').split('\t')
    #             cutoffDict[el[0]] = el[1]
    #
    #
    #     print cutoffDict
    #
    #     annotationDict = {}
    #     i=0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i > 0:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[nrType] in annotationDict:
    #                     annotationDict[el[nrType]]=[]
    #                 if not el[0] in annotationDict[el[nrType]]:
    #                     annotationDict[el[nrType]].append(el[0])
    #             i+=1
    #     i=0
    #
    #     print annotationDict
    #
    #     rnaSeqDataDictList=[]
    #     rnaSeqDataDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i == 2:
    #                 el = x.strip('\n').split('\t')
    #                 header=[]
    #                 for elN in range(2, len(el)):
    #                     header.append(el[elN])
    #                     rnaSeqDataDict[el[elN]]={}
    #                     # for key1 in annotationDict.keys():
    #                     #     rnaSeqDataDict[el[elN]][key1]=[]
    #             if i > 2:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[0] in rnaSeqDataDictList:
    #                     rnaSeqDataDictList.append(el[0])
    #                 for elN in range(2, len(el)):
    #                     for key1, it1 in annotationDict.iteritems():
    #                         for it11 in it1:
    #                             if it11 == header[elN-2]:
    #                                 if key1 not in rnaSeqDataDict[header[elN-2]]:
    #                                     rnaSeqDataDict[header[elN-2]][key1]=[]
    #                                 #if key1 in cutoffDict.keys() and el[elN] >= cutoffDict[key1]:
    #                                 rnaSeqDataDict[header[elN-2]][key1].append(el[0])
    #
    #             i+=1
    #
    #     #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
    #     #rnaSeqDataDictList = list(set(rnaSeqDataDictList))
    #
    #
    #     i=0
    #     filesReferenceDict={}
    #     referenceDict={}
    #
    #     header=[]
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
    #         for x in f.readlines():
    #
    #             if i > 4:
    #
    #                 el = x.strip('\n').split(' ')
    #                 geneID = el[1].replace('"', '').replace(';','')
    #
    #                 elNewDiv = x.strip('\n').split('\t')
    #
    #                 j=0
    #                 xNew=[]
    #                 for elND in elNewDiv:
    #                     if j==0:
    #                         xNew.append('chr' + str(elNewDiv[0]))
    #                     else:
    #                         xNew.append(elND)
    #                     j+=1
    #
    #
    #                 if geneID in rnaSeqDataDictList:
    #                     if not geneID in referenceDict:
    #                         referenceDict[geneID] = []
    #                     referenceDict[geneID].append(i)
    #
    #                     if i not in filesReferenceDict:
    #                         filesReferenceDict[i]=[]
    #                     filesReferenceDict[i].append('\t'.join(xNew))
    #
    #                 # print referenceDict
    #                 # print '\n' + '<br \>'
    #             else:
    #                 header.append(x)
    #             i+=1
    #
    #     # print '\n' + '<br \>'
    #     # print '\n' + '<br \>'
    #     # print referenceDict
    #
    #     #build files and then gSuite
    #
    #     outGSuite = GSuite()
    #     for trackName, it0 in annotationDict.items():
    #         uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
    #                                             extraFileName=trackName,
    #                                             suffix='gff')
    #         gSuiteTrack = GSuiteTrack(uri)
    #         outFn = gSuiteTrack.path
    #         ensurePathExists(outFn)
    #
    #
    #         with open(outFn, 'w') as outFile:
    #             outFile.write(''.join(header))
    #
    #             for it00 in it0:
    #                 if it00 in rnaSeqDataDict:
    #                     for it1 in rnaSeqDataDict[it00][trackName]:
    #                         for it2 in referenceDict[it1]:
    #                             outFile.write(filesReferenceDict[it2][0] + '\n')
    #
    #         outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))
    #
    #     GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])
    #
    #     # trackNameList = [ 'tissue', 'blood']
    #     #
    #     # for trackName in trackNameList:
    #     #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
    #     #     gSuiteTrack = GSuiteTrack(uri)
    #     #     outFn = gSuiteTrack.path
    #     #     ensurePathExists(outFn)
    #     #     line = ['chr1', '10', '200']
    #     #     with open(outFn, 'w') as outFile:
    #     #         outFile.write('\t'.join(line) + '\n')
    #     #
    #     #
    #     #
    #     #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
    #     #     #from quick.util.CommonFunctions import ensurePathExists
    #     #
    #     #     #ensurePathExists(fn)
    #     #
    #     #
    #     #
    #     #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
    #     #
    #     #     trackType = 'segments'
    #     #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
    #     #
    #     #
    #     #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
    #     #
    #     # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])
    #
    # # @staticmethod
    # # def getOutputFormat(choices):
    # #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None


    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]



#gSuite of bed files without coutoff value
class geneExpressionV4(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Gene expression per tissue (gSuite)"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select genome', 'genome'),
                ('Select annotatations', 'annotations'),
                ('Select RNA-Seq Data', 'rnaSeqData'),
                ('Select reference', 'reference'),
                ('Select file with tissue', 'fileTypeTissue'),
                ('List of possible tissue', 'typeTissue'),
                ('Select tissue type', 'type')
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxAnnotations(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxRnaSeqData(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxReference(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxFileTypeTissue(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @staticmethod
    def getOptionsBoxTypeTissue(prevChoices):
        listAnswer=OrderedDict()
        if prevChoices.fileTypeTissue:
            fileTissue = prevChoices.fileTypeTissue
            #listAnswer.append(fileTissue)
            with open(ExternalTrackManager.extractFnFromGalaxyTN(fileTissue.split(':')), 'r') as f:
                for x in f.readlines():
                    tissueName  = x.replace('\t','').replace('\n','')
                    if not tissueName in listAnswer:
                        listAnswer[tissueName] = False
        return listAnswer


    @staticmethod
    def getOptionsBoxCutOff(prevChoices):
        return ''

    @staticmethod
    def getOptionsBoxType(prevChoices):
        return ['SMTS', 'SMTSD']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        annotation = choices.annotations
        rnaSeqData = choices.rnaSeqData
        reference = choices.reference
        typeTissueList = choices.typeTissue
        type = choices.type

        if type == 'SMTSD':
            nrType = 6
        if type == 'SMTS':
            nrType = 5

        #typeTissue = 'Brain - Cortex'


        outGSuite = GSuite()

        for typeTissue, ans in typeTissueList.items():

            if ans == 'True':

                print typeTissue

                annotationDict = {} #tissue -> list of samID
                annotationDict.clear()

                i=0
                with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i > 0:
                            el = x.strip('\n').split('\t')
                            if el[nrType] == typeTissue:
                                if not el[nrType] in annotationDict:
                                    annotationDict[el[nrType]]=[]
                                if not el[0] in annotationDict[el[nrType]]:
                                    annotationDict[el[nrType]].append(el[0])
                        i+=1
                i=0

                print 'annotationDict - done'

                #print annotationDict

                rnaSeqDataDictList=[]
                rnaSeqDataDict={}
                rnaSeqDataDict.clear()

                with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i%1000==0:
                            print i
                        if i == 2:
                            el = x.strip('\n').split('\t')
                            header=[]
                            for elN in range(2, len(el)):
                                header.append(el[elN])
                                #rnaSeqDataDict[el[elN]]=[]
                        if i > 2:
                            el = x.strip('\n').split('\t')
                            for elN in range(2, len(el)):
                                if header[elN-2] in annotationDict[typeTissue]:
                                    #if el[elN] >= cutoff:
                                    if not el[0] in rnaSeqDataDict:
                                        rnaSeqDataDict[el[0]]=[]
                                        rnaSeqDataDictList.append(el[0])
                                         
                                    rnaSeqDataDict[el[0]].append(float(el[elN]))
                                        
                                        
#                                     if not header[elN-2] in rnaSeqDataDict:
#                                         rnaSeqDataDict[header[elN-2]]=[]
#                                         
#                                     if not el[0] in rnaSeqDataDict[header[elN-2]]:
#                                         rnaSeqDataDict[header[elN-2]].append([el[0], el[elN]])
#                                         rnaSeqDataDictList.append(el[0])
                        i+=1



                print 'rnaSeqDataDict - done'
                #print rnaSeqDataDict


                #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
                #rnaSeqDataDictList = list(set(rnaSeqDataDictList))

                #print rnaSeqDataDictList

                print 'rnaSeqDataDictList - done'

                i=0
                filesReferenceDict={}
                filesReferenceDict.clear()
                # referenceDict={}
                # referenceDict.clear()

                header=[]
                with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
                    for x in f.readlines():
                        if i%10000==0:
                            print i
                        if i > 4:

                            el = x.strip('\n').split(' ')
                            geneID = el[1].replace('"', '').replace(';','')

                            elNewDiv = x.strip('\n').split('\t')
                            
                            
                            xNew=[]
                            
                            xNew.append('chr' + str(elNewDiv[0]))
                            xNew.append(elNewDiv[3])
                            xNew.append(elNewDiv[4])
                            
                            avgVal = float(sum(rnaSeqDataDict[geneID])/float(len(rnaSeqDataDict[geneID])))
                            xNew.append(str(geneID) + '---' + str(avgVal))
                            

                            if geneID in rnaSeqDataDictList:
                                if elNewDiv[2] == 'transcript':
                                    # if not geneID in referenceDict:
                                    #     referenceDict[geneID] = []
                                    # referenceDict[geneID].append(i)

                                    if i not in filesReferenceDict:
                                        filesReferenceDict[i]=[]
                                    filesReferenceDict[i].append('\t'.join(xNew))

                            # print referenceDict
                        else:
                            pass
                            #header.append(x)
                        i+=1

                # print '\n' + '<br \>'
                # print '\n' + '<br \>'

                print 'reference - done'

                #build files and then gSuite


                for trackName, it0 in annotationDict.items():
                    uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                        extraFileName=trackName,
                                                        suffix='bed')
                    gSuiteTrack = GSuiteTrack(uri)
                    outFn = gSuiteTrack.path
                    ensurePathExists(outFn)

                    print str(trackName) + '-' + str(len(it0))
                    with open(outFn, 'w') as outFile:
                        outFile.write(''.join(header))

                        for el in filesReferenceDict:
                            outFile.write(filesReferenceDict[el][0] + '\n')

                    print 'done with' + str(trackName)
                    annotationDict[trackName]=[]


                    outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])

        print 'GSuiteComposer - done'


    @staticmethod
    def validateAndReturnErrors(choices):
        return None

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]

    # @staticmethod
    # def getToolName():
    #     return "Gene expression"
    #
    # @staticmethod
    # def getInputBoxNames():
    #     return [
    #             ('Select genome', 'genome'),
    #             ('Select annotatations', 'annotations'),
    #             ('Select RNA-Seq Data', 'rnaSeqData'),
    #             #('RNA-Seq Data Histogram', 'rnaSeqDataPlot'),
    #             ('Select reference', 'reference'),
    #             ('Select cutoff value', 'cutOff'),
    #             ('Select tissue type', 'type')
    #             ]
    #
    # @staticmethod
    # def getOptionsBoxGenome():
    #     return '__genome__'
    #
    # @staticmethod
    # def getOptionsBoxAnnotations(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxRnaSeqData(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # # @classmethod
    # # def asDict(cls, vector):
    # #     """Convert an RPy2 ListVector to a Python dict"""
    # #     from rpy2 import robjects
    # #     import types
    # #     result = {}
    # #     for i, name in enumerate(vector.names):
    # #         if isinstance(vector[i], robjects.ListVector):
    # #             result[name] = as_dict(vector[i])
    # #         elif type(vector[i]) != types.BooleanType and len(vector[i]) == 1:
    # #             result[name] = vector[i][0]
    # #         else:
    # #             result[name] = vector[i]
    # #     return result
    #
    # # @staticmethod
    # # def getOptionsBoxRnaSeqDataPlot(prevChoices):
    # #
    # #     htmlCore = HtmlCore()
    # #     htmlCore.begin()
    # #
    # #     vg = visualizationGraphs()
    # #     rnaSeqDataPlot=[]
    # #     i=0
    # #     if prevChoices.rnaSeqData:
    # #
    # #
    # #
    # #         f = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r')
    # #         data = f.readlines()
    # #         colLen = data[2]
    # #         colLen = len(colLen.strip('\n').split('\t'))
    # #
    # #         col = [w for w in range(2, colLen)]
    # #
    # #         # #rnaSeqDataPlot = pd.read_csv(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), sep='\t', skiprows=2, header=2)
    # #
    # #         # # with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), 'r') as f:
    # #         # #     for x in f.readlines():
    # #         # #         if i > 2:
    # #         # #             el = x.strip('\n').split('\t')
    # #         # #             rnaSeqDataPlot.append(el[2:len(el)])
    # #         # #         i+=1
    # #         #
    # #         # #
    # #
    # #
    # #
    # #         #count histoggram
    # #         rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
    # #         dd=robjects.FloatVector(list(itertools.chain.from_iterable(np.loadtxt(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.rnaSeqData.split(':')), skiprows=3, usecols=col))))
    # #         simpleHist = r(rCode)(dd)
    # #         simpleHistDict = geneExpression.asDict(simpleHist)
    # #
    # #
    # #         res = vg.drawColumnChart(list(simpleHistDict['counts']),
    # #                                 xAxisRotation=90,
    # #                                 categories=list(simpleHistDict['breaks']),
    # #                                 showInLegend=False,
    # #                                 histogram=True,
    # #                                 height=400
    # #                                 )
    # #         htmlCore.line(res)
    # #
    # #     htmlCore.end()
    # #
    # #     return '', str(res)
    #
    #
    # @staticmethod
    # def getOptionsBoxReference(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxCutOff(prevChoices):
    #     return GeneralGuiTool.getHistorySelectionElement()
    #
    # @staticmethod
    # def getOptionsBoxType(prevChoices):
    #     return ['SMTS', 'SMTSD']

    # @classmethod
    # def execute(cls, choices, galaxyFn=None, username=''):
    #
    #     annotation = choices.annotations
    #     rnaSeqData = choices.rnaSeqData
    #     reference = choices.reference
    #
    #     cutoff = choices.cutOff
    #     type = choices.type
    #
    #     if type == 'SMTSD':
    #         nrType = 6
    #     if type == 'SMTS':
    #         nrType = 5
    #
    #
    #     cutoffDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(cutoff.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             el = x.strip('\n').split('\t')
    #             cutoffDict[el[0]] = el[1]
    #
    #
    #     print cutoffDict
    #
    #     annotationDict = {}
    #     i=0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(annotation.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i > 0:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[nrType] in annotationDict:
    #                     annotationDict[el[nrType]]=[]
    #                 if not el[0] in annotationDict[el[nrType]]:
    #                     annotationDict[el[nrType]].append(el[0])
    #             i+=1
    #     i=0
    #
    #     print annotationDict
    #
    #     rnaSeqDataDictList=[]
    #     rnaSeqDataDict={}
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(rnaSeqData.split(':')), 'r') as f:
    #         for x in f.readlines():
    #             if i == 2:
    #                 el = x.strip('\n').split('\t')
    #                 header=[]
    #                 for elN in range(2, len(el)):
    #                     header.append(el[elN])
    #                     rnaSeqDataDict[el[elN]]={}
    #                     # for key1 in annotationDict.keys():
    #                     #     rnaSeqDataDict[el[elN]][key1]=[]
    #             if i > 2:
    #                 el = x.strip('\n').split('\t')
    #                 if not el[0] in rnaSeqDataDictList:
    #                     rnaSeqDataDictList.append(el[0])
    #                 for elN in range(2, len(el)):
    #                     for key1, it1 in annotationDict.iteritems():
    #                         for it11 in it1:
    #                             if it11 == header[elN-2]:
    #                                 if key1 not in rnaSeqDataDict[header[elN-2]]:
    #                                     rnaSeqDataDict[header[elN-2]][key1]=[]
    #                                 #if key1 in cutoffDict.keys() and el[elN] >= cutoffDict[key1]:
    #                                 rnaSeqDataDict[header[elN-2]][key1].append(el[0])
    #
    #             i+=1
    #
    #     #rnaSeqDataDictList = list(itertools.chain.from_iterable(rnaSeqDataDict.values()))
    #     #rnaSeqDataDictList = list(set(rnaSeqDataDictList))
    #
    #
    #     i=0
    #     filesReferenceDict={}
    #     referenceDict={}
    #
    #     header=[]
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(reference.split(':')), 'r') as f:
    #         for x in f.readlines():
    #
    #             if i > 4:
    #
    #                 el = x.strip('\n').split(' ')
    #                 geneID = el[1].replace('"', '').replace(';','')
    #
    #                 elNewDiv = x.strip('\n').split('\t')
    #
    #                 j=0
    #                 xNew=[]
    #                 for elND in elNewDiv:
    #                     if j==0:
    #                         xNew.append('chr' + str(elNewDiv[0]))
    #                     else:
    #                         xNew.append(elND)
    #                     j+=1
    #
    #
    #                 if geneID in rnaSeqDataDictList:
    #                     if not geneID in referenceDict:
    #                         referenceDict[geneID] = []
    #                     referenceDict[geneID].append(i)
    #
    #                     if i not in filesReferenceDict:
    #                         filesReferenceDict[i]=[]
    #                     filesReferenceDict[i].append('\t'.join(xNew))
    #
    #                 # print referenceDict
    #                 # print '\n' + '<br \>'
    #             else:
    #                 header.append(x)
    #             i+=1
    #
    #     # print '\n' + '<br \>'
    #     # print '\n' + '<br \>'
    #     # print referenceDict
    #
    #     #build files and then gSuite
    #
    #     outGSuite = GSuite()
    #     for trackName, it0 in annotationDict.items():
    #         uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
    #                                             extraFileName=trackName,
    #                                             suffix='gff')
    #         gSuiteTrack = GSuiteTrack(uri)
    #         outFn = gSuiteTrack.path
    #         ensurePathExists(outFn)
    #
    #
    #         with open(outFn, 'w') as outFile:
    #             outFile.write(''.join(header))
    #
    #             for it00 in it0:
    #                 if it00 in rnaSeqDataDict:
    #                     for it1 in rnaSeqDataDict[it00][trackName]:
    #                         for it2 in referenceDict[it1]:
    #                             outFile.write(filesReferenceDict[it2][0] + '\n')
    #
    #         outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), genome=choices.genome))
    #
    #     GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene expression GSuite'])
    #
    #     # trackNameList = [ 'tissue', 'blood']
    #     #
    #     # for trackName in trackNameList:
    #     #     uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=trackName)
    #     #     gSuiteTrack = GSuiteTrack(uri)
    #     #     outFn = gSuiteTrack.path
    #     #     ensurePathExists(outFn)
    #     #     line = ['chr1', '10', '200']
    #     #     with open(outFn, 'w') as outFile:
    #     #         outFile.write('\t'.join(line) + '\n')
    #     #
    #     #
    #     #
    #     #     #staticFile = HbGSuiteTrack.generateURI(trackName=[trackName])
    #     #     #from quick.util.CommonFunctions import ensurePathExists
    #     #
    #     #     #ensurePathExists(fn)
    #     #
    #     #
    #     #
    #     #     #trackType = TrackInfo(choices.genome, trackName).trackFormatName.lower()
    #     #
    #     #     trackType = 'segments'
    #     #     #hbUri = HbGSuiteTrack.generateURI(trackName=trackName)
    #     #
    #     #
    #     #     outGSuite.addTrack(GSuiteTrack(uri, title=''.join(trackName), trackType=trackType, genome=choices.genome))
    #     #
    #     # GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['gene eGSuite'])
    #
    # # @staticmethod
    # # def getOutputFormat(choices):
    # #     return 'customhtml'

    @staticmethod
    def validateAndReturnErrors(choices):
        return None


    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('gene expression GSuite', 'gsuite')]


class rankingTFtracks2(GeneralGuiTool, UserBinMixin):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make ranking for TFs using permutation test"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select target track collection GSuite','gSuiteFirst')
                ] + UserBinMixin.getUserBinInputBoxNames()


    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')


    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        i=0
        for x in targetGSuite.allTracks():
            if i==0:
                analysisBins = GlobalBinSource(x.genome)
#                 analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, x.genome)

        tracks = [Track(x.trackName) for x in targetGSuite.allTracks()]
        results = doAnalysis(AnalysisSpec(SumTrackPointsStat), analysisBins, tracks)
        print results

            #resultDict = results.getGlobalResult()

    @staticmethod
    def _getGenome(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.genome

    @staticmethod
    def _getTrackName1(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.allTracks().next().trackName

    @staticmethod
    def _getTrackName2(choices):
        return None

    @classmethod
    def getToolDescription(cls):
        return ''

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


class mRNATool(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Show heatmap with correlation"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select matures','mature'),
                ('Select precursor','precursor'),
                ('Select files','files')
                ]

    @staticmethod
    def getOptionsBoxMature():
        return GeneralGuiTool.getHistorySelectionElement('txt')
          
    @staticmethod
    def getOptionsBoxPrecursor(prevChoices):            
        return GeneralGuiTool.getHistorySelectionElement('txt')
    
    @staticmethod
    def getOptionsBoxFiles(prevChoices):            
        return ('__multihistory__', 'sam')
    
    
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        from quick.webtools.restricted.DianasTool2 import calculationPS
        
        print choices.files
        print choices.mature
        print choices.precursor
        
        
        cps = calculationPS(choices.files, choices.mature, choices.precursor)
        
        cps.calcRes()
             
            
        
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
   
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'

class rankingTFtracks2(GeneralGuiTool, UserBinMixin):
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make ranking for TFs using permutation test"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select target track collection GSuite','gSuiteFirst')
                ] + UserBinMixin.getUserBinInputBoxNames()


    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

  
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        
        i=0
        for x in targetGSuite.allTracks():
            if i==0:
                analysisBins = GlobalBinSource(x.genome)
#                 analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, x.genome)

        tracks = [Track(x.trackName) for x in targetGSuite.allTracks()]
        results = doAnalysis(AnalysisSpec(SumTrackPointsStat), analysisBins, tracks)
        print results
            
            #resultDict = results.getGlobalResult()
        
    @staticmethod
    def _getGenome(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.genome

    @staticmethod
    def _getTrackName1(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.allTracks().next().trackName

    @staticmethod
    def _getTrackName2(choices):
        return None

    @classmethod
    def getToolDescription(cls):
        return ''
  
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
    
class rankingTFtracks(GeneralGuiTool, UserBinMixin):

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make ranking for all possibilities"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select target track collection GSuite','gSuiteFirst'),
                ('Select reference track collection GSuite', 'gSuiteSecond'),
                ('Select statistic', 'statistic'),
                ('Select overlap handling', 'intraOverlap')
                ] + UserBinMixin.getUserBinInputBoxNames()


    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices): # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        return [
#                 STAT_OVERLAP_COUNT_BPS,
#                 STAT_OVERLAP_RATIO,
#                 STAT_FACTOR_OBSERVED_VS_EXPECTED,
#                 STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                STAT_COVERAGE_RATIO_VS_REF_TRACK
                ]

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [rankingTFtracks.MERGE_INTRA_OVERLAPS,
                 rankingTFtracks.ALLOW_MULTIPLE_OVERLAP]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)


        if choices.intraOverlap == rankingTFtracks.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()
        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    result = rankingTFtracks.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False).getGlobalResult()
                if targetTrackName not in results :
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = choices.statistic
        statIndex = STAT_LIST_INDEX[stat]
        title = 'Ranking for  (' + stat + ')'

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)
        
        transposedProcessedResults = [list(x) for x in zip(*processedResults)]
        
        input = targetGSuite.allTrackTitles()
        ref = transposedProcessedResults
        
        
        from itertools import combinations
        
#         #header = ['Track', 'Track number', 'Ranking']
#         #outputRes=[]
#         writeFile = open(galaxyFn,'w')  
#         writeFile.write('Track' + '\t' + 'Track number'  + '\t' +  'Ranking'  + '\n')
#         
#         for i in range(len(input) + 1):
#             output =  map(list, combinations(input, i))
#             for el in output:
#                 if len(el)!=0:
#                     outputResPart = 1
#                     outputTrackNum = ''
#                     outputHeaderPart = ''
#                     for elN in range(0, len(el)):
#                         outputHeaderPart += str(el[elN]) + ', '
#                         outputTrackNum += str(input.index(el[elN])) + ', '
#                         outputResPart *= ref[0][input.index(el[elN])]
#                     #outputRes.append([outputHeaderPart, outputTrackNum, outputResPart])
#                     writeFile.write(str(outputHeaderPart) + '\t' +  str(outputTrackNum) + '\t' + str(outputResPart) + '\n')
        
        outputHeaderPart1 = ''
        outputTrackNum1 = ''
        outputResPart1 = -100
        
        writeFile = open(galaxyFn,'w')  
        writeFile.write('Track' + '\t' + 'Track number'  + '\t' +  'Ranking'  + '\n')
        for i in range(len(input) + 1):
            output =  map(list, combinations(input, i))
            for el in output:
                if len(el)!=0:
                    outputResPart = 1
                    outputTrackNum = ''
                    outputHeaderPart = ''
                    for elN in range(0, len(el)):
                        outputHeaderPart += str(el[elN]) + ', '
                        outputTrackNum += str(input.index(el[elN])) + ', '
                        outputResPart *= ref[0][input.index(el[elN])]
                    
                    if outputResPart1 < outputResPart:
                        outputResPart1=outputResPart
                        outputTrackNum1 = outputTrackNum
                        outputHeaderPart1 = outputHeaderPart
                            
                    
        #outputRes.append([outputHeaderPart1, outputTrackNum1, outputResPart1])
        writeFile.write(str(outputHeaderPart1) + '\t' +  str(outputTrackNum1) + '\t' + str(outputResPart1) + '\n')
   
#         htmlCore = HtmlCore()
#         htmlCore.begin()
#         htmlCore.header(title)
#         htmlCore.divBegin('resultsDiv')
#         htmlCore.tableHeader(header, sortable=True, tableId='resultsTable')
#         for line in outputRes:
#             htmlCore.tableLine(line)
#         htmlCore.tableFooter()
#         htmlCore.divEnd()

        #hicharts can't handle strings that contain ' or " as input for series names
#         targetTrackNames = [x.replace('\'', '').replace('"','') for x in targetGSuite.allTrackTitles()]
#         refTrackNames = [x.replace('\'', '').replace('"','') for x in refGSuite.allTrackTitles()]
        
        

        
        
#         from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
#         vg = visualizationGraphs()
#         result = vg.drawColumnChart(processedResults,
#                       height=600,
#                       yAxisTitle=stat,
#                       categories=refTrackNames,
#                       xAxisRotation=90,
#                       seriesName=targetTrackNames,
#                       shared=False,
#                       titleText=title + ' plot',
#                       overMouseAxisX=True,
#                       overMouseLabelX = ' + this.value.substring(0, 10) +')
#         htmlCore.line(vg.visualizeResults(result, htmlCore))
#         
#         htmlCore.hideToggle(styleClass='debug')
#         htmlCore.end()
        
#         htmlCore.hideToggle(styleClass='debug')
#         htmlCore.end()
#         
#         print htmlCore
        
    @staticmethod
    def _getGenome(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.genome

    @staticmethod
    def _getTrackName1(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.allTracks().next().trackName

    @staticmethod
    def _getTrackName2(choices):
        return None

    @classmethod
    def getToolDescription(cls):
        return ''
  
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'txt'

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):
        
        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)
        
        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()


class rankingTFtracks3(GeneralGuiTool, UserBinMixin):

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make TF bp overlapping"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select target track collection GSuite','gSuiteFirst'),
                ('Select reference track collection GSuite', 'gSuiteSecond'),
                ('Select statistic', 'statistic'),
                ('Select overlap handling', 'intraOverlap')
                ] + UserBinMixin.getUserBinInputBoxNames()


    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices): # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        return [
#                 STAT_OVERLAP_COUNT_BPS,
#                 STAT_OVERLAP_RATIO,
#                 STAT_FACTOR_OBSERVED_VS_EXPECTED,
#                 STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                STAT_COVERAGE_RATIO_VS_REF_TRACK
                ]

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [rankingTFtracks.MERGE_INTRA_OVERLAPS,
                 rankingTFtracks.ALLOW_MULTIPLE_OVERLAP]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)


        if choices.intraOverlap == rankingTFtracks.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()
        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    result = rankingTFtracks.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False).getGlobalResult()
                if targetTrackName not in results :
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = choices.statistic
        statIndex = STAT_LIST_INDEX[stat]
        title = 'Ranking for  (' + stat + ')'

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)
        
        transposedProcessedResults = [list(x) for x in zip(*processedResults)]
        
        input = targetGSuite.allTrackTitles()
        ref = transposedProcessedResults
        
        
        from itertools import combinations
        
#         #header = ['Track', 'Track number', 'Ranking']
#         #outputRes=[]
#         writeFile = open(galaxyFn,'w')  
#         writeFile.write('Track' + '\t' + 'Track number'  + '\t' +  'Ranking'  + '\n')
#         
#         for i in range(len(input) + 1):
#             output =  map(list, combinations(input, i))
#             for el in output:
#                 if len(el)!=0:
#                     outputResPart = 1
#                     outputTrackNum = ''
#                     outputHeaderPart = ''
#                     for elN in range(0, len(el)):
#                         outputHeaderPart += str(el[elN]) + ', '
#                         outputTrackNum += str(input.index(el[elN])) + ', '
#                         outputResPart *= ref[0][input.index(el[elN])]
#                     #outputRes.append([outputHeaderPart, outputTrackNum, outputResPart])
#                     writeFile.write(str(outputHeaderPart) + '\t' +  str(outputTrackNum) + '\t' + str(outputResPart) + '\n')
        
        outputHeaderPart1 = ''
        outputTrackNum1 = ''
        outputResPart1 = -100
        
        writeFile = open(galaxyFn,'w')  
        writeFile.write('Track' + '\t' + 'Track number'  + '\t' +  'Ranking'  + '\n')
        for i in range(len(input) + 1):
            output =  map(list, combinations(input, i))
            for el in output:
                if len(el)!=0:
                    outputResPart = 1
                    outputTrackNum = ''
                    outputHeaderPart = ''
                    for elN in range(0, len(el)):
                        outputHeaderPart += str(el[elN]) + ', '
                        outputTrackNum += str(input.index(el[elN])) + ', '
                        outputResPart *= ref[0][input.index(el[elN])]
                    
                    if outputResPart1 < outputResPart:
                        outputResPart1=outputResPart
                        outputTrackNum1 = outputTrackNum
                        outputHeaderPart1 = outputHeaderPart
                            
                    
        #outputRes.append([outputHeaderPart1, outputTrackNum1, outputResPart1])
        writeFile.write(str(outputHeaderPart1) + '\t' +  str(outputTrackNum1) + '\t' + str(outputResPart1) + '\n')
   
#         htmlCore = HtmlCore()
#         htmlCore.begin()
#         htmlCore.header(title)
#         htmlCore.divBegin('resultsDiv')
#         htmlCore.tableHeader(header, sortable=True, tableId='resultsTable')
#         for line in outputRes:
#             htmlCore.tableLine(line)
#         htmlCore.tableFooter()
#         htmlCore.divEnd()

        #hicharts can't handle strings that contain ' or " as input for series names
#         targetTrackNames = [x.replace('\'', '').replace('"','') for x in targetGSuite.allTrackTitles()]
#         refTrackNames = [x.replace('\'', '').replace('"','') for x in refGSuite.allTrackTitles()]
        
        

        
        
#         from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
#         vg = visualizationGraphs()
#         result = vg.drawColumnChart(processedResults,
#                       height=600,
#                       yAxisTitle=stat,
#                       categories=refTrackNames,
#                       xAxisRotation=90,
#                       seriesName=targetTrackNames,
#                       shared=False,
#                       titleText=title + ' plot',
#                       overMouseAxisX=True,
#                       overMouseLabelX = ' + this.value.substring(0, 10) +')
#         htmlCore.line(vg.visualizeResults(result, htmlCore))
#         
#         htmlCore.hideToggle(styleClass='debug')
#         htmlCore.end()
        
#         htmlCore.hideToggle(styleClass='debug')
#         htmlCore.end()
#         
#         print htmlCore
        
    @staticmethod
    def _getGenome(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.genome

    @staticmethod
    def _getTrackName1(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.allTracks().next().trackName

    @staticmethod
    def _getTrackName2(choices):
        return None

    @classmethod
    def getToolDescription(cls):
        return ''
  
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'txt'

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):
        
        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)
        
        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()
        




class miRNAPrecursors(GeneralGuiTool, UserBinMixin):

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Screen two track collections (precursors)"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select target track collection GSuite','gSuiteFirst'),
                ('Select reference track collection GSuite', 'gSuiteSecond'),
                ('Select statistic', 'statistic'),
                ('Select overlap handling', 'intraOverlap')
                ] + UserBinMixin.getUserBinInputBoxNames()


    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices): # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxStatistic(prevChoices):
        return [STAT_OVERLAP_COUNT_BPS,
                STAT_OVERLAP_RATIO,
                STAT_FACTOR_OBSERVED_VS_EXPECTED,
                STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
                STAT_COVERAGE_RATIO_VS_REF_TRACK
                ]

    @staticmethod
    def getOptionsBoxIntraOverlap(prevChoices):
        return [miRNAPrecursors.MERGE_INTRA_OVERLAPS,
                 miRNAPrecursors.ALLOW_MULTIPLE_OVERLAP]

    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)


        if choices.intraOverlap == miRNAPrecursors.MERGE_INTRA_OVERLAPS:
            analysisDef = 'dummy -> RawOverlapStat'
        else:
            analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()
        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    result = miRNAPrecursors.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False).getGlobalResult()
                if targetTrackName not in results :
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = choices.statistic
        statIndex = STAT_LIST_INDEX[stat]
        title = 'Screening track collections  (' + stat + ')'

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)

        transposedProcessedResults = [list(x) for x in zip(*processedResults)]

        tableHeader = ['Track names'] + targetGSuite.allTrackTitles()
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(tableHeader, sortable=True, tableId='resultsTable')
        for i, row in enumerate(transposedProcessedResults):
            line = [headerColumn[i]] + [strWithStdFormatting(x) for x in row]
            htmlCore.tableLine(line)
        htmlCore.tableFooter()
        htmlCore.divEnd()

        #hicharts can't handle strings that contain ' or " as input for series names
        targetTrackNames = [x.replace('\'', '').replace('"','') for x in targetGSuite.allTrackTitles()]
        refTrackNames = [x.replace('\'', '').replace('"','') for x in refGSuite.allTrackTitles()]

        '''
        addColumnPlotToHtmlCore(htmlCore, targetTrackNames, refTrackNames,
                                stat, title + ' plot',
                                processedResults, xAxisRotation = -45, height=800)
        '''
        '''
        addPlotToHtmlCore(htmlCore, targetTrackNames, refTrackNames,
                                stat, title + ' plot',
                                processedResults, xAxisRotation = -45, height=400)
        '''
        
        from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
        vg = visualizationGraphs()
        result = vg.drawColumnChart(processedResults,
                      height=600,
                      yAxisTitle=stat,
                      categories=refTrackNames,
                      xAxisRotation=90,
                      seriesName=targetTrackNames,
                      shared=False,
                      titleText=title + ' plot',
                      overMouseAxisX=True,
                      overMouseLabelX = ' + this.value.substring(0, 10) +')
        htmlCore.line(vg.visualizeResults(result, htmlCore))
        
        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()

        print htmlCore
        
    @staticmethod
    def _getGenome(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.genome

    @staticmethod
    def _getTrackName1(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.allTracks().next().trackName

    @staticmethod
    def _getTrackName2(choices):
        return None

    @classmethod
    def getToolDescription(cls):
        core = HtmlCore()

        core.paragraph('The tool provides screening of two track collections '
                       '(GSuite files) against each other. The input for the tool are '
                       'two GSuite files, a target and a reference one, that contain '
                       'one or more tracks each.')

        core.paragraph('To run the tool, follow these steps:')

        core.orderedList(['Select two track collections (GSuite files) from history.'
                          'Select the desired statistic that you want to be calculated '
                          'for each track pair.'
                          'Select the genome region for the anaysis',
                          'Click "Execute"'])

        core.paragraph('The results are presented in a sortable table and an interactive chart.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)

  
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

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):
        
        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)
        
        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()
        
class makeRainfallPlots(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Make rainfall plots based on gSuite"
    
    @staticmethod
    def getInputBoxNames():
        return [
                ('Select gsuite','gSuite'),
                ('Select option', 'color'),
                ('Select type of results', 'interactive'),
                ('Select type of plotting', 'multiPlot'),
                ('Select scale for bps value', 'scale'),
                ('Select bps (10000)', 'bps')
                ]
    
    @staticmethod
    def getOptionsBoxGSuite():
        return '__history__', 'gsuite'
    
    @staticmethod
    def getOptionsBoxColor(prevChoices):
        return ['Single color', 'Various colors']
    
    @staticmethod
    def getOptionsBoxInteractive(prevChoices):
        return ['Interactive', 'Figure']


    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single', 'Multi']
    
    @staticmethod
    def getOptionsBoxScale(prevChoices):
        return ['Linear', 'Log']


    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return ''

    @classmethod
    def drawInteractiveSingle(cls, seriesNameRes, listRes, listResLine, listResBubble):
        vg = visualizationGraphs()
        res = vg.drawScatterChart(
             [listRes],
             seriesName = ['All Series'],
             #titleText = ['Scatter plot'],
             label = '<b>{series.name}</b>: {point.x} {point.y}',
             height = 300,
             
             markerRadius=1,
             xAxisTitle = 'chr start pos',
             yAxisTitle = 'distance',
             marginTop=30
             )
        res += vg.drawLineChart(
             listResLine,
             seriesName = seriesNameRes,
             #label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
             height = 300,
             xAxisTitle = 'chr start pos',
             yAxisTitle = 'values',
             marginTop=30
             )
        res += vg.drawBubbleChart(
             [listResBubble],
             seriesName = ['All Series'],
             label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
             height = 300,
             xAxisTitle = 'chr start pos',
             yAxisTitle = 'distance',
             marginTop=30
             )
        return res


    @classmethod
    def drawInteractiveVariousColor(cls, seriesNameRes, listRes, listResLine, listResBubble):
        vg = visualizationGraphs()
        res = vg.drawScatterChart(
            listRes,
            seriesName = seriesNameRes,
            #titleText = ['Scatter plot'],
            label = '<b>{series.name}</b>: {point.x} {point.y}',
            height = 300,
            
            markerRadius=1,
            xAxisTitle = 'chr start pos',
            yAxisTitle = 'distance',
            marginTop=30
            )


        res += vg.drawLineChart(
            listResLine,
            seriesName = seriesNameRes,
            #label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
            height = 300,
            xAxisTitle = 'chr start pos',
            yAxisTitle = 'values',
            marginTop=30
            )

        res += vg.drawBubbleChart(
            listResBubble,
            seriesName = seriesNameRes,
            label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
            height = 300,
            xAxisTitle = 'chr start pos',
            yAxisTitle = 'distance',
            marginTop=30
            )
        return res


    @classmethod
    def drawInteractiveMulti(cls, listResLine, elementOrder, listResCopy, seriesNameRes, listResBubble, bps, scale,chrStPos):
        vg = visualizationGraphs()
        percentagePlot = str(int(float(100)/float(len(listResLine)))) + '%'
        #percentagePlot = '800px'

        res=''

        #elementOrder=[0,1,2,3]

        listMaxVal = []
        for elCount in elementOrder:
            lmax = -10000
            lmin = 10000000000000000
            for elN in range(0, len(listResCopy[elCount])):
                if listResCopy[elCount][elN][0] > lmax:
                    lmax = listResCopy[elCount][elN][0]
                if listResCopy[elCount][elN][0] < lmin:
                    lmin = listResCopy[elCount][elN][0]
            listMaxVal.append([lmin, lmax])

        # print listMaxVal
        # print '========'
        # print listResCopy[0]
        #
        # print '----'

        # print str(listMaxVal)+ '<br \>'

        listResBubbleX={}
        howManyPerBin=OrderedDict()
        j=0
        for elCount in elementOrder:
            listResBubbleX[elCount]={}

            for elN in range(0, len(listResCopy[elCount])):
                if not listResCopy[elCount][elN][0] in listResBubbleX[elCount]:
                    listResBubbleX[elCount][listResCopy[elCount][elN][0]]=0
                listResBubbleX[elCount][listResCopy[elCount][elN][0]]+=1


            if not elCount in howManyPerBin:
                howManyPerBin[elCount]=[]

            lmin = int(math.floor(listMaxVal[j][0])/bps)
            lmax = int(math.ceil(listMaxVal[j][1])/bps) + 1

            addValue=0
            if elCount!=0:
                for elM in range(0, elCount):
                    addValue += listMaxVal[elM][1]

            for vv in range(lmin, lmax):


                binStart = vv * bps
                binEnd = vv * bps + bps
                endCount = binEnd-1



                valueCount = 0
                # print 'binStart: ' + str(binStart) + '<br \>'
                # print 'binEnd: ' + str(binEnd) + '<br \>'
                # print 'valueCount1: ' + str(valueCount) + '<br \>'



                for elN in range(0, len(listResCopy[elCount])):

                    val = listResCopy[elCount][elN][0]
                    if val >= binStart and val < binEnd:
                        # print 'val: ' + str(binStart) + '<br \>'
                        valueCount += 1

                # print 'valueCount2: ' + str(valueCount) + '<br \>'
                howManyPerBin[elCount].append([binStart+addValue, valueCount])
                howManyPerBin[elCount].append([endCount+addValue, valueCount])
                valueCount = 0
            j+=1


        listResBubble=OrderedDict()
        for elCount in elementOrder:
            listResBubble[elCount]=[]
            for elN in range(0, len(listResCopy[elCount])):

                addValue=0
                if elCount!=0:
                    for elM in range(0, elCount):
                        addValue += listMaxVal[elM][1]
                vLog = 0
                if listResCopy[elCount][elN][1]> 0:
                    vLog = math.log(listResCopy[elCount][elN][1],10)
                listResBubble[elCount].append([listResCopy[elCount][elN][0]+addValue, vLog, listResBubbleX[elCount][listResCopy[elCount][elN][0]]])


        #
        # howManyPerBin2=OrderedDict()
        # j=0
        # for elCount in elementOrder:
        #     if not elCount in howManyPerBin2:
        #         howManyPerBin2[elCount]=[]
        #
        #     lmin = int(math.floor(listMaxVal[j][0]))
        #     lmax = int(math.ceil(listMaxVal[j][1])) + 1
        #
        #     print 'lmin: ' + str(lmin) + '<br \>'
        #     print 'lmax: ' + str(lmax) + '<br \>'
        #
        #     for vv in range(lmin, lmax):
        #
        #
        #         binStart = vv #1mln - 1mln+1
        #         binEnd =  vv + bps #1mln + 1 - 1mln+2
        #         endCount = binEnd-1
        #
        #         addValue=0
        #         if len(listMaxVal) > elCount and elCount!=0:
        #             addValue = listMaxVal[elCount-1][1]+1
        #
        #         valueCount = 0
        #         # print 'binStart: ' + str(binStart) + '<br \>'
        #         # print 'binEnd: ' + str(binEnd) + '<br \>'
        #         # print 'valueCount1: ' + str(valueCount) + '<br \>'
        #
        #
        #
        #         for elN in range(0, len(listResCopy[elCount])):
        #             val = listResCopy[elCount][elN][0]
        #             if val >= binStart and val < binEnd:
        #                 # print 'val: ' + str(binStart) + '<br \>'
        #                 valueCount += 1
        #
        #         # print 'valueCount2: ' + str(valueCount) + '<br \>'
        #         howManyPerBin2[elCount].append([binStart+addValue, valueCount])
        #         howManyPerBin2[elCount].append([endCount+addValue, valueCount])
        #         valueCount = 0
        #     j+=1


        # print howManyPerBin[0]

        newListResCopy=[]
        for elCount in elementOrder:

            addValue=0
            if elCount!=0:
                for elM in range(0, elCount):
                    addValue += listMaxVal[elM][1]

            for elN in range(0, len(listResCopy[elCount])):
                vLog = 0
                if listResCopy[elCount][elN][1]> 0:
                    vLog = math.log(listResCopy[elCount][elN][1],10)
                listResCopy[elCount][elN][1] = vLog
                listResCopy[elCount][elN][0] = listResCopy[elCount][elN][0] + addValue

            newListResCopy.append(listResCopy[elCount])

        for elCount in howManyPerBin:
            newhowManyPerBin = []

            ik=True
            for elN in range(0, len(howManyPerBin[elCount])):
                if elN%2==0:
                    ik=True
                else:
                    if howManyPerBin[elCount][elN][1] != 0:
                        st=(howManyPerBin[elCount][elN][0] + howManyPerBin[elCount][elN-1][0])/2
                        end = howManyPerBin[elCount][elN][1]
                        if scale == 'Log':
                            if end!=0:
                                end = math.log(end, 10)
                        newhowManyPerBin.append([st, end])
                    else:
                        st=(howManyPerBin[elCount][elN][0] + howManyPerBin[elCount][elN-1][0])/2
                        end = None
                        newhowManyPerBin.append([st, end])
                    ik=False
            if ik == False:
                st=howManyPerBin[elCount][elN][0]
                end = howManyPerBin[elCount][elN][1]
                if scale == 'Log':
                    if end!=0:
                        end = math.log(end, 10)
                newhowManyPerBin.append([st, end])

            newListResCopy.append(newhowManyPerBin)
            
            #newListResCopy.append(howManyPerBin[elCount])
        #
        # for elCount in howManyPerBin2:
        #     newListResCopy.append(howManyPerBin2[elCount])

        seriesType=[]
        newSeriesNameRes=[]
        yAxisMultiVal=[]
        for sn in seriesNameRes:
            newSeriesNameRes.append(sn)
            seriesType.append('scatter')
            yAxisMultiVal.append(0)

        for sn in seriesNameRes:
            newSeriesNameRes.append(str(sn) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)
        #
        # for sn in seriesNameRes:
        #     newSeriesNameRes.append(str(sn) + '--bin')
        #     seriesType.append('line')
        #     yAxisMultiVal.append(2)
        
        


        #for elCount in elementOrder:
        res += vg.drawLineChartMultiYAxis(
             newListResCopy,
             seriesName = newSeriesNameRes,
             seriesType = seriesType,
             #label = '<b>{series.name}</b>: [endElement0] {point.x} [startElement1-endElement0] {point.y}',
             height = 500,
             reversed=False,
             markerRadius=1,
             xAxisTitle = 'chr start pos',
             yAxisTitle = ['distance(log10)','points per bin (' +str(scale)+')'],
             yAxisMulti = yAxisMultiVal,
             minY=0,
             #plotLines=chrStPos
             #marginTop=30,
             #addOptions='float:left;width:' + str(percentagePlot)
         )
        #
        # res += '<div style="clear:both;"> </div>'
        #
        # for elCount in elementOrder:
        #     res += vg.drawLineChart(
        #          [listResLine[elCount]],
        #          seriesName = [seriesNameRes[elCount]],
        #          label = '<b>{series.name}</b>: [endElement0] {point.x} [value] {point.y}',
        #          height = 300,
        #          xAxisTitle = 'chr start pos',
        #          yAxisTitle = 'values',
        #          marginTop=30,
        #          addOptions='float:left;width:' + str(percentagePlot)
        #          )
        #




        # for elN in range(0, len(listResBubble)):
        #     listResBubble[elN][1] = math.log(listResBubble[elN][1], 10)


#odpada
#         res += vg.drawBubbleChart(
#              listResBubble.values(),
#              seriesName = seriesNameRes,
#              #label = '<b>{series.name}</b>:  [endElement0] {point.x} [startElement1-endElement0] {point.y} [value] {point.z}',
#              height = 400,
#              xAxisTitle = 'chr start pos',
#              yAxisTitle = 'distance',
#              marginTop=30
#              )

        res += '<div style="clear:both;"> </div>'

        return res


    @classmethod
    def drawInteractiveSingleV2(cls, listResLine, elementOrder, listResCopy, seriesNameRes, listResBubble, bps, scale,chrLength):
        vg = visualizationGraphs()
        percentagePlot = str(int(float(100)/float(len(listResLine)))) + '%'
        #percentagePlot = '800px'

        res=''

        #elementOrder=[0,1,2,3]
        
        
        
        
        listMaxVal = []
        for elCount in elementOrder:
            lmax = -10000
            lmin = 10000000000000000
            for elN in range(0, len(listResCopy[elCount])):
                if listResCopy[elCount][elN][0] > lmax:
                    lmax = listResCopy[elCount][elN][0]
                if listResCopy[elCount][elN][0] < lmin:
                    lmin = listResCopy[elCount][elN][0]
            listMaxVal.append([0, lmax])

        # print listMaxVal
        # print '========'
        # print listResCopy[0]
        #
        # print '----'

        # print str(listMaxVal)+ '<br \>'

        listResBubbleX={}
        howManyPerBin=OrderedDict()
        j=0
        
       
        
        
        for elCount in elementOrder:
            listResBubbleX[elCount]={}

            for elN in range(0, len(listResCopy[elCount])):
                if not listResCopy[elCount][elN][0] in listResBubbleX[elCount]:
                    listResBubbleX[elCount][listResCopy[elCount][elN][0]]=0
                listResBubbleX[elCount][listResCopy[elCount][elN][0]]+=1
#                 if not listResCopy[elCount][elN][0] in listResBubbleX:
#                     listResBubbleX[listResCopy[elCount][elN][0]]=[listResCopy[elCount][elN][0],y,0]
#                 listResBubbleX[listResCopy[elCount][elN][0]]+=1


            if not elCount in howManyPerBin:
                howManyPerBin[elCount]=[]

            lmin = int(math.floor(listMaxVal[j][0])/bps)
            lmax = int(math.ceil(listMaxVal[j][1])/bps) + 1

            addValue=0
            # if elCount!=0:
            #     for elM in range(0, elCount):
            #         addValue += listMaxVal[elM][1]

            for vv in range(lmin, lmax):


                binStart = vv * bps
                binEnd = vv * bps + bps
                endCount = binEnd-1



                valueCount = 0
                # print 'binStart: ' + str(binStart) + '<br \>'
                # print 'binEnd: ' + str(binEnd) + '<br \>'
                # print 'valueCount1: ' + str(valueCount) + '<br \>'



                for elN in range(0, len(listResCopy[elCount])):

                    val = listResCopy[elCount][elN][0]
                    if val >= binStart and val < binEnd:
                        # print 'val: ' + str(binStart) + '<br \>'
                        valueCount += 1

                # print 'valueCount2: ' + str(valueCount) + '<br \>'
                howManyPerBin[elCount].append([binStart+addValue, valueCount])
                howManyPerBin[elCount].append([endCount+addValue, valueCount])
                valueCount = 0
            j+=1

        

        # listResBubble=OrderedDict()
        # for elCount in elementOrder:
        #     listResBubble[elCount]=[]
        #     for elN in range(0, len(listResCopy[elCount])):
        #
        #         addValue=0
        #         # if elCount!=0:
        #         #     for elM in range(0, elCount):
        #         #         addValue += listMaxVal[elM][1]
        #         vLog = 0
        #         if listResCopy[elCount][elN][1]> 0:
        #             vLog = math.log(listResCopy[elCount][elN][1],10)
        #         listResBubble[elCount].append([listResCopy[elCount][elN][0]+addValue, vLog, listResBubbleX[elCount][listResCopy[elCount][elN][0]]])


        #
        # howManyPerBin2=OrderedDict()
        # j=0
        # for elCount in elementOrder:
        #     if not elCount in howManyPerBin2:
        #         howManyPerBin2[elCount]=[]
        #
        #     lmin = int(math.floor(listMaxVal[j][0]))
        #     lmax = int(math.ceil(listMaxVal[j][1])) + 1
        #
        #     print 'lmin: ' + str(lmin) + '<br \>'
        #     print 'lmax: ' + str(lmax) + '<br \>'
        #
        #     for vv in range(lmin, lmax):
        #
        #
        #         binStart = vv #1mln - 1mln+1
        #         binEnd =  vv + bps #1mln + 1 - 1mln+2
        #         endCount = binEnd-1
        #
        #         addValue=0
        #         if len(listMaxVal) > elCount and elCount!=0:
        #             addValue = listMaxVal[elCount-1][1]+1
        #
        #         valueCount = 0
        #         # print 'binStart: ' + str(binStart) + '<br \>'
        #         # print 'binEnd: ' + str(binEnd) + '<br \>'
        #         # print 'valueCount1: ' + str(valueCount) + '<br \>'
        #
        #
        #
        #         for elN in range(0, len(listResCopy[elCount])):
        #             val = listResCopy[elCount][elN][0]
        #             if val >= binStart and val < binEnd:
        #                 # print 'val: ' + str(binStart) + '<br \>'
        #                 valueCount += 1
        #
        #         # print 'valueCount2: ' + str(valueCount) + '<br \>'
        #         howManyPerBin2[elCount].append([binStart+addValue, valueCount])
        #         howManyPerBin2[elCount].append([endCount+addValue, valueCount])
        #         valueCount = 0
        #     j+=1


        # print howManyPerBin[0]

        bubbleVal={}

        newListResCopy=[]
        for elCount in elementOrder:

            addValue=0
            # if elCount!=0:
            #     for elM in range(0, elCount):
            #         addValue += listMaxVal[elM][1]

            for elN in range(0, len(listResCopy[elCount])):
                vLog = 0
                if listResCopy[elCount][elN][1]> 0:
                    vLog = math.log(listResCopy[elCount][elN][1],10)
                listResCopy[elCount][elN][1] = vLog
                listResCopy[elCount][elN][0] = listResCopy[elCount][elN][0] + addValue
                if not listResCopy[elCount][elN][0] in bubbleVal:
                    bubbleVal[listResCopy[elCount][elN][0]] = {}
                if not listResCopy[elCount][elN][1] in bubbleVal[listResCopy[elCount][elN][0]]:
                    bubbleVal[listResCopy[elCount][elN][0]][listResCopy[elCount][elN][1]]=0
                bubbleVal[listResCopy[elCount][elN][0]][listResCopy[elCount][elN][1]]+=1

            newListResCopy.append(listResCopy[elCount])

        listResBubble=[]
        for x, it0 in bubbleVal.items():
            for y, v in it0.items():
                listResBubble.append([x,y,v])
                
        #print listResBubble
        
        # print '<br \>'+'<br \>'+'<br \>'+'-1111--'+'<br \>'+'<br \>'+'<br \>'+'<br \>'
        # print howManyPerBin
        # print '<br \>'+'<br \>'+'<br \>'+'-2222--'+'<br \>'+'<br \>'+'<br \>'+'<br \>'


        maxVVP=-100
        for elCount in elementOrder:
            if maxVVP <  len(howManyPerBin[elCount]):
                maxVVP  = len(howManyPerBin[elCount])
            
            
            
            
            newhowManyPerBin = []

            ik=True
            for elN in range(0, len(howManyPerBin[elCount])):
                if elN%2==0:
                    ik=True
                else:
                    if howManyPerBin[elCount][elN][1] != 0:
                        st=(howManyPerBin[elCount][elN][0] + howManyPerBin[elCount][elN-1][0])/2
                        end = howManyPerBin[elCount][elN][1]
                        if scale == 'Log':
                            if end!=0:
                                end = math.log(end, 10)
                        newhowManyPerBin.append([st, end])
                    else:
                        st=(howManyPerBin[elCount][elN][0] + howManyPerBin[elCount][elN-1][0])/2
                        end = None
                        newhowManyPerBin.append([st, end])
                    ik=False
            if ik == False:
                st=howManyPerBin[elCount][elN][0]
                end = howManyPerBin[elCount][elN][1]
                if scale == 'Log':
                    if end!=0:
                        end = math.log(end, 10)
                newhowManyPerBin.append([st, end])

            newListResCopy.append(newhowManyPerBin)


#         print newListResCopy
#         print '<br \>'+'<br \>'+'<br \>'+'-3333--'+'<br \>'+'<br \>'+'<br \>'+'<br \>'

        seriesType=[]
        newSeriesNameRes=[]
        yAxisMultiVal=[]
        for sn in seriesNameRes:
            newSeriesNameRes.append(sn)
            seriesType.append('scatter')
            yAxisMultiVal.append(0)

        for sn in seriesNameRes:
            newSeriesNameRes.append(str(sn) + '-- point')
            seriesType.append('line')
            yAxisMultiVal.append(1)

        allSeriesPoints=[]
        
        
        

        howManyPerBinC = copy.deepcopy(howManyPerBin)



        for elN in range(0, maxVVP):
            i=0
            for elCount in howManyPerBinC:
                if  elN < len(howManyPerBinC[elCount]):
                    if i == 0:
                        allSeriesPoints.append(howManyPerBinC[elCount][elN])
                    else:
                        allSeriesPoints[elN][1] += howManyPerBinC[elCount][elN][1]
                    i+=1
                    # print str(elCount) + '   ' + str(len(howManyPerBinC[elCount])) + ' - ' + str(maxVVP) + '   ' + str(elN) +  '    ' + str(howManyPerBinC[elCount][elN])+ '===' + str(allSeriesPoints[elN]) + '<br \>'
            # print '------' + '<br \>'
        newSeriesNameRes.append('all points')
        seriesType.append('line')
        yAxisMultiVal.append(1)


        

        newSeriesNameResAvg = []

        ik=True
        for elN in range(0, len(allSeriesPoints)):
            if elN%2==0:
                ik=True
            else:
                if allSeriesPoints[elN][1] != 0:
                    st=(allSeriesPoints[elN][0] + allSeriesPoints[elN-1][0])/2
                    end = allSeriesPoints[elN][1]
                    if scale == 'Log':
                        if end!=0:
                            end = math.log(end, 10)
                    newSeriesNameResAvg.append([st, end])
                else:
                    st=(allSeriesPoints[elN][0] + allSeriesPoints[elN-1][0])/2
                    end = None
                    newSeriesNameResAvg.append([st, end])
                ik=False
        if ik == False:
            st=allSeriesPoints[elN][0]
            end = allSeriesPoints[elN][1]
            if scale == 'Log':
                if end!=0:
                    end = math.log(end, 10)
            newSeriesNameResAvg.append([st, end])



#         print allSeriesPoints


        #
        # for sn in seriesNameRes:
        #     newSeriesNameRes.append(str(sn) + '--bin')
        #     seriesType.append('line')
        #     yAxisMultiVal.append(2)


        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        #
        # print allSeriesPoints
        #
        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        # print newListResCopy

        # print allSeriesPoints
        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        # print '<br \>'
        #
        # print newSeriesNameResAvg

        
        lineHtml=OrderedDict()
        
        ij=0
        for key, it0 in howManyPerBin.iteritems():
            for it1 in it0:
                if ij%2==1:
                    if not str(preV) + '-' + str(it1[0]) in lineHtml:
                        lineHtml[str(preV) + '-' + str(it1[0])] = []
                    lineHtml[str(preV) + '-' + str(it1[0])].append(it1[1])
                preV = it1[0]
                ij+=1
        
        

        res += vg.drawLineChart(
             #[allSeriesPoints]+[newSeriesNameResAvg],
             [newSeriesNameResAvg],
             #seriesName = ['all points', 'all point bin avg'],
             seriesName = ['all point bin avg'],
             height = 300,
             xAxisTitle = 'chr start pos',
             yAxisTitle = 'points per bin ('+ str(scale) +')',
             minY=0,
             plotLines=chrLength.values(),
             plotLinesName=chrLength.keys()
         )
        
        #for elCount in elementOrder:
        res += vg.drawLineChartMultiYAxis(
             newListResCopy, #+[newSeriesNameResAvg],
             seriesName = newSeriesNameRes,
             seriesType = seriesType,
             #label = '<b>{series.name}</b>: [endElement0] {point.x} [startElement1-endElement0] {point.y}',
             height = 500,
             reversed=False,
             markerRadius=1,
             xAxisTitle = 'chr start pos',
             yAxisTitle = ['distance(log10)','points per bin (' + str(scale) + ')'],
             yAxisMulti = yAxisMultiVal,
             minY=0,
             plotLines=chrLength.values(),
             plotLinesName=chrLength.keys()
             #marginTop=30,
             #addOptions='float:left;width:' + str(percentagePlot)
         )
        #
        # res += '<div style="clear:both;"> </div>'
        #
        # for elCount in elementOrder:
        #     res += vg.drawLineChart(
        #          [listResLine[elCount]],
        #          seriesName = [seriesNameRes[elCount]],
        #          label = '<b>{series.name}</b>: [endElement0] {point.x} [value] {point.y}',
        #          height = 300,
        #          xAxisTitle = 'chr start pos',
        #          yAxisTitle = 'values',
        #          marginTop=30,
        #          addOptions='float:left;width:' + str(percentagePlot)
        #          )
        #




        # for elN in range(0, len(listResBubble)):
        #     listResBubble[elN][1] = math.log(listResBubble[elN][1], 10)



        res += vg.drawBubbleChart(
             [listResBubble],
             seriesName = ['all series'],
             label = '<b>{series.name}</b>:  [endElement0] {point.x} [startElement1-endElement0] {point.y} [value] {point.z}',
             height = 400,
             xAxisTitle = 'chr start pos',
             yAxisTitle = 'distance log',
             marginTop=30,
             minY=0,
             plotLines=chrLength.values(),
             plotLinesName=chrLength.keys()
             )

        res += '<div style="clear:both;"> </div>'

        return res, lineHtml
    
    
    
    @classmethod
    def sortChrDict(cls, chr):
        
        remeberString=[]
        keysList=[]
        for el in chr.keys():
            try:
                elC=int(el.replace('chr',''))
                keysList.append(elC)
            except:
                remeberString.append(el.replace('chr',''))
        
        
        sChr = sorted(keysList) + sorted(remeberString)
        
        chrDict=OrderedDict()
        chrLength=OrderedDict()
        val=0
        for elChr in sChr:
            el='chr'+str(elChr)
            chrDict[el] = chr[el]
            chrLength[el] = val
            val+=chr[el] 
            
        return chrDict, chrLength


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        dataDict=OrderedDict()
        dataDictLine=OrderedDict()
        elementOrder=[]

        scale=choices.scale

        bps=choices.bps
        if bps == '':
            bps  = 10000
        else:
            bps = int(bps)

        #dataDict {endPosition: {val: end-start, tot: howMany} ...}

        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)  
        chrOrder, chrLength = makeRainfallPlots.sortChrDict(GenomeInfo.getStdChrLengthDict(gSuite.genome))
        
        
        chrList = {}
        chrStPos = []
        sumChr=0
        for chrLen in chrOrder.values():
            sumChr+=chrLen
            chrStPos.append(sumChr)
        
        
        #parse the tracks!
        for track in gSuite.allTrackTitles():
            gSuiteTrack = gSuite.getTrackFromTitle(track)
            trackName = track

            dataDict[trackName]=OrderedDict()
            dataDictLine[trackName]=OrderedDict()
            
            newDict={}
            with open(gSuiteTrack.path, 'r') as f:
                i=0
                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if len(el)>=2:
                        if not el[0] in newDict:
                            newDict[el[0]] = []
                        newDict[el[0]].append([el[0], int(el[1]), int(el[2])])
                i+=1
            
        
            
            newDict2=OrderedDict()
            for key, it in chrLength.items():
                if key in newDict:
                    newDict2[key] = sorted(newDict[key], key=lambda x: x[1])
            
            
            for key, it in newDict2.items():
                if i==0:
                    chr=key
                i=0
                prevEnd=0
                label=0
                
                for el in it:
                    if len(el)>=2:
                        
                        if not int(el[1]) in dataDictLine[trackName]:
                            dataDictLine[trackName][int(el[1])] = 1
                        start = int(el[1])
                        if prevEnd != 0:
                            if not label in dataDict[trackName]:
                                dataDict[trackName][label] = OrderedDict()
                                dataDict[trackName][label]['val']=0
                                dataDict[trackName][label]['tot']=0
                            dataDict[trackName][label]['val']+=start-prevEnd
                            dataDict[trackName][label]['tot']+=1
                        
                        label = int(el[1])+int(chrLength[el[0]])
                        prevEnd = int(el[2])
                        i+=1
    
            elementOrder.append(i)

        listResCopy=[]
        for key0, it0 in dataDict.iteritems():
            listResPart=[]
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)

        elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k])

        if choices.color =='Single color':
            
            seriesNameRes=[]
            listRes=[]
            listResBubble=[]
            listResLine=[]

            #counting part
            for key0, it0 in dataDictLine.iteritems():
                listResLinePart=[]
                i=0
                for key2 in sorted(it0):
                    en=key2
                    if i==0:
                        for elK in range(key2-2, key2):
                            listResLinePart.append([elK, 0])
                        st = key2+1
                    else:
                        for elK in range(en-2, en):
                            listResLinePart.append([elK, 0])
                        st = en
                    listResLinePart.append([key2, it0[key2]])
                    i+=1
                for elK in range(key2+1, key2+2):
                    listResLinePart.append([elK, 0])

                listResLine.append(listResLinePart)


            for key0, it0 in dataDict.iteritems():
                seriesNameRes.append(key0)

                for key2 in sorted(it0):
                    if not [key2, it0[key2]['val']] in listRes:
                        listRes.append([key2, it0[key2]['val']])
                        listResBubble.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    else:
                        for elN in range(0, len(listResBubble)):
                            if listResBubble[elN][0]==key2 and listResBubble[elN][1]==it0[key2]['val']:
                                listResBubble[elN][2] += it0[key2]['tot']


            
            if choices.interactive == 'Interactive':

                lineHtml=''
                if choices.multiPlot == 'Single':
                    #res = makeRainfallPlots.drawInteractiveSingle(seriesNameRes, listRes, listResLine, listResBubble)
                    res, lineHtml = makeRainfallPlots.drawInteractiveSingleV2(listResLine, elementOrder, listResCopy, seriesNameRes, listResBubble, bps, scale,chrLength)


                if choices.multiPlot == 'Multi':

                    res = makeRainfallPlots.drawInteractiveMulti(listResLine, elementOrder, listResCopy, seriesNameRes, listResBubble, bps, scale,chrStPos)


                htmlCore = HtmlCore()
                htmlCore.begin()
                htmlCore.line('Bin size: ' + str(bps))
                
                if lineHtml!='':
                    sumLine=[]
                    for sN in seriesNameRes:
                        sumLine.append(0)
                    htmlCore.tableHeader(['Bins']+seriesNameRes, sortable=True, tableId=1)
                    for key, it0 in lineHtml.iteritems():
                        htmlCore.tableLine([key]+it0)
                        for iN in range(0, len(it0)):
                                sumLine[iN]+=it0[iN]
                    htmlCore.tableLine(['<b>Sum</b>']+sumLine)

                
                htmlCore.line(res)
                htmlCore.end()
                htmlCore.hideToggle(styleClass='debug')
                print htmlCore

            # if choices.interactive == 'Figure':
            #     fig = plt.figure()
            #
            #     #scatter plot
            #     plotOutput = GalaxyRunSpecificFile(['Scatter', 'scatter.png'], galaxyFn)
            #     xListRes = []
            #     yListRes = []
            #     for el in listRes:
            #         xListRes.append(el[0])
            #         yListRes.append(el[1])
            #
            #     for i in range(0,1):
            #         x = np.array(xListRes)
            #         y = np.array(yListRes)
            #         scale = 20
            #         plt.scatter(x, y,  s=scale)
            #     plt.grid(True)
            #     plt.savefig(plotOutput.getDiskPath(ensurePath=True))
            #
            #     core = HtmlCore()
            #     core.begin()
            #     core.divBegin(divId='plot')
            #     core.image(plotOutput.getURL())
            #     core.divEnd()
            #     core.end()
            #     print core

        if choices.color =='Various colors':
                
            seriesNameRes=[]
            listRes=[]
            listResBubble=[]
            listResLine=[]

            for key0, it0 in dataDictLine.iteritems():
                listResLinePart=[]
                i=0
                for key2 in sorted(it0):
                    listResLinePart.append([key2, it0[key2]])
                    i+=1

                listResLine.append(listResLinePart)
             
            listResBubbleTemp=[]
            listResBubble1=[]
            for key0, it0 in dataDict.iteritems():
                seriesNameRes.append(key0)
                listResPart=[]
                listResBubblePart=[]
                for key2 in sorted(it0):
                    listResPart.append([key2, it0[key2]['val']])
                    listResBubblePart.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    if [key2, it0[key2]['val']] not in listResBubbleTemp:
                        listResBubbleTemp.append([key2, it0[key2]['val']])
                        listResBubble1.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    else:
                        for elN in range(0, len(listResBubble1)):
                            if listResBubble1[elN][0]==key2 and listResBubble1[elN][1]==it0[key2]['val']:
                                listResBubble1[elN][2] += it0[key2]['tot']
                listRes.append(listResPart)
                listResBubble.append(listResBubblePart)

            
            if choices.interactive == 'Interactive':

                res = makeRainfallPlots.drawInteractiveVariousColor(seriesNameRes, listRes, listResLine, listResBubble)

                htmlCore = HtmlCore()
                htmlCore.begin()
                htmlCore.line('Bin size: ' + str(bps))
                htmlCore.line(res)
                htmlCore.end()
                htmlCore.hideToggle(styleClass='debug')
                print htmlCore
            
            # if choices.interactive == 'Figure':
            #     f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False, figsize=(15,10))
            #
            #     #scatter plot
            #     plotOutput = GalaxyRunSpecificFile(['plotsGroup', 'plot.png'], galaxyFn)
            #
            #     colList = [
            #           '#7cb5ec',
            #           '#434348',
            #           '#99D6D6',
            #           '#005C5C',
            #           '#292933',
            #           '#336699',
            #           '#8085e9',
            #           '#B2CCFF',
            #           '#90ed7d',
            #           '#f7a35c',
            #           '#f15c80',
            #           '#e4d354',
            #           '#8085e8',
            #           '#8d4653',
            #           '#6699FF',
            #           '#91e8e1',
            #           '#7A991F',
            #           '#525266',
            #           '#1A334C',
            #           '#334C80',
            #           '#292900',
            #           '#142900',
            #           '#99993D',
            #           '#009999',
            #           '#1A1A0A',
            #           '#5C85AD',
            #           '#804C4C',
            #           '#1A0F0F',
            #           '#A3A3CC',
            #           '#660033',
            #           '#3D4C0F',
            #           '#fde720',
            #           '#554e44',
            #           '#1ce1ce',
            #           '#dedbbb',
            #           '#facade',
            #           '#baff1e',
            #           '#aba5ed',
            #           '#f2b3b3',
            #           '#f9e0e0',
            #           '#abcdef',
            #           '#f9dcd3',
            #           '#eb9180',
            #           '#c2dde5',
            #            '#008B8B',
            #         '#B8860B',
            #         '#A9A9A9',
            #         '#006400',
            #         '#BDB76B',
            #         '#8B008B',
            #         '#556B2F',
            #         '#FF8C00',
            #         '#9932CC',
            #         '#8B0000',
            #         '#E9967A',
            #         '#8FBC8F',
            #         '#483D8B',
            #         '#2F4F4F',
            #         '#00CED1',
            #         '#9400D3',
            #         '#FF1493',
            #         '#00BFFF',
            #         '#696969',
            #         '#1E90FF',
            #         '#B22222',
            #         '#FFFAF0',
            #         '#228B22',
            #         '#FF00FF',
            #         '#DCDCDC',
            #         '#F8F8FF',
            #         '#FFD700',
            #         '#DAA520',
            #             '#808080',
            #             '#008000',
            #             '#ADFF2F',
            #             '#F0FFF0',
            #             '#FF69B4',
            #             '#CD5C5C',
            #             '#4B0082',
            #             '#FFFFF0',
            #             '#F0E68C',
            #             '#E6E6FA',
            #             '#FFF0F5',
            #             '#7CFC00',
            #             '#FFFACD',
            #             '#ADD8E6',
            #             '#F08080',
            #             '#E0FFFF',
            #             '#FAFAD2',
            #             '#D3D3D3',
            #             '#90EE90',
            #             '#FFB6C1',
            #             '#FFA07A',
            #             '#20B2AA',
            #             '#87CEFA',
            #             '#778899',
            #             '#B0C4DE',
            #             '#FFFFE0',
            #             '#00FF00',
            #             '#32CD32',
            #             '#FAF0E6',
            #             '#FF00FF',
            #             '#800000',
            #             '#66CDAA',
            #             '#0000CD',
            #             '#BA55D3',
            #             '#9370DB',
            #             '#3CB371',
            #             '#7B68EE',
            #             '#00FA9A',
            #             '#48D1CC',
            #             '#C71585',
            #             '#191970',
            #             '#F5FFFA',
            #             '#FFE4E1',
            #             '#FFE4B5',
            #             '#FFDEAD',
            #             '#000080',
            #             '#FDF5E6',
            #             '#808000',
            #             '#6B8E23',
            #             '#FFA500',
            #             '#FF4500',
            #             '#DA70D6',
            #             '#EEE8AA',
            #             '#98FB98',
            #             '#AFEEEE',
            #             '#DB7093',
            #             '#FFEFD5',
            #             '#FFDAB9',
            #             '#CD853F',
            #             '#FFC0CB',
            #             '#DDA0DD',
            #             '#B0E0E6',
            #             '#800080',
            #             '#663399',
            #             '#FF0000',
            #             '#BC8F8F',
            #             '#4169E1',
            #             '#8B4513',
            #             '#FA8072',
            #             '#F4A460',
            #             '#2E8B57',
            #             '#FFF5EE',
            #             '#A0522D',
            #             '#C0C0C0',
            #             '#87CEEB',
            #             '#6A5ACD',
            #             '#708090',
            #             '#FFFAFA',
            #             '#00FF7F',
            #             '#4682B4'
            #           ];
            #
            #
            #     #line plot
            #     i=0
            #     for elList in listResLine:
            #         xListRes = []
            #         yListRes = []
            #         wListRes=[]
            #         sizes=[]
            #         scale=10
            #
            #         num = ((float(i)/float(len(listResLine))) - 0.0)/(1.0 - 0.0) * (0.9  - 0.1) + 0.1
            #         print num
            #         for el in elList:
            #             xListRes.append(el[0])
            #             yListRes.append(el[1])
            #             wListRes.append(num)
            #
            #         x = np.array(xListRes)
            #         y = np.array(yListRes)
            #         w = np.array(wListRes)
            #
            #
            #         ax1.plot(x,w, c=colList[i], label=dataDictLine.keys()[i], linewidth=4.0)
            #         i+=1
            #
            #
            #     #scatter plot
            #     i=0
            #     for elList in listRes:
            #         xListRes = []
            #         yListRes = []
            #         sizes=[]
            #         scale=10
            #         for el in elList:
            #             xListRes.append(el[0])
            #             yListRes.append(el[1])
            #
            #         x = np.array(xListRes)
            #         y = np.array(yListRes)
            #
            #
            #         ax3.scatter(x, y, s=scale, c=colList[i], label=dataDictLine.keys()[i])
            #         i+=1
            #
            #     i=0
            #
            #     #bubble plot
            #     xListRes = []
            #     yListRes = []
            #     sizes=[]
            #     scale=100
            #     #sizeUnique=[]
            #     for el in listResBubble1:
            #         xListRes.append(el[0])
            #         yListRes.append(el[1])
            #         sizes.append(el[2]*scale)
            #
            #
            #     x = np.array(xListRes)
            #     y = np.array(yListRes)
            #
            #     ax2.scatter(x, y , s=sizes, c=colList[i], label=dataDictLine.keys()[i], linewidths=1, edgecolor='g')
            #     i+=1
            #
            #
            #     ax1.grid(True)
            #     ax2.grid(True)
            #     ax3.grid(True)
            #
            #     ax1.legend(loc='upper left', fontsize=8)
            #
            #
            #     plt.savefig(plotOutput.getDiskPath(ensurePath=True))
            #
            #     core = HtmlCore()
            #     core.begin()
            #     core.divBegin(divId='plot')
            #     core.image(plotOutput.getURL())
            #     core.divEnd()
            #     core.end()
            #     print core
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


class rainfallPlotsGSuite(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Rainfall plots gSuite"

    @staticmethod
    def getInputBoxNames():
        return [
               
                ('Select files','files'),
                ('Select option', 'color'),
                ('Select type of results', 'interactive'),
                ('Select type of plotting', 'multiPlot'),
                ('Select bps', 'bps')
                ]

    @staticmethod
    def getOptionsBoxFiles():
        return ('__multihistory__', 'bed')

    @staticmethod
    def getOptionsBoxColor(prevChoices):
        return ['Single color', 'Various colors']

    @staticmethod
    def getOptionsBoxInteractive(prevChoices):
        return ['Interactive', 'Figure']


    @staticmethod
    def getOptionsBoxMultiPlot(prevChoices):
        return ['Single', 'Multi']

    @staticmethod
    def getOptionsBoxBps(prevChoices):
        return ''

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
        import numpy as np
        import matplotlib.pyplot as plt

        tf=choices.files
        trackList =  tf.values()

        dataDict=OrderedDict()
        dataDictLine=OrderedDict()

        

        elementOrder=[]
        #dataDict {endPosition: {val: end-start, tot: howMany} ...}

        #parse the tracks!
        for track in trackList:
            trackName = track.split(':')[len(track.split(':'))-1].replace('%20', '-')
            dataDict[trackName]=OrderedDict()
            dataDictLine[trackName]=OrderedDict()
            with open(ExternalTrackManager.extractFnFromGalaxyTN(track.split(':')), 'r') as f:
                i=0
                prevEnd=0
                label=0


                for x in f.readlines():
                    el = x.strip('\n').split('\t')
                    if not int(el[1]) in dataDictLine[trackName]:
                        dataDictLine[trackName][int(el[1])] = 1
                    start = int(el[1])
                    if prevEnd != 0:
                        if not label in dataDict[trackName]:
                            dataDict[trackName][label] = OrderedDict()
                            dataDict[trackName][label]['val']=0
                            dataDict[trackName][label]['tot']=0
                        dataDict[trackName][label]['val']+=start-prevEnd
                        dataDict[trackName][label]['tot']+=1
                    label = int(el[1])
                    prevEnd = int(el[2])
                    i+=1

                elementOrder.append(i)

            f.closed




        listResCopy=[]
        for key0, it0 in dataDict.iteritems():
            listResPart=[]
            for key2 in sorted(it0):
                listResPart.append([key2, it0[key2]['val']])
            listResCopy.append(listResPart)



        elementOrder = sorted(range(len(elementOrder)), key=lambda k: elementOrder[k])


        if choices.color =='Various colors':

            seriesNameRes=[]
            listRes=[]
            listResBubble=[]
            listResLine=[]

            for key0, it0 in dataDictLine.iteritems():
                listResLinePart=[]
                i=0
                for key2 in sorted(it0):
                    listResLinePart.append([key2, it0[key2]])
                    i+=1

                listResLine.append(listResLinePart)

            listResBubbleTemp=[]
            listResBubble1=[]
            for key0, it0 in dataDict.iteritems():
                seriesNameRes.append(key0)
                listResPart=[]
                listResBubblePart=[]
                for key2 in sorted(it0):
                    listResPart.append([key2, it0[key2]['val']])
                    listResBubblePart.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    if [key2, it0[key2]['val']] not in listResBubbleTemp:
                        listResBubbleTemp.append([key2, it0[key2]['val']])
                        listResBubble1.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    else:
                        for elN in range(0, len(listResBubble1)):
                            if listResBubble1[elN][0]==key2 and listResBubble1[elN][1]==it0[key2]['val']:
                                listResBubble1[elN][2] += it0[key2]['tot']
                listRes.append(listResPart)
                listResBubble.append(listResBubblePart)


            if choices.interactive == 'Interactive':

                vg = visualizationGraphs()
                res = vg.drawScatterChart(
                    listRes,
                    seriesName = seriesNameRes,
                    #titleText = ['Scatter plot'],
                    label = '<b>{series.name}</b>: {point.x} {point.y}',
                    height = 300,
                    xAxisTitle = 'chr start pos',
                    yAxisTitle = 'distance',
                    marginTop=30
                    )


                res += vg.drawLineChart(
                    listResLine,
                    seriesName = seriesNameRes,
                    #label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
                    height = 300,
                    xAxisTitle = 'chr start pos',
                    yAxisTitle = 'values',
                    marginTop=30
                    )

                res += vg.drawBubbleChart(
                    listResBubble,
                    seriesName = seriesNameRes,
                    label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
                    height = 300,
                    xAxisTitle = 'chr start pos',
                    yAxisTitle = 'distance',
                    marginTop=30
                    )




                htmlCore = HtmlCore()
                htmlCore.begin()
                htmlCore.line(res)
                htmlCore.end()
                htmlCore.hideToggle(styleClass='debug')
                print htmlCore

            if choices.interactive == 'Figure':
                f, (ax1, ax2, ax3) = plt.subplots(3, sharex=True, sharey=False, figsize=(15,10))

                #scatter plot
                plotOutput = GalaxyRunSpecificFile(['plotsGroup', 'plot.png'], galaxyFn)

                colList = [
                      '#7cb5ec',
                      '#434348',
                      '#99D6D6',
                      '#005C5C',
                      '#292933',
                      '#336699',
                      '#8085e9',
                      '#B2CCFF',
                      '#90ed7d',
                      '#f7a35c',
                      '#f15c80',
                      '#e4d354',
                      '#8085e8',
                      '#8d4653',
                      '#6699FF',
                      '#91e8e1',
                      '#7A991F',
                      '#525266',
                      '#1A334C',
                      '#334C80',
                      '#292900',
                      '#142900',
                      '#99993D',
                      '#009999',
                      '#1A1A0A',
                      '#5C85AD',
                      '#804C4C',
                      '#1A0F0F',
                      '#A3A3CC',
                      '#660033',
                      '#3D4C0F',
                      '#fde720',
                      '#554e44',
                      '#1ce1ce',
                      '#dedbbb',
                      '#facade',
                      '#baff1e',
                      '#aba5ed',
                      '#f2b3b3',
                      '#f9e0e0',
                      '#abcdef',
                      '#f9dcd3',
                      '#eb9180',
                      '#c2dde5',
                       '#008B8B',
                    '#B8860B',
                    '#A9A9A9',
                    '#006400',
                    '#BDB76B',
                    '#8B008B',
                    '#556B2F',
                    '#FF8C00',
                    '#9932CC',
                    '#8B0000',
                    '#E9967A',
                    '#8FBC8F',
                    '#483D8B',
                    '#2F4F4F',
                    '#00CED1',
                    '#9400D3',
                    '#FF1493',
                    '#00BFFF',
                    '#696969',
                    '#1E90FF',
                    '#B22222',
                    '#FFFAF0',
                    '#228B22',
                    '#FF00FF',
                    '#DCDCDC',
                    '#F8F8FF',
                    '#FFD700',
                    '#DAA520',
                        '#808080',
                        '#008000',
                        '#ADFF2F',
                        '#F0FFF0',
                        '#FF69B4',
                        '#CD5C5C',
                        '#4B0082',
                        '#FFFFF0',
                        '#F0E68C',
                        '#E6E6FA',
                        '#FFF0F5',
                        '#7CFC00',
                        '#FFFACD',
                        '#ADD8E6',
                        '#F08080',
                        '#E0FFFF',
                        '#FAFAD2',
                        '#D3D3D3',
                        '#90EE90',
                        '#FFB6C1',
                        '#FFA07A',
                        '#20B2AA',
                        '#87CEFA',
                        '#778899',
                        '#B0C4DE',
                        '#FFFFE0',
                        '#00FF00',
                        '#32CD32',
                        '#FAF0E6',
                        '#FF00FF',
                        '#800000',
                        '#66CDAA',
                        '#0000CD',
                        '#BA55D3',
                        '#9370DB',
                        '#3CB371',
                        '#7B68EE',
                        '#00FA9A',
                        '#48D1CC',
                        '#C71585',
                        '#191970',
                        '#F5FFFA',
                        '#FFE4E1',
                        '#FFE4B5',
                        '#FFDEAD',
                        '#000080',
                        '#FDF5E6',
                        '#808000',
                        '#6B8E23',
                        '#FFA500',
                        '#FF4500',
                        '#DA70D6',
                        '#EEE8AA',
                        '#98FB98',
                        '#AFEEEE',
                        '#DB7093',
                        '#FFEFD5',
                        '#FFDAB9',
                        '#CD853F',
                        '#FFC0CB',
                        '#DDA0DD',
                        '#B0E0E6',
                        '#800080',
                        '#663399',
                        '#FF0000',
                        '#BC8F8F',
                        '#4169E1',
                        '#8B4513',
                        '#FA8072',
                        '#F4A460',
                        '#2E8B57',
                        '#FFF5EE',
                        '#A0522D',
                        '#C0C0C0',
                        '#87CEEB',
                        '#6A5ACD',
                        '#708090',
                        '#FFFAFA',
                        '#00FF7F',
                        '#4682B4'
                      ];


                #line plot
                i=0
                for elList in listResLine:
                    xListRes = []
                    yListRes = []
                    wListRes=[]
                    sizes=[]
                    scale=10

                    num = ((float(i)/float(len(listResLine))) - 0.0)/(1.0 - 0.0) * (0.9  - 0.1) + 0.1
                    print num
                    for el in elList:
                        xListRes.append(el[0])
                        yListRes.append(el[1])
                        wListRes.append(num)

                    x = np.array(xListRes)
                    y = np.array(yListRes)
                    w = np.array(wListRes)


                    ax1.plot(x,w, c=colList[i], label=dataDictLine.keys()[i], linewidth=4.0)
                    i+=1


                #scatter plot
                i=0
                for elList in listRes:
                    xListRes = []
                    yListRes = []
                    sizes=[]
                    scale=10
                    for el in elList:
                        xListRes.append(el[0])
                        yListRes.append(el[1])

                    x = np.array(xListRes)
                    y = np.array(yListRes)


                    ax3.scatter(x, y, s=scale, c=colList[i], label=dataDictLine.keys()[i])
                    i+=1

                i=0

                #bubble plot
                xListRes = []
                yListRes = []
                sizes=[]
                scale=100
                #sizeUnique=[]
                for el in listResBubble1:
                    xListRes.append(el[0])
                    yListRes.append(el[1])
                    sizes.append(el[2]*scale)


                x = np.array(xListRes)
                y = np.array(yListRes)

                ax2.scatter(x, y , s=sizes, c=colList[i], label=dataDictLine.keys()[i], linewidths=1, edgecolor='g')
                i+=1


                ax1.grid(True)
                ax2.grid(True)
                ax3.grid(True)

                ax1.legend(loc='upper left', fontsize=8)


                plt.savefig(plotOutput.getDiskPath(ensurePath=True))

                core = HtmlCore()
                core.begin()
                core.divBegin(divId='plot')
                core.image(plotOutput.getURL())
                core.divEnd()
                core.end()
                print core



        if choices.color =='Single color':


            seriesNameRes=[]
            listRes=[]
            listResBubble=[]
            listResLine=[]
            #         maxVal=0
#         for key0, it0 in dataDictLine.iteritems():
#             if maxVal < max(sorted(it0)):
#                 maxVal = max(sorted(it0))

            #counting part
            for key0, it0 in dataDictLine.iteritems():
                listResLinePart=[]
                i=0
                for key2 in sorted(it0):
                    en=key2
                    if i==0:
                        for elK in range(key2-2, key2):
                            listResLinePart.append([elK, 0])
                        st = key2+1
                    else:
                        for elK in range(en-2, en):
                            listResLinePart.append([elK, 0])
                        st = en
                    listResLinePart.append([key2, it0[key2]])
                    i+=1
                for elK in range(key2+1, key2+2):
                    listResLinePart.append([elK, 0])

                listResLine.append(listResLinePart)


            for key0, it0 in dataDict.iteritems():
                seriesNameRes.append(key0)

                for key2 in sorted(it0):
                    if not [key2, it0[key2]['val']] in listRes:
                        listRes.append([key2, it0[key2]['val']])
                        listResBubble.append([key2, it0[key2]['val'], it0[key2]['tot']])
                    else:
                        for elN in range(0, len(listResBubble)):
                            if listResBubble[elN][0]==key2 and listResBubble[elN][1]==it0[key2]['val']:
                                listResBubble[elN][2] += it0[key2]['tot']




            if choices.interactive == 'Figure':
                fig = plt.figure()

                #scatter plot
                plotOutput = GalaxyRunSpecificFile(['Scatter', 'scatter.png'], galaxyFn)
                xListRes = []
                yListRes = []
                for el in listRes:
                    xListRes.append(el[0])
                    yListRes.append(el[1])

                for i in range(0,1):
                    x = np.array(xListRes)
                    y = np.array(yListRes)
                    scale = 20
                    plt.scatter(x, y,  s=scale)
                plt.grid(True)
                plt.savefig(plotOutput.getDiskPath(ensurePath=True))

                core = HtmlCore()
                core.begin()
                core.divBegin(divId='plot')
                core.image(plotOutput.getURL())
                core.divEnd()
                core.end()
                print core


            if choices.interactive == 'Interactive':

                vg = visualizationGraphs()
                if choices.multiPlot == 'Single':

                    res = vg.drawScatterChart(
                         [listRes],
                         seriesName = ['All Series'],
                         #titleText = ['Scatter plot'],
                         label = '<b>{series.name}</b>: {point.x} {point.y}',
                         height = 300,
                         xAxisTitle = 'chr start pos',
                         yAxisTitle = 'distance',
                         marginTop=30
                         )
                    res += vg.drawLineChart(
                         listResLine,
                         seriesName = seriesNameRes,
                         #label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
                         height = 300,
                         xAxisTitle = 'chr start pos',
                         yAxisTitle = 'values',
                         marginTop=30
                         )
                    res += vg.drawBubbleChart(
                         [listResBubble],
                         seriesName = ['All Series'],
                         label = '<b>{series.name}</b>: X:{point.x} Y:{point.y} value: {point.z}',
                         height = 300,
                         xAxisTitle = 'chr start pos',
                         yAxisTitle = 'distance',
                         marginTop=30
                         )

                if choices.multiPlot == 'Multi':

                    percentagePlot = str(int(float(100)/float(len(listResLine)))) + '%'
                    #percentagePlot = '800px'




                    res=''

                    for elCount in elementOrder:

                        for elN in range(0, len(listResCopy[elCount])):
                            listResCopy[elCount][elN][1] = math.log(listResCopy[elCount][elN][1], 10)


                        res += vg.drawScatterChart(
                             [listResCopy[elCount]],
                             seriesName = [seriesNameRes[elCount]],
                             #titleText = ['Scatter plot'],
                             label = '<b>{series.name}</b>: [endElement0] {point.x} [startElement1-endElement0] {point.y}',
                             height = 300,
                             xAxisTitle = 'chr start pos',
                             yAxisTitle = 'distance (log)',
                             marginTop=30,
                            addOptions='float:left;width:' + str(percentagePlot)
                         )


                    res += '<div style="clear:both;"> </div>'

                    for elCount in elementOrder:
                        res += vg.drawLineChart(
                             [listResLine[elCount]],
                             seriesName = [seriesNameRes[elCount]],
                             label = '<b>{series.name}</b>: [endElement0] {point.x} [value] {point.y}',
                             height = 300,
                             xAxisTitle = 'chr start pos',
                             yAxisTitle = 'values',
                             marginTop=30,
                             addOptions='float:left;width:' + str(percentagePlot)
                             )

                    res += '<div style="clear:both;"> </div>'

                # for elN in range(0, len(listResBubble)):
                #     listResBubble[elN][1] = math.log(listResBubble[elN][1], 10)
                #
                # res += vg.drawBubbleChart(
                #      [listResBubble],
                #      seriesName = ['All Series'],
                #      label = '<b>{series.name}</b>:  [endElement0] {point.x} [startElement1-endElement0] {point.y} [value] {point.z}',
                #      height = 300,
                #      xAxisTitle = 'chr start pos',
                #      yAxisTitle = 'distance',
                #      marginTop=30
                #      )


                htmlCore = HtmlCore()
                htmlCore.begin()
                htmlCore.line(res)
                htmlCore.end()
                htmlCore.hideToggle(styleClass='debug')
                print htmlCore

        #code for R which WORKS!
        #openRfigure from quick.util.static
        #GalaxyRunSpecificFile
        #use rPlot
        #closeRfigure
        #getLink or getEmbeddedImage

#         from gold.application.RSetup import robjects, r
#         rPlot = robjects.r.plot
#         rPlot([1,2,3], [4,5,6], type='p', xlim=[0,2], ylim=[0,2], main = 'tit', xlab='xlab', ylab='ylab')
# #         print RPlotUtil.drawXYPlot([1,2,3], [4,5,6], plotType='p', xLim=[0,2], yLim=[0,2], mainTitle='tit', xTitle='xTit', yTitle='yTit')
# #         res = RPlotUtil.drawXYPlot([1,2,3], [4,5,6], plotType='p', xLim=[0,2], yLim=[0,2], mainTitle='tit', xTitle='xTit', yTitle='yTit')
# #
#
#
#         core = HtmlCore()
#         core.begin()
#         core.divBegin(divId='plot')
#         core.image(plotOutput.getURL())
#         core.divEnd()
#         core.end()
#         print core



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

class rainfallPlots(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Generate synthetics tracks with Poisson distribution"

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select genome:','genome'),
                ('Select interRate (default 0.0000001):','paramInterRate'),
                ('Select intraRate (default 0.0000001):','paramIntraRate'),
                ('Select interProb (default 1):','paramInterProb')
                ]

    @staticmethod
    def getOptionsBoxGenome():
        return '__genome__'

    @staticmethod
    def getOptionsBoxParamInterRate(prevChoices):
        return ''
    
    @staticmethod
    def getOptionsBoxParamIntraRate(prevChoices):
        return ''
    
    @staticmethod
    def getOptionsBoxParamInterProb(prevChoices):
        return ''
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        from quick.extra.SimulationTools import PointIter, SimulationPointIter

        genome = choices.genome

        if choices.paramInterRate == '':
            paramInterRate = [0.0000001]
        else:
            paramInterRate = choices.paramInterRate
            paramInterRate = paramInterRate.replace(' ', '')
            paramInterRate = paramInterRate.split(",")

        if choices.paramIntraRate == '':
            paramIntraRate = [0.0000001]
        else:
            paramIntraRate = choices.paramIntraRate
            paramIntraRate = paramIntraRate.replace(' ', '')
            paramIntraRate = paramIntraRate.split(",")

        if choices.paramInterProb == '':
            paramInterProb = [0.0000001]
        else:
            paramInterProb = choices.paramInterProb
            paramInterProb = paramInterProb.replace(' ', '')
            paramInterProb = paramInterProb.split(",")



        if len(paramInterProb) == len(paramIntraRate) and len(paramIntraRate)==len(paramInterRate):

            g = SimulationPointIter()
            outGSuite = GSuite()
            for trackNameEl in range(0, len(paramIntraRate)):

                fileName = 'syn-'+ 'iInterR-' + str(paramInterRate[trackNameEl]) + 'iIntraR-' + str(paramIntraRate[trackNameEl]) + 'prob-' + str(paramInterProb[trackNameEl]) + '--' + str(trackNameEl)

                uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                    extraFileName=fileName,
                                                    suffix='bed')

                gSuiteTrack = GSuiteTrack(uri)
                outFn = gSuiteTrack.path
                ensurePathExists(outFn)

                g.createChrTrack(genome, 'chr1',  PointIter, outFn, paramInterRate[trackNameEl], paramIntraRate[trackNameEl], paramInterProb[trackNameEl])

                outGSuite.addTrack(GSuiteTrack(uri, title=''.join(fileName), genome=genome))

            GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['synthetic GSuite'])



    @staticmethod
    def validateAndReturnErrors(choices):
        genome = choices.genome

        if choices.paramInterRate == '':
            paramInterRate = [0.0000001]
        else:
            paramInterRate = choices.paramInterRate
            paramInterRate = paramInterRate.replace(' ', '')
            paramInterRate = paramInterRate.split(",")

        if choices.paramIntraRate == '':
            paramIntraRate = [0.0000001]
        else:
            paramIntraRate = choices.paramIntraRate
            paramIntraRate = paramIntraRate.replace(' ', '')
            paramIntraRate = paramIntraRate.split(",")

        if choices.paramInterProb == '':
            paramInterProb = [0.0000001]
        else:
            paramInterProb = choices.paramInterProb
            paramInterProb = paramInterProb.replace(' ', '')
            paramInterProb = paramInterProb.split(",")


        if len(paramInterProb) != len(paramIntraRate) or len(paramIntraRate)!=len(paramInterRate):
            return 'Number of parameters are not equal'

        return None

    @staticmethod
    def getToolDescription():

        htmlCore = HtmlCore()
        htmlCore.begin()

        htmlCore.header('Example 1:')
        htmlCore.line('Tool with the default values generate GSuite with one track')
        htmlCore.header('Example 2:')
        htmlCore.line('Tool with the following values:')
        htmlCore.line('- interRate: 0.0000001,0.0000001')
        htmlCore.line('- intraRate: 0.000001,0.000001')
        htmlCore.line('- interProb: 0.3, 0.2')
        htmlCore.line('generate GSuite with two tracks')

        htmlCore.end()

        return htmlCore

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('synthetic GSuite', 'gsuite')]
        
class divideGSuite(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select file','track'),
                ('Gsuite name','gSuiteName'),
                ('Expression','param')
                ]


    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxGSuiteName(prevChoices):
        return ''
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''
        
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        #Track.trackname
        #store pickle 
        
        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        
        
        dataCopy=data[:]
        if choices.param !='':
            for el in choices.param.split(','):
                
                newlC = str(el)
                
                outputFile =  open(cls.makeHistElement(galaxyExt='gsuite',title=str(choices.gSuiteName) + ' (' + str(el) + ')'), 'w')
                output=''
                for d in range(0, len(data)):
                    if d<5:
                        output += data[d]
                        output +='\n'
                    else:
                        newData = data[d].split("\t")
                        if str(el) in newData[1]:
                            output += '\t'.join(newData)
                            output +='\n'
                            dataCopy.remove(data[d])
                
                outputFile.write(output) 
                outputFile.close()
                
                data=dataCopy[:]
                
                htmlCore.line('File ' + str(newlC) + ' is in the history.')

            
        htmlCore.end()
        
        htmlCore.hideToggle(styleClass='debug')
            
            
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

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'bed'



class removeStringFromGSuite(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Remove string from gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select file','track'),
                ('Expression','param')
                ]


    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''
        
        
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        output=''
        for d in range(0, len(data)):
            if d<5:
                output += data[d]
            else:
                newData = data[d].split("\t")
                newData[1] = newData[1].replace(str(choices.param), '')
                
                output += '\t'.join(newData)
            output +='\n'
        
        open(galaxyFn,'w').write(output)  
        
        
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

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'




class removeFromBedFile(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Remove string from bed files"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','bedFile'),
                ('Name','nameBox'),
                ('Parameter','par')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement('bed')
          
    
    @staticmethod
    def getOptionsBoxNameBox(prevChoices):            
        return ''
    
    @staticmethod
    def getOptionsBoxPar(prevChoices):            
        return ''
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')  
        with inputFile as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        
        headerFirst = 'track name="' + str(choices.nameBox) + '" description="' + str(choices.nameBox) + '" priority=1'
        
        outputFile=open(galaxyFn,"w")
        outputFile.write(headerFirst + '\n')
        
        for d in range(0, len(data)):
            if not choices.par in data[d]:
                outputFile.write(data[d] + '\n')    
        
        inputFile.close()
        outputFile.close()
     
        
                        
            
        
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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
        return 'bed'

class divideBedFileTool(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file through columns"

    @staticmethod
    def getInputBoxNames():
        return [('Select file','bedFile'),
                ('Select name of columns','cols')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement()
          
    
    @staticmethod
    def getOptionsBoxCols(prevChoices):
        
        listCol=[]
        if prevChoices.bedFile:
            inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.bedFile.split(':')), 'r')  
            with inputFile as f:
                data=[x.strip('\n') for x in f.readlines()]
            f.closed
            inputFile.close()
            
            return data[0].split("\t")#4
            
        return listCol
                
           
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        
        listCol=[]
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')  
        with inputFile as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        inputFile.close()
        
        countLineNum = 6
        countHeaderLine = 0#4
        
        num=0
        lenDD=0
        for d in range(0, len(data)):
            dd = data[d].split("\t")
            if d == countHeaderLine:
                lenDD = len(dd)
                num = data[countHeaderLine].split("\t").index(choices.cols)
            if d>=countLineNum and len(dd) == lenDD:
                if dd[num] not in listCol:
                    listCol.append(dd[num])
            
        
        
#         from gold.gsuite.GSuite import GSuite
#         from gold.description.TrackInfo import TrackInfo
#         from gold.gsuite.GSuiteTrack import HbGSuiteTrack, GSuiteTrack, GalaxyGSuiteTrack, HttpGSuiteTrack
#         from gold.gsuite import GSuiteComposer
#         
#         outGSuite = GSuite()
        
        print 'Start making history elements'
        
        i=0
        for lC in listCol:
            if i < 700:
                newlC = str(lC).replace('_', '-').replace('--', '-')
                 
                outputFile =  open(cls.makeHistElement(galaxyExt='gtrack',title=str(newlC)), 'w')
                lenDD=0
                for d in range(0, len(data)):
                    dd = data[d].split("\t")
                    if d < countLineNum:
                        outputFile.write(data[d] + '\n')
                    if d == countHeaderLine:
                        lenDD = len(dd)
                    if d>=countLineNum and len(dd) == lenDD:
                        if dd[num] == str(lC):
                            outputFile.write(data[d] + '\n')    
                  
                outputFile.close()
                print 'File: ' + str(newlC) + ' is in the history' + '<br\>'
                
#                 outputFile=''
#                 outStaticFile = GalaxyRunSpecificFile([md5(str(newlC)).hexdigest() + '.gtrack'], galaxyFn)
#                 f = outStaticFile.getFile('w')
#                 lenDD=0
#                 for d in range(0, len(data)):
#                     dd = data[d].split("\t")
#                     if d < countLineNum:
#                         outputFile += data[d] + '\n'
#                     if d == countHeaderLine:
#                         lenDD = len(dd)
#                     if d>=countLineNum and len(dd) == lenDD:
#                         if dd[num] == str(lC):
#                             outputFile += data[d] + '\n'   
#                 
#                 f.write(outputFile)
#                 f.close()
#                 
#                 trackName = str(newlC)
#                 uri = HbGSuiteTrack.generateURI(trackName=trackName)
#                 outGSuite.addTrack(GSuiteTrack(uri, trackType='points', genome='hg19'))
                
     
            i+=1
            
#         GSuiteComposer.composeToFile(outGSuite, galaxyFn)
   
                        
    
   
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

class divideBedFile(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','bedFile'),
                ('Select name of columns','rows')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement('bed')
          
    
    @staticmethod
    def getOptionsBoxRows(prevChoices):
        
        listCol=[]
        if prevChoices.bedFile:
            with open(ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.bedFile.split(':')), 'r') as f:
                data=[x.strip('\n') for x in f.readlines()]
            f.closed
            
            lenDD=0
            for d in range(0, len(data)):
                dd = data[d].split("\t")
                if d == 1:
                    lenDD = len(dd)
                if len(dd) == lenDD:
                    if dd[3] not in listCol:
                        listCol.append(dd[3])
            
                    
        return listCol
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')  
        with inputFile as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        
        headerFirst = 'track name="' + str(choices.rows) + '" description="' + str(choices.rows) + '" priority=1'
        
        outputFile=open(galaxyFn,"w")
        outputFile.write(headerFirst + '\n')
        lenDD=0
        for d in range(0, len(data)):
            dd = data[d].split("\t")
            if d == 1:
                lenDD = len(dd)
            if len(dd) == lenDD:
                if dd[3] == str(choices.rows):
                    outputFile.write(data[d] + '\n')    
        
        inputFile.close()
        outputFile.close()
     
        
                        
            
        
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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
        return 'bed'
    

class divideBedFileV2(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file into bed files"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','bedFile'),
                ('Expression','param'),
                ('Contain','paramString')
                ]

    @staticmethod
    def getOptionsBoxBedFile():
        return GeneralGuiTool.getHistorySelectionElement('bed')
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''
    
    @staticmethod
    def getOptionsBoxParamString(prevChoices):
        return ['Full string', 'Part string']
          
    
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        
        
        listCol=[]
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.bedFile.split(':')), 'r')  
        with inputFile as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        lenDD=0
        for d in range(0, len(data)):
            dd = data[d].split("\t")
            if d == 1:
                lenDD = len(dd)
            if len(dd) == lenDD:
                if dd[3] not in listCol:
                    listCol.append(dd[3])
            
        
        
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        
        if choices.param =='':
        
            for lC in listCol:
                newlC = str(lC).replace('_', '-').replace('--', '-')
                headerFirst = 'track name="' + str(newlC) + '" description="' + str(newlC) + '" priority=1'
                
                #outStaticFile = GalaxyRunSpecificFile([md5(str(lC)).hexdigest() + '.bed'], galaxyFn)
                #outputFile = outStaticFile.getFile('w')
                
                outputFile =  open(cls.makeHistElement(galaxyExt='bed',title=str(newlC)), 'w')
                
                outputFile.write(headerFirst + '\n')
                lenDD=0
                for d in range(0, len(data)):
                    dd = data[d].split("\t")
                    if d == 1:
                        lenDD = len(dd)
                    if len(dd) == lenDD:
                        if dd[3] == str(lC):
                            outputFile.write(data[d] + '\n')    
                
                inputFile.close()
                outputFile.close()
                
                htmlCore.line('File ' + str(newlC) + ' is in the history.')
                #htmlCore.line(outStaticFile.getLoadToHistoryLink('%s' %lC, 'bed'))
            
        else:
            if choices.paramString == 'Full string':
                for el in choices.param.split(','):
                    newlC = str(el)
                    headerFirst = 'track name="' + str(newlC) + '" description="' + str(newlC) + '" priority=1'
                    outputFile =  open(cls.makeHistElement(galaxyExt='bed',title=str(newlC)), 'w')
                    #outStaticFile = GalaxyRunSpecificFile([md5(str(lC)).hexdigest() + '.bed'], galaxyFn)
                    #outputFile = outStaticFile.getFile('w')
                    outputFile.write(headerFirst + '\n')
                    for lC in listCol:
                        if el in lC:
                            lenDD=0
                            for d in range(0, len(data)):
                                dd = data[d].split("\t")
                                if d == 1:
                                    lenDD = len(dd)
                                if len(dd) == lenDD:
                                    if dd[3] == str(lC):
                                        outputFile.write(data[d] + '\n')    
                            
                    outputFile.close()
                    
                    htmlCore.line('File ' + str(newlC) + ' is in the history.')
                    #htmlCore.line(outStaticFile.getLoadToHistoryLink('%s' %lC, 'bed'))
            elif choices.paramString == 'Part string':
                for el in choices.param.split(','):
                    newlC = str(el)
                    headerFirst = 'track name="' + str(newlC) + '" description="' + str(newlC) + '" priority=1'
                    outputFile =  open(cls.makeHistElement(galaxyExt='bed',title=str(newlC)), 'w')
                    #outStaticFile = GalaxyRunSpecificFile([md5(str(lC)).hexdigest() + '.bed'], galaxyFn)
                    #outputFile = outStaticFile.getFile('w')
                    outputFile.write(headerFirst + '\n')
                    for lC in listCol:
                        if el in lC:
                            lenDD=0
                            for d in range(0, len(data)):
                                if len(data[d]) > 1:
                                    dd = data[d].split("\t")
                                    if d == 1:
                                        lenDD = len(dd)
                                    if len(dd) == lenDD:
                                        if str(lC) in dd[3]:
                                            outputFile.write(data[d] + '\n')
                                            data[d] = []
                               
                            
                            
                    outputFile.close()
                    
                    htmlCore.line('File ' + str(newlC) + ' is in the history.')
                
            
        htmlCore.end()
        
        htmlCore.hideToggle(styleClass='debug')
            
            
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

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'

class showGSuiteResultsInTable(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Show gSuite results in table"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','gSuite'),
                ('Select name of columns','rows'),
                ('Select name of rows','columns')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
          
    
    @staticmethod
    def getOptionsBoxRows(prevChoices):
        return ''
    
    @staticmethod
    def getOptionsBoxColumns(prevChoices):
        return ''
    
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.gSuite.split(':')), 'r') as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
           
        for d in range(0, 5):
            del data[0]
        
        nRows=[]
        for el in choices.rows.split(','):
            nRows.append([el.replace(' ',''), len(el)])
        
        from operator import itemgetter
        nRows.sort(key=itemgetter(1), reverse=True)
        
        
        output=[]
        inx=[]
        for el in nRows:
            for iEl in inx:
                del data[data.index(iEl)]
                inx=[]
            
            for d in range(0, len(data)):
                dd = data[d].split("\t")
                if dd[1].find(el[0]) != -1:
                    for elCol in choices.columns.split(','):
                        if dd[1].find(elCol.replace(' ','')) != -1:
                            output.append([el[0], elCol, dd[2]])
                            inx.append(data[d])
        
        
        output.sort(key=itemgetter(1, 0))
        
        
        res=[]
        resTab=[]
        el = output[0][1]
        res.append(el)
        firstEl=False
        header=['Tracks']
        for inEl in range(0, len(output)):
            if output[inEl][0] not in header:
                header.append(output[inEl][0])
            if el == output[inEl][1]:
                res.append(output[inEl][2])
            else:
                resTab.append(res)
                res=[]
                res.append(output[inEl][1])
                res.append(output[inEl][2])
                el = output[inEl][1]
        resTab.append(res)
                            
            
        
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.header('Results') 
        htmlCore.tableHeader(header, sortable=True, tableId=1)
        for el in resTab:
            htmlCore.tableLine(el)
        htmlCore.end()
        
        htmlCore.hideToggle(styleClass='debug')
        
        
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
        
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'
        
        
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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
        return 'html'


class gSuiteInverse(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Do inverse for gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','gSuite')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
          
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        #use gSuite from option
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        tracks = list(gSuite.allTracks())

        for track in tracks:
            tr = ('/').join(track.trackName)
            print ExternalTrackManager.extractFnFromGalaxyTN("hb:/Private/GK/Hilde/Mutations/eta-")
            with open(ExternalTrackManager.extractFnFromGalaxyTN("hb:/Private/GK/Hilde/Mutations/eta-"), 'r') as f:
                data=[x.strip('\n') for x in f.readlines()]
            f.closed
            print data
            
            
        
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'
        
        
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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
        return 'html'

class VisTrackFrequencyBetweenTwoTracks(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot frequency of mutation alonge the chromosomes for each pair separately in gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','gSuite1'),
                ('Select statistic', 'statistic1'),
                ('Select track collection GSuite','gSuite2'),
                ('Select statistic', 'statistic2'),
                ('User bin source', 'binSourceParam')
                ]
   

    @staticmethod
    def getOptionsBoxGSuite1():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxStatistic1(prevChoices):
        return ['Count Point', 'Count Segment']
    
    @staticmethod
    def getOptionsBoxGSuite2(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxStatistic2(prevChoices):
        return ['Count Point', 'Count Segment', 'Count Proportion']
    

    @staticmethod
    def getOptionsBoxBinSourceParam(prevChoices):
        return ''
    
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        from gold.statistic.CountPointStat import CountPointStat
        from gold.statistic.CountSegmentStat import CountSegmentStat
        from quick.statistic.ProportionCountPerBinAvgStat import ProportionCountPerBinAvgStat
        
        if choices.statistic1 == 'Count Point':
            analysisSpec1 = AnalysisSpec(CountPointStat)
        elif choices.statistic1 == 'Count Segment':
            analysisSpec1 = AnalysisSpec(CountSegmentStat)
        elif choices.statistic1=='Count Proportion':
            analysisSpec1 = AnalysisSpec(ProportionCountPerBinAvgStat)
            
        
        #use gSuite from option
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        tracks = list(gSuite1.allTracks())

        if choices.binSourceParam:
            binSourceParam = choices.binSourceParam
        else:
            binSourceParam = '1M'
        
          
        from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs  
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('plotDiv')
        
        
        
        from operator import itemgetter

            
            
        title1 = choices.gSuite1
        title2 = choices.gSuite2
        
        import urllib2
        title1 = urllib2.unquote(title1.split('/')[-1])
        title2 = urllib2.unquote(title2.split('/')[-1])
        
        if choices.statistic2 == 'Count Point':
            analysisSpec2 = AnalysisSpec(CountPointStat)
        elif choices.statistic2 == 'Count Segment':
            analysisSpec2 = AnalysisSpec(CountSegmentStat)
        elif choices.statistic2=='Count Proportion':
            analysisSpec2 = AnalysisSpec(ProportionCountPerBinAvgStat)
        
        #use gSuite from option
        gSuite2 = getGSuiteFromGalaxyTN(choices.gSuite2)
        
        tracks2 = list(gSuite2.allTracks())
        
        #visResgSuiteY1=[]
        #visResgSuiteY2=[]
        
        seriesNameRes=[]
        listResRes=[]
        title1Res=[]
        title2Res=[]
        titleText=[]
        
        visRes1All=OrderedDict()
        visRes2All=OrderedDict()
        
        countChr=0
        for chr in GenomeInfo.getChrList(gSuite1.genome):      
            
            titleText.append('Visualization for the ' + str(chr))
            categories=[]
            seriesName1=[]
            seriesType1=[]
            analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite1.genome)
            #results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
            inx=0
            visRes1=[]
            plotBandsMax=0
            
            for track in tracks:
                visResTrack=[]
                dataY=[]
                results = doAnalysis(analysisSpec1, analysisBins, [PlainTrack(track.trackName)])
                for index, track1 in enumerate(results):
                    visResTrack.append(results[track1]['Result'])
                    #print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                    dataY.append([track1.start, track1.end, results[track1]['Result']])
                dataY.sort(key=itemgetter(0))
                visResTrack=[elDataY[2] for elDataY in dataY]
                if inx ==0:
                    categories=[str(elDataY[0])+"-"+str(elDataY[1]) for elDataY in dataY]
                
                if max(dataY,key=itemgetter(2))[2] >= plotBandsMax:
                    plotBandsMax=max(dataY,key=itemgetter(2))[2]
                
                seriesName1.append(track.trackName[-1].replace("'",''))
                seriesType1.append('bubble')
                visRes1.append(visResTrack)
                inx+=1
                
            #visResgSuiteY1.append(visRes)
            
            seriesName2=[]
            seriesType2=[]
            analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite2.genome)
            #results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
            inx=0
            visRes2=[]
            plotBandsMax=0
            for track in tracks2:
                visResTrack=[]
                dataY=[]
                results = doAnalysis(analysisSpec2, analysisBins, [PlainTrack(track.trackName)])
                for index, track1 in enumerate(results):
                    visResTrack.append(results[track1]['Result'])
                    #print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                    dataY.append([track1.start, track1.end, results[track1]['Result']])
                dataY.sort(key=itemgetter(0))
                visResTrack=[elDataY[2] for elDataY in dataY]
                #if inx ==0:
                #    categories2=[str(elDataY[0])+"-"+str(elDataY[1]) for elDataY in dataY]
                
                if max(dataY,key=itemgetter(2))[2] >= plotBandsMax:
                    plotBandsMax=max(dataY,key=itemgetter(2))[2]
                
                seriesName2.append(track.trackName[-1].replace("'",''))
                seriesType2.append('bubble')
                visRes2.append(visResTrack)
                inx+=1
                
            
            
            
            dictTemp=OrderedDict()
            for numElY1 in range(0, len(visRes1)):
                if countChr==0:
                    visRes1All[numElY1] = visRes1[numElY1]
                else:
                    visRes1All[numElY1] += visRes1[numElY1]
                if not numElY1 in dictTemp.keys():
                    dictTemp[numElY1]=OrderedDict()
                for numElY2 in range(0, len(visRes2)):
                    if countChr==0:
                        visRes2All[numElY2] = visRes2[numElY2] 
                    else:
                        visRes2All[numElY2] += visRes2[numElY2] 
                    if not numElY2 in dictTemp[numElY1].keys():
                        dictTemp[numElY1][numElY2]=OrderedDict()
                    pair = zip(visRes1[numElY1], visRes2[numElY2])
                    for el in pair:
                        if not el in dictTemp[numElY1][numElY2].keys():
                            dictTemp[numElY1][numElY2][el]=1
                        else:
                            dictTemp[numElY1][numElY2][el]+=1
            
            
            listRes=[]
            seriesName=[]
            
            for key1, item1 in dictTemp.items():
                for key2, item2 in item1.items():
                    listResPart=[]
                    for key3, item3 in item2.items():
                        listResPart.append(list(key3) + [item3])
                    listRes.append(listResPart)
                    seriesName.append(seriesName1[key1] + ' X ' + seriesName2[key2])
            seriesNameRes.append(seriesName)
            listResRes.append(listRes)
            
            
            
            countChr+=1   
        
        
        
 
        dictTemp=OrderedDict()
        for numElY1 in range(0, len(visRes1All)):
            if not numElY1 in dictTemp.keys():
                dictTemp[numElY1]=OrderedDict()
            for numElY2 in range(0, len(visRes2All)):
                if not numElY2 in dictTemp[numElY1].keys():
                    dictTemp[numElY1][numElY2]=OrderedDict()
                pair = zip(visRes1All[numElY1], visRes2All[numElY2])
                for el in pair:
                    if not el in dictTemp[numElY1][numElY2].keys():
                        dictTemp[numElY1][numElY2][el]=1
                    else:
                        dictTemp[numElY1][numElY2][el]+=1
        
        
        
        listRes=[]
        seriesName=[]
        for key1, item1 in dictTemp.items():
            for key2, item2 in item1.items():
                listResPart=[]
                for key3, item3 in item2.items():
                    listResPart.append(list(key3) + [item3])
                listRes.append(listResPart)
                seriesName.append(seriesName1[key1] + ' X ' + seriesName2[key2])
        seriesNameRes.append(seriesName)
        listResRes.append(listRes)
        
        
        vg = visualizationGraphs()
        res = vg.drawBubbleCharts(
            listResRes,
            seriesName = seriesNameRes,
            titleText = titleText + ['Visualization through all chromosomes'],
            label = '<b>{series.name}</b>: {point.x} {point.y} value: {point.z}',
            height = 400,
            xAxisTitle = title1,
            yAxisTitle = title2,
            visible=False,
            marginTop=30,
            addTable=True
            )
        htmlCore.line(res)
        
    #                 print title1
    #                 print title2
    #                 print "categories=" + str(categories)
    #                 print "dataY1=" + str(visRes1)
    #                 print "dataY2=" + str(visRes2)
    #                 print "seriesName1=" + str(seriesName1)
    #                 print "seriesName2=" + str(seriesName2)
    #                 print "seriesType1=" + str(seriesType1)
    #                 print "seriesType2=" + str(seriesType2)
                    
                
            
        
        htmlCore.divEnd()
        htmlCore.end()
        
        htmlCore.hideToggle(styleClass='debug')

        
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
        
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite1)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        if gSuite1.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite1.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite1.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite1.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'
        
        
        return None
  
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'



class VisTrackFrequency(GeneralGuiTool):
    
    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Plot frequency of mutation alonge the chromosomes in gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select way of plotting','showResults'),
                ('Select track collection GSuite','gSuite1'),
                ('Select statistic', 'statistic1'),
                ('Select track collection GSuite','gSuite2'),
                ('Select statistic', 'statistic2'),
                ('Show on plot % the highest values', 'visParam'),
                ('User bin source', 'binSourceParam')
                ]
    
    @staticmethod
    def getOptionsBoxShowResults():
        return ['Show results separately','Show results on one plot']
   

    @staticmethod
    def getOptionsBoxGSuite1(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxStatistic1(prevChoices):
        return ['Count Point', 'Count Segment']
    
    @staticmethod
    def getOptionsBoxGSuite2(prevChoices):
        if prevChoices.showResults == 'Show results on one plot':
            return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxStatistic2(prevChoices):
        if prevChoices.showResults == 'Show results on one plot':
            return ['Count Point', 'Count Segment', 'Count Proportion']
    
    @staticmethod
    def getOptionsBoxVisParam(prevChoices):
        if prevChoices.showResults != 'Show results on one plot':
            return ['0', '10', '15', '20', '30', '40', '50']

    @staticmethod
    def getOptionsBoxBinSourceParam(prevChoices):
        return ''
    
    
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        
        from gold.statistic.CountPointStat import CountPointStat
        from gold.statistic.CountSegmentStat import CountSegmentStat
        from quick.statistic.ProportionCountPerBinAvgStat import ProportionCountPerBinAvgStat
        
        if choices.statistic1 == 'Count Point':
            analysisSpec1 = AnalysisSpec(CountPointStat)
        elif choices.statistic1 == 'Count Segment':
            analysisSpec1 = AnalysisSpec(CountSegmentStat)
        elif choices.statistic1=='Count Proportion':
            analysisSpec1 = AnalysisSpec(ProportionCountPerBinAvgStat)
            
        
        #use gSuite from option
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        tracks = list(gSuite1.allTracks())

        if choices.binSourceParam:
            binSourceParam = choices.binSourceParam
        else:
            binSourceParam = '1M'
        
        import quick.webtools.restricted.visualization.visualizationPlots as vp    
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('plotDiv')
        htmlCore.line(vp.addJSlibs())
        htmlCore.line(vp.addJSlibsExport())
        htmlCore.line(vp.axaddJSlibsOverMouseAxisisPopup())
        
        
        plotNumber=0
        
        from operator import itemgetter
        
        if choices.showResults == 'Show results separately':
            
            for chr in GenomeInfo.getChrList(gSuite1.genome):            
                categories=[]
                seriesName=[]
                seriesType=[]
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite1.genome)
                #results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx=0
                visRes=[]
                plotBandsMax=0
                for track in tracks:
                    visResTrack=[]
                    dataY=[]
                    results = doAnalysis(analysisSpec1, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        #print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack=[elDataY[2] for elDataY in dataY]
                    if inx ==0:
                        categories=[str(elDataY[0])+"-"+str(elDataY[1]) for elDataY in dataY]
                    
                    if max(dataY,key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax=max(dataY,key=itemgetter(2))[2]
                    
                    seriesName.append(track.trackName[-1].replace("'",''))
                    seriesType.append('line')
                    visRes.append(visResTrack)
                    inx+=1
                    
                htmlCore.line(vp.drawChartMulti([visRes],
                                                plotNumber=plotNumber,
                                                seriesType=[seriesType],
                                                legend=False, 
                                                minWidth=300,
                                                height=700,
                                                lineWidth=1, 
                                                titleText='Visualization for frequency of mutation along the ' + str(chr), 
                                                yAxisTitle=['Value'],
                                                seriesName = seriesName,
                                                enabled=True,
                                                categories=categories,
                                                interaction=False,
                                                plotBandsY=[int(plotBandsMax-float(choices.visParam)/100*plotBandsMax), plotBandsMax, '#FDFD96', str(choices.visParam) + '% the highest values']
                                                ))
                plotNumber+=1
            

        if choices.showResults == 'Show results on one plot':
            
            
            title1 = choices.gSuite1
            title2 = choices.gSuite2
            
            import urllib2
            title1 = urllib2.unquote(title1.split('/')[-1])
            title2 = urllib2.unquote(title2.split('/')[-1])
            
            if choices.statistic2 == 'Count Point':
                analysisSpec2 = AnalysisSpec(CountPointStat)
            elif choices.statistic2 == 'Count Segment':
                analysisSpec2 = AnalysisSpec(CountSegmentStat)
            elif choices.statistic2=='Count Proportion':
                analysisSpec2 = AnalysisSpec(ProportionCountPerBinAvgStat)
            
            #use gSuite from option
            gSuite2 = getGSuiteFromGalaxyTN(choices.gSuite2)
            
            tracks2 = list(gSuite2.allTracks())
            
            #visResgSuiteY1=[]
            #visResgSuiteY2=[]
            
            for chr in GenomeInfo.getChrList(gSuite1.genome):            
                categories=[]
                seriesName1=[]
                seriesType1=[]
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite1.genome)
                #results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx=0
                visRes1=[]
                plotBandsMax=0
                
                for track in tracks:
                    visResTrack=[]
                    dataY=[]
                    results = doAnalysis(analysisSpec1, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        #print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack=[elDataY[2] for elDataY in dataY]
                    if inx ==0:
                        categories=[str(elDataY[0])+"-"+str(elDataY[1]) for elDataY in dataY]
                    
                    if max(dataY,key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax=max(dataY,key=itemgetter(2))[2]
                    
                    seriesName1.append(track.trackName[-1].replace("'",''))
                    seriesType1.append('line')
                    visRes1.append(visResTrack)
                    inx+=1
                    
                #visResgSuiteY1.append(visRes)
                
                seriesName2=[]
                seriesType2=[]
                analysisBins = UserBinSource(chr, binSourceParam, genome=gSuite2.genome)
                #results = doAnalysisSupportingGsuite(analysisSpec, analysisBins, [gSuite])#not working
                inx=0
                visRes2=[]
                plotBandsMax=0
                for track in tracks2:
                    visResTrack=[]
                    dataY=[]
                    results = doAnalysis(analysisSpec2, analysisBins, [PlainTrack(track.trackName)])
                    for index, track1 in enumerate(results):
                        visResTrack.append(results[track1]['Result'])
                        #print str(inx) + " " + str(index) + " " + str(results[track1]) + " " + str(track1) + " " + str(track.trackName)
                        dataY.append([track1.start, track1.end, results[track1]['Result']])
                    dataY.sort(key=itemgetter(0))
                    visResTrack=[elDataY[2] for elDataY in dataY]
                    #if inx ==0:
                    #    categories2=[str(elDataY[0])+"-"+str(elDataY[1]) for elDataY in dataY]
                    
                    if max(dataY,key=itemgetter(2))[2] >= plotBandsMax:
                        plotBandsMax=max(dataY,key=itemgetter(2))[2]
                    
                    seriesName2.append(track.trackName[-1].replace("'",''))
                    seriesType2.append('line')
                    visRes2.append(visResTrack)
                    inx+=1
                
                htmlCore.line(vp.drawMultiYAxis(
                    dataY1=visRes1,
                    dataY2=visRes2,
                    categories= categories,
                    titleText='Visualization for the ' + str(chr),
                    minWidth=300,
                    height=700,
                    title1=title1,
                    title2=title2,
                    seriesType1=seriesType1,
                    seriesName1=seriesName1,
                    seriesType2=seriesType2,
                    seriesName2=seriesName2,
                    plotNumber=plotNumber
                    ))
                
                '''
                print title1
                print title2
                print "categories=" + str(categories)
                print "dataY1=" + str(visRes1)
                print "dataY2=" + str(visRes2)
                print "seriesName1=" + str(seriesName1)
                print "seriesName2=" + str(seriesName2)
                print "seriesType1=" + str(seriesType1)
                print "seriesType2=" + str(seriesType2)
                '''
                
                plotNumber+=1
            
            
        
        htmlCore.divEnd()
        htmlCore.end()
        
        htmlCore.hideToggle(styleClass='debug')

        
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
        
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite1)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite1 = getGSuiteFromGalaxyTN(choices.gSuite1)
        if gSuite1.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite1.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite1.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite1.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'
        
        
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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
        return 'html'


    
class gSuiteName(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "gSuite for 4D"

    @staticmethod
    def getInputBoxNames():
        return [('Select file','track')
                ]


    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''
        
        
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        output=''
        for d in range(0, len(data)):
            if d<5:
                output += data[d]
            else:
                newData = data[d].split("\t")
                if len(newData) == 7:
                    newData[1] = str(newData[2]) + ' ' + str(newData[3]) + ' ' + str(newData[4])
                else:
                    newData[1] = str(newData[2]) + ' ' + str(newData[3])
                output += '\t'.join(newData)
            output +='\n'
        
        open(galaxyFn,'w').write(output)  
        
        
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

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'





class KseniagSuite(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Ksenia gSuite for 3D"

    @staticmethod
    def getInputBoxNames():
        return [('Select file','track')
                ]


    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''
        
        
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r') as f:
            data=[x.strip('\n') for x in f.readlines()]
        f.closed
        
        ll=[]
        for i in data:
            new = [x for x in i.split()]
            ll.append(new)
        
        
        targetTracksDict = []
        d=[]
        i=0
        for l in ll:
            if i>4:
                if i== 5:
                    fv1=l[2]
                if fv1 != l[2]:
                    dd={'folderName1':fv1, 'data': d}
                    targetTracksDict.append(dd)
                    fv1 = l[2]
                    dd={}
                    d=[]
                path = l[0].split('/')
                path.pop(0)
                d.append({'folderName2': l[1], 'trackName': 'file.bed', 'trackPath' : path})
                    
                if len(ll)-1 == i:
                    dd={'folderName1':fv1, 'data': d}
                    targetTracksDict.append(dd)
            i+=1
        
        print 'targetTracksDict='+str(targetTracksDict)
        
               
        
        
        
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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
        return 'html'




class DivideBedFileForChosenPhrase(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Divide bed file according to some string"

    @staticmethod
    def getInputBoxNames():
        return [('Select track','track'), \
                ('Parametr', 'param')
                ]


    @staticmethod
    def getOptionsBoxTrack():
        return GeneralGuiTool.getHistorySelectionElement('bed')
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        return ''
        
        
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):

        outputFile=open(galaxyFn,"w")
        inputFile = open(ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':')), 'r')
        
        resMutList=[]
        i=0
        for line in inputFile:
            for l in line.split(): 
                if l.find("".join(choices.param)) != -1:
                    resMutList.append(line)            
        
        for res in resMutList:
            outputFile.write(res)
        
        inputFile.close()
        outputFile.close()
        
        
        
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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
        return 'bed'

class GenerateRipleysK(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compute RipleysK for gSuite"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','gSuite'),
                ('Bp window', 'param'),
                ('if only in regions in gSuite', 'chParam'),
                ('Select track from history (Accepted formats: bed)','track'),
                ('Show results', 'showResults')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())
            
            if len(tracks) >0 and gSuite.isPreprocessed():
                return OrderedDict([
                    ('2', False), 
                    ('5', False), 
                    ('10', False), 
                    ('100', True), 
                    ('1000', False),
                    ('10000', False),
                    ('100000', False),
                    ('1000000', False)
                    ])
    @staticmethod
    def getOptionsBoxChParam(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())
            
            if len(tracks) >0 and gSuite.isPreprocessed():
                return OrderedDict([
                    ('Yes', True),
                    ('No', False)
                    ])
    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())
    
            return GeneralGuiTool.getHistorySelectionElement('category.bed', 'bed')
                        
    
    @staticmethod
    def getOptionsBoxShowResults(prevChoices):
        if prevChoices.param:
            return ['Show results per table','Show results in one table']
        
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        analysisSpec = AnalysisSpec(RipleysKStat)
        
        #one table per bpW
        
        print choices.showResults 
        
        if choices.showResults == 'Show results per table':
        
            htmlCore = HtmlCore()
            htmlCore.begin()
            htmlCore.divBegin('resDiv')
            selectedBpWindow = [key for key,val in choices.param.iteritems() if val == 'True']
            for bpW in selectedBpWindow:
                htmlCore.header('Compute RipleysK for bp window: ' + str(bpW))
                htmlCore.tableHeader(['Track names'] + ['Value'] + ['Ranking'], sortable=True, tableId='resultsTable_'+str(bpW))
                analysisSpec.addParameter("bpWindow", str(bpW))
            
                #use gSuite from option
                gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
                tracks = list(gSuite.allTracks())
                
                import scipy.stats as statRank
                
                row=[]
                elChParam = [key for key,val in choices.param.iteritems() if val == 'True']
                for track in tracks:
                    #analysisBins = GlobalBinSource(gSuite.genome)
                    
                    if str(elChParam[0])=='Yes':                        
                        binFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':'))
                        analysisBins = UserBinSource('bed', binFn, genome=gSuite.genome)
                        
                    else:    
                        analysisBins = UserBinSource('*', '10m', genome=gSuite.genome)
                   
                    result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName)])
                    resultDict = result.getGlobalResult()
                    row.append(resultDict['Result'])
                
                rank = len(row)+1 - statRank.rankdata(row)
                
                for i in range(0, len(tracks)):
                    htmlCore.tableLine([tracks[i].trackName] + [row[i]] + [int(rank[i])])
                htmlCore.tableFooter()
            
            htmlCore.divEnd()
            htmlCore.end()
        else:
        #one table for everything
            htmlCore = HtmlCore()
            htmlCore.begin()
            htmlCore.divBegin('resDiv')
            selectedBpWindow = [key for key,val in choices.param.iteritems() if val == 'True']
            
            htmlCore.header('Compute RipleysK for bp window')
            htmlCore.tableHeader(['Track names'] + [ 'Values for bp window: ' + str(bpW) + ' (Ranking)' for bpW in selectedBpWindow], sortable=True, tableId='resultsTable_'+str(bpW))
            
            rowVisRes=[]
            rowCol=[]
            for bpW in selectedBpWindow:
                
                analysisSpec.addParameter("bpWindow", str(bpW))
            
                #use gSuite from option
                gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
                tracks = list(gSuite.allTracks())
                
                import scipy.stats as statRank
                
                row=[]
                countI=0
                elChParam = [key for key,val in choices.chParam.iteritems() if val == 'True']
                for track in tracks:
                    #analysisBins = GlobalBinSource(gSuite.genome)
                    
                    if str(elChParam[0])=='Yes':                        
                        binFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':'))
                        analysisBins = UserBinSource('bed', binFn, genome=gSuite.genome)
                        
                    else:    
                        analysisBins = UserBinSource('*', '10m', genome=gSuite.genome)
                       
                       
                    result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName)])
                    
                    resultDict = result.getGlobalResult()
                    row.append(resultDict['Result'])
            
                rank = len(row)+1 - statRank.rankdata(row)
                
                
                rowVis = []
                rowC=[]
                for i in range(0, len(tracks)):
                    rowC.append(str(row[i]) + " (" + str(int(rank[i])) + ")")
                    rowVis.append(row[i])
                rowCol.append(rowC)
                rowVisRes.append(rowVis)
            
            
            
            nRowColT = zip(*rowCol)
            nRowVisRes = map(list, (zip(*rowVisRes)))
            seriesName=[]
            
            for i in range(0, len(nRowColT)):
                tN=tracks[i].trackName
                seriesName.append(tN[len(tN)-1])
                newList= [tracks[i].trackName] + [el for el in list(nRowColT[i])]
                htmlCore.tableLine(el for el in newList)
            htmlCore.tableFooter()
            
            categories=[bpW for bpW in selectedBpWindow]
            
          
            
            from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs
            vg = visualizationGraphs()
            result = vg.drawLineChart(nRowVisRes,
                                        seriesName=seriesName,
                                        categories=categories,
                                        extraScriptButton=[OrderedDict({'Use linear scale':'linear','Use log10 scale':'logarithmic'}), 'yAxisType']
                                        )
            htmlCore.line(result)
            
            htmlCore.divEnd()
            htmlCore.end()
        

        htmlCore.hideToggle(styleClass='debug')

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
        
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'
        
        
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
    #@staticmethod
    #def isPublic():
    #    '''
    #    Specifies whether the tool is accessible to all users. If False, the
    #    tool is only accessible to a restricted set of users as defined in
    #    LocalOSConfig.py.
    #    '''
    #    return False
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
        return 'html'
    

class GenerateRipleysKForEachChromosomeSeparately(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compute RipleysK for  for each chromosome separately"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','gSuite'),
                ('Bp window', 'param'),
                ('if only in regions in gSuite', 'chParam'),
                ('Select track from history (Accepted formats: bed)','track')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxParam(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())
            
            if len(tracks) >0 and gSuite.isPreprocessed():
                return OrderedDict([
                    ('10', False), 
                    ('100', True), 
                    ('1000', False),
                    ('10000', False),
                    ('100000', False),
                    ('1000000', False)
                    ])
    @staticmethod
    def getOptionsBoxChParam(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())
            
            if len(tracks) >0 and gSuite.isPreprocessed():
                return OrderedDict([
                    ('Yes', True),
                    ('No', False)
                    ])
    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        if prevChoices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(prevChoices.gSuite)
            tracks = list(gSuite.allTracks())
    
            return GeneralGuiTool.getHistorySelectionElement('category.bed', 'bed')
                        
    
   
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        analysisSpec = AnalysisSpec(RipleysKStat)
        
        #one table per bpW
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('resDiv')
        selectedBpWindow = [key for key,val in choices.param.iteritems() if val == 'True']
        
        
        
        rowCol=[]
        for bpW in selectedBpWindow:
            
            analysisSpec.addParameter("bpWindow", str(bpW))
        
            #use gSuite from option
            gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
            tracks = list(gSuite.allTracks())
            
            nameTracks=[]

            row=[]
            countI=0
            elChParam = [key for key,val in choices.chParam.iteritems() if val == 'True']
            i=0
            for track in tracks:
                #analysisBins = GlobalBinSource(gSuite.genome)
                for chr in GenomeInfo.getChrList(gSuite.genome):  
                    if str(elChParam[0])=='Yes':                        
                        binFn = ExternalTrackManager.extractFnFromGalaxyTN(choices.track.split(':'))
                        analysisBins = UserBinSource('bed', binFn, genome=gSuite.genome)
                        
                    else:    
                        analysisBins = UserBinSource(chr, '10m', genome=gSuite.genome)
                       
                    nameTracks.append([str(tracks[i].trackName),str(chr)])   
                    result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName)])
                    
                    resultDict = result.getGlobalResult()
                     
                    if len(resultDict)==0:
                        row.append('No results')
                    else:
                        row.append(resultDict['Result'])
                i+=1        
        
                #rank = len(row)+1 - statRank.rankdata(row)
            
            rowC=[]
            for i in range(0, len(tracks)*len(GenomeInfo.getChrList(gSuite.genome))):
                rowC.append(str(row[i])) #+ " (" + str(int(rank[i])) + ")")
            rowCol.append(rowC)
        
        nRowColT = zip(*rowCol)
        
        nT = nameTracks[0][0]
        htmlCore.header('Compute RipleysK for bp window for' + str(nameTracks[0][0]))
        htmlCore.tableHeader(['Chr'] + [ 'Values for bp window: ' + str(bpW) + ' (Ranking)' for bpW in selectedBpWindow], sortable=True, tableId='resultsTable_'+str(bpW))
        for j in range(0, len(nameTracks)):
            if nT == nameTracks[j][0]:
                newList= [nameTracks[j][1]] + [el for el in list(nRowColT[j])]
                htmlCore.tableLine(el for el in newList)
            elif j == len(nameTracks)-1:
                newList= [nameTracks[j][1]] + [el for el in list(nRowColT[j])]
                htmlCore.tableFooter()
            else:
                htmlCore.tableFooter()
                htmlCore.header('Compute RipleysK for bp window for' + str(nameTracks[j][0]))
                htmlCore.tableHeader(['Chr'] + [ 'Values for bp window: ' + str(bpW) + ' (Ranking)' for bpW in selectedBpWindow], sortable=True, tableId='resultsTable_'+str(bpW))
                newList= [nameTracks[j][1]] + [el for el in list(nRowColT[j])]
                nT = nameTracks[j][0]
        
        htmlCore.divEnd()
        htmlCore.end()
        

        htmlCore.hideToggle(styleClass='debug')

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
        
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'
        
        
        return None

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'


from quick.statistic.TwoLevelOverlapPreferenceStat import TwoLevelOverlapPreferenceStat
class GenerateTwoLevelOverlapPreferenceStat(GeneralGuiTool):

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Compute Two level overlap preference"

    @staticmethod
    def getInputBoxNames():
        return [('Select track collection GSuite','gSuite'),
                ('Select track','track'),
                ('User bin source', 'binSourceParam')
                ]

    @staticmethod
    def getOptionsBoxGSuite():
        return GeneralGuiTool.getHistorySelectionElement('gsuite')
    
    @staticmethod
    def getOptionsBoxTrack(prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed')
  
    @staticmethod
    def getOptionsBoxBinSourceParam(prevChoices):
        return ''
        
    @staticmethod
    def execute(choices, galaxyFn=None, username=''):
        analysisSpec = AnalysisSpec(TwoLevelOverlapPreferenceStat)
        
        #use gSuite from option
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        tracks = list(gSuite.allTracks())
        
        trackComp = choices.track.split(':')
        
        trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(gSuite.genome, trackComp)
    
    
    
        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.divBegin('resDiv')
        htmlCore.header('Compute two level overlap for: ' + str(trackName))
        htmlCore.tableHeader(['Track names'] + ['Individual coverage per bin correlation (Ranking)'] + ['Ratio Of Obs To Exp Given Individual Bin Coverages (Ranking)'] + ['Ratio Of Obs To Exp Given Global Coverages (Ranking)'], sortable=True, tableId='resultsTable')
            
          
        
        import scipy.stats as statRank
        
        if choices.binSourceParam:
            binSourceParam = choices.binSourceParam
        else:
            binSourceParam = '10m'
        
        row=[]
        for track in tracks:
            analysisBins = UserBinSource('*', binSourceParam, genome=gSuite.genome)
            result = doAnalysis(analysisSpec, analysisBins, [PlainTrack(track.trackName), PlainTrack(trackName)])
            resultDict = result.getGlobalResult()
            row.append([resultDict['IndividualCoveragePerBinCorrelation'], resultDict['RatioOfObsToExpGivenIndividualBinCoverages'], resultDict['RatioOfObsToExpGivenGlobalCoverages']])
            
        newRow = zip(*row)
        rank=[]
        for nr in range(0, len(newRow)):
            rank.append(len(newRow[nr])+1 - statRank.rankdata(newRow[nr]))
        
        rankRes = zip(*rank)
        buildRow=[]
        for i in range(0, len(row)):
            partEl=[]
            for j in range(0, len(row[i])):
                partEl += [str(row[i][j]) + " ("  + str(int(rankRes[i][j])) + ")"]
            buildRow.append(partEl)
        
        for i in range(0, len(tracks)):
            htmlCore.tableLine([tracks[i].trackName] + buildRow[i])
        htmlCore.tableFooter()
        
        htmlCore.divEnd()
        htmlCore.end()
        
        htmlCore.hideToggle(styleClass='debug')
        
        print htmlCore
    @staticmethod
    def validateAndReturnErrors(choices):
        '''-
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        
        from gold.gsuite.GSuiteConstants import UNKNOWN, MULTIPLE

        errorStr = GeneralGuiTool._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        if gSuite.numTracks() == 0:
            return 'Please select a GSuite file with at least one track'

        if not gSuite.isPreprocessed():
            return 'Selected GSuite file is not preprocess. Please preprocess ' \
                   'the GSuite file before continuing the analysis.'

        if gSuite.trackType in [UNKNOWN]:
            return 'The track type of the GSuite file is not known. The track type ' \
                   'is needed for doing analysis.'

        if gSuite.trackType in [MULTIPLE]:
            return 'All tracks in the GSuite file needs to be of the same track ' \
                   'type. Multiple track types are not supported.'
        
        
        return None
    
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'html'

class driverGeneIdentification(GeneralGuiTool, UserBinMixin, DebugMixin):

    MERGE_INTRA_OVERLAPS = 'Merge any overlapping points/segments within the same track'
    ALLOW_MULTIPLE_OVERLAP = 'Allow multiple overlapping points/segments within the same track'
    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page. 
        '''
        return "Identification of genomic elements with high event recurrence "

    @staticmethod
    def getInputBoxNames():
        return [
                ('Select target track collection GSuite','gSuiteFirst'),
                ('Select reference track collection GSuite [rows]', 'gSuiteSecond'),
                ] + \
               UserBinMixin.getUserBinInputBoxNames() + \
               DebugMixin.getInputBoxNamesForDebug()


    @staticmethod
    def getOptionsBoxGSuiteFirst():
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

    @staticmethod
    def getOptionsBoxGSuiteSecond(prevChoices): # Alternatively: getOptionsBox2()
        return GeneralGuiTool.getHistorySelectionElement('gsuite', 'txt', 'tabular')

#     @staticmethod
#     def getOptionsBoxStatistic(prevChoices):
#         return [
#                 STAT_OVERLAP_COUNT_BPS,
# #                 STAT_OVERLAP_RATIO,
# #                 STAT_FACTOR_OBSERVED_VS_EXPECTED,
# #                 STAT_COVERAGE_RATIO_VS_QUERY_TRACK,
# #                 STAT_COVERAGE_RATIO_VS_REF_TRACK
#                 ]

   
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        cls._setDebugModeIfSelected(choices)

        targetGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteSecond)

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

#         from gold.statistic.RawOverlapStat import RawOverlapStat
#         
#         
#         tab=[]
#         tabName=[]
        
        
#         for targetTrack in targetGSuite.allTracks():
#             targetTrackName = targetTrack.title
#             tabName.append(targetTrackName)
#             tabPart=[]
#             for refTrack in refGSuite.allTracks():
#                 refTrackName = refTrack.title
#                 analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, refTrack.genome)
#                 results = doAnalysis(AnalysisSpec(RawOverlapStat), analysisBins, [PlainTrack(refTrack.trackName),PlainTrack(targetTrack.trackName)])
#                 resultDict = results.getGlobalResult()
#                 tabPart.append(resultDict)
#             tab.append(tabPart)
        

        analysisDef = 'dummy -> RawOverlapStat'
        #analysisDef = 'dummy [withOverlaps=yes] -> RawOverlapAllowSingleTrackOverlapsStat'
        results = OrderedDict()
        
        for targetTrack in targetGSuite.allTracks():
            targetTrackName = targetTrack.title
            for refTrack in refGSuite.allTracks():
                refTrackName = refTrack.title
                if targetTrack.trackName == refTrack.trackName:
                    result = driverGeneIdentification.handleSameTrack(targetTrack.trackName, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn)
                else:
                    result = GalaxyInterface.runManual([targetTrack.trackName, refTrack.trackName],
                                                       analysisDef, regSpec, binSpec,
                                                       targetGSuite.genome, galaxyFn,
                                                       printRunDescription=False,
                                                       printResults=False).getGlobalResult()
                if targetTrackName not in results :
                    results[targetTrackName] = OrderedDict()
                results[targetTrackName][refTrackName] = result

        stat = STAT_OVERLAP_COUNT_BPS
        statIndex = STAT_LIST_INDEX[stat]
        title = ''

        processedResults = []
        headerColumn = []
        for targetTrackName in targetGSuite.allTrackTitles():
            resultRowDict = processRawResults(results[targetTrackName])
            resultColumn = []
            headerColumn = []
            for refTrackName, statList in resultRowDict.iteritems():
                resultColumn.append(statList[statIndex])
                headerColumn.append(refTrackName)
            processedResults.append(resultColumn)
        
        outputTable = {}
        for elN in range(0, len(headerColumn)):
            outputTable[elN]={}
            outputTable[elN]['id']=headerColumn[elN]
        
        transposedProcessedResults = [list(x) for x in zip(*processedResults)]
       
        #second question sumSecondgSuite
        #first question numSecondgSuite
        #fifth question numSecondgSuitePercentage
        for i in range(0, len(transposedProcessedResults)):
            outputTable[i]['sumSecondgSuite'] = sum(transposedProcessedResults[i])
            if not 'numSecondgSuite' in outputTable[i]:
                outputTable[i]['numSecondgSuite']=0
            for j in range(0, len(transposedProcessedResults[i])):
                if transposedProcessedResults[i][j]>=1:
                    outputTable[i]['numSecondgSuite'] += 1
                else:
                    outputTable[i]['numSecondgSuite'] += 0
            outputTable[i]['numSecondgSuitePercentage'] = float(outputTable[i]['numSecondgSuite'])/float(targetGSuite.numTracks()) * 100
        
        from gold.statistic.CountSegmentStat import CountSegmentStat
        from gold.statistic.CountPointStat import CountPointStat
        from gold.description.TrackInfo import TrackInfo
        
        #third question numPairBpSecondgSuite
        #fourth question numFreqBpSecondgSuite
        i=0
        for refTrack in refGSuite.allTracks():
            formatName = TrackInfo(refTrack.genome, refTrack.trackName).trackFormatName
            analysisDef = CountSegmentStat if 'segments' in formatName else CountPointStat
            analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, refTrack.genome)
            results = doAnalysis(AnalysisSpec(analysisDef), analysisBins, [PlainTrack(refTrack.trackName)])
            resultDict = results.getGlobalResult()
            if len(resultDict)==0:
                outputTable[i]['numPairBpSecondgSuite'] = None
                outputTable[i]['numFreqBpSecondgSuite'] = None
                outputTable[i]['numFreqUniqueBpSecondgSuite'] = None
            else:
                outputTable[i]['numPairBpSecondgSuite'] = resultDict['Result']
                if outputTable[i]['numPairBpSecondgSuite'] != 0:
                    outputTable[i]['numFreqBpSecondgSuite'] = float(outputTable[i]['sumSecondgSuite'])/float(outputTable[i]['numPairBpSecondgSuite'])
                else:
                    outputTable[i]['numFreqBpSecondgSuite']=None
                if outputTable[i]['sumSecondgSuite'] !=0:
                    outputTable[i]['numFreqUniqueBpSecondgSuite'] = float(outputTable[i]['numPairBpSecondgSuite'])/float(outputTable[i]['sumSecondgSuite'])
                else:
                    outputTable[i]['numFreqUniqueBpSecondgSuite']=None
               
            i+=1
        
        
        #sortTable
        outputTableLine=[]
        for key, item in outputTable.iteritems():
            line = [
                    item['id'],
                    item['numSecondgSuite'],
                    item['sumSecondgSuite'],
                    item['numPairBpSecondgSuite'],
                    item['numFreqBpSecondgSuite'],
                    item['numFreqUniqueBpSecondgSuite'],
                    item['numSecondgSuitePercentage']
                    ]
            outputTableLine.append(line)
        
        import operator
        outputTableLineSort = sorted(outputTableLine, key=operator.itemgetter(1), reverse=True)
        
        
        tableHeader = ['Region ID ', 
                       'Number of cases with at least one event ', 
                       'Total number of events', 
                       'Genome coverage (unique bp)', 
                       'Number of events per unique bp',
                       'Number of unique bp per event',
                       'Percentage of cases with at least one event']
        htmlCore = HtmlCore()
        
        htmlCore.begin()
        
        htmlCore.line("<b>Identification of genomic elements with high event recurrence</b> ")
        
        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        htmlCore.tableHeader(tableHeader, sortable=True, tableId='resultsTable')
        
        
        
        for line in outputTableLineSort:
            htmlCore.tableLine(line)
            
        plotRes=[]
        plotXAxis=[]
        for lineInx in range(1, len(outputTableLineSort[0])):
            plotResPart=[]
            plotXAxisPart=[]
            for lineInxO in range(0, len(outputTableLineSort)):
                #if outputTableLineSort[lineInxO][lineInx]!=0 and 
                #if outputTableLineSort[lineInxO][lineInx]!=None:
                plotResPart.append(outputTableLineSort[lineInxO][lineInx])
                plotXAxisPart.append(outputTableLineSort[lineInxO][0])   
            plotRes.append(plotResPart) 
            plotXAxis.append(plotXAxisPart)
        
        htmlCore.tableFooter()
        htmlCore.divEnd()
        
        
        htmlCore.divBegin('plot', style='padding-top:20px;margin-top:20px;')
        
        
        
        vg = visualizationGraphs()
        res = vg.drawColumnCharts(
            plotRes,
            titleText=tableHeader[1:],
            categories=plotXAxis,
            height = 500,
            xAxisRotation=270,
            xAxisTitle = 'Ragion ID',
            yAxisTitle = 'Number of cases with at least one event',
            marginTop=30,
            addTable=True,
            sortableAccordingToTable=True,
            legend=False
            )
        htmlCore.line(res)
        htmlCore.divEnd()
      
        
        htmlCore.hideToggle(styleClass='debug')
        htmlCore.end()

        print htmlCore
        
    @staticmethod
    def _getGenome(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.genome

    @staticmethod
    def _getTrackName1(choices):
        refGSuite = getGSuiteFromGalaxyTN(choices.gSuiteFirst)
        return refGSuite.allTracks().next().trackName

    @staticmethod
    def _getTrackName2(choices):
        return None

    @classmethod
    def getToolDescription(cls):
        core = HtmlCore()

        core.paragraph('''
        
        <p>The tool provides screening of two track collections (GSuite files) against each other:</p>

        <p>- The target collection should corespond to a collection of cases (e.g. patients), each of which is defined by a set of events (e.g. somatic mutations). Any events sufficiently characterized by genomic locations/regions can be considered.</p>
        
        <p>- The reference collection should define genomic elements (e.g. genes) for which event recurrence should be calculated. Each genomic element can be composed of multiple subunits (e.g. exons in the case of genes), forming an individual track.</p>
        
        <p>To run the tool, follow these steps:</p>
        
        <p>Select the target and reference track collections (GSuite files) from your current history. Select genomic regions to which the analysis should be limited (or keep the default choice of chromosome arms).
        Click "Execute" in order to start the analysis.</p>''')

        core.paragraph('The results are presented in a sortable table and an interactive chart.')
        
        
        core.paragraph('''
        <p>Examples:</p>

        <p>- The tool can be used for identification of "cancer driver genes" (i.e. genes most frequently mutated in a patient cohort), with the reference collection serving for accurate description of a custom gene panel or, generally, the regions of any targeted sequencing study. Mutation frequencies are automatically normalized with respect to the total observed gene lengths.</p>

        <p>- Similarly, one could investigate the number of transcription factors (TFs) potentially binding to the intronic regions of genes. In this case, the target collection should map the binding sites of TFs (with one TF per track), while the reference collection should correspond to the intronic genomic regions (with each gene's introns occupying an own track). By default, both the total as well as the normalized counts of TFs (and TF binding sites) per gene would be included in the results.</p> 
        ''')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES)

        return str(core)
    

  
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

    @classmethod
    def handleSameTrack(cls, trackName, regSpec, binSpec, genome, galaxyFn):
        
        analysisSpec = AnalysisSpec(RawOverlapToSelfStat)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome)
        
        return doAnalysis(analysisSpec, analysisBins, [Track(trackName)]).getGlobalResult()
        
    @staticmethod
    def isDebugMode():
        '''
        Specifies whether debug messages are printed.
        '''
        return False


    #code for R which WORKS!
        #openRfigure from quick.util.static
        #GalaxyRunSpecificFile
        #use rPlot
        #closeRfigure
        #getLink or getEmbeddedImage

#         from gold.application.RSetup import robjects, r
#         rPlot = robjects.r.plot
#         rPlot([1,2,3], [4,5,6], type='p', xlim=[0,2], ylim=[0,2], main = 'tit', xlab='xlab', ylab='ylab')
# #         print RPlotUtil.drawXYPlot([1,2,3], [4,5,6], plotType='p', xLim=[0,2], yLim=[0,2], mainTitle='tit', xTitle='xTit', yTitle='yTit')
# #         res = RPlotUtil.drawXYPlot([1,2,3], [4,5,6], plotType='p', xLim=[0,2], yLim=[0,2], mainTitle='tit', xTitle='xTit', yTitle='yTit')
# #
#
#
#         core = HtmlCore()
#         core.begin()
#         core.divBegin(divId='plot')
#         core.image(plotOutput.getURL())
#         core.divEnd()
#         core.end()
#         print core
