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
import functools
#from proto.RSetup import r

from config.Config import HB_SOURCE_CODE_BASE_DIR
import config.Config
LOG_PATH = HB_SOURCE_CODE_BASE_DIR + os.sep + '.testlogs'

import gold.statistic.Statistic
import gold.statistic.ResultsMemoizer
import gold.application.StatRunner
from gold.application.GalaxyInterface import GalaxyInterface

import gold.description.Analysis
from test.util.Asserts import smartRecursiveAssertList
from test.integration.ProfiledIntegrationTest import ProfiledIntegrationTest

gold.application.StatRunner.PRINT_PROGRESS = False
#gold.description.Analysis.PASS_ON_VALIDSTAT_EXCEPTIONS = True
from config.Config import DebugConfig
DebugConfig.PASS_ON_VALIDSTAT_EXCEPTIONS = True

GalaxyInterface.APPEND_ASSEMBLY_GAPS = False
GalaxyInterface.APPEND_COUNTS = False
#quick.application.GalaxyInterface.DEFAULT_GENOME ='TestGenome'

class GalaxyIntegrationTest(ProfiledIntegrationTest):
    
    def _assertEqualResults(self, target, res):
        resList = [sorted(res[region].items()) for region in res.getAllRegionKeys()]
        if len(res.getAllErrors()) != 0:
            raise res.getAllErrors()[0]
        if self.VERBOSE:
            print 'Target: ', target
            print 'Result: ', resList

        self.assertListsOrDicts(target, resList)
    
    def _assertEqualGlobalResults(self, target, res):
        resList = sorted(res.getGlobalResult().items())
        if len(res.getAllErrors()) != 0:
            raise res.getAllErrors()[0]
        if self.VERBOSE:
            print 'Target: ', target
            print 'Result: ', resList

        self.assertListsOrDicts(target, resList)
    
    def _assertRunEqual(self, target, *args, **kwArgs):
        if self.VERBOSE:
            DebugConfig.PASS_ON_COMPUTE_EXCEPTIONS = True
            print '\n***\n' + str(self.id()) + '\n***'
        
        args = list(args)
        analysisDef = [x.strip() for x in args[2].split('->')]
        if len(analysisDef) == 1:
            analysisDef.append(analysisDef[0])
        analysisDef[0] += ' [randomSeed:=0:]'
        
        args[2] = analysisDef[0] + " -> " + analysisDef[1]
        
        for diskMemo in [False, True]:
            gold.statistic.ResultsMemoizer.LOAD_DISK_MEMOIZATION = diskMemo

            if self._usesProfiling():
                DebugConfig.USE_PROFILING = True
                
            res = GalaxyInterface.run(*args, **{'genome':'TestGenome'})

            self._assertEqualResults(target, res)
            if kwArgs.get('globalTarget') != None:
                self._assertEqualGlobalResults(kwArgs['globalTarget'], res)
                
            if self._usesProfiling():
                self._storeProfile(diskMemo)
    
    def _assertBatchEqual(self, target, *args):
        for diskMemo in [False, True]:
            gold.statistic.ResultsMemoizer.LOAD_DISK_MEMOIZATION = diskMemo
            batchRes = GalaxyInterface.runBatchLines(*args)
            for i in range(len(batchRes)):
                self._assertEqualResults(target[i], batchRes[i])
