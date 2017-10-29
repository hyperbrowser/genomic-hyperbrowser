import numpy as np

from gold.track.NumpyDataFrame import NumpyDataFrame


class RandomizedTrackDataStorage(object):
    # For the joint consecutive index defined from the double for loop over all tracks and bins
    ORIG_TRACK_BIN_INDEX_KEY = 'origTrackBinIndex'

    ORIG_TRACK_EL_INDEX_IN_BIN = 'origTrackElIndexInBin'
    NEW_TRACK_BIN_INDEX_KEY = 'newTrackBinIndex'
    LENGTH_KEY = 'lengths'

    def __init__(self, trackBinIndexer, readFromDiskTrackColNames, generatedTrackColNames, needsMask):
        self._trackBinIndexer = trackBinIndexer
        self._readFromDiskTrackColNames = readFromDiskTrackColNames
        self._generatedTrackColNames = generatedTrackColNames
        self._needsMask = needsMask

        assert len(self._readFromDiskTrackColNames) > 0

        self._dataFrame = self._initDataFrame()

    def _initDataFrame(self):
        dataFrame = NumpyDataFrame()

        listOfColNameToTrackBinArrayDicts = self._initializeRandAlgArrays()
        arrayLengths = self._addConcatenatedTrackBinArraysToDataFrame(dataFrame, listOfColNameToTrackBinArrayDicts)
        self._addMandatoryArraysToDataFrame(dataFrame, arrayLengths)
        if self._needsMask:
            dataFrame.mask = np.zeros(len(self._dataFrame), dtype=bool)

        return dataFrame

    def _initializeRandAlgArrays(self):
        listOfColToArrayDicts = []

        for trackBinIndex in self._trackBinIndexer.allTrackBinIndexes():
            trackBinPair = self._trackBinIndexer.getTrackBinPairForTrackBinIndex(trackBinIndex)
            trackView = trackBinPair.getTrackView()

            colToArrayDict = {}
            self._readArraysFromDiskAndUpdateDict(colToArrayDict, trackView)
            self._generateArraysAndUpdateDict(colToArrayDict, trackView)
            listOfColToArrayDicts.append(colToArrayDict)

        return listOfColToArrayDicts

    def _generateArraysAndUpdateDict(self, colToArrayDict, trackView):
        for col in self._generatedTrackColNames:
            if col == self.LENGTH_KEY:
                numpyArray = trackView.startsAsNumpyArray()
            else:
                numpyArray = trackView.getNumpyArrayFromPrefix(col)
            colToArrayDict[col] = np.zeros(len(numpyArray), dtype=numpyArray.dtype)

    def _readArraysFromDiskAndUpdateDict(self, colToArrayDict, trackView):
        for col in self._readFromDiskTrackColNames:
            if col == self.LENGTH_KEY:
                colToArrayDict[col] = trackView.endsAsNumpyArray() - trackView.startsAsNumpyArray()
            else:
                colToArrayDict[col] = trackView.getNumpyArrayFromPrefix(col)

    def _addConcatenatedTrackBinArraysToDataFrame(self, dataFrame, listOfColNameToTrackBinArrayDicts):
        for i, colName in enumerate(self._readFromDiskTrackColNames + self._generatedTrackColNames):
            allTrackBinArraysForColName = [colNameToTrackBinArrayDict[colName] for colNameToTrackBinArrayDict in
                                           listOfColNameToTrackBinArrayDicts]
            fullArrayForColName = np.concatenate(allTrackBinArraysForColName)

            if i == 0:
                arrayLengths = [len(_) for _ in allTrackBinArraysForColName]

            dataFrame.addArray(colName, fullArrayForColName)

        return arrayLengths

    def _addMandatoryArraysToDataFrame(self, dataFrame, arrayLengths):
        self._addOrigTrackBinIndexArray(dataFrame, arrayLengths)
        self._addOrigTrackElIndexInBinArray(dataFrame, arrayLengths)
        self._addNewTrackBinIndexArray(dataFrame, arrayLengths)

    def _addOrigTrackBinIndexArray(self, dataFrame, arrayLengths):
        origTrackBinIndexArrays = [np.ones(length, dtype='int32') for length in arrayLengths]
        fullOrigTrackBinIndexArray = np.concatenate([array * i for i, array in enumerate(origTrackBinIndexArrays)])
        dataFrame.addArray(self.ORIG_TRACK_BIN_INDEX_KEY, fullOrigTrackBinIndexArray)

    def _addOrigTrackElIndexInBinArray(self, dataFrame, arrayLengths):
        origTrackElIndexInBinArrays = [np.arange(length, dtype='int32') for length in arrayLengths]
        fullOrigTrackElIndexInBinArray = np.concatenate([array for array in origTrackElIndexInBinArrays])
        dataFrame.addArray(self.ORIG_TRACK_EL_INDEX_IN_BIN, fullOrigTrackElIndexInBinArray)

    def _addNewTrackBinIndexArray(self, dataFrame, arrayLengths):
        dataFrame.addArray(self.NEW_TRACK_BIN_INDEX_KEY, np.zeros(sum(arrayLengths), dtype='int32'))

    def shuffle(self):
        np.random.shuffle(self._dataFrame)

    def getTrackStorageView(self, origTrackBinIndex):
        pass

    def getTrackView(self, origTrackBinIndex):
        # Provides a TrackView with a VirtualNumpyArray for all columns that are found in all tracks (intersection of set of columns per track)
        pass
