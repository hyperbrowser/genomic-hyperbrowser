from collections import defaultdict, OrderedDict

from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.application.GalaxyInterface import GalaxyInterface
from quick.application.ProcTrackOptions import ProcTrackOptions
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from quick.extra.TrackIntersection import TrackIntersection
from quick.extra.tfbs.TfbsTrackNameMappings import TfbsTrackNameMappings, TfbsGSuiteNameMappings
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.extra.tfbs.TfTrackNameMappings import TfTrackNameMappings
from quick.extra.tfbs.getTrackRelevantInfo import getTrackRelevantInfo
from quick.multitrack.MultiTrackCommon import getGSuiteFromGSuiteFile, getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.UserBinMixin import UserBinMixin

#from docs.manual.InstantRunningForTesting import trackTitles
from gold.util import CommonConstants
from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs, plotFunction
from gold.gsuite import GSuiteConstants, GSuiteStatUtils
from gold.description.AnalysisList import REPLACE_TEMPLATES
from gold.application.HBAPI import doAnalysis
from gold.track.Track import Track

'''
Created on Nov 12, 2014
@author: Antonio Mora
Last update: Antonio Mora; Nov 10, 2015
'''

class AllTfsOfRegions(GeneralGuiTool, UserBinMixin):
    REGIONS_FROM_HISTORY = 'History (user-defined)'
    SELECT = '--- Select ---'
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
        return 'Scan transcription factors of a genomic region'

    @staticmethod
    def getInputBoxNames():
        return [('Genome', 'genome'),\
                ('Genomic Regions Source', 'genomicRegions'),\
                ('Genomic Regions Tracks', 'genomicRegionsTracks'),\
                ('TF Source', 'sourceTfs'),\
                ('TF Source Details', 'sourceTfsDetails'),\
                ('TF Tracks', 'tfTracks')\
                ] + UserBinMixin.getUserBinInputBoxNames()

    @staticmethod
    def getOptionsBoxGenome():
        return ['hg19','mm9']

    @classmethod
    def getOptionsBoxGenomicRegions(cls, prevChoices):
        return [cls.SELECT] + ['Hyperbrowser repository'] + ['Hyperbrowser repository (cell-type-specific)'] + \
        [cls.REGIONS_FROM_HISTORY] # ['Input Genomic Region']

    @classmethod
    def getOptionsBoxGenomicRegionsTracks(cls, prevChoices):
        if prevChoices.genomicRegions == cls.REGIONS_FROM_HISTORY:
            return ('__history__','bed','category.bed','gtrack')
        #elif prevChoices.genomicRegions == 'Input Genomic Region':
        #    return #('', 1, False) # Function to extract this region from a track and send it to history? Or do it before using this function?
        elif prevChoices.genomicRegions == cls.SELECT:
            return
        elif prevChoices.genomicRegions == 'Hyperbrowser repository':
            return [cls.SELECT] + TfbsTrackNameMappings.getTfbsTrackNameMappings(prevChoices.genome).keys()
        else:
            selectedTrackNames = []
            genElementGSuiteName = TfbsGSuiteNameMappings.getTfbsGSuiteNameMappings(prevChoices.genome).values()
            for gSuite in genElementGSuiteName:
                thisGSuite = getGSuiteFromGSuiteFile(gSuite)
                for track in thisGSuite.allTracks():
                    uri = track.uri
                    selectedTrackNames.append(uri.replace("hb:/Private:Antonio:","hb:"))
            return [cls.SELECT] + selectedTrackNames

    '''@classmethod
    def getOptionsBoxSourceTfs(cls, prevChoices):
        if prevChoices.genomicRegions != '--- Select ---':
            return TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome).keys()
        else:
            return

    @classmethod
    def getOptionsBoxTfTracks(cls, prevChoices):
        if prevChoices.genomicRegions != '--- Select ---':
            tfSourceTN = TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome)[ prevChoices.sourceTfs ]
            subtypes = ProcTrackOptions.getSubtypes(prevChoices.genome, tfSourceTN, True)
            falses = ['False']*len(subtypes)
            return OrderedDict(zip(subtypes,falses))'''

    @classmethod
    def getOptionsBoxSourceTfs(cls, prevChoices):
        if prevChoices.genomicRegionsTracks:
            if prevChoices.genomicRegionsTracks != cls.SELECT:
                return [cls.SELECT] + ['Hyperbrowser repository'] + [cls.REGIONS_FROM_HISTORY]
            else:
                return
        else:
            return

    @classmethod
    def getOptionsBoxSourceTfsDetails(cls, prevChoices):
        if prevChoices.sourceTfs != cls.SELECT:
            if prevChoices.sourceTfs == 'Hyperbrowser repository':
                sourceTfKeys = [cls.SELECT] + TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome).keys()
                return sourceTfKeys
            elif prevChoices.sourceTfs == cls.REGIONS_FROM_HISTORY:
                return ('__history__','bed','category.bed','gtrack','gsuite')
        else:
            return

    @classmethod
    def getOptionsBoxTfTracks(cls, prevChoices):
        if prevChoices.sourceTfsDetails != cls.SELECT:
            genome = prevChoices.genome
            sourceTfs = prevChoices.sourceTfs
            sourceTfsDetails = prevChoices.sourceTfsDetails
            if sourceTfs == cls.SELECT:
                return
            elif sourceTfs == 'Hyperbrowser repository':
                tfSourceTN = TfTrackNameMappings.getTfTrackNameMappings(prevChoices.genome)[ sourceTfsDetails ]
                subtypes = ProcTrackOptions.getSubtypes(prevChoices.genome, tfSourceTN, True)
                falses = ['False']*len(subtypes)
                return OrderedDict(zip(subtypes,falses))
            elif sourceTfs == cls.REGIONS_FROM_HISTORY:
                if isinstance(sourceTfsDetails, str):
                    galaxyTN = sourceTfsDetails.split(':')
                    if galaxyTN[1] == "gsuite":  #ExternalTrackManager.extractFileSuffixFromGalaxyTN(prevChoices.sourceTfsDetails, allowUnsupportedSuffixes=True) == "gsuite"
                        errorString = GeneralGuiTool._checkGSuiteFile(sourceTfsDetails)
                        if not errorString:
                            gSuite = getGSuiteFromGalaxyTN(sourceTfsDetails)
                            sizeErrorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite, 1, 1000)
                            if not sizeErrorString:
                                reqErrorString = GeneralGuiTool._checkGSuiteRequirements \
                                    (gSuite,
                                     AllTfsOfRegions.GSUITE_ALLOWED_FILE_FORMATS,
                                     AllTfsOfRegions.GSUITE_ALLOWED_LOCATIONS,
                                     AllTfsOfRegions.GSUITE_ALLOWED_TRACK_TYPES,
                                     AllTfsOfRegions.GSUITE_DISALLOWED_GENOMES)
                                if not reqErrorString:
                                    validity = 'Valid'
                                else:
                                    return
                            else:
                                return
                        else:
                            return
                        if validity == 'Valid':
                            selectedTrackNames = []
                            gSuite = getGSuiteFromGalaxyTN(sourceTfsDetails)
                            for track in gSuite.allTracks():
                                selectedTrackNames.append('hb:/' + '/'.join(track.trackName))
                            falses = ['False']*len(selectedTrackNames)
                            return OrderedDict(zip(selectedTrackNames,falses))
                    else:
                        tfTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)
                        return ['hb:/' + '/'.join(tfTrackName)]
                else:
                    return
            else:
                return
        else:
            return

    @staticmethod
    def countStatistics(similarityFunc, choices, genome, tracks, trackTitles):
        
        trackList = tracks[1:]

        resultsForStatistics=OrderedDict()
        
        llDict=OrderedDict()
        trackT =  trackTitles[1:]
        i=0
        for tt1 in trackT:
            if not tt1 in llDict:
                llDict[tt1] = []
                resultsForStatistics[tt1]={}
                for tt2 in range(i, len(trackT)):
                    llDict[tt1].append(trackT[tt2])
            i+=1
#         
#         print 'llDict=' + str(llDict)
#         print 'trackT=' + str(trackT)
#         print 'trackList=' + str(trackList)
        
        for key0, it0 in llDict.iteritems():
            if len(it0) > 1: 
#                 print 'it0' + str(it0)
                
                trackCollection=[]
                for it1 in it0:
#                     print 'it1' + str(it1)
#                     print 'trackT[it1]' + str(trackT[it1])
                    
                    trackNumber = trackT.index(it1)
                    trackCollection.append(trackList[trackNumber])
                    
                trackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(it0)
                
#                 print str(key0) + '- trackCollection: ' + str(trackCollection) + ' trackTitles: ' + str(trackTitles)
                
                for similarityStatClassName in similarityFunc:
                    regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
                    analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)
                        
                    mcfdrDepth = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$']).getOptionsAsText().values()[0][0]
                    analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> GSuiteSimilarityToQueryTrackRankingsAndPValuesWrapperStat'
                    analysisSpec = AnalysisDefHandler(analysisDefString)
                    analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
                    analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
                    analysisSpec.addParameter('rawStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName])
                    analysisSpec.addParameter('pairwiseStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName]) #needed for call of non randomized stat for assertion
                    analysisSpec.addParameter('tail', 'more')
                    analysisSpec.addParameter('trackTitles', trackTitles)#that need to be string
                    results = doAnalysis(analysisSpec, analysisBins, trackCollection).getGlobalResult()
                        
                    if not similarityStatClassName in resultsForStatistics[key0]:
                        resultsForStatistics[key0][similarityStatClassName] = {}
                  
                  
                    resultsForStatistics[key0][similarityStatClassName] = results
                    
        return resultsForStatistics

    @staticmethod
    def countStatisticResults(resultDict, tfList, trackTitlesForStat):
        
        
        for key0, it0 in resultDict.iteritems():
#             print key0
            tfTrue = True
            
            if len(it0)!=2:
                for tfE in tfList:
                    if not tfE in resultDict[key0].keys():
                        resultDict[key0][tfE]={}
                
            for key1, it1 in it0.iteritems():
                tfTrue=False
#                 print 'key1' + str(key1) + ' ' + str(it1)
                if len(it1) != len(trackTitlesForStat)-1:
                    for elN in range(1, len(trackTitlesForStat)):
                        nameEl = trackTitlesForStat[elN]
                        if nameEl not in it1.keys():
                            if nameEl == key0:
                                resultDict[key0][key1][nameEl] = [None, None]
                            else:
                                if key1 in resultDict[nameEl]:
                                    if key0 in resultDict[nameEl][key1]:
                                        resultDict[key0][key1][nameEl] = resultDict[nameEl][key1][key0]
                                    else:
                                        resultDict[key0][key1][nameEl] = [None, None]
                                else:
                                    resultDict[key0][key1][nameEl] = [None, None]
        #                             print '----' + str(key0) + ' ' + str(key1) + ' ' + str(nameEl)
            if tfTrue == True:
                for el in tfList:
                    resultDict[key0][el]=OrderedDict
                    for elN in range(1, len(trackTitlesForStat)):
                        nameEl = trackTitlesForStat[elN]
                        if nameEl == key0:
                            resultDict[key0][el][nameEl] = [None, None]
                        else:
                            if el in resultDict[nameEl]:
                                if key0 in resultDict[nameEl][el]:
                                    resultDict[key0][el][nameEl] = resultDict[nameEl][el][key0]
                                else:
                                    resultDict[key0][el][nameEl] = [None, None]
        
        
        
        resultDictlineTablePart=['Data']
        for elN in range(1, len(trackTitlesForStat)):
            resultDictlineTablePart.append(str(trackTitlesForStat[elN]) + ' -- value ')
            resultDictlineTablePart.append(str(trackTitlesForStat[elN]) + ' -- p-value ')
        
        
        resultDictlineTable={}
        for el in tfList:
            resultDictlineTable[el] = [resultDictlineTablePart]
        
        for key0, it0 in resultDict.iteritems(): 
            for key1, it1 in it0.iteritems():
                resultDictlineTablePart=[]
                resultDictlineTablePart.append(key0)
                for elN in range(1, len(trackTitlesForStat)):
                    resultDictlineTablePart.append(it1[trackTitlesForStat[elN]][0])
                    resultDictlineTablePart.append(it1[trackTitlesForStat[elN]][1])
                    
                resultDictlineTable[key1].append(resultDictlineTablePart)
        
        return resultDictlineTable

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        genome = choices.genome
        genomicRegions = choices.genomicRegions
        genomicRegionsTracks = choices.genomicRegionsTracks
        sourceTfs = choices.sourceTfs
        sourceTfsDetails = choices.sourceTfsDetails
        tfTracks = choices.tfTracks

        # Get Genomic Region track name:
        if genomicRegions == cls.REGIONS_FROM_HISTORY:
            galaxyTN = genomicRegionsTracks.split(':')
            genElementTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)
        elif genomicRegions == 'Hyperbrowser repository':
                selectedGenRegTrack = TfbsTrackNameMappings.getTfbsTrackNameMappings(genome)[ genomicRegionsTracks ]
                if isinstance(selectedGenRegTrack,dict):
                    genElementTrackName = selectedGenRegTrack.values()
                else:
                    genElementTrackName = selectedGenRegTrack
        elif genomicRegions == 'Hyperbrowser repository (cell-type-specific)':
                genomicRegionsTrackOld = genomicRegionsTracks.replace("hb:","Private:Antonio:")
                genElementTrackName = genomicRegionsTrackOld.split(":")
        else:
            return

        # Get TF track names:
        if isinstance(tfTracks,dict):
            selectedTfTracks = [key for key,val in tfTracks.iteritems() if val == 'True']
        else:
            selectedTfTracks = [tfTracks]
            
        
        
        
        
        queryTrackTitle = '--'.join(genElementTrackName)
    
        trackTitles = [queryTrackTitle]
        tracks = [Track(genElementTrackName, trackTitle=queryTrackTitle)]
        
        for i in selectedTfTracks:
            if sourceTfs == 'Hyperbrowser repository':
                tfTrackName = TfTrackNameMappings.getTfTrackNameMappings(genome)[ sourceTfsDetails ] + [i]
                tracks.append(Track(tfTrackName, trackTitle=tfTrackName[len(tfTrackName)-1]))
                trackTitles.append(tfTrackName[len(tfTrackName)-1])
        
        trackTitlesForStat= trackTitles 
        
        trackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(trackTitles)
        
        
        ##first statistic for Q2
        resultsForStatistics=OrderedDict()
        #'Ratio of observed to expected overlap (Forbes similarity measure)' - T5
        #'Normalized ratio of observed to expected overlap (normalized Forbes similarity measure)' - T7
        similarityFunc = [GSuiteStatUtils.T7_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP, GSuiteStatUtils.T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP]
          
        for similarityStatClassName in similarityFunc:
            regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
            analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome=genome)
              
            mcfdrDepth = AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDR$']).getOptionsAsText().values()[0][0]
            analysisDefString = REPLACE_TEMPLATES['$MCFDR$'] + ' -> GSuiteSimilarityToQueryTrackRankingsAndPValuesWrapperStat'
            analysisSpec = AnalysisDefHandler(analysisDefString)
            analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
            analysisSpec.addParameter('assumptions', 'PermutedSegsAndIntersegsTrack_')
            analysisSpec.addParameter('rawStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName])
            analysisSpec.addParameter('pairwiseStatistic', GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[similarityStatClassName]) #needed for call of non randomized stat for assertion
            analysisSpec.addParameter('tail', 'more')
            analysisSpec.addParameter('trackTitles', trackTitles)#that need to be string
            results = doAnalysis(analysisSpec, analysisBins, tracks).getGlobalResult()
              
            if not similarityStatClassName in resultsForStatistics:
                resultsForStatistics[similarityStatClassName] = {}
            
            
            resultsForStatistics[similarityStatClassName] = results
            
        
        
        keyTitle = ['Normalized ratio of observed to expected overlap (normalized Forbes similarity measure)',
        'Ratio of observed to expected overlap (Forbes similarity measure)']
        resultDict = AllTfsOfRegions.countStatistics(similarityFunc, choices, genome, tracks, trackTitlesForStat)
        resultDictShow = AllTfsOfRegions.countStatisticResults(resultDict, keyTitle, trackTitlesForStat)
        
        
        
#         print resultsForStatistics
        
        
            

        '''selectedTrackNames = []
        if sourceTfs == 'History (user-defined)':
            if selectedTfTracks.split(":")[1] == "gsuite":
                gSuite = getGSuiteFromGalaxyTN(selectedTfTracks)
                for track in gSuite.allTracks():
                    selectedTrackNames.append(track.trackName)
            else:
                galaxyTN = selectedTfTracks.split(':')
                gRegTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)
                selectedTrackNames.append(gRegTrackName)
        else:'''

        
        
        tfNameList = []
        
        #Intersection between TF Tracks and selected region (Table 1):
        n = 0
        allTargetBins = []; alltfNames = []; table1 = []
        for i in selectedTfTracks:
            n = n+1
            #newGalaxyFn = galaxyFn.split(".")[0] + str(n) + "." + "dat"

            if sourceTfs == 'Hyperbrowser repository':
                tfTrackName = TfTrackNameMappings.getTfTrackNameMappings(genome)[ sourceTfsDetails ] + [i]
            else:
                tfTrackName = i.split(':')[1].split('/')
                tfTrackName.pop(0)
            #tfIntersection.expandReferenceTrack(upFlankSize, downFlankSize)
            tfIntersection = TrackIntersection(genome, genElementTrackName, tfTrackName, galaxyFn, str(n))
            
            
            regFileNamer = tfIntersection.getIntersectedRegionsStaticFileWithContent()
            targetBins = tfIntersection.getIntersectedReferenceBins()
            
            #regSpec, targetBins = UserBinSelector.getRegsAndBinsSpec(choices)

            tfHits = [i] * len(targetBins)
            fixedTargetBins = [str(a).split(" ")[0] for a in targetBins]
            extendedTargetBins = [list(a) for a in zip(fixedTargetBins, tfHits)]
            allTargetBins = allTargetBins + extendedTargetBins
            tfName = i
            alltfNames = alltfNames + [tfName]

            # Save output table:
            tfNameList.append(tfName)
            line = [tfName] + [len(targetBins)] + [regFileNamer.getLink('Download bed-file')] + [regFileNamer.getLoadToHistoryLink('Send bed-file to History')]
            table1 = table1 + [line]
        

        # Computing totals:
        fullCase = ','.join(alltfNames)
        firstColumn = [item[0] for item in allTargetBins]
        uniqueAllTargetBins = list(set(firstColumn))
        
        # Group TFs by bound region:
        d1 = defaultdict(list)
        for k, v in allTargetBins:
            d1[k].append(v)
        allTFTargetBins = dict((k, ','.join(v)) for k, v in d1.iteritems())
        
        allTFTargetList = []; fullCaseTFTargetList = []
        for key, value in allTFTargetBins.iteritems():
            allTFTargetList = allTFTargetList + [[key,value]]
            if value == fullCase:
                fullCaseTFTargetList = fullCaseTFTargetList + [[key,value]]
        
        analysis3 = TrackIntersection.getFileFromTargetBins(allTFTargetList, galaxyFn, str(3))
        analysis4 = TrackIntersection.getFileFromTargetBins(fullCaseTFTargetList, galaxyFn, str(4))

        # Print output to table:
        title = 'TF targets and co-occupancy of ' + genElementTrackName[-1] + ' genomic regions'
        htmlCore = HtmlCore()
        
        pf = plotFunction(tableId='resultsTable')
        
        htmlCore.begin()
        htmlCore.header(title)
        htmlCore.divBegin('resultsDiv')
        
        htmlCore.line(pf.createButton(bText = 'Show/Hide more results'))
        
        # htmlCore.tableHeader(['Transcription Factor', 'Normalized ratio of observed to expected overlap (normalized Forbes similarity measure) -- Similarity to genomic regions track', 'Normalized ratio of observed to expected overlap (normalized Forbes similarity measure) -- p-value','Ratio of observed to expected overlap (Forbes similarity measure) -- Similarity to genomic regions track', 'Ratio of observed to expected overlap (Forbes similarity measure) -- p-value', 'Number of TF-Target Track Regions', 'File of TF Target Regions', 'File of TF Target Regions', 'Number of TF-co-occupied Regions', 'File of TF co-occupied Regions', 'File of TF co-occupied Regions', 'Rank of TF co-occupancy motifs', 'Rank of TF co-occupancy motifs'], sortable=True, tableId='resultsTable')
        htmlCore.tableHeader(['Transcription Factor', 'Normalized Forbes index --overlap score',
                              'Normalized Forbes index --p-value',
                              'Forbes index --overlap score', 'Forbes index --p-value',
                              'Number of TF-Target Track Regions', 'File of TF Target Regions',
                              'File of TF Target Regions', 'Number of target track regions occupied by this TF',
                              'File of TF co-occupied Regions', 'File of TF co-occupied Regions',
                              'Rank of TF co-occupancy motifs', 'Rank of TF co-occupancy motifs'],
                             sortable=True, tableId='resultsTable')



        # Adding co-occupancy results to table:
        n = 1000 
        genRegionNumElements = [int(x) for x in getTrackRelevantInfo.getNumberElements(genome, genElementTrackName)]
        
        
        for key0, it0 in resultsForStatistics.iteritems():
            for el in tfNameList:
                if el not in it0:
                    resultsForStatistics[key0][el]=[None, None]
        
        
        
        resultsPlotDict={}
        resultPlotCat=[]
        resultsPlot=[]
        
        resultsForStatisticsProper={}
        for key0, it0 in resultsForStatistics.iteritems():
            if not key0 in resultsPlotDict:
                resultsPlotDict[key0]={}
            resultsPlotPart=[]
            for key1, it1 in it0.iteritems():
                resultsPlotPart.append(it1[0])
                if not key1 in resultsForStatisticsProper:
                    resultsForStatisticsProper[key1] = []
                if not key1 in resultsPlotDict[key0]:
                    resultsPlotDict[key0][key1]=None
                for el in it1: 
                    resultsForStatisticsProper[key1].append(el)
                resultsPlotDict[key0][key1] = it1[0]

        resultPlotCat.append(tfNameList)
        resultPlotCat.append(tfNameList)
        
        
        
        
        #resultPlotCatPart = tfNameList
        
#         print resultPlotCatPart
        
        for key0, it0 in resultsPlotDict.iteritems():
            resultsPlotPart=[]
            for el in tfNameList:
                if el in it0:
                    resultsPlotPart.append(it0[el])
                else:
                    resultsPlotPart.append(None)
            resultsPlot.append(resultsPlotPart)
        
        
        
        for i in table1:
            thisCaseTFTargetList = []
            for key, value in allTFTargetList:
                if i[0] in value and ',' in value:
                    thisCaseTFTargetList = thisCaseTFTargetList + [[key,value]]
            n = n + 1
            
            thisAnalysis = TrackIntersection.getFileFromTargetBins(thisCaseTFTargetList, galaxyFn, str(n))

            thisCaseCoCountsList = []
            thing = [x[1] for x in thisCaseTFTargetList]
            for k in list(set(thing)):
                thisCount = thing.count(k)
                thisCaseCoCountsList = thisCaseCoCountsList +  \
                                       [[k, thisCount, 100*float(thisCount)/float(sum(genRegionNumElements)), 100*float(thisCount)/float(len(thisCaseTFTargetList))]]
            thisCaseCoCountsList.sort(key=lambda x: x[2], reverse=True)
            n = n + 1
            
            thisCoCountsAnalysis = TrackIntersection.getOccupancySummaryFile(thisCaseCoCountsList, galaxyFn, str(n))
            
            thisLine = [len(thisCaseTFTargetList)] + \
            [thisAnalysis.getLink('Download file')] + [thisAnalysis.getLoadToHistoryLink('Send file to History')] + \
            [thisCoCountsAnalysis.getLink('Download file')] + [thisCoCountsAnalysis.getLoadToHistoryLink('Send file to History')]
            
            newLineI = []
            tfName = i[0] 
            newLineI.append(tfName)
            
            for el in resultsForStatisticsProper[tfName]:
                newLineI.append(el)
            
            for elN in range(1, len(i)):
                newLineI.append(i[elN])
            
            
#             htmlCore.tableLine(i + thisLine)

            htmlCore.tableLine(newLineI + thisLine)
            
        totalCoOccupancyTargetList = []; n = 2000
        for key, value in allTFTargetList:
            n = n + 1
            if ',' in value:
                totalCoOccupancyTargetList = totalCoOccupancyTargetList + [[key,value]]
        #newGalaxyFn = galaxyFn.split(".")[0] + str(n) + "." + "dat"
        totalCoOccupancyAnalysis = TrackIntersection.getFileFromTargetBins(totalCoOccupancyTargetList, galaxyFn, str(n))
        #line = ['Total reported regions'] + [len(allTargetBins)] + [''] + [''] + [''] + [''] + ['']
        line = ['Full co-occupancy of ' + fullCase] + ['-'] + ['-'] + ['-'] + ['-'] + ['-'] + ['-'] + ['-'] + [len(fullCaseTFTargetList)] + [analysis4.getLink('Download file')] + [analysis4.getLoadToHistoryLink('Send file to History')] + ['-'] + ['-']
        htmlCore.tableLine(line)
        line = ['Total unique regions'] + ['-'] + ['-'] + ['-'] + ['-']  + [len(allTFTargetList)] + [analysis3.getLink('Download bed-file')] + [analysis3.getLoadToHistoryLink('Send bed-file to History')] + [len(totalCoOccupancyTargetList)] + [totalCoOccupancyAnalysis.getLink('Download file')] + [totalCoOccupancyAnalysis.getLoadToHistoryLink('Send file to History')] + ['-'] + ['-']
        htmlCore.tableLine(line)

        htmlCore.tableFooter()
        htmlCore.divEnd()
        
        
        
        htmlCore.line(pf.hideColumns(indexList=[6,7, 9, 10, 11, 12]))
        
        vg = visualizationGraphs()
        result = vg.drawColumnCharts(
                                    resultsPlot,
                                    height=300,
                                    categories=resultPlotCat,
                                    legend=False,
                                    addOptions='width: 40%; float:left; margin: 0 5%;',
                                    titleText=['Overlap between TFs and genomic region using normalized Forbes', 'Overlap between TFs and genomic region using Forbes'],
                                    xAxisRotation=90,
                                    xAxisTitle='TF',
                                    yAxisTitle='value'
                                    )
        
        htmlCore.line(result)
        
        
        for key0, it0 in resultDictShow.iteritems():
            htmlCore.divBegin('resultsDiv'+str(key0))
            htmlCore.header(key0)
            htmlCore.tableHeader(it0[0], sortable=True, tableId='resultsTable'+str(key0))
            
            for elN in range(1, len(it0)):
                htmlCore.tableLine(it0[elN])
        
            htmlCore.tableFooter()
            htmlCore.divEnd()
        
        
        htmlCore.hideToggle(styleClass='debug')

        htmlCore.end()
        print htmlCore


    @staticmethod
    def validateAndReturnErrors(choices):
        genome = choices.genome
        genomicRegions = choices.genomicRegions
        genomicRegionsTracks = choices.genomicRegionsTracks
        sourceTfs = choices.sourceTfs
        sourceTfsDetails = choices.sourceTfsDetails
        tfTracks = choices.tfTracks

        # Check that all region boxes have data:
        if genomicRegions == AllTfsOfRegions.SELECT:
            return 'Please select a genomic region.'
        if genomicRegionsTracks == AllTfsOfRegions.SELECT:
            return 'Please select a genomic region track.'

        # Check tracks for Genomic Regions-History:
        if genomicRegions == AllTfsOfRegions.REGIONS_FROM_HISTORY:
            errorString = GeneralGuiTool._checkTrack(choices, 'genomicRegionsTracks', 'genome')
            if errorString:
                return errorString

        # Check that TF box has data:
        if sourceTfs == AllTfsOfRegions.SELECT:
            return 'Please select a TF source.'

        # Check tracks for TFs-History:
        if sourceTfs == AllTfsOfRegions.REGIONS_FROM_HISTORY:
            if sourceTfsDetails == AllTfsOfRegions.SELECT:
                return 'Please select a TF track.'
            else:
                if isinstance(sourceTfsDetails, str):
                    trackType = sourceTfsDetails.split(':')[1]
                    if trackType == "gsuite":
                        errorString = GeneralGuiTool._checkGSuiteFile(sourceTfsDetails)
                        if errorString:
                            return errorString
                        gSuite = getGSuiteFromGalaxyTN(sourceTfsDetails)
                        sizeErrorString = GeneralGuiTool._checkGSuiteTrackListSize(gSuite, 1, 1000)
                        if sizeErrorString:
                            return sizeErrorString
                        reqErrorString = GeneralGuiTool._checkGSuiteRequirements \
                            (gSuite,
                             AllTfsOfRegions.GSUITE_ALLOWED_FILE_FORMATS,
                             AllTfsOfRegions.GSUITE_ALLOWED_LOCATIONS,
                             AllTfsOfRegions.GSUITE_ALLOWED_TRACK_TYPES,
                             AllTfsOfRegions.GSUITE_DISALLOWED_GENOMES)

                        if reqErrorString:
                            return reqErrorString
                    else:
                        errorString = GeneralGuiTool._checkTrack(choices, 'sourceTfsDetails', 'genome')
                        if errorString:
                            return errorString

        return None

    @staticmethod
    def getOutputFormat(choices=None):
        return 'customhtml'

    @staticmethod
    def getToolIllustration():
        return ['illustrations','tools','TF5.jpg']

    @staticmethod
    def getToolDescription():
        return '<b>Transcription Factor Binding Site Scanning Tool, v.1.0</b><p>\
        This tool allows the user to explore:<p>\
        * All TF binding sites inside a given genomic region (genes, exons, introns, promoters or enhancers) for\
        all chosen TFs.<p>\
        The tool works with pre-determined tracks of TF binding sites from the Hyperbrowser repository and \
        offers a certain number of useful genomic tracks to be compared to the TF tracks of interest. If \
        the genomic track you need is not there, you can upload it to History using "Get Data";\
        then select Genomic Region = History Element.\
        <p>The following picture illustrates the goal/scope of this tool.<p>'

    @staticmethod
    def isPublic():
        return True

    @staticmethod
    def getFullExampleURL():
        return 'https://hyperbrowser.uio.no/gsuite/u/hb-superuser/p/use-case---tfs-in-enhancers'
