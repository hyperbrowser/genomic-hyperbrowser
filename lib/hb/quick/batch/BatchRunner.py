import sys
import os
import time

from gold.application.StatRunner import AnalysisDefJob, AssemblyGapJob
from gold.description.RunDescription import RunDescription
from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.result.Results import Results
from gold.track.Track import Track
from gold.util.CustomExceptions import InvalidRunSpecException, IdenticalTrackNamesError

from quick.batch.SuperBatchConverter import SuperBatchConverter
from quick.application.UserBinSource import UserBinSource
from quick.util.CommonFunctions import wrapClass

from quick.application.ProcTrackOptions import ProcTrackOptions
from config.Config import DEFAULT_GENOME, DebugConfig, USE_PARALLEL
from gold.util.CommonConstants import BATCH_COL_SEPARATOR
from quick.application.ProcTrackNameSource import ProcTrackNameSource
from gold.application.LogSetup import logMessage, logException

from gold.description.Analysis import Analysis
from quick.util.CommonFunctions import convertTNstrToTNListFormat


class BatchContents(object):
    def __init__(self):
        self.errorResult = None
        self.regSpec = None
        self.binSpec = None
        self.userBinSource = None
        self.trackNames = None
        self.cleanedTrackNames = None
        self.statClassName = None
        self.paramDict = None


class BatchRunner(object):
    @staticmethod
    def runFromFn(batchFn, genome, fullAccess):
        return BatchRunner.runManyLines([line for line in open(batchFn, genome, fullAccess)])

    @staticmethod
    def runManyLines(batchLines, genome, fullAccess, useBatchId=True, galaxyFn=None, printProgress=True):
        # TODO: useBatchId is currently ignored! Do something with it if this was a meaningful name from a
        #  standard batch run....

        resList = []
        for line in batchLines:
            resList.append(BatchRunner.runJob(line, genome, fullAccess, galaxyFn=galaxyFn, printProgress=printProgress))
        return resList
    
    @staticmethod
    def parseBatchLine(batchLine, genome, fullAccess):
        if batchLine[0] == '#' or batchLine.strip() == '':
            return
            
        from urllib import unquote
        
        # Split and check number of columns
        cols = [x for x in batchLine.strip().split(BATCH_COL_SEPARATOR)]
        if len(cols) != 6:
            results = Results(['N/A'], ['N/A'], 'N/A')
            results.addError(InvalidRunSpecException('Error in batch specification. 6 columns are required, while '\
                                        + str(len(cols)) + ' are given: ' + batchLine))
            return results, None, None, None, None 

        bc = BatchContents()
        
        bc.regSpec = cols[1]
        bc.binSpec = unquote(cols[2])

        from quick.application.ExternalTrackManager import ExternalTrackManager
        if ExternalTrackManager.isGalaxyTrack(bc.binSpec.split(':')):
            bc.binSpec = ExternalTrackManager.extractFnFromGalaxyTN(bc.binSpec.split(':'))

        bc.statClassName, bc.paramDict = BatchRunner._parseClassAndParams(cols[5])

        bc.trackNames = [[unquote(x) for x in cols[i].split(':')] for i in [3, 4]]
        if 'trackNameIntensity' in bc.paramDict:
            bc.trackNames.append(convertTNstrToTNListFormat(bc.paramDict['trackNameIntensity'], doUnquoting=True))

        from quick.application.GalaxyInterface import GalaxyInterface

        partlyCleanedTrackNames = GalaxyInterface._cleanUpTracks(bc.trackNames, genome, realPreProc=True)

        try:
            bc.cleanedTrackNames = BatchRunner._inferTrackNames(partlyCleanedTrackNames, genome, fullAccess)

        except (InvalidRunSpecException,IdenticalTrackNamesError), e:
            if DebugConfig.PASS_ON_BATCH_EXCEPTIONS:
                raise
            bc.errorResult = Results(['N/A'],['N/A'],'N/A')
            bc.errorResult.addError(e)
            return bc

        bc.errorResult, bc.userBinSource = BatchRunner._constructBins(bc.regSpec, bc.binSpec,
                                                                      genome, bc.cleanedTrackNames)
        if bc.errorResult is not None:
            return bc
    
        return bc
    
    @staticmethod
    def runJob(batchLine, genome, fullAccess, galaxyFn=None, printProgress=True):
        bc = BatchRunner.parseBatchLine(batchLine, genome, fullAccess)
        if bc.errorResult is not None:
            return bc.errorResult
        
        #Try a full run, and return either results or an exception
        try:
            #track = Track(trackName1)
            #track2 = Track(trackName2)
            #if 'tf1' in paramDict:
            #    track.setFormatConverter(formatConverter)
            
            #results = StatRunner.run(userBinSource , Track(trackName1), Track(trackName2), \
            #                         wrapClass(STAT_CLASS_DICT[statClassName], keywords=paramDict) )
            #results = StatRunner.run(userBinSource , track, track2, \
            #                         wrapClass(STAT_CLASS_DICT[statClassName], keywords=paramDict) )
            fullRunParams = {}
            
            if USE_PARALLEL:
                # TODO: Requirements for parallel runs should not be added in places like these. Parallelization
                #  should be a feature of the job runner somehow

                #if galaxyFn == None: #then this is a test
                uniqueId = time.time()
                #else:
                    #uniqueId = extractIdFromGalaxyFn(galaxyFn)[1]
                    
                fullRunParams["uniqueId"] = uniqueId

            from quick.application.GalaxyInterface import GalaxyInterface

            analysisDefParams = [ '[' + key + '=' + value + ']' for key,value in bc.paramDict.items()]
            analysisDef = ''.join(analysisDefParams) + '->' + bc.statClassName

            # TODO: Keeping the ugly accesses to private methods in GalaxyInterface for now. To be refactored.
            trackNames, analysisDef = GalaxyInterface._cleanUpAnalysisDef(bc.cleanedTrackNames, analysisDef)

            if printProgress:
                revEngBatchLine = RunDescription.getRevEngBatchLine(
                    analysisDef, bc.trackNames, bc.cleanedTrackNames, bc.regSpec, bc.binSpec, genome
                )

                print 'Corresponding batch command line:<br>{}<br><br>'.format(revEngBatchLine)

            results = AnalysisDefJob(analysisDef, bc.cleanedTrackNames[0], bc.cleanedTrackNames[1], bc.userBinSource, galaxyFn=galaxyFn, **fullRunParams).run(printProgress)
            presCollectionType = results.getPresCollectionType()

            if len(results.getResDictKeys()) > 0 and GalaxyInterface.APPEND_ASSEMBLY_GAPS and presCollectionType=='standard':
                if USE_PARALLEL:
                    gapRes = AssemblyGapJob(bc.userBinSource, genome, uniqueId=uniqueId).run(printProgress)
                else:
                    gapRes = AssemblyGapJob(bc.userBinSource, genome).run(printProgress)
                results.includeAdditionalResults(gapRes, ensureAnalysisConsistency=False)

        except Exception, e:
            #print 'NOWAG BExc'
            results = Results(bc.cleanedTrackNames[0], bc.cleanedTrackNames[1], bc.statClassName)
            results.addError(e)
            logException(e,message='Error in batch run')
            if DebugConfig.PASS_ON_BATCH_EXCEPTIONS:
                raise
            return results
        
        return results
                

    @staticmethod
    def _constructBins(regSpec, binSpec, genome, trackNames):
        # Construct and check bins
        try:
            from quick.application.GalaxyInterface import GalaxyInterface
            userBinSource = GalaxyInterface._getUserBinSource(regSpec, binSpec, genome, trackNames)
            return [None, userBinSource]
        except Exception, e:
            results = Results([], [], '')
            results.addError(InvalidRunSpecException('Error in specification of analysis region or binsize: ' + str(e)))
            logMessage('Error in specification of analysis region (' + regSpec +') or binsize: (' + binSpec + ')')
            if DebugConfig.PASS_ON_BATCH_EXCEPTIONS:
                raise
            return [results, None]

    @staticmethod
    def _parseClassAndParams(spec):        
        if '(' in spec:
            assert(spec.count('(') == spec.count(')') == 1), spec
            paramSpec = spec[spec.find('(')+1: spec.find(')')]
            if paramSpec == '':
                paramDict = {}
            else:
                paramDict = dict([param.split('=') for param in paramSpec.split(',')])
            return spec[0: spec.find('(')], paramDict
        else:
            return spec, {}

    @staticmethod
    def _inferTrackNames(trackNames, genome, fullAccess):
        return [BatchRunner._inferTrackName(trackName, genome, fullAccess) for trackName in trackNames]

    @staticmethod
    def _inferTrackName(trackName, genome, fullAccess):
        if len(trackName) == 0 or \
                len(trackName) == 1 and trackName[0].lower() in ['blank', 'none', 'dummy', '_', ' ', '']:
            return None

        # trackName = rawTN.replace('_',' ').split(':')
        # trackName = rawTN.split(':')
        #
        # trackName = convertTNstrToTNListFormat(rawTN)

        if ProcTrackOptions.isValidTrack(genome, trackName, fullAccess):
            return trackName
        else:
            raise InvalidRunSpecException('Error in trackname specification. \'' +\
                                          ':'.join(trackName) + '\' does not match any tracknames. ' +\
                                          'This may be because of limited user permissions.')

            # print 'No exact match for track name (%s). Searching for submatch in genome %s. ' % (rawTN, genome)
            # candidates = [candidate for candidate in ProcTrackNameSource(genome, fullAccess, avoidLiterature=True)\
            #    #if rawTN.lower() in (':'.join(candidate)).replace(' ','_').lower()]
            #    if rawTN.lower() in (':'.join(candidate)).lower()]
            # if len(candidates) == 0:
            #    raise InvalidRunSpecException('Error in trackname specification. \''\
            #                                  + rawTN + '\' does not match any tracknames. This may be because of limited user permissions.')
            # elif len(candidates) > 1:
            #    raise InvalidRunSpecException('Error in trackname specification. \''\
            #                                  + rawTN + '\' matches more than one trackname: \n- ' + '\n- '.join([':'.join(x) for x in candidates]))
            # else:
            #    return candidates[0]

    
class SuperBatchRunner:
    "For parsing super-batch format to standard batch format."
    @staticmethod
    def runManyLines(superLines, genome, fullAccess, galaxyFn=None, printProgress=True):
        batchLines = SuperBatchConverter.super2batch(superLines, genome)
        return BatchRunner.runManyLines(batchLines, genome, fullAccess, useBatchId=False, galaxyFn=galaxyFn, printProgress=printProgress)
#        except Exception, e:
#            results = Results(['N/A'],['N/A'],'N/A')
#            results.addError(InvalidRunSpecException('Error in batch specification: ' + str(e)))
#            return [results]


if __name__ == '__main__':
    if len(sys.argv != 3):
        print 'Syntax: BatchRunner genome batchFn'
    else:
        BatchRunner.runFromFn(sys.argv[2], sys.argv[1], fullAccess=True)
