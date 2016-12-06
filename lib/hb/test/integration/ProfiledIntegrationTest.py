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

import sys
import StringIO

from asteval import Interpreter

from gold.util.Profiler import Profiler
from test.integration.ProfilingStorage import ProfilingStorage
from test.util.Asserts import TestCaseWithImprovedAsserts

class ProfiledIntegrationTest(TestCaseWithImprovedAsserts):
    VERBOSE = False
    def setUp(self):
        if not self.VERBOSE:
            sys.stdout = StringIO.StringIO()
        if not hasattr(ProfiledIntegrationTest, '_svnRevision'):
            ProfiledIntegrationTest._svnRevision = ProfilingStorage.getSvnRevision()
            
        #print ProfiledIntegrationTest._svnRevision, self._getId(), ProfilingStorage.isStored(self._getId(), ProfiledIntegrationTest._svnRevision)
        
        if ProfiledIntegrationTest._svnRevision != None and \
            not ProfilingStorage.isStored(self._getId(), ProfiledIntegrationTest._svnRevision):
            self._profiler = Profiler()
        else:
            self._profiler = None
        
    def _getId(self):
        return self.id().split('.')[-1]
    
    def _usesProfiling(self):
        return self._profiler is not None
    
    def _runWithProfiling(self, runStr, symbolDict={}):
        aeval = Interpreter()
        if symbolDict:
            aeval.symtable.update(symbolDict)

        if not self._usesProfiling():
            return aeval(runStr)
        else:
            print 'Running with profiling..'
            res = self._profiler.run('aeval(%s)' % runStr, globals, locals)
            self._profiler.printStats()
            return res
        
    def _storeProfile(self, diskMemo=False):
        if self.VERBOSE or not self._usesProfiling():
            return 
        
        ProfilingStorage.parseAndStoreProfile(sys.stdout.getvalue(), self._getId(),\
                                              ProfiledIntegrationTest._svnRevision, diskMemo)
