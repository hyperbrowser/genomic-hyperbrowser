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
import re
import traceback
import numpy
import functools
import operator
from collections import Iterable

from config.Config import PROCESSED_DATA_PATH, DEFAULT_GENOME, \
    ORIG_DATA_PATH, OUTPUT_PRECISION, MEMOIZED_DATA_PATH, NONSTANDARD_DATA_PATH, \
    PARSING_ERROR_DATA_PATH, IS_EXPERIMENTAL_INSTALLATION
from gold.util.CommonConstants import THOUSANDS_SEPARATOR
from gold.util.CustomExceptions import InvalidFormatError
from gold.util.CommonConstants import BINARY_MISSING_VAL
from quick.application.SignatureDevianceLogging import takes,returns
from third_party.decorator import decorator

def createDirPath(trackName, genome, chr=None, allowOverlaps=False, basePath=PROCESSED_DATA_PATH):
    """
    >>> createDirPath(['trackname'],'genome','chr1')
    '/100000/noOverlaps/genome/trackname/chr1'
    """
    from gold.util.CompBinManager import CompBinManager
    if len(trackName)>0 and trackName[0] == 'redirect':
        genome = trackName[1]
        chr = trackName[2]
        #trackName[3] is description
        trackName = trackName[4:]

    #print [basePath, str(CompBinManager.getIndexBinSize()), ('withOverlaps' if allowOverlaps else 'noOverlaps'), genome] +\
    #    list(trackName) + ([chr] if chr is not None else [])

    return os.sep.join( [basePath, str(CompBinManager.getIndexBinSize()), ('withOverlaps' if allowOverlaps else 'noOverlaps'), genome] +\
        list(trackName) + ([chr] if chr is not None else []) )

#def createMemoPath(trackName, genome, chr, statName):
#    return os.sep.join( [MEMOIZED_DATA_PATH, statName, str(COMP_BIN_SIZE), genome]+list(trackName)+[chr] )
def createMemoPath(region, statId, configHash, track1Hash, track2Hash):
    chr = region.chr
    genome = region.genome
    return os.sep.join( [MEMOIZED_DATA_PATH, str(len(region)), statId, genome, str(track1Hash)] + \
                        ([str(track2Hash)] if track2Hash is not None else []) + \
                        [str(configHash), chr] ).replace('-','_') #replace('-','_') because hashes can be minus, and minus sign makes problems with file handling

@takes(str,(list,tuple),(str,type(None)))
def createOrigPath(genome, trackName, fn=None):
    #print 'genome:',genome
    #print 'trackName:',trackName
    return os.sep.join([ORIG_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))

@takes(str,(list,tuple),(str,type(None)))
def createCollectedPath(genome, trackName, fn=None):
    return os.sep.join([NONSTANDARD_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))

@takes(str,(list,tuple),(str,type(None)))
def createParsingErrorPath(genome, trackName, fn=None):
    return os.sep.join([PARSING_ERROR_DATA_PATH, genome] + trackName + ([fn] if fn is not None else []))

@takes(str)
def getFileSuffix(fn):
    from gold.application.DataTypes import getSupportedFileSuffixes
    for suffix in getSupportedFileSuffixes():
        if '.' in suffix and fn.endswith('.' + suffix):
            return suffix
    return os.path.splitext(fn)[1].replace('.','')

@takes(str)
def stripFileSuffix(fn):
    suffix = getFileSuffix(fn)
    return fn[:-len(suffix)-1]

def getOrigFns(genome, trackName, suffix, fileTree='standardized'):
    assert fileTree in ['standardized', 'collected', 'parsing error']
    from gold.application.LogSetup import logMessage, logging

    if fileTree == 'standardized':
        path = createOrigPath(genome, trackName)
    elif fileTree == 'collected':
        path = createCollectedPath(genome, trackName)
    else:
        path = createParsingErrorPath(genome, trackName)

    if not os.path.exists(path):
        if IS_EXPERIMENTAL_INSTALLATION:
            logMessage('getOrigFn - Path does not exist: ' + path, logging.WARNING)
        return []

    return [path + os.sep + x for x in os.listdir(path) if os.path.isfile(path + os.sep + x) \
            and x.endswith(suffix) and not x[0] in ['.','_','#'] and not x[-1] in ['~','#']]

def getOrigFn(genome, trackName, suffix, fileTree='standardized'):
    fns = getOrigFns(genome, trackName, suffix, fileTree=fileTree)
    if len(fns) != 1:
        if IS_EXPERIMENTAL_INSTALLATION:
            from gold.application.LogSetup import logMessage, logging
            logMessage('getOrigFn - Cannot decide among zero or several filenames: %s' % fns, logging.WARNING)
        return None

    return fns[0]

def parseDirPath(path):
    'Returns [genome, trackName, chr] from directory path'
    path = path[len(PROCESSED_DATA_PATH + os.sep):]# + str(CompBinManager.getIndexBinSize())):]
    while path[0] == os.sep:
        path = path[1:]
    path.replace(os.sep*2, os.sep)
    el = path.split(os.sep)
    return el[2], tuple(el[3:-1]), el[-1]

def extractTrackNameFromOrigPath(path):
    excludeEl = None if os.path.isdir(path) else -1
    path = path[len(ORIG_DATA_PATH):]
    path = path.replace('//','/')
    if path[0]=='/':
        path = path[1:]
    if path[-1]=='/':
        path = path[:-1]
    return path.split(os.sep)[1:excludeEl]

def getStringFromStrand(strand):
    if strand in (None, BINARY_MISSING_VAL):
        return '.'
    return '+' if strand else '-'

def parseTrackNameSpec(trackNameSpec):
    return trackNameSpec.split(':')

def prettyPrintTrackName(trackName, shortVersion=False):
    from urllib import unquote
    if len(trackName) == 0:
        return ''
    elif len(trackName) == 1:
        return trackName[0]
    elif trackName[0] in ['galaxy','redirect','virtual']:
        return "'" + re.sub('([0-9]+) - (.+)', '\g<2> (\g<1>)', unquote(trackName[3])) + "'"
    elif trackName[0] in ['external']:
        return "'" + re.sub('[0-9]+ - ', '', unquote(trackName[-1])) + "'"
    else:
        if trackName[-1]=='':
            return "'" + trackName[-2] + "'"
        return "'" + trackName[-1] + (' (' + trackName[-2] + ')' if not shortVersion else '') + "'"
        #return "'" + trackName[1] + (' (' + '-'.join(trackName[2:]) + ')' if len(trackName) > 2 else '') + "'"
        #return trackName[1] + (' (' + '-'.join(trackName[2:]) + ')' if len(trackName) > 2 else '')

def insertTrackNames(text, trackName1, trackName2 = None, shortVersion=False):
    PREFIX = '(the points of |points of |point of |the segments of |segments of |segment of |the function of |function of )?'
    POSTFIX = '([- ]?segments?|[- ]?points?|[- ]?function)?'
    newText = re.sub(PREFIX + '[tT](rack)? ?1' +  POSTFIX, prettyPrintTrackName(trackName1, shortVersion), text)
    if trackName2 != None:
        newText = re.sub(PREFIX + '[tT](rack)? ?2' + POSTFIX, prettyPrintTrackName(trackName2, shortVersion), newText)
    return newText

def resultsWithoutNone(li, ignoreNans=False):
    for el in li:
        if el is not None and not (ignoreNans and numpy.isnan(el)):
            yield el

def smartSum(li, ignoreNans=False):
    try:
        resultsWithoutNone(li, ignoreNans).next()
    except StopIteration:
        return None

    return sum(resultsWithoutNone(li, ignoreNans))

def smartMean(li, ignoreNans=False, excludeNonesFromMean=False, returnZeroForEmpty=False):

    smrtSum = smartSum(li, ignoreNans=ignoreNans)
    if smrtSum is not None:
        if excludeNonesFromMean:
            return float(smrtSum)/len(resultsWithoutNone(li, ignoreNans=ignoreNans))
        else:
            return float(smrtSum)/len(li)
    if returnZeroForEmpty:
        return 0.0

def smartMeanNoNones(li):
    return smartMean(li, excludeNonesFromMean=True)

def smartMeanWithNones(li):
    return smartMean(li)

def smartMin(li, ignoreNans=False):
    try:
        resultsWithoutNone(li, ignoreNans).next()
    except StopIteration:
        return None

    return min(resultsWithoutNone(li, ignoreNans))

def isIter(obj):
    from numpy import memmap
    if isinstance(obj, memmap):
        return False
    return hasattr(obj, '__iter__')

def isNumber(s):
    try:
        float(s)
        return True
    except:
        return False

def getClassName(obj):
    return obj.__class__.__name__

def strWithStdFormatting(val, separateThousands=True, floatFormatFlag='g'):
    try:
        assert val != int(val)
        integral, fractional = (('%#.' + str(OUTPUT_PRECISION) + floatFormatFlag) % val).split('.')
    except:
        integral, fractional = str(val), None

    if not separateThousands:
        return integral + ('.' + fractional if fractional is not None else '')
    else:
        try:
            return ('-' if integral[0] == '-' else '') + \
                '{:,}'.format(abs(int(integral))).replace(',', THOUSANDS_SEPARATOR) + \
                ('.' + fractional if fractional is not None else '')
        except:
            return integral

def strWithNatLangFormatting(val, separateThousands=True):
    return strWithStdFormatting(val, separateThousands=separateThousands, floatFormatFlag='f')


def smartStrLower(obj):
    return str.lower(str(obj))

def splitOnWhitespaceWhileKeepingQuotes(msg):
    return re.split('\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', msg.strip())

def parseShortenedSizeSpec(spec):
    spec = spec.strip()
    if spec[-1].lower() == 'k':
        size = int(spec[0:-1]) * 1000
    elif spec[-1].lower() == 'm':
        size = int(spec[0:-1]) * 1000000
    else:
        size = int(spec)
    return size

def generateStandardizedBpSizeText(size):
    if size == 0:
        return '0 bp'
    elif size % 10**9 == 0:
        return str(size/10**9) + ' Gb'
    elif size % 10**6 == 0:
        return str(size/10**6) + ' Mb'
    elif size % 10**3 == 0:
        return str(size/10**3) + ' kb'
    else:
        return str(size) + ' bp'

def quenchException(fromException, replaceVal):
    "if a certain exception occurs within method, catch this exception and instead return a given value"
    def _quenchException(func, *args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except fromException,e:
            return replaceVal
    return decorator(_quenchException)

def reverseDict(mapping):
    vals = mapping.values()
    assert len(set(vals)) == len(vals) #Ensure all values are unique
    return dict((v,k) for k, v in mapping.iteritems())

def mean(l):
    return float(sum(l)) / len(l)

def product(l):
    """Product of a sequence."""
    return functools.reduce(operator.mul, l, 1)

def flatten(l):
    for el in l:
        if isinstance(el, Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el
 
def findKeysWithValDefinedByNumpyFunc(d, func=max):
    import numpy as np
    vals = np.array(d.values())
    keys = np.array(d.keys())
    return list(keys[vals == func(vals)])

def findKeysWithMaxVal(d):
    return findKeysWithValDefinedByNumpyFunc(d, lambda x: x.max())

def findKeysWithMinVal(d):
    return findKeysWithValDefinedByNumpyFunc(d, lambda x: x.min())

def pairwise(iterable):
    from itertools import tee, izip

    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def multiReplace(str, fromList, toList):
    assert len(fromList) == len(toList)
    for i, fromStr in enumerate(fromList):
        str = str.replace(fromStr, toList[i])
    return str

def replaceIllegalElementsInTrackNames(string):
    return multiReplace(string, [':','=','[',']','/','-->'],['.','-','(',')','_', '-'])

def arrayEquals(x, y):
    try:
        return x == y
    except:
        return (x == y).all()

def repackageException(fromException, toException):
    def _repackageException(func, *args, **kwArgs):
        try:
            return func(*args, **kwArgs)
        except fromException,e:
            raise toException('Repackaged exception.., original was: ' + getClassName(e) + ' - '+str(e) + ' - ' + traceback.format_exc())
    return decorator(_repackageException)

#Typical use, for instance
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)

#Repackaging can also be done manually for chunks of code by:
    #import traceback
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #from gold.util.CommonFunctions import getClassName
    #try:
    #    pass #code chunk here..
    #except Exception,e:
    #    raise ShouldNotOccurError('Repackaged exception.., original was: ' + getClassName(e) + ' - '+str(e) + ' - ' + traceback.format_exc())
