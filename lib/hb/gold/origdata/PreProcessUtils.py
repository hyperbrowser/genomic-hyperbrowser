import os
import sys
import shutil
import numpy
from config.Config import PROCESSED_DATA_PATH
from config.DebugConfig import DebugConfig
from gold.description.TrackInfo import TrackInfo, PrefixInfo
from gold.origdata.PreProcMetaDataCollector import PreProcMetaDataCollector
from gold.origdata.GenomeElement import GenomeElement
from gold.track.BoundingRegionShelve import BoundingRegionShelve
from gold.track.CommonMemmapFunctions import parseMemmapFileFn
from gold.track.TrackFormat import TrackFormat
from gold.track.TrackSource import TrackSource
from gold.util.CommonConstants import RESERVED_PREFIXES
from gold.util.CommonFunctions import createDirPath
from gold.util.CustomExceptions import InvalidFormatError, ShouldNotOccurError
from quick.util.GenomeInfo import GenomeInfo

class PreProcessUtils(object):
    @classmethod
    def shouldPreProcessGESource(cls, trackName, geSource, allowOverlaps):
        genome = geSource.getGenome()
        storedInfo = TrackInfo(genome, trackName)
        
        validFilesExist = cls.preProcFilesExist(genome, trackName, allowOverlaps) and \
            storedInfo.isValid()
        
        if not geSource.hasOrigFile():
            return False if validFilesExist or geSource.isExternal() else True

        from gold.origdata.PreProcessTracksJob import PreProcessTracksJob
        if DebugConfig.VERBOSE:
            print os.linesep.join(["GenomeElementSource id: {}, ".format(cls.constructId(geSource)) +
                                   "TrackInfo.id: {}".format(storedInfo.id),
                                   "GenomeElementSource version: {}, ".format(geSource.getVersion()) +
                                   "TrackInfo.geSourceVersion: {}".format(storedInfo.geSourceVersion),
                                   "PreProcessTracksJob version: {}, ".format(PreProcessTracksJob.VERSION) +
                                   "TrackInfo.preProcVersion: {}".format(storedInfo.preProcVersion),])
        storedAsAccordingToGeSource = \
            (cls.constructId(geSource) == storedInfo.id and
             geSource.getVersion() == storedInfo.geSourceVersion and
             PreProcessTracksJob.VERSION == storedInfo.preProcVersion)
        
        #from gold.application.LogSetup import logMessage
        #logMessage(geSource.getGenome())
        #logMessage(':'.join(trackName))
        #logMessage('%s %s %s %s %s' % (cls.preProcFilesExist(genome, trackName, allowOverlaps), \
        #                               storedInfo.isValid(), \
        #                               geSource.hasOrigFile(), \
        #                               cls.constructId(geSource) == storedInfo.id, \
        #                               geSource.getVersion() == storedInfo.preProcVersion))
        
        return not (validFilesExist and storedAsAccordingToGeSource)
    
    @classmethod
    def preProcFilesExist(cls, genome, trackName, allowOverlaps):
        collector = PreProcMetaDataCollector(genome, trackName)
        preProcFilesExist = collector.preProcFilesExist(allowOverlaps)
        if preProcFilesExist is None:
            merged = cls.mergedPreProcFilesExist(genome, trackName, allowOverlaps)
            if merged:
                preProcFilesExist = True
            else:
                preProcFilesExist = cls.oldTypePreProcFilesExist(genome, trackName, allowOverlaps)
            collector.updatePreProcFilesExistFlag(allowOverlaps, preProcFilesExist, merged)
        return preProcFilesExist

    @staticmethod
    def mergedPreProcFilesExist(genome, trackName, allowOverlaps):
        return BoundingRegionShelve(genome, trackName, allowOverlaps).fileExists()

    @classmethod
    def oldTypePreProcFilesExist(cls, genome, trackName, allowOverlaps):
        dirPath = createDirPath(trackName, genome, allowOverlaps=allowOverlaps)
        return os.path.exists(dirPath) and cls._hasOldTypeChromSubDirs(dirPath, genome)

    @classmethod
    def _hasOldTypeChromSubDirs(cls, dirPath, genome):
        for subDir in os.listdir(dirPath):
            fullSubDirPath = os.path.join(dirPath, subDir)
            if os.path.isdir(fullSubDirPath) and \
                cls._isOldTypeChromDirectory(fullSubDirPath, genome):
                    return True
        return False
    
    @staticmethod
    def _isOldTypeChromDirectory(dirPath, genome):
        if dirPath[-1] == os.sep:
            dirPath = os.path.dirname(dirPath)
        dirName = os.path.basename(dirPath)
        return dirName in set(GenomeInfo.getExtendedChrList(genome)) and \
            not any(os.path.isdir(os.path.join(dirPath, subFn)) for subFn in os.listdir(dirPath))
    
    @staticmethod
    def constructId(geSource):
        from gold.origdata.PreProcessTracksJob import PreProcessTracksJob
        if geSource.hasOrigFile():
            origPath = os.path.dirname(geSource.getFileName()) if not geSource.isExternal() else geSource.getFileName()
            return TrackInfo.constructIdFromPath(geSource.getGenome(), origPath, \
                                                 geSource.getVersion(), PreProcessTracksJob.VERSION)
        else:
            return geSource.getId()
        
    @classmethod
    def removeOutdatedPreProcessedFiles(cls, genome, trackName, allowOverlaps, mode):
        collector = PreProcMetaDataCollector(genome, trackName)
        if cls.preProcFilesExist(genome, trackName, allowOverlaps) and not \
            collector.hasRemovedPreProcFiles(allowOverlaps):
                dirPath = createDirPath(trackName, genome, allowOverlaps=allowOverlaps)
                
                assert( dirPath.startswith(PROCESSED_DATA_PATH) )
                if mode == 'Real':
                    print 'Removing outdated preprocessed data: ', dirPath
                    for fn in os.listdir(dirPath):
                        fullFn = os.path.join(dirPath, fn)
                        if os.path.isfile(fullFn):
                            os.unlink(fullFn)
                        if os.path.isdir(fullFn):
                            if cls._isOldTypeChromDirectory(fullFn, genome):
                                shutil.rmtree(fullFn)
                else:
                    print 'Would now have removed outdated preprocessed data if real run: ', dirPath
                
                collector.updateRemovedPreProcFilesFlag(allowOverlaps, True)
        
        if mode == 'Real':
            ti = TrackInfo(genome, trackName)
            ti.resetTimeOfPreProcessing()
                
    @staticmethod
    def createBoundingRegionShelve(genome, trackName, allowOverlaps):
        collector = PreProcMetaDataCollector(genome, trackName)
        boundingRegionTuples = collector.getBoundingRegionTuples(allowOverlaps)
        if not collector.getTrackFormat().reprIsDense():
            boundingRegionTuples = sorted(boundingRegionTuples)
        
        geChrList = collector.getPreProcessedChrs(allowOverlaps)
        brShelve = BoundingRegionShelve(genome, trackName, allowOverlaps)
        brShelve.storeBoundingRegions(boundingRegionTuples, geChrList, not collector.getTrackFormat().reprIsDense())
        
        #Sanity check
        if brShelve.getTotalElementCount() != collector.getNumElements(allowOverlaps):
            raise ShouldNotOccurError("Error: The total element count for all bounding regions is not equal to the total number of genome elements. %s != %s" % \
                                      (brShelve.getTotalElementCount(), collector.getNumElements(allowOverlaps)) )
    
    @staticmethod
    def removeChrMemmapFolders(genome, trackName, allowOverlaps):
        chrList = PreProcMetaDataCollector(genome, trackName).getPreProcessedChrs(allowOverlaps)
        for chr in chrList:
            path = createDirPath(trackName, genome, chr, allowOverlaps)
            assert os.path.exists(path), 'Path does not exist: ' + path
            assert os.path.isdir(path), 'Path is not a directory: ' + path
            shutil.rmtree(path)

    @staticmethod
    def checkIfEdgeIdsExist(genome, trackName, allowOverlaps):
        collector = PreProcMetaDataCollector(genome, trackName)
        if not collector.getTrackFormat().isLinked():
            return
        
        uniqueIds = numpy.array([], dtype='S')
        uniqueEdgeIds = numpy.array([], dtype='S')
        
        for chr in collector.getPreProcessedChrs(allowOverlaps):
            trackSource = TrackSource()
            trackData = trackSource.getTrackData(trackName, genome, chr, allowOverlaps)
            uniqueIds = numpy.unique(numpy.concatenate((uniqueIds, trackData['id'][:])))
            uniqueEdgeIds = numpy.unique(numpy.concatenate((uniqueEdgeIds, trackData['edges'][:].flatten())))
        
        uniqueIds = uniqueIds[uniqueIds != '']
        uniqueEdgeIds = uniqueEdgeIds[uniqueEdgeIds != '']
        
        unmatchedIds = set(uniqueEdgeIds) - set(uniqueIds)
        if len(unmatchedIds) > 0:
            raise InvalidFormatError("Error: the following ids specified in the 'edges' column do not exist in the dataset: " + ', '.join(sorted(unmatchedIds)))
    
    @classmethod
    def checkUndirectedEdges(cls, genome, trackName, allowOverlaps):
        collector = PreProcMetaDataCollector(genome, trackName)
        if not (collector.getTrackFormat().isLinked() and collector.hasUndirectedEdges()):
            return
        
        complementEdgeWeightDict = {}
        
        for chr in collector.getPreProcessedChrs(allowOverlaps):
            trackSource = TrackSource()
            trackData = trackSource.getTrackData(trackName, genome, chr, allowOverlaps)
            
            ids = trackData['id']
            edges = trackData['edges']
            weights = trackData.get('weights')
            
            for i, id in enumerate(ids):
                edgesAttr = edges[i][edges[i] != '']
                weightsAttr = weights[i][edges[i] != ''] if weights is not None else None
                cls._adjustComplementaryEdgeWeightDict(complementEdgeWeightDict, id, edgesAttr, weightsAttr)
        
        if len(complementEdgeWeightDict) != 0:
                unmatchedPairs = []
                for toId in complementEdgeWeightDict:
                    for fromId in complementEdgeWeightDict[toId]:
                        unmatchedPairs.append((fromId, toId, complementEdgeWeightDict[toId][fromId]))
                raise InvalidFormatError("Error: All edges are not undirected. The following edges specifications " +\
                                         "are not matched by an opposite edge with equal weight:" + os.linesep +\
                                         os.linesep.join(["from '%s' to '%s'" % (fromId, toId) + \
                                                          (" with weight '%s'" % weight  if weight != '' else '') \
                                                          for fromId, toId, weight in unmatchedPairs]))
        
    @staticmethod
    def _adjustComplementaryEdgeWeightDict(complementEdgeWeightDict, id, edges, weights):
        for index, edgeId in enumerate(edges):
            weight = weights[index] if weights is not None else ''
                
            if id in complementEdgeWeightDict and edgeId in complementEdgeWeightDict[id]:
                complWeight = complementEdgeWeightDict[id][edgeId]
                try:
                    equal = numpy.all(complWeight == weight | numpy.isnan(complWeight) & numpy.isnan(weight))
                except TypeError:
                    try:
                        equal = (complWeight == weight) or (numpy.isnan(complWeight) and numpy.isnan(weight))
                    except (TypeError, ValueError):
                        equal = numpy.all(complWeight == weight)
                if not equal:
                    raise InvalidFormatError("Error: edge ('%s' <-> '%s') is not undirected. The weight must be equal in both directions (%s != %s)" % (edgeId, id, complementEdgeWeightDict[id][edgeId], weights[index]))
                del complementEdgeWeightDict[id][edgeId]
                if len(complementEdgeWeightDict[id]) == 0:
                    del complementEdgeWeightDict[id]
                        
            elif id == edgeId:
                continue
                
            elif edgeId in complementEdgeWeightDict:
                if id in complementEdgeWeightDict[edgeId]:
                    raise ShouldNotOccurError('Error: the complementary edge(%s) has already been added to complementEdgeWeightDict["%s"] ... ' % (id, edgeId))
                complementEdgeWeightDict[edgeId][id] = weight
            else:
                complementEdgeWeightDict[edgeId] = {id: weight}

    @classmethod
    def getMergedPrefixInfoDict(cls, genome, trackName, allowOverlaps):
        assert cls.mergedPreProcFilesExist(genome, trackName, allowOverlaps)
        trackData = TrackSource().getTrackData(trackName, genome, None, allowOverlaps)
        prefixInfoDict = {}
        for prefix, smartMemmap in trackData.items():
            if prefix not in ['leftIndex', 'rightIndex']:
                prefixInfoDict[prefix] = PrefixInfo(*parseMemmapFileFn(smartMemmap.getFilename()))
        return prefixInfoDict
