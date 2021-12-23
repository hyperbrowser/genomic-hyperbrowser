from collections import namedtuple

import numpy as np

from gold.track.CommonMemmapFunctions import parseMemmapFileFn
from gold.track.SmartMemmap import SmartMemmap
from gold.track.TrackSource import TrackSource
from gold.track.trackstructure.random.Constants import START_KEY, END_KEY, RIGHTINDEX_KEY, LEFTINDEX_KEY

ArrayInfo = namedtuple('ArrayInfo', ('numElements', 'elementDim', 'dtypeDim', 'dtypeStr'))


class ArrayInfoStorage(object):
    IGNORE_PREFIXES = [START_KEY,
                       END_KEY,
                       RIGHTINDEX_KEY,
                       LEFTINDEX_KEY]

    def __init__(self):
        self._arrayInfoDict = {}
        self._initialized = False

    def updateInfoForTrackView(self, trackBinPair, trackView):
        track = trackBinPair.track
        curBin = trackBinPair.bin

        trackData = self._getTrackData(track, curBin, trackView.allowOverlaps)
        prefixList = [_ for _ in trackData.keys() if _ not in self.IGNORE_PREFIXES]

        if self._initialized:
            self._removeMissingPrefixesFromStorage(prefixList)

        for prefix in prefixList:
            arrayInfo = self._getArrayInfo(prefix, trackData)
            if not self._initialized:
                self._arrayInfoDict[prefix] = arrayInfo
            else:
                self._updateInfoForPrefix(prefix, arrayInfo)

    def _getTrackData(self, track, curBin, allowOverlaps):
        return TrackSource().getTrackData(track.trackName, curBin.genome,
                                          curBin.chr, allowOverlaps)

    def _getArrayInfo(self, prefix, trackData):
        smartMemmap = trackData[prefix]
        assert isinstance(smartMemmap, SmartMemmap)

        fnPrefix, elementDim, dtypeDim, dtypeStr = parseMemmapFileFn(smartMemmap.filename)
        assert prefix == fnPrefix

        numElements = smartMemmap.shape[0]

        return ArrayInfo(numElements, elementDim, dtypeDim, dtypeStr)

    def _removeMissingPrefixesFromStorage(self, prefixList):
        missingPrefixes = set(self._arrayInfoDict.keys()) - set(prefixList)
        for prefix in missingPrefixes:
            del self._arrayInfoDict[prefix]

    def _updateInfoForPrefix(self, prefix, arrayInfo):
        if prefix in self._arrayInfoDict:
            storedArrayInfo = self._arrayInfoDict[prefix]
            if not (self._compatibleDTypes(arrayInfo.dtypeStr, storedArrayInfo.dtypeStr) and
                    self._compatibleDtypeDims(arrayInfo.dtypeDim, storedArrayInfo.dtypeDim)):
                del self._arrayInfoDict[prefix]
            else:
                self._arrayInfoDict[prefix] = \
                    ArrayInfo(storedArrayInfo.numElements + arrayInfo.numElements,
                              max(storedArrayInfo.elementDim, arrayInfo.elementDim),
                              storedArrayInfo.dtypeDim,
                              self._mergeDtypes(storedArrayInfo.dtypeStr, arrayInfo.dtypeStr))

    @staticmethod
    def _compatibleDTypes(dtypeStrA, dtypeStrB):
        if np.dtype(dtypeStrA).type != np.dtype(dtypeStrB).type:
            if not all(np.dtype(dtypeStr).kind in ['i', 'f']
                       for dtypeStr in [dtypeStrA, dtypeStrB]):
                return False
        return True

    @staticmethod
    def _compatibleDtypeDims(dtypeDimA, dtypeDimB):
        return dtypeDimA == dtypeDimB

    @staticmethod
    def _mergeDtypes(dtypeStrA, dtypeStrB):
        dtypeA = np.dtype(dtypeStrA)
        dtypeB = np.dtype(dtypeStrB)

        if dtypeA.kind == dtypeB.kind:
            kind = dtypeA.kind
        else:
            assert dtypeA.kind == 'f' or dtypeB.kind == 'f'
            kind = 'f'

        itemsize = max(dtypeA.itemsize, dtypeB.itemsize)
        return kind + str(itemsize)
