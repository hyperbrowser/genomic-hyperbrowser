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
import shelve
import urllib
from collections import OrderedDict

from proto.CommonConstants import THOUSANDS_SEPARATOR
from proto.config.Config import GALAXY_BASE_DIR, OUTPUT_PRECISION
from proto.config.Security import galaxySecureEncodeId, galaxySecureDecodeId

"""
Note on datasetInfo and datasetId (used in several functions):

DatasetInfo is an especially coded list of strings, used mainly to process
files from galaxy history, but can also be used otherwise. Structure is:
['galaxy', fileEnding, datasetFn, name]. The first element is used for
assertion. The second element contains the file format (as galaxy force
the ending '.dat'). datasetFn is the dataset file name, typically ending
with 'XXX/dataset_YYYY.dat', where XXX and YYYY are numbers which may be
extracted and used as a datasetId in the form [XXX, YYYY]. The last element
is the name of the history element, mostly used for presentation purposes.
"""


def getToolPrototype(toolId):
    tool_shelve = None
    try:
        tool_shelve = shelve.open(
            GALAXY_BASE_DIR + '/database/proto-tool-cache.shelve', 'r')
        module_name, class_name = tool_shelve[str(toolId)]
        module = __import__(module_name, fromlist=[class_name])
        # print module, class_name, toolId
        prototype = getattr(module, class_name)(toolId)
        # print "Loaded proto tool:", class_name
    #except KeyError:
    #    prototype = None
    finally:
        if tool_shelve:
            tool_shelve.close()
    return prototype


def ensurePathExists(fn):
    "Assumes that fn consists of a basepath (folder) and a filename, and ensures that the folder exists."
    path = os.path.split(fn)[0]

    if not os.path.exists(path):
        #oldMask = os.umask(0002)
        os.makedirs(path)
        #os.umask(oldMask)


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
    num = int(num)
    id2 = str(num)
    id1 =  '%03d' % (num / 1000)
    return [id1, id2]


def getGalaxyFnFromDatasetId(num, galaxyFilePath=None):
    if not galaxyFilePath:
        from proto.config.Config import GALAXY_FILE_PATH
        galaxyFilePath = GALAXY_FILE_PATH

    id1, id2 = createFullGalaxyIdFromNumber(num)
    return os.path.join(galaxyFilePath, id1, 'dataset_%s.dat' % id2)


def getEncodedDatasetIdFromPlainGalaxyId(plainId):
    return galaxySecureEncodeId(plainId)


def getEncodedDatasetIdFromGalaxyFn(galaxyFn):
    plainId = extractIdFromGalaxyFn(galaxyFn)[1]
    return getEncodedDatasetIdFromPlainGalaxyId(plainId)


def getGalaxyFnFromEncodedDatasetId(encodedId, galaxyFilePath=None):
    plainId = galaxySecureDecodeId(encodedId)
    return getGalaxyFnFromDatasetId(plainId, galaxyFilePath=galaxyFilePath)


def getGalaxyFnFromAnyDatasetId(id, galaxyFilePath=None):
    try:
        return getGalaxyFnFromEncodedDatasetId(id,
                                               galaxyFilePath=galaxyFilePath)
    except:
        return getGalaxyFnFromDatasetId(id, galaxyFilePath=galaxyFilePath)


def getGalaxyFilesDir(galaxyFn):
    return galaxyFn[:-4] + '_files'


def getGalaxyFilesFilename(galaxyFn, id):
    """
    id is the relative file hierarchy, encoded as a list of strings
    """
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

    if fileSuffixFilterList and not suffix.lower() in fileSuffixFilterList:
        raise Exception('File type "' + suffix + '" is not supported.')

    return suffix


def extractNameFromDatasetInfo(datasetInfo):
    if isinstance(datasetInfo, basestring):
        datasetInfo = datasetInfo.split(':')

    from urllib import unquote
    return unquote(datasetInfo[-1])


def createToolURL(toolId, **kwArgs):
    from proto.tools.GeneralGuiTool import GeneralGuiTool
    return GeneralGuiTool.createGenericGuiToolURL(toolId, tool_choices=kwArgs)


def createGalaxyToolURL(toolId, **kwArgs):
    from proto.config.Config import URL_PREFIX
    return URL_PREFIX + '/tool_runner?tool_id=' + toolId + \
            ''.join(['&' + urllib.quote(key) + '=' + urllib.quote(value) for key,value in kwArgs.iteritems()])


def getLoadToGalaxyHistoryURL(fn, genome='hg18', galaxyDataType='bed', urlPrefix=None):
    if urlPrefix is None:
        from proto.config.Config import URL_PREFIX
        urlPrefix = URL_PREFIX

    import base64

    assert galaxyDataType is not None
    return urlPrefix + '/tool_runner?tool_id=file_import&dbkey=%s&runtool_btn=yes&input=' % (genome,) \
            + base64.urlsafe_b64encode(fn) + ('&format=' + galaxyDataType if galaxyDataType is not None else '')


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


def sortDictOfLists(dictOfLists, sortColumnIndex, descending=True):
    return OrderedDict(sorted(
        list(dictOfLists.iteritems()), key=lambda t: (t[1][sortColumnIndex]), reverse=descending))


def smartSortDictOfLists(dictOfLists, sortColumnIndex, descending=True):
    """Sort numbers first than strings, take into account formatted floats"""
    # convert = lambda text: int(text) if text.isdigit() else text
    # alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return OrderedDict(sorted(
        list(dictOfLists.iteritems()), key=lambda t: forceNumericSortingKey(t[1][sortColumnIndex]), reverse=descending))


def _strIsFloat(s):
    try:
        float(s)
        return True
    except:
        return False


def forceNumericSortingKey(key):
    sortKey1 = 0
    sortKey2 = key
    if _strIsFloat(str(key).replace(THOUSANDS_SEPARATOR, '')):
        sortKey1 = 1
        sortKey2 = float(str(key).replace(THOUSANDS_SEPARATOR, ''))
    return [sortKey1, sortKey2]
