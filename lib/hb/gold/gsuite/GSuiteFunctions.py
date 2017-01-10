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
import os

from gold.gsuite.GSuiteConstants import LOCAL, REMOTE, UNKNOWN, PRIMARY, COMPRESSION_SUFFIXES
from gold.gsuite.GSuiteRequirements import GSuiteRequirements
from gold.gsuite.GSuiteTrack import GSuiteTrack, SearchQueryForSuffixGSuiteTrack
from gold.util.CommonFunctions import getFileSuffix, stripFileSuffix


def splitTitleIfDuplicate(title):
    import re
    duplicateMatch = re.match('.*( \([0-9]+\))$', title)
    if duplicateMatch:
        duplicateStr = duplicateMatch.groups()[0]
        title = title[:-len(duplicateStr)]
        return title, duplicateStr
    else:
        return title, ''


def getDuplicateIdx(title):
    duplicateStr = splitTitleIfDuplicate(title)[1]
    if duplicateStr:
        import re
        countMatch = re.match(' \(([0-9])+\)$', duplicateStr)
        return int(countMatch.groups()[0])
    else:
        return 1


def renameBaseFileNameWithDuplicateIdx(baseFileName, duplicateIdx):
    if duplicateIdx == 1:
        return baseFileName
    else:
        suffixes = []
        while True:
            suffix = getFileSuffix(baseFileName)
            if suffix:
                suffixes.insert(0, suffix)
                baseFileName = baseFileName[:-len('.' + suffix)]
            else:
                break

        return baseFileName + '_%s' % duplicateIdx +\
               (('.' +'.'.join(suffixes)) if suffixes else '')


def changeSuffixIfPresent(text, oldSuffix=None, newSuffix=None):
    assert newSuffix
    prefix, suffix = os.path.splitext(text)

    if suffix and oldSuffix is None or suffix == '.' + oldSuffix:
        return prefix + '.' + newSuffix
    else:
        return text


def getTitleSuffix(title):
    return getFileSuffix(splitTitleIfDuplicate(title)[0])


def getTitleWithSuffixReplaced(title, newSuffix):
    titleSuffix = getTitleSuffix(title)
    if titleSuffix:
        rawTitle, duplicateStr = splitTitleIfDuplicate(title)
        rawTitle = stripFileSuffix(rawTitle) + (('.' + newSuffix) if newSuffix else '')
        title = rawTitle + duplicateStr

    return title


def getTitleAndSuffixWithCompressionSuffixesRemoved(gSuiteTrack):
    gSuiteReq = GSuiteRequirements(allowedLocations=[LOCAL, REMOTE], allowedFileFormats=[PRIMARY, UNKNOWN])
    gSuiteReq.check(gSuiteTrack)

    title, suffix, path = gSuiteTrack.title, gSuiteTrack.suffix, gSuiteTrack.path

    if suffix:
        for compSuffix in COMPRESSION_SUFFIXES:
            reduceLen = len(compSuffix)+1

            if suffix.lower() == compSuffix:
                if path.endswith('.' + compSuffix):
                    path = path[:-reduceLen]
                    suffix = getFileSuffix(path)
                else:
                    if isinstance(gSuiteTrack, SearchQueryForSuffixGSuiteTrack):
                        tempGSuiteTrack = GSuiteTrack(gSuiteTrack.uri.replace('.' + compSuffix, ''), title='')
                        suffix = tempGSuiteTrack.suffix
                    else:
                        suffix = None # Impossible to find uncompressed suffix
            elif suffix.lower().endswith('.' + compSuffix):
                suffix = suffix[:-reduceLen] # e.g. suffix = 'bed.gz' -> 'bed'
            else:
                continue

            title = getTitleWithSuffixReplaced(title, '')
            break

    return title, suffix


def getTitleWithCompressionSuffixesRemoved(gSuiteTrack):
    return getTitleAndSuffixWithCompressionSuffixesRemoved(gSuiteTrack)[0]


def getSuffixWithCompressionSuffixesRemoved(gSuiteTrack):
    return getTitleAndSuffixWithCompressionSuffixesRemoved(gSuiteTrack)[1]


