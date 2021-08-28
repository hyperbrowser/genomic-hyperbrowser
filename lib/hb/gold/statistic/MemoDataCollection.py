import os
from gold.util.CustomExceptions import ShouldNotOccurError
from gold.util.SafeFile import SafePickleFile
from gold.application.LogSetup import logMessageOnce


class MemoDataCollection(object):
    def __init__(self):
        self._memoDicts = {}
        # dict.__init__(self)
        
    @staticmethod
    def _createFilePath(memoPath):
        return memoPath + os.sep + 'memo.dict'
    
    def __getitem__(self, memoPath):
        if memoPath not in self._memoDicts:
            memoFn = self._createFilePath(memoPath)
            try:
                safePickleFile = SafePickleFile(memoFn)
                if safePickleFile.object is None:
                    safePickleFile.object = {}
                    safePickleFile.sync(conflictResolution='remote')
                self._memoDicts[memoPath] = safePickleFile
            except Exception as e:
                logMessageOnce("Exception when accessing memo file '%s': %s" % (memoFn, str(e)))
                raise
        # self._memoDicts[memoPath].sync(conflictResolution='remote', readOnly=True)
        return self._memoDicts[memoPath]

    def __setitem__(self, key, value):
        raise ShouldNotOccurError

    def syncDict(self, memoPath):
        try:
            self._memoDicts[memoPath].sync(conflictResolution='local')
        except Exception as e:
            logMessageOnce('No memoization due to error: ' + str(e))

    def syncAllDicts(self):
        for path in self._memoDicts.keys():
            self.syncDict(path)

    def syncAllDicts(self):
        for path in self._memoDicts.keys():
            self.syncDict(path)

    def close(self):
        for path in self._memoDicts.keys():
            try:
                self.syncDict(path)
                self._memoDicts[path].close()
            except Exception as e:
                logMessageOnce('No memoization due to error: ' + str(e))
                
            del self._memoDicts[path]
