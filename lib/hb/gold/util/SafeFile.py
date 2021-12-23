import os
import os.path
import cPickle
import fcntl
import json
import time

from abc import ABCMeta, abstractmethod
from collections import namedtuple
from datetime import datetime
from fcntl import LOCK_SH, LOCK_EX, LOCK_UN, LOCK_NB
from gold.util.CustomExceptions import SyncConflictError, NotDictLikeError, NotSyncedError
from proto.CommonFunctions import ensurePathExists


# Convenience classes

Conflict = namedtuple('Conflict', 'object, key')
Conflict.__new__.__defaults__ = (False, None)


class FileLock(object):
    def __init__(self, managedFilePath, mode):
        self._lockFilePath = managedFilePath + '.lck'
        assert mode in ['r', 'w']
        self._mode = mode
        self._lckFile = None

    def __enter__(self):
        if self._mode == 'r':
            lockflags = LOCK_SH | LOCK_NB
        else:
            lockflags = LOCK_EX

        ensurePathExists(self._lockFilePath)
        # os.open with os.O_SHLOCK instead?
        self._lckFile = open(self._lockFilePath, self._mode)
        fcntl.flock(self._lckFile.fileno(), lockflags)

    def __exit__(self, exc_type, exc_value, tb):
        fcntl.flock(self._lckFile.fileno(), LOCK_UN)
        self._lckFile.close()
        del self._lckFile


# SafeFile

class SafeFile(object):
    __metaclass__ = ABCMeta

    DICTLIKE_REQ_ATTRS = ('__getitem__', '__setitem__', '__delitem__', '__contains__', 'get', 'keys', 'update')

    def __init__(self, fn):
        self._fn = fn
        self._lckfilename = os.path.dirname(fn) + os.sep + '.' + os.path.basename(fn) + '.lck'

        self._empty = True
        self._closed = False
        self._obj = None
        self._prevFileModTime = None
        self._prevFileObj = None

        self._addedKeys = set()
        self._deletedKeys = set()
        self._updatedKeys = set()
        self._replacedObj = False
        self._postponeWrite = False

    @property
    def object(self):
        """
        :return: locally stored version of object. If no local object is held, reads the currently pickled  from disk.
        """
        self._checkIfClosed()
        if self._empty:
            self.sync()
        return self._obj

    @object.setter
    def object(self, obj):
        """
        Stores object locally, replacing the current locally stored object. Does not sync with disk, but marks the
        object as dirty (changed) for next sync().
        :param obj: serializable object. Correct conflict management depends the existence of an obj.__eg__() method
        :return: None
        """
        self._checkIfClosed()

        self._obj = obj
        self._empty = False
        self._cleanEditHistory()
        self._replacedObj = True

    def _cleanEditHistory(self, postponeWrite=False):
        self._addedKeys = set()
        self._deletedKeys = set()
        self._updatedKeys = set()
        self._replacedObj = False
        self._postponeWrite = postponeWrite

    def __getitem__(self, key):
        self._checkIfClosed()
        self._assertObjectIsDictLikeAndInitiallySynced()
        return self._obj[key]

    def __setitem__(self, key, value):
        self._checkIfClosed()
        self._assertObjectIsDictLikeAndInitiallySynced()
        if key not in self._obj:
            self._addedKeys.add(key)
        elif not self._obj[key] == value:
            self._updatedKeys.add(key)
        self._obj[key] = value

    def __delitem__(self, key):
        self._checkIfClosed()
        self._assertObjectIsDictLikeAndInitiallySynced()
        del self._obj[key]
        self._deletedKeys.add(key)

    def __contains__(self, key):
        self._checkIfClosed()
        self._assertObjectIsDictLikeAndInitiallySynced()
        return key in self._obj

    def get(self, key):
        self._checkIfClosed()
        self._assertObjectIsDictLikeAndInitiallySynced()
        return self._obj.get(key)

    def _dirty(self):
        return self._keysWithLocalEdits() != set() or self._replacedObj

    def _keysWithLocalEdits(self):
        return self._addedKeys | self._deletedKeys | self._updatedKeys

    @classmethod
    def _typeIsSameAndDictLike(cls, object1, object2, object3):
        return type(object1) == type(object2) == type(object3) and cls._isDictLike(object1)

    def _objectIsInitiallySynced(self):
        return not self._replacedObj

    def _assertObjectIsDictLikeAndInitiallySynced(self):
        if not self._isDictLike(self._obj):
            raise NotDictLikeError("SafePickleFile object is not dict-like: {}".format(self._obj))
        if not self._objectIsInitiallySynced():
            raise NotSyncedError("SafePickle object is dict-like, but is not synced yet. Item access is restricted "
                                 "until after first sync.")

    @classmethod
    def _isDictLike(cls, obj):
        return all(hasattr(obj, attr) for attr in cls.DICTLIKE_REQ_ATTRS)

    def sync(self, conflictResolution='raise', readOnly=False):
        """
        Two-way sync with the pickled file object on disk. Supports syncing contents of objects implementing an
        'update()' method (e.g. dicts). Only reads the stored file if its modification time has been changed.
        :param conflictResolution: One of 'raise', 'local', 'remote'. A conflict happens if both the local object and
            the file stored object has changed and is not equal. If 'raise`, a SyncConflictError is raised, if
            'local', the locally stored object replaces the object stored in the file, and if 'remote', the object
            stored in the file replaces the locally stored object.
        :param readOnly: If True, only syncs and remote changes into the local state (according to conflimtResolution)
            but the local state is not written to the file until the next time sync is called with readOnly=False.
        :return: None
        """
        self._checkIfClosed()
        assert conflictResolution in ['raise', 'local', 'remote']
        assert readOnly in [False, True]

        ensurePathExists(self._fn)

        fileModTime = self._getFileModTime()
        fileDirty = fileModTime != self._prevFileModTime

        if fileDirty or self._dirty() or self._postponeWrite:
            with FileLock(self._fn, 'w' if self._dirty() else 'r'):
                if fileDirty:
                    self._readFileAndSyncWithLocalObject(fileModTime, conflictResolution)

                if self._dirty() or self._postponeWrite:
                    if readOnly:
                        self._cleanEditHistory(postponeWrite=True)
                    else:
                        self._writeSyncedObjectToFile(fileModTime)
                        self._cleanEditHistory()

    def _getFileModTime(self):
        return datetime.fromtimestamp(os.path.getmtime(self._fn)) if os.path.exists(self._fn) else None

    def _readFileAndSyncWithLocalObject(self, fileModTime, conflictResolution):
        objFromFile = self._readFile(self._fn)
        if self._empty:
            self._obj = objFromFile
            self._empty = False
        else:
            if self._typeIsSameAndDictLike(self._obj, self._prevFileObj, objFromFile) \
                    and self._objectIsInitiallySynced():
                self._mergeDictLikeObjFromFile(objFromFile, conflictResolution)
            else:
                self._syncObjFromFile(objFromFile, conflictResolution)
        self._prevFileModTime = fileModTime
        self._prevFileObj = objFromFile

    def _writeSyncedObjectToFile(self, fileModTime):
        writtenContent = self._dumpToString(self._obj)

        with open(self._fn, 'w') as outFile:
            outFile.write(writtenContent)

        readContent = self._readFileToConfirmWrite(writtenContent)

        self._prevFileModTime = self._getFileModTime()
        assert self._prevFileModTime != fileModTime
        self._prevFileObj = self._loadFromString(readContent)

    def _readFileToConfirmWrite(self, writtenContent):
        readContent = None
        while readContent != writtenContent:
            if readContent is not None:
                time.sleep(0.05)
            with open(self._fn, 'r') as inFile:
                readContent = inFile.read()
        return readContent

    def _syncObjFromFile(self, objFromFile, conflictResolution):
        doRemoteSync = True
        if not self._fileObjectChanged(objFromFile):
            doRemoteSync = False
        elif self._dirty():
            doRemoteSync = self._resolveConflict(Conflict(object=True), objFromFile, conflictResolution)

        if doRemoteSync:
            self._obj = objFromFile

    def _isObjectConflict(self, objFromFile):
        return self._dirty() and self._fileObjectChanged(objFromFile)

    def _fileObjectChanged(self, objFromFile):
        return not objFromFile == self._prevFileObj

    def _mergeDictLikeObjFromFile(self, objFromFile, conflictResolution='raise'):
        fileAddedKeys, fileDeletedKeys, fileUpdatedKeys = self._getDiffKeys(self._prevFileObj, objFromFile)

        keysToDeleteLocally = set(key for key in fileDeletedKeys if key in self._obj)
        keysToUpdateLocally = fileAddedKeys | fileUpdatedKeys

        self._filterKeysAccordingToConflictManagement(keysToDeleteLocally, objFromFile, conflictResolution)
        self._filterKeysAccordingToConflictManagement(keysToUpdateLocally, objFromFile, conflictResolution)

        for key in keysToDeleteLocally:
            del self[key]

        self._obj.update((key, objFromFile[key]) for key in keysToUpdateLocally)

    @staticmethod
    def _getDiffKeys(dictLikeOld, dictLikeNew):
        keysOld = set(dictLikeOld.keys())
        keysNew = set(dictLikeNew.keys())
        addedKeys = keysNew - keysOld
        deletedKeys = keysOld - keysNew
        updatedKeys = set(key for key in keysOld & keysNew if dictLikeOld[key] != dictLikeNew[key])
        return addedKeys, deletedKeys, updatedKeys

    def _filterKeysAccordingToConflictManagement(self, keysToSyncLocally, objFromFile, conflictResolution):
        conflictKeys = keysToSyncLocally & self._keysWithLocalEdits()
        conflicts = (Conflict(key=key) for key in conflictKeys)
        for conflict in conflicts:
            doRemoteSync = self._resolveConflict(conflict, objFromFile, conflictResolution)
            if not doRemoteSync:
                keysToSyncLocally.remove(conflict.key)

    def _resolveConflict(self, conflict, objFromFile, conflictResolution):
        if self._conflictButSameResults(conflict, objFromFile) or conflictResolution == 'local':
            return False
        if conflictResolution == 'raise':
            self._raiseSyncConflictError(conflict, objFromFile)
        return True

    def _conflictButSameResults(self, conflict, objFromFile):
        if conflict.object:
            return self._obj == objFromFile
        else:
            return self._obj.get(conflict.key) == objFromFile.get(conflict.key)

    def _raiseSyncConflictError(self, conflict, objFromFile):
        localValue = self._obj if conflict.object else self._formatValueForKey(self._obj, conflict.key)
        remoteValue = objFromFile if conflict.object else self._formatValueForKey(objFromFile, conflict.key)
        itemDescription = ('' if conflict.object else 'item with key "{}" of '.format(conflict.key)) + \
                          'contained object'
        raise SyncConflictError('Conflict discovered for {}, which has been '.format(itemDescription) +
                                'changed both locally [current value: {}] '.format(localValue) +
                                'and on disk [current value: {}].'.format(remoteValue))

    @staticmethod
    def _formatValueForKey(dictLike, key):
        return '"{}"'.format(dictLike[key]) if key in dictLike else '(deleted)'

    def close(self):
        if self._dirty():
            self.sync()
        self._closed = True

    def _checkIfClosed(self):
        if self._closed:
            raise ValueError('SafePickleFile object for the file "{}" has been closed. '.format(self._fn) +
                             'Please create a new object.')

    # Abstract methods

    @abstractmethod
    def _loadFromString(self, readContent):
        pass

    @abstractmethod
    def _dumpToString(self,  obj):
        pass

    @abstractmethod
    def _readFile(self, filePath):
        pass


# SafePickleFile

class SafePickleFile(SafeFile):
    PROTOCOL = 2

    def __init__(self, fn, protocol=PROTOCOL):
        super(SafePickleFile, self).__init__(fn)
        self._protocol = protocol

    def _loadFromString(self, readContent):
        return cPickle.loads(readContent)

    def _dumpToString(self, obj):
        return cPickle.dumps(obj, protocol=self._protocol)

    def _readFile(self, filePath):
        return cPickle.load(open(filePath, 'r'))


# SafeJsonFile

class SafeJsonFile(SafeFile):
    def __init__(self, fn):
        super(SafeJsonFile, self).__init__(fn)

    def _loadFromString(self, readContent):
        return json.loads(readContent)

    def _dumpToString(self, obj):
        return json.dumps(obj)

    def _readFile(self, filePath):
        return json.load(open(filePath, 'r'))
