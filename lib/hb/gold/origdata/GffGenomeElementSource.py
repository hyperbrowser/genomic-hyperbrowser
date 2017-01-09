# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

import numpy
from urllib import unquote

from gold.origdata.GenomeElementSource import GenomeElementSource
from gold.origdata.GenomeElement import GenomeElement
from gold.util.CustomExceptions import InvalidFormatError

class GffGenomeElementSource(GenomeElementSource):
    _VERSION = '1.2'
    FILE_SUFFIXES = ['gff', 'gff3']
    FILE_FORMAT_NAME = 'GFF'
    _numHeaderLines = 0

    _inputIsOneIndexed = True
    _inputIsEndInclusive = True

    def __new__(cls, *args, **kwArgs):
        return object.__new__(cls)

    def _next(self, line):
        if line.startswith('##FASTA'):
            raise StopIteration

        if len(line)>0 and line[0]=='#':
            return None

        origCols = line.split('\t')
        cols = [unquote(x) for x in origCols]

        if len(cols) != 9:
            raise InvalidFormatError("Error: GFF files must contain 9 tab-separated columns")

        ge = GenomeElement(self._genome)
        ge.chr = self._checkValidChr(cols[0])
        ge.source = cols[1]

        self._parseThirdCol(ge, cols[2])

        ge.start = self._checkValidStart(ge.chr, int(cols[3]) - 1)
        ge.end =  self._checkValidEnd(ge.chr, int(cols[4]), start=ge.start)

        self._parseSixthCol(ge, cols[5])

        ge.strand = self._getStrandFromString(cols[6])
        ge.phase = cols[7]
        ge.attributes = cols[8]

        for attr in origCols[8].split(';'):
            attrSplitted = attr.split('=')
            if len(attrSplitted) == 2:
                key, val = attrSplitted
                if key.lower() == 'id':
                    ge.id = unquote(val)
                elif key.lower() == 'name':
                    ge.name = unquote(val)

        return ge

    def _parseThirdCol(self, ge, contents):
        ge.type = contents

    def _parseSixthCol(self, ge, contents):
        ge.val = numpy.float(self._handleNan(contents))

    @classmethod
    def _getStrandFromString(cls, val):
        if val == '?':
            return BINARY_MISSING_VAL
        else:
            return GenomeElementSource._getStrandFromString(val)

class GffCategoryGenomeElementSource(GffGenomeElementSource):
    FILE_SUFFIXES = ['category.gff', 'category.gff3']
    FILE_FORMAT_NAME = 'Category GFF'

    def _parseThirdCol(self, ge, contents):
        ge.val = contents

    def _parseSixthCol(self, ge, contents):
        ge.score = self._handleNan(contents)

    def getValDataType(self):
        return 'S'
