from copy import copy

import numpy as np
import pyBigWig
from plastid.readers.autosql import AutoSqlDeclaration

from GenomeElementSource import GenomeElementSource
from GenomeElement import GenomeElement
from gold.util.CommonConstants import BINARY_MISSING_VAL
from gold.util.CustomExceptions import InvalidFormatError


class BigBedGenomeElementSource(GenomeElementSource):
    _VERSION = '1.0'
    FILE_SUFFIXES = ['bb', 'bigbed']
    FILE_FORMAT_NAME = 'BigBed'
    BED_EXTRA_COLUMNS = ['name', 'score', 'strand', 'thickStart', 'thickEnd', 'reserved', 'blockCount', 'blockSizes',
                         'blockStarts']

    _numHeaderLines = 0
    _isSliceSource = True
    _isSorted = True
    _inputIsOneIndexed = True
    _inputIsEndInclusive = True
    _addsStartElementToDenseIntervals = False

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def __init__(self, *args, **kwArgs):
        GenomeElementSource.__init__(self, *args, **kwArgs)
        self._bigBedFile = pyBigWig.open(self._fn)
        self._chrIter = iter(sorted(self._bigBedFile.chroms().items()))

        self._extraColNames = self._initColumnNames()
        self._numOfExtraCols = 0
        if self._extraColNames:
            self._numOfExtraCols = len(self._extraColNames)

        self._parseValVec = np.vectorize(self._parseVal)
        self._getStrandFromStringVec = np.vectorize(self._getStrandFromString)

    def __iter__(self):
        self._bigBedFile = pyBigWig.open(self._fn)
        self._chrIter = iter(sorted(self._bigBedFile.chroms().items()))
        geIter = copy(self)

        return geIter

    def _initColumnNames(self):
        autoSql = self._bigBedFile.SQL()
        if autoSql:
            autoSqlParser = AutoSqlDeclaration(self._bigBedFile.SQL())
            colNames = autoSqlParser.field_formatters.keys()
            return colNames[3:]

    def _iter(self):
        return self

    def next(self):
        currentChrom = next(self._chrIter, None)
        if not currentChrom:
            self._bigBedFile.close()
            raise StopIteration

        chrName, chrLengths = currentChrom

        entries = self._bigBedFile.entries(str(chrName), 0, chrLengths)
        # self._extraColNames are initialized during the first iteration
        if self._extraColNames is None:
            self._initExtraCols(entries)

        start, end = self._parseStartAndEnd(entries)

        ge = GenomeElement(genome=self._genome, chr=chrName,
                           start=start, end=end)

        if self._numOfExtraCols != 0:
            strVals = [x[2] for x in entries]
            values = np.genfromtxt(strVals, dtype=None, names=self._extraColNames, delimiter='\t')
            if values.size == 1:
                values = values.reshape((1,))
            tmpColNames = self._extraColNames[:]
            if 'score' in self._extraColNames:
                ge.val = np.array(self._parseValVec(values['score']), dtype=np.int32)
                tmpColNames.remove('score')
            if 'strand' in self._extraColNames:
                ge.strand = np.array(self._getStrandFromStringVec(values['strand']), dtype=np.int8)
                tmpColNames.remove('strand')
            for colName in tmpColNames:
                setattr(ge, colName, values[colName].astype(str))

        #print ge

        return ge

    def _initExtraCols(self, entries):
        numOfCols = len(entries[0])
        if numOfCols >= 2 and entries[0][2]:
            extraCols = entries[0][2].split('\t')
            self._extraColNames = self.BED_EXTRA_COLUMNS[:len(extraCols)]
            self._numOfExtraCols = len(extraCols)
        else:
            self._extraColNames = []

        self._extraColNames = self.BED_EXTRA_COLUMNS[:len(extraCols)]
        self._numOfExtraCols = len(extraCols)

    def _parseStartAndEnd(self, entries):
        tupleVals = [(x[0], x[1]) for x in entries]
        intervals = np.array(tupleVals, dtype=np.dtype([('start', 'int32'), ('end', 'int32')]))

        return intervals['start'], intervals['end']

    def _parseVal(self, strVal):
        if strVal in ['-', '.']:
            val = 0
        else:
            val = int(strVal)
        if val < 0 or val > 1000:
            raise InvalidFormatError("Error: BigBed score column must be an integer between 0 and 1000")
        return val

    @classmethod
    def _getStrandFromString(cls, val):
        if val == '+':
            return 1
        elif val == '-':
            return 0
        elif val == '.':
            return BINARY_MISSING_VAL
        # val == ''?
        else:
            raise InvalidFormatError(
                "Error: strand must be either '+', '-' or '.'. Value: %s" % val)

    def getValDataType(self):
        return 'int32'
