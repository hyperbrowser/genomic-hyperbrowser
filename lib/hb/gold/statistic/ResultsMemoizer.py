
from config.DebugConfig import DebugConfig
from gold.application.LogSetup import logMessage
from gold.formatconversion.AllFormatConverters import getFormatConverterByName
from gold.util.CustomExceptions import ShouldNotOccurError, MissingInfoError

from collections import namedtuple

from gold.statistic.MemoDataCollection import MemoDataCollection
from gold.util.CommonFunctions import createMemoPath, getClassName, ensurePathExists
from gold.util.CompBinManager import CompBinManager
from config.Config import (LOAD_DISK_MEMOIZATION as CFG_LOAD_DISK_MEMOIZATION,
                           STORE_DISK_MEMOIZATION as CFG_STORE_DISK_MEMOIZATION,
                           USE_DISK_MEMOIZATION_FOR_MINIMAL_RUNS,
                           MEMOIZED_DATA_PATH)

import os

from quick.util.CommonFunctions import isIter

MinimalMemoResult = namedtuple('MinimalMemoResult', ['result', 'formatConverters', 'error'])
MinimalMemoResult.__new__.__defaults__ = (None, None, None)

from tblib.decorators import Error


class ResultsMemoizer(object):
    LOAD_DISK_MEMOIZATION = CFG_LOAD_DISK_MEMOIZATION
    STORE_DISK_MEMOIZATION = CFG_STORE_DISK_MEMOIZATION

    MINIMAL_MEMO_PATH = os.path.join(*(list(os.path.split(MEMOIZED_DATA_PATH)) + ['minimal']))

    memoDataCollection = MemoDataCollection()

    # STATS_WITHOUT_MEMOIZATION = ['RawDataStatUnsplittable', 'CustomRStatUnsplittable', \
    #                             'BasicCustomRStatUnsplittable','ZipperStatUnsplittable', \
    #                             'XYPairStatUnsplittable', 'DataComparisonStatUnsplittable',\
    #                             'ListCollapserStatUnsplittable', 'SingleValExtractorStatUnsplittable']
    
    @classmethod
    def storeResult(cls, stat):
        if stat.resultLoadedFromDisk():
            return

        if cls._shouldUseDiskMemoization(stat, store=True):
            memoPath = cls._createMemoPath(stat)
            key = cls._createMemoKey(stat)

            if DebugConfig.VERBOSE:
                logMessage('Storing result "{}" in "{}"'.format(stat._result, memoPath))
            cls.memoDataCollection[memoPath][key] = stat._result

    @classmethod
    def loadResult(cls, stat):
        if cls._shouldUseDiskMemoization(stat, store=False):
            memoPath = cls._createMemoPath(stat)
            key = cls._createMemoKey(stat)

            memoDict = cls.memoDataCollection[memoPath]
            if key in memoDict:
                res = cls.memoDataCollection[memoPath][key]
                stat.setMemoizedResult(res)

                if DebugConfig.VERBOSE:
                    logMessage('Loading result "{}" in "{}"'.format(res, memoPath))

                stat.setMemoizedResult(res)

    @classmethod
    def _createMemoKey(cls, stat):
        posIndex = str(stat._region.start)
        return '_'.join((stat._region.chr, posIndex))

    @classmethod
    def storeMinimalError(cls, stat,  exc_info=None):
        # if stat.resultLoadedFromDisk():
        #     return

        if cls._shouldUseDiskMemoizationForMinimalRuns(stat):
            cls._storeMinimalMemoResult(stat, MinimalMemoResult(error=Error(*exc_info)))

    @classmethod
    def storeMinimalResult(cls, stat):
        if stat.resultLoadedFromDisk():
            return

        if cls._shouldUseDiskMemoizationForMinimalRuns(stat):
            formatConverters = [[getClassName(converter) for converter in track.formatConverters]
                                if track.formatConverters else track.formatConverters for track in stat.getAllTracks()]
            cls._storeMinimalMemoResult(stat, MinimalMemoResult(result=stat._result, formatConverters=formatConverters))

    @classmethod
    def _storeMinimalMemoResult(cls, stat, minimalMemoResult):
        minimalMemoDict = cls.memoDataCollection[cls.MINIMAL_MEMO_PATH]
        minimalMemoKey = cls._createMinimalMemoKey(stat)
        if minimalMemoKey in minimalMemoDict:
            raise ShouldNotOccurError('Trying to store minimal memo result for "{}"'.format(minimalMemoKey) +
                                      'when already present in minimal memoized result dict. The existing result '
                                      'should have been loaded and used, and no result should subsequently be stored.')
        else:
            if minimalMemoResult.error:
                if DebugConfig.VERBOSE:
                    logMessage('Storing exception "{}" for "{}"'.format(minimalMemoResult.error.exc_value,
                                                                        minimalMemoKey))
            else:
                if DebugConfig.VERBOSE:
                    logMessage('Storing result "{}" for "{}"'.format(minimalMemoResult.result, minimalMemoKey))
            minimalMemoDict[minimalMemoKey] = minimalMemoResult

        # cls.memoDataCollection.syncDict(cls.MINIMAL_MEMO_PATH)

    @classmethod
    def loadMinimalResult(cls, stat):
        if cls._shouldUseDiskMemoizationForMinimalRuns(stat):
            minimalMemoDict = cls.memoDataCollection[cls.MINIMAL_MEMO_PATH]
            minimalMemoKey = cls._createMinimalMemoKey(stat)
            if DebugConfig.VERBOSE:
                logMessage('Checking minimal memo dict for key "{}"'.format(minimalMemoKey))
            if minimalMemoKey in minimalMemoDict:
                minimalMemoResult = minimalMemoDict[minimalMemoKey]
                if minimalMemoResult.error is not None:
                    error = minimalMemoResult.error
                    if DebugConfig.VERBOSE:
                        logMessage('Loading exception "{}" from "{}"'.format(error.exc_value, minimalMemoKey))
                    # stat.setMemoizedResult(None)
                    stat.flagResultLoadedFromDisk()
                    return error
                else:
                    if DebugConfig.VERBOSE:
                        logMessage('Loading result "{}" from "{}"'.format(minimalMemoResult.result, minimalMemoKey))
                    stat.setMemoizedResult(minimalMemoResult.result)

                    for i, track in enumerate(stat.getAllTracks()):
                        track.formatConverters = [getFormatConverterByName(converterClassName)
                                                  for converterClassName in minimalMemoResult.formatConverters[i]]

    @classmethod
    def _shouldUseDiskMemoization(cls, stat, store):
        assert store in [True, False]

        if CompBinManager.isMinimalBin(stat._region):
            return False

        return (cls.STORE_DISK_MEMOIZATION if store else cls.LOAD_DISK_MEMOIZATION) and \
               CompBinManager.isMemoBin(stat._region) and \
               stat.IS_MEMOIZABLE and \
               cls._allTracksAreMemoizable(stat)

    @classmethod
    def _shouldUseDiskMemoizationForMinimalRuns(cls, stat):
        return USE_DISK_MEMOIZATION_FOR_MINIMAL_RUNS and \
               stat.IS_MINIMAL_MEMOIZABLE and \
               cls._noTracksAreRandomized(stat)

    @classmethod
    def _createMinimalMemoPath(cls, pathItems):
        return os.path.join(*(list(os.path.split(MEMOIZED_DATA_PATH)) + pathItems))

        if cls._shouldUseDiskMemoizationForMinimalRuns(stat):
            formatConverters = [[getClassName(converter) for converter in track.formatConverters]
                                if track.formatConverters else track.formatConverters for track in stat.getAllTracks()]
            cls._storeMinimalMemoResult(stat, MinimalMemoResult(result=stat._result, formatConverters=formatConverters))

    @classmethod
    def _storeMinimalMemoResult(cls, stat, minimalMemoResult):
        minimalMemoDict = cls.memoDataCollection[cls.MINIMAL_MEMO_PATH]
        minimalMemoKey = cls._createMinimalMemoKey(stat)
        if minimalMemoKey in minimalMemoDict:
            raise ShouldNotOccurError('Trying to store minimal memo result for "{}"'.format(minimalMemoKey) +
                                      'when already present in minimal memoized result dict. The existing result '
                                      'should have been loaded and used, and no result should subsequently be stored.')
        else:
            if minimalMemoResult.error:
                if DebugConfig.VERBOSE:
                    logMessage('Storing exception "{}" for "{}"'.format(minimalMemoResult.error.exc_value,
                                                                        minimalMemoKey))
            else:
                if DebugConfig.VERBOSE:
                    logMessage('Storing result "{}" for "{}"'.format(minimalMemoResult.result, minimalMemoKey))
            minimalMemoDict[minimalMemoKey] = minimalMemoResult

        # cls.memoDataCollection.syncDict(cls.MINIMAL_MEMO_PATH)

    @classmethod
    def loadMinimalResult(cls, stat):
        if cls._shouldUseDiskMemoizationForMinimalRuns(stat):
            minimalMemoDict = cls.memoDataCollection[cls.MINIMAL_MEMO_PATH]
            minimalMemoKey = cls._createMinimalMemoKey(stat)
            if DebugConfig.VERBOSE:
                logMessage('Checking minimal memo dict for key "{}"'.format(minimalMemoKey))
            if minimalMemoKey in minimalMemoDict:
                minimalMemoResult = minimalMemoDict[minimalMemoKey]
                if minimalMemoResult.error is not None:
                    error = minimalMemoResult.error
                    if DebugConfig.VERBOSE:
                        logMessage('Loading exception "{}" from "{}"'.format(error.exc_value, minimalMemoKey))
                    # stat.setMemoizedResult(None)
                    stat.flagResultLoadedFromDisk()
                    return error
                else:
                    if DebugConfig.VERBOSE:
                        logMessage('Loading result "{}" from "{}"'.format(minimalMemoResult.result, minimalMemoKey))
                    stat.setMemoizedResult(minimalMemoResult.result)

                    for i, track in enumerate(stat.getAllTracks()):
                        track.formatConverters = [getFormatConverterByName(converterClassName)
                                                  for converterClassName in minimalMemoResult.formatConverters[i]]

    @classmethod
    def _shouldUseDiskMemoization(cls, stat, store):
        assert store in [True, False]

        if CompBinManager.isMinimalBin(stat._region):
            return False

        return (cls.STORE_DISK_MEMOIZATION if store else cls.LOAD_DISK_MEMOIZATION) and \
               CompBinManager.isMemoBin(stat._region) and \
               stat.IS_MEMOIZABLE and \
               cls._allTracksAreMemoizable(stat)

    @classmethod
    def _shouldUseDiskMemoizationForMinimalRuns(cls, stat):
        return USE_DISK_MEMOIZATION_FOR_MINIMAL_RUNS and \
               stat.IS_MINIMAL_MEMOIZABLE and \
               cls._noTracksAreRandomized(stat)

    @classmethod
    def _createMinimalMemoPath(cls, pathItems):
        return os.path.join(*(list(os.path.split(MEMOIZED_DATA_PATH)) + pathItems))

    @classmethod
    def _createMemoPath(cls, stat):
        return createMemoPath(*cls._createMemoItems(stat, useTrackFormatAsKey=False))

    @classmethod
    def _createMemoItems(cls, stat, useTrackFormatAsKey=True):
        from gold.description.TrackInfo import TrackInfo

        genome = stat.getGenome()

        statId = getClassName(stat) + '_' + stat.VERSION
        configHash = stat.getConfigKey(ignoreUsername=False)

        trackHashList = []
        tracks = [stat._track]
        if hasattr(stat, '_track2') and stat._track2 is not None:
            tracks.append(stat._track2)
        for track in tracks:
            if useTrackFormatAsKey and not cls._isRandomizedTrack(track):
                trackFormatHash = TrackInfo(genome, track.trackName).trackFormatHash
                if not trackFormatHash:
                    raise MissingInfoError('Precalculated TrackFormat hash is missing from TrackInfo, '
                                           'for track "{}" of genome "{}". '.format(track.trackName, genome) +
                                           'Please consider to repeat the preprocessing step.')
                trackHashList.append(trackFormatHash)
            else:
                trackHashList.append(track.getUniqueKey(genome))
        return [stat._region, statId, configHash] + trackHashList

    @classmethod
    def _createMinimalMemoKey(cls, stat):
        memoItems = cls._createMemoItems(stat, useTrackFormatAsKey=True)

        region = memoItems[0]
        # if isIter(region), we can access first item as we know it is a minimalBin, which is a list
        region = "[{}]".format(region[0]) if isIter(region) else str(region)
        return '_'.join(str(_) for _ in [region] + memoItems[1:])

    @classmethod
    def _allTracksAreMemoizable(cls, stat):
        return all(track.IS_MEMOIZABLE for track in stat.getAllTracks())

    @classmethod
    def _noTracksAreRandomized(cls, stat):
        return not any(cls._isRandomizedTrack(track) for track in stat.getAllTracks())

    @classmethod
    def _isRandomizedTrack(cls, track):
        from gold.track.RandomizedTrack import RandomizedTrack
        return isinstance(track, RandomizedTrack)

    @classmethod
    def flushStoredResults(cls):
        cls.memoDataCollection.syncAllDicts()
