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
from gold.util.CustomExceptions import ShouldNotOccurError
from gold.util.DiskMirroredDict import SafeDiskMirroredDict
from quick.util.CommonFunctions import ensurePathExists
from gold.application.LogSetup import logMessageOnce

class MemoDataCollection(dict):
    def __init__(self):
        self._memoDicts = {}
        dict.__init__(self)
        
    @staticmethod
    def _createPickleFn(memoPath):
        return memoPath + os.sep + 'memo.dict'
    
    #def has_key(self, key):
        #return os.path.exists( self._createPickleFn(memoPath) )
    
    def __getitem__(self, memoPath):
        if not memoPath in self._memoDicts:
            memoFn = self._createPickleFn(memoPath)
            ensurePathExists( memoFn )
            try:
                self._memoDicts[memoPath] = SafeDiskMirroredDict(memoFn)
            except Exception, e:
                logMessageOnce("Exception when accessing memo file '%s': %s" % (memoFn, str(e)))
                raise
        return self._memoDicts[memoPath]

    def __setitem__(self, key, value):
        raise ShouldNotOccurError
    
    #def __del__(self):
        #as del is not always safe, make sure to instead call close manually..
        #self.close()

    def close(self):
        for key in self._memoDicts.keys():
            try:
                self._memoDicts[key].close()
            except Exception, e:
                logMessageOnce('No memoization due to IOError (probably because some other process are writing same data): ' + str(e))
                
            del self._memoDicts[key]
