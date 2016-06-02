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
import sys
import functools
import re
import urllib
import contextlib


def ensurePathExists(fn):
    "Assumes that fn consists of a basepath (folder) and a filename, and ensures that the folder exists."
    path = os.path.split(fn)[0]

    if not os.path.exists(path):
        #oldMask = os.umask(0002)
        os.makedirs(path)
        #os.umask(oldMask)


def reloadModules():
    for module in [val for key,val in sys.modules.iteritems() \
                   if key.startswith('gold') or key.startswith('quick') or key.startswith('test')]:
        try:
            reload(module)
        except:
            print module


def wrapClass(origClass, keywords={}):
    #for key in keywords.keys():
    #    if re.match('^[0-9]+$',keywords[key]) is not None:
    #        keywords[key] = int(keywords[key])
    #    elif re.match('^[0-9]?[.][0-9]?$',keywords[key]) is not None and keywords[key] != '.':
    #        keywords[key] = float(keywords[key])

    args = []
    wrapped = functools.partial(origClass, *args, **keywords)
    functools.update_wrapper(wrapped, origClass)
    return wrapped


def extractIdFromGalaxyFn(fn):
    '''
    Extracts the Galaxy history ID from a history file path, e.g.:

    '/path/to/001/dataset_00123.dat' -> ['001', '00123']

    For files related to a Galaxy history (e.g. dataset_00123_files):

    '/path/to/001/dataset_00123_files/myfile/myfile.bed' -> ['001', '00123', 'myfile']

    Also, if the input is a run-specific file, the history and batch ID, is also extracted, e.g.:

    '/path/to/dev2/001/00123/0/somefile.bed' -> ['001', '00123', '0']
    '''
    #'''For temporary Galaxy files:
    #
    #/path/to/tmp/primary_49165_wgEncodeUmassDekker5CEnmPrimer.doc.tgz_visible_.doc.tgz -> '49165'
    #'''

    pathParts = fn.split(os.sep)
    assert len(pathParts) >= 2, pathParts

    if fn.endswith('.dat'):
        id1 = pathParts[-2]
        id2 = re.sub('[^0-9]', '', pathParts[-1])
        id = [id1, id2]
    elif any(part.startswith('dataset_') and part.endswith('_files') for part in pathParts):
        extraIds = []
        for i in range(len(pathParts)-1, 0, -1):
            part = pathParts[i-1]
            if part.startswith('dataset_') and part.endswith('_files'):
                id2 = re.sub('[^0-9]', '', part)
                id1 = pathParts[i-2]
                break
            else:
                extraIds = [part] + extraIds
        id = [id1, id2] + extraIds
    #elif os.path.basename(fn).startswith('primary'):
    #    basenameParts = os.path.basename(fn).split('_')
    #    assert len(basenameParts) >= 2
    #    id = basenameParts[1] # id does not make sense. Removed for now, revise if needed.
    else: #For run-specific files
        for i in range(len(pathParts)-2, 0, -1):
            if not pathParts[i].isdigit():
                id = pathParts[i+1:-1]
                assert len(id) >= 2, 'Could not extract id from galaxy filename: ' + fn
                break

    return id


def createFullGalaxyIdFromNumber(num):
    id2 = str(num)
    id1 =  ('%.3f' % (int(id2)/1000 *1.0 / 1000))[2:]
    return [id1, id2]


def getGalaxyFnFromDatasetId(num):
    from config.Config import GALAXY_FILE_PATH
    id1, id2 = createFullGalaxyIdFromNumber(num)
    return os.path.join(GALAXY_FILE_PATH, id1, 'dataset_%s.dat' % id2)


def galaxySecureEncodeId(plainId):
    from config.Config import GALAXY_SECURITY_HELPER_OBJ
    return GALAXY_SECURITY_HELPER_OBJ.encode_id(plainId)


def galaxySecureDecodeId(encodedId):
    from config.Config import GALAXY_SECURITY_HELPER_OBJ
    return GALAXY_SECURITY_HELPER_OBJ.decode_id(encodedId)


def getEncodedDatasetIdFromPlainGalaxyId(plainId):
    return galaxySecureEncodeId(plainId)


def getEncodedDatasetIdFromGalaxyFn(cls, galaxyFn):
    plainId = extractIdFromGalaxyFn(galaxyFn)[1]
    return getEncodedDatasetIdFromPlainGalaxyId(plainId)


def getGalaxyFnFromEncodedDatasetId(encodedId):
    plainId = galaxySecureDecodeId(encodedId)
    return getGalaxyFnFromDatasetId(plainId)


def getGalaxyFilesDir(galaxyFn):
    return galaxyFn[:-4] + '_files'

    '''
    id is the relative file hierarchy, encoded as a list of strings
    '''


def getGalaxyFilesFilename(galaxyFn, id):
    return os.path.sep.join([getGalaxyFilesDir(galaxyFn)] + id)


def getGalaxyFilesFnFromEncodedDatasetId(encodedId):
    galaxyFn = getGalaxyFnFromEncodedDatasetId(encodedId)
    return getGalaxyFilesDir(galaxyFn)


def createGalaxyFilesFn(galaxyFn, filename):
    return os.path.sep.join([getGalaxyFilesDir(galaxyFn), filename])


def createGalaxyFilesFn(galaxyFn, filename):
    return os.path.sep.join(
        [getGalaxyFilesDir(galaxyFn), filename])


def extractFnFromDatasetInfo(datasetInfo):
    if isinstance(datasetInfo, basestring):
        datasetInfo = datasetInfo.split(':')
    return getGalaxyFnFromEncodedDatasetId(datasetInfo[2])


def extractFileSuffixFromDatasetInfo(datasetInfo, fileSuffixFilterList=None):
    if isinstance(datasetInfo, basestring):
        datasetInfo = datasetInfo.split(':')

    suffix = datasetInfo[1]

    if fileSuffixFilterList and not suffix.lower() in fileSuffixFilterList():
        raise Exception('File type "' + suffix + '" is not supported.')

    return suffix


def extractNameFromDatasetInfo(datasetInfo):
    if isinstance(datasetInfo, basestring):
        datasetInfo = datasetInfo.split(':')

    from urllib import unquote
    return unquote(datasetInfo[-1])


# def getUniqueRunSpecificId(id=[]):
#    return ['run_specific'] + id
#
# def getUniqueWebPath(id=[]):
#    from config.Config import STATIC_PATH
#    return os.sep.join([STATIC_PATH] + getUniqueRunSpecificId(id))


def getLoadToGalaxyHistoryURL(fn, genome='hg18', galaxyDataType='bed', urlPrefix=None):
    if urlPrefix is None:
        from config.Config import URL_PREFIX
        urlPrefix = URL_PREFIX

    import base64

    assert galaxyDataType in ['bed', 'bedgraph', 'gtrack', 'gsuite']

    return urlPrefix + '/tool_runner?tool_id=file_import_%s&dbkey=%s&runtool_btn=yes&input=' % (galaxyDataType, genome) \
            + base64.urlsafe_b64encode(fn) + ('&datatype='+galaxyDataType if galaxyDataType is not None else '')

# def getRelativeUrlFromWebPath(webPath):
#    from config.Config import GALAXY_BASE_DIR, URL_PREFIX
#    if webPath.startswith(GALAXY_BASE_DIR):
#        return URL_PREFIX + webPath[len(GALAXY_BASE_DIR):]


def isFlatList(list):
    for l in list:
        if type(l) == type([]):
            return False
    return True


def flattenList(list):
    '''
    recursively flattens a nested list (does not handle dicts and sets..) e.g.
    [1, 2, 3, 4, 5] == flattenList([[], [1,2],[3,4,5]])
    '''
    if isFlatList(list):
        return list
    else:
        return flattenList( reduce(lambda x,y: x+y, list ) )


def listStartsWith(a, b):
    return len(a) > len(b) and a[:len(b)] == b


def isNan(a):
    import numpy

    try:
        return numpy.isnan(a)
    except (TypeError, NotImplementedError):
        return False


def isListType(x):
    import numpy
    return type(x) == list or type(x) == tuple or isinstance(x, numpy.ndarray) or isinstance(x, dict)


def ifDictConvertToList(d):
    return [(x, d[x]) for x in sorted(d.keys())] if isinstance(d, dict) else d


def smartRecursiveAssertList(x, y, assertEqualFunc, assertAlmostEqualFunc):
    import numpy

    if isListType(x):
        if isinstance(x, numpy.ndarray):
            try:
                if not assertEqualFunc(x.shape, y.shape):
                    return False
            except Exception, e:
                raise AssertionError(str(e) + ' on shape of lists: ' + str(x) + ' and ' + str(y))

            try:
                if not assertEqualFunc(x.dtype, y.dtype):
                    return False
            except Exception, e:
                raise AssertionError(str(e) + ' on datatypes of lists: ' + str(x) + ' and ' + str(y))
        else:
            try:
                if not assertEqualFunc(len(x), len(y)):
                    return False
            except Exception, e:
                raise AssertionError(str(e) + ' on length of lists: ' + str(x) + ' and ' + str(y))

        for el1,el2 in zip(*[ifDictConvertToList(x) for x in [x, y]]):
            if not smartRecursiveAssertList(el1, el2, assertEqualFunc, assertAlmostEqualFunc):
                return False
        return True

    else:
        try:
            return assertAlmostEqualFunc(x, y)
        except TypeError:
            return assertEqualFunc(x, y)


def bothIsNan(a, b):
    import numpy

    try:
        if not any(isListType(x) for x in [a,b]):
            return numpy.isnan(a) and numpy.isnan(b)
    except (TypeError, NotImplementedError):
        pass
    return False


def smartEquals(a, b):
    if bothIsNan(a, b):
        return True
    return a == b


def smartRecursiveEquals(a, b):
    return smartRecursiveAssertList(a, b, smartEquals, smartEquals)


def reorderTrackNameListFromTopDownToBottomUp(trackNameSource):
    prevTns = []
    source = trackNameSource.__iter__()
    trackName = source.next()

    try:
        while True:
            if len(prevTns) == 0 or listStartsWith(trackName, prevTns[0]):
                prevTns.insert(0, trackName)
                trackName = source.next()
                continue
            yield prevTns.pop(0)

    except StopIteration:
        while len(prevTns) > 0:
            yield prevTns.pop(0)


R_ALREADY_SILENCED = False
R_ALREADY_SILENCED_OUTPUT = False


def silenceRWarnings():
    global R_ALREADY_SILENCED
    if not R_ALREADY_SILENCED:
        from proto.RSetup import r
        r('sink(file("/dev/null", open="wt"), type="message")')
        R_ALREADY_SILENCED = True


def silenceROutput():
    global R_ALREADY_SILENCED_OUTPUT
    if not R_ALREADY_SILENCED_OUTPUT:
        from proto.RSetup import r
        r('sink(file("/dev/null", open="wt"), type="output")')
        R_ALREADY_SILENCED_OUTPUT = True


def createHyperBrowserURL(genome, trackName1, trackName2=None, track1file=None, track2file=None, \
                          demoID=None, analcat=None, analysis=None, \
                          configDict=None, trackIntensity=None, method=None, region=None, \
                          binsize=None, chrs=None, chrArms=None, chrBands=None, genes=None):
    urlParams = []
    urlParams.append( ('dbkey', genome) )
    urlParams.append( ('track1', ':'.join(trackName1)) )
    if trackName2:
        urlParams.append( ('track2', ':'.join(trackName2)) )
    if track1file:
        urlParams.append( ('track1file', track1file) )
    if track2file:
        urlParams.append( ('track2file', track2file) )
    if demoID:
        urlParams.append( ('demoID', demoID) )
    if analcat:
        urlParams.append( ('analcat', analcat) )
    if analysis:
        urlParams.append( ('analysis', analysis) )
    if configDict:
        for key, value in configDict.iteritems():
            urlParams.append( ('config_%s' % key, value) )
    if trackIntensity:
        urlParams.append( ('trackIntensity', trackIntensity) )
    if method:
        urlParams.append( ('method', method) )
    if region:
        urlParams.append( ('region', region) )
    if binsize:
        urlParams.append( ('binsize', binsize) )
    if chrs:
        urlParams.append( ('__chrs__', chrs) )
    if chrArms:
        urlParams.append( ('__chrArms__', chrArms) )
    if chrBands:
        urlParams.append( ('__chrBands__', chrBands) )
    if genes:
        urlParams.append( ('genes', genes) )
    #genes not __genes__?
    #encode?

    from config.Config import URL_PREFIX
    return URL_PREFIX + '/hyper?' + '&'.join([urllib.quote(key) + '=' + \
                                              urllib.quote(value) for key,value in urlParams])


def createToolURL(toolId, **kwArgs):
    from config.Config import URL_PREFIX
    return URL_PREFIX + '/hyper?mako=generictool&tool_id=' + toolId + \
            ''.join(['&' + urllib.quote(key) + '=' + urllib.quote(value) for key,value in kwArgs.iteritems()])


def createGalaxyToolURL(toolId, **kwArgs):
    from config.Config import URL_PREFIX
    return URL_PREFIX + '/tool_runner?tool_id=' + toolId + \
            ''.join(['&' + urllib.quote(key) + '=' + urllib.quote(value) for key,value in kwArgs.iteritems()])



def numAsPaddedBinary(comb, length):
    return '0'*(length-len(bin(comb)[2:]))+bin(comb)[2:]


@contextlib.contextmanager
def changedWorkingDir(new_dir):
    orig_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(orig_dir)


def convertTNstrToTNListFormat(tnStr, doUnquoting=False):
    tnList = re.split(':|\^|\|', tnStr)
    if doUnquoting:
        tnList = [urllib.unquote(x) for x in tnList]
    return tnList


#used by echo
def format_arg_value(arg_val):
    """ Return a string representing a (name, value) pair.

    >>> format_arg_value(('x', (1, 2, 3)))
    'x=(1, 2, 3)'
    """
    arg, val = arg_val
    return "%s=%r" % (arg, val)


def echo(fn, write=sys.stdout.write):
    """ Echo calls to a function.

    Returns a decorated version of the input function which "echoes" calls
    made to it by writing out the function's name and the arguments it was
    called with.
    """
    import functools
    # Unpack function's arg count, arg names, arg defaults
    code = fn.func_code
    argcount = code.co_argcount
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.func_defaults or list()
    argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

    @functools.wraps(fn)
    def wrapped(*v, **k):
        # Collect function arguments by chaining together positional,
        # defaulted, extra positional and keyword arguments.
        positional = map(format_arg_value, zip(argnames, v))
        defaulted = [format_arg_value((a, argdefs[a]))
                     for a in argnames[len(v):] if a not in k]
        nameless = map(repr, v[argcount:])
        keyword = map(format_arg_value, k.items())
        args = positional + defaulted + nameless + keyword
        write("%s(%s)\n" % (name(fn), ", ".join(args)))
        return fn(*v, **k)
    return wrapped


def getGeSource(track, genome=None):

    from quick.application.ExternalTrackManager import ExternalTrackManager
    from gold.origdata.BedGenomeElementSource import BedGenomeElementSource, BedCategoryGenomeElementSource
    from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
    from gold.origdata.TrackGenomeElementSource import FullTrackGenomeElementSource

    if type(track) == str:
        track = track.split(':')

    try:
        fileType = ExternalTrackManager.extractFileSuffixFromGalaxyTN(track)
        fn = ExternalTrackManager.extractFnFromGalaxyTN(track)
        if fileType == 'category.bed':
            return BedCategoryGenomeElementSource(fn)
        elif fileType == 'gtrack':
            return GtrackGenomeElementSource(fn)
        else:
            return BedGenomeElementSource(fn)
    except:
        return FullTrackGenomeElementSource(genome, track, allowOverlaps=False)


# generate powerset for set
# powerset([a,b,c]) = [(), (a), (b), (c), (a,b), (a,c), (a,b), (a,b,c))
def powerset(iterable):
    from itertools import chain, combinations
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


# Generate all supersets of a set represented by a binary string
# e.g. allSupersets('010') = ['110','011','111']
def allSupersets(binaryString):
    length = len(binaryString)
    binaryList = list(binaryString)
    zeroIndex = [i for i,val in enumerate(binaryList) if val == '0']
    for comb in powerset(zeroIndex):
        if comb:
            yield ''.join([binaryList[i] if i not in comb else '1' for i in range(length)])


def getUniqueFileName(origFn):
    import os

    i = 0
    newOrigFn = origFn

    while os.path.exists(newOrigFn):
        newOrigFn = origFn + '.%s' % i
        i += 1

    return newOrigFn
