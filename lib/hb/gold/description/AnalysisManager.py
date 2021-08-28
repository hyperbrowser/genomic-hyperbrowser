import os
from collections import OrderedDict
from contextlib import closing

from gold.description.Analysis import Analysis
from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisList import ANALYSIS_SPECS
from config.Config import DebugConfig, MEMOIZED_DATA_PATH
from gold.application.LogSetup import logMessage, logException
from gold.description.TrackInfo import TrackInfo
from gold.util.SafeFile import SafePickleFile
from gold.statistic.ResultsMemoizer import ResultsMemoizer
from quick.application.SignatureDevianceLogging import takes,returns


class AnalysisManager(object):
    _analyses = None

    @classmethod
    def getAnalysisDict(cls):
        if cls._analyses is None:
            pickleFilePath = cls._getAnalysisPickleFilePath()
            with closing(SafePickleFile(pickleFilePath)) as pickleFile:
                cls._analyses = pickleFile.object
                if cls._analyses is None:
                    cls._analyses = OrderedDict()
                    for category in ANALYSIS_SPECS.keys():
                        cls._analyses[category] = AnalysisManager._filterAndParseAnalyses(ANALYSIS_SPECS[category])
                    pickleFile.object = cls._analyses
        return cls._analyses

    @classmethod
    def _filterAndParseAnalyses(cls, analysisList):
        from config.Config import IS_EXPERIMENTAL_INSTALLATION

        analysisDict = dict(zip(analysisList,
                        [AnalysisDefHandler(q) for q in analysisList]))

        if not IS_EXPERIMENTAL_INSTALLATION:
            experimentalAnalyses = [analysisDef for analysisDef, analysis in analysisDict.iteritems()
                                    if analysis.getChoice('isExperimental') == 'True']
            for analysisDef in experimentalAnalyses:
                del analysisDict[analysisDef]

        return analysisDict

    @classmethod
    def _getAnalysisPickleFilePath(cls):
        return os.path.join(*(list(os.path.split(MEMOIZED_DATA_PATH)) + ['analyses', 'AnalysisList.pickle']))

    @staticmethod
    def getAllCategoryNames():
        return ANALYSIS_SPECS.keys()

    @classmethod
    @returns(list)
    def getMainCategoryNames(cls):
        return sorted( set([ x.split(':')[0] for x in cls.getAllCategoryNames() ]) )

    @classmethod
    def getSubCategoryNames(cls, mainCategory):
        return sorted( set([ x.split(':')[1] for x in cls.getAllCategoryNames() \
                          if x.count(':')>0 and x.split(':')[0] == mainCategory]) )

    @staticmethod
    def combineMainAndSubCategories(mainCategory, subCategory):
        return mainCategory + ':' + subCategory

    @classmethod
    def _tryAnalysisDefForValidity(cls, analysisDef, genome, trackName1, trackName2, tryReversed=True):
        analysis = AnalysisDefHandler(analysisDef)
        return cls._tryAnalysisForValidity(analysis, genome, trackName1, trackName2, tryReversed=tryReversed)

    @classmethod
    def _tryAnalysisForValidity(cls, analysis, genome, trackName1, trackName2, tryReversed=True):
        if DebugConfig.VERBOSE:
            logMessage('Trying analysisDef: ' + str(analysis.getDef()) )
        try:
            if cls._trackFormatsAreEqual(genome, trackName1, trackName2):
                tryReversed = False
            for tnA, tnB, reversed in [(trackName1, trackName2, False)] + \
                                      ([(trackName2, trackName1, True)] if tryReversed and trackName2 not in [None, []] else
                                      []):
                analysis = Analysis.createFromParsedAnalysis(analysis, genome, tnA, tnB, reversed)
                if analysis.isValidForListing():
                   return analysis, reversed
        except Exception, e:
            if DebugConfig.VERBOSE:
                logException(e)
            if DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS:
                raise
        return None, False

    @staticmethod
    def _trackFormatsAreEqual(genome, trackName1, trackName2):
        trackInfoHash1 = TrackInfo(genome, trackName1).trackFormatHash
        if trackInfoHash1:
            trackInfoHash2 = TrackInfo(genome, trackName2).trackFormatHash
            if trackInfoHash1 == trackInfoHash2:
                return True
        return False

    @staticmethod
    @takes(str, str, list, list)
    def getValidAnalysesInCategory(category, genome, trackName1, trackName2):#, formatConverter1=None, formatConverter2=None):
        #print 'AnalysisManager: ',trackName1
        validAnalyses = []
        for analysis in AnalysisManager.getAnalysisDict()[category].values():
            #from time import time
            #t = time()
            analysis, reversed = AnalysisManager._tryAnalysisForValidity(analysis, genome, trackName1, trackName2)
            #logMessage(analysisDef)
            #logMessage('%s' % (time() - t))
            if analysis is not None:
                validAnalyses.append(analysis)

        ResultsMemoizer.flushStoredResults()

        return validAnalyses

    @classmethod
    def getAllAnalyses(cls):
        analyses = cls.getAnalysisDict()
        return reduce( lambda x,y:x+y, [analyses[cat].values() for cat in analyses.keys()] )

    @classmethod
    def getAllAnalysesInCategory(cls, mainCategory, subCategory=None):
        analyses = cls.getAnalysisDict()
        if subCategory:
            subCategories = [subCategory]
        else:
            subCategories = cls.getSubCategoryNames(mainCategory)
        fullCategories = [cls.combineMainAndSubCategories(mainCategory, subCat) for subCat in subCategories]
        return reduce(lambda x, y: x + y, [analyses[cat].values() for cat in fullCategories])

    @classmethod
    def _getAllAnalysisKeys(cls):
        analyses = cls.getAnalysisDict()
        return reduce( lambda x,y:x+y, [analyses[cat].keys() for cat in analyses.keys()] )

    @classmethod
    def getAllAnalysisTuples(cls):
        analyses = cls.getAnalysisDict()
        return reduce( lambda x,y:x+y, [analyses[cat].items() for cat in analyses.keys()] )
    
    @classmethod
    def getAnalysisFromId(cls, id):
        matchingAnalyses = [x for x in cls._getAllAnalysisKeys() if x==id]
        assert( len(matchingAnalyses) == 1)
        return matchingAnalyses[0]
    
    @classmethod
    def getValidAnalysisDefFromTitle(cls, analysisTitle, genome, trackName1, trackName2):
        matchingAnalyses = [analysis for key, analysis in cls.getAllAnalysisTuples()
                            if ':' in key and key[0:key.find(':')] == analysisTitle]
        validAnalyses = []
        validReversedAnalyses = []
        
        for analysis in matchingAnalyses:
            analysis, reversed = cls._tryAnalysisForValidity(analysis, genome, trackName1, trackName2)
            if analysis is not None:
                if reversed:
                    validReversedAnalyses.append(analysis)
                else:
                    validAnalyses.append(analysis)
        ResultsMemoizer.flushStoredResults()

        if len(validAnalyses) == 1:
            return validAnalyses[0].getDef()
        elif len(validReversedAnalyses) == 1:
            return validReversedAnalyses[0].getDef()
        
#        logMessage('No analysisDef chosen. validAnalyses: %s, validReversedAnalyses: %s' \
#                   % ([x.getDef() for x in validAnalyses], [x.getDef() for x in validReversedAnalyses]))
        return ''
