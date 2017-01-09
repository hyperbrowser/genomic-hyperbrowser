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

import numpy
from collections import OrderedDict

import config.Config
import gold.statistic.ResultsMemoizer as ResultsMemoizer
import gold.util.CompBinManager

from gold.track.GenomeRegion import GenomeRegion
from gold.track.TrackView import TrackView
from gold.util.CompBinManager import CompBinManager
from gold.util.CustomExceptions import IncompatibleTracksError, NoneResultError, NoMoreUniqueValsError
from quick.util.CommonFunctions import silenceRWarnings
from test.gold.track.common.SampleTrack import SampleTrack
from test.gold.track.common.SampleTrackWithConverters import SampleTrackWithConverters
from test.util.Asserts import TestCaseWithImprovedAsserts

ResultsMemoizer.LOAD_DISK_MEMOIZATION = False
ResultsMemoizer.STORE_DISK_MEMOIZATION = False

class StatUnitTest(TestCaseWithImprovedAsserts):
    THROW_EXCEPTION = True
    SPLITTABLE = True
    CLASS_TO_CREATE = None
    
    def setUp(self):
        silenceRWarnings()
        if self.SPLITTABLE:
            gold.util.CompBinManager.COMP_BIN_SIZE = 100
            self._ALLOW_COMP_BIN_SPLITTING = CompBinManager.ALLOW_COMP_BIN_SPLITTING
            CompBinManager.ALLOW_COMP_BIN_SPLITTING = True
        
    def tearDown(self):
        if self.SPLITTABLE:
            gold.util.CompBinManager.COMP_BIN_SIZE = config.Config.COMP_BIN_SIZE
            CompBinManager.ALLOW_COMP_BIN_SPLITTING = self._ALLOW_COMP_BIN_SPLITTING

    def _createStat(self, *args, **kwArgs):
        assert(isinstance(args[0], TrackView))
        tv1 = args[0]
        if len(args) > 1 and isinstance(args[1], TrackView):
            tv2 = args[1]
            assert(tv1.genomeAnchor == tv2.genomeAnchor)

            #Temporary hack for multiple tracks
#             if len(args) > 2:
            extraTrackViews = [arg for arg in args[2:] if isinstance(arg, TrackView)]


            self.stat = self.CLASS_TO_CREATE(kwArgs['binRegs'] if 'binRegs' in kwArgs else tv1.genomeAnchor, \
                                             SampleTrack(tv1) if kwArgs.get('testWithConverter') != True else SampleTrackWithConverters(tv1),\
                                             SampleTrack(tv2) if kwArgs.get('testWithConverter') != True else SampleTrackWithConverters(tv2),\
                                             *args[2 + len(extraTrackViews):], **kwArgs)

            #Temporary hack for multiple tracks
            for tv in extraTrackViews:
                track = SampleTrack(tv) if kwArgs.get('testWithConverter') != True else SampleTrackWithConverters(tv)
                if hasattr(self.stat, '_tracks'):
                    self.stat._tracks.append(track)
                else:#for splittable
                    if 'extraTracks' not in self.stat._kwArgs:
                        self.stat._kwArgs['extraTracks'] = tuple()
                    self.stat._kwArgs['extraTracks'] += tuple([track]) 

        else:
            self.stat = self.CLASS_TO_CREATE(kwArgs['binRegs'] if 'binRegs' in kwArgs else tv1.genomeAnchor, \
                                             SampleTrack(tv1) if kwArgs.get('testWithConverter') != True else SampleTrackWithConverters(tv1),\
                                             *args[1:], **kwArgs)




    def _assertIncompatibleTracks(self, *args, **kwArgs):
        self.assertRaises(IncompatibleTracksError, self._assertCompute, None, *args, **kwArgs)
        
    def _assertCompute(self, targetResult, *args, **kwArgs):
        self._createStat(*args, **kwArgs)
        #
        #self.stat.createChildren()
        #self.stat.compute()
        self._assertResult(targetResult, *args, **kwArgs)
        
    def _assertResult(self, targetResult, *args, **kwArgs):
        if kwArgs.has_key('assertFunc'):
            assertFunc = kwArgs['assertFunc']
        else:
            if type(targetResult) in [list, dict, tuple, numpy.ndarray, OrderedDict]:
                assertFunc = self.assertListsOrDicts
            elif type(targetResult) in [float]:
                assertFunc = self.assertAlmostEqual
            else:
                assertFunc = self.assertEqual
            
        try:
            res = self.stat.getResult()
        except NoneResultError:
            res = None

        try:
            assertFunc(targetResult, res)
        except Exception, e:
            if self.THROW_EXCEPTION:
                raise
            else:
                print 'Assert error:',e
                print ''
                print '****'
                print res
                print '****'
                print ''
                
        
    def _assertCreateChildren(self, childrenClassList, *args, **kwArgs):
        self._createStat(*args, **kwArgs)
        self.stat._createChildren()

        self.assertEqual(len(childrenClassList), len(self.stat._children))
        for i, cls in enumerate(childrenClassList):
            self.assertTrue(cls == self.stat._children[i].__class__)
            
    
