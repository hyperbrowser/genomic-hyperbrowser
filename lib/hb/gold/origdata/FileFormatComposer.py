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

from collections import namedtuple
from cStringIO import StringIO
from config.Config import OUTPUT_PRECISION
from gold.util.CustomExceptions import InvalidFormatError, AbstractClassError, NotIteratedYetError
from quick.util.CommonFunctions import isNan, ensurePathExists
from gold.util.CommonConstants import BINARY_MISSING_VAL
from gold.origdata.GEDependentAttributesHolder import GEDependentAttributesHolder

MatchResult = namedtuple('MatchResult', ['match', 'trackFormatName'])
ComposerInfo = namedtuple('ComposerInfo', ['trackFormatName','fileFormatName','fileSuffix'])


def findMatchingFileFormatComposers(trackFormat):
    matchingComposers = []
    for composer in getAllComposers():
        matchResult = composer.matchesTrackFormat(trackFormat)
        if matchResult.match:
            matchingComposers.append(ComposerInfo(trackFormatName=matchResult.trackFormatName, \
                                                  fileFormatName=composer.FILE_FORMAT_NAME, \
                                                  fileSuffix=composer.getDefaultFileNameSuffix()))
    return matchingComposers


def getComposerClsFromFileFormatName(fileFormatName):
    for composerCls in getAllComposers():
        if fileFormatName.lower() == composerCls.FILE_FORMAT_NAME.lower():
            return composerCls
    raise InvalidFormatError("Error: file format composer for format '%s' was not found." % fileFormatName)


def getComposerClsFromFileSuffix(fileSuffix):
    for composerCls in getAllComposers():
        if fileSuffix.lower() in [x.lower() for x in composerCls.FILE_SUFFIXES]:
            return composerCls
    raise InvalidFormatError("Error: file format composer for file suffix '%s' was not found." % fileSuffix)


class FileFormatComposer(object):
    FILE_SUFFIXES = ['']
    FILE_FORMAT_NAME = ''

    def __init__(self, geSource):
        try:
            if not geSource.hasBoundingRegionTuples():
                self._geSource = GEDependentAttributesHolder(geSource)
            else:
                self._geSource = geSource
        except NotIteratedYetError:
            self._geSource = geSource

        try:
            self._geSource.parseFirstDataLine()
            self._emptyGeSource = False
        except:
            self._emptyGeSource = True

        #self._emptyGeSource = True
        #for ge in self._geSource:
        #    self._emptyGeSource = False
        #    break

    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=False, trackFormatName=trackFormat.getFormatName())

    def composeToFile(self, fn, ignoreEmpty=False, **kwArgs):
        ensurePathExists(fn)
        f = open(fn, 'w')
        ok = self._composeCommon(f, ignoreEmpty, **kwArgs)
        f.close()
        return ok

    def returnComposed(self, ignoreEmpty=False, **kwArgs):
        memFile = StringIO()
        self._composeCommon(memFile, ignoreEmpty, **kwArgs)
        return memFile.getvalue()

    def _composeCommon(self, out, ignoreEmpty=False, **kwArgs):
        if ignoreEmpty and self._emptyGeSource:
            return False

        self._compose(out, **kwArgs)
        return True

    def _compose(self, out, **kwArgs):
        raise AbstractClassError()

    def _commonFormatNumberVal(self, val):
        if isNan(val) or val is None:
            return '.'
        return ('%#.' + str(OUTPUT_PRECISION) + 'g') % val
        #return '%.5f' % val

    def _commonFormatBinaryVal(self, val):
        if val == BINARY_MISSING_VAL:
            return '.'
        return 1 if val == True else 0

    @classmethod
    def getDefaultFileNameSuffix(cls):
        return cls.FILE_SUFFIXES[0]


def getAllComposers():
    from gold.origdata.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
    from gold.origdata.BedComposer import BedComposer, PointBedComposer, CategoryBedComposer, ValuedBedComposer
    from gold.origdata.BedGraphComposer import BedGraphComposer, BedGraphTargetControlComposer
    from gold.origdata.GffComposer import GffComposer, CategoryGffComposer
    from gold.origdata.WigComposer import WigComposer
    from gold.origdata.FastaComposer import FastaComposer

    return [BedComposer, PointBedComposer, CategoryBedComposer, ValuedBedComposer, BedGraphComposer, \
            BedGraphTargetControlComposer, GffComposer, CategoryGffComposer, WigComposer, FastaComposer, \
            StdGtrackComposer, ExtendedGtrackComposer]
