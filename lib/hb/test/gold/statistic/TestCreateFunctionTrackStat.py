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

import unittest
import os
import sys

from gold.application.StatRunner import AnalysisDefJob
from gold.util.CommonFunctions import createDirPath
from gold.track.GenomeRegion import GenomeRegion
from gold.track.BoundingRegionShelve import BoundingRegionShelve, BoundingRegionInfo
from gold.track.TrackSource import TrackSource
from gold.util.CustomExceptions import OutsideBoundingRegionError
from test.util.FileUtils import removeDirectoryTree
from test.util.Asserts import TestCaseWithImprovedAsserts

import config.Config
import gold.util.CompBinManager
import gold.statistic.CreateFunctionTrackStat
from quick.util.GenomeInfo import GenomeInfo


class MyGenomeInfo(GenomeInfo):
    @classmethod
    def getChrList(cls, genome):
        return ['chrM']

class TestCreateFunctionTrackStat(TestCaseWithImprovedAsserts):
    def setUp(self):
        self.stdout = sys.stdout
        sys.stdout = open('/dev/null', 'w')

        self._trackName = ['intensity_test']
        self._genome = 'TestGenome'
        self._chr = 'chrM'
        self._path = createDirPath(self._trackName, self._genome)
        assert self._path.endswith(self._trackName[-1])
        removeDirectoryTree(self._path)
        gold.util.CompBinManager.COMP_BIN_SIZE = config.Config.COMP_BIN_SIZE
        gold.statistic.CreateFunctionTrackStat.GenomeInfo = MyGenomeInfo
    
    def tearDown(self):
        removeDirectoryTree(self._path)
        sys.stdout = self.stdout
    
    def testCreateIntensityTrack(self):
        regions = [GenomeRegion(self._genome, self._chr, 1000, 5000),\
                   GenomeRegion(self._genome, self._chr, 6000, 7000),\
                   GenomeRegion(self._genome, self._chr, 10000, 16000)]
        job = AnalysisDefJob('[dataStat=SimpleBpIntensityStat] [outTrackName=' + '^'.join(self._trackName) + '] [numDiscreteVals=10] -> CreateFunctionTrackStat', \
                              ['nums'], ['points'], regions, genome=self._genome)
        for x in range(2):
            job.run()
            
        brShelve = BoundingRegionShelve(self._genome, self._trackName, allowOverlaps=False)
        self.assertRaises(OutsideBoundingRegionError, \
                          brShelve.getBoundingRegionInfo, GenomeRegion(self._genome, self._chr, 0, 1))
        #self.assertEquals(BoundingRegionInfo(0, 1, 0, 0, 0, 0),
        #                  brShelve.getBoundingRegionInfo(GenomeRegion(self._genome, self._chr, 0, 1)))
        self.assertEquals(BoundingRegionInfo(1000, 5000, 0, 4000, 0, 0),
                          brShelve.getBoundingRegionInfo(GenomeRegion(self._genome, self._chr, 2000, 2001)))
        self.assertRaises(OutsideBoundingRegionError, \
                          brShelve.getBoundingRegionInfo, GenomeRegion(self._genome, self._chr, 5500, 5501))
        #self.assertEquals(BoundingRegionInfo(5500, 5501, 0, 0, 0, 0),
        #                  brShelve.getBoundingRegionInfo(GenomeRegion(self._genome, self._chr, 5500, 5501)))
        self.assertEquals(BoundingRegionInfo(6000, 7000, 4000, 5000, 0, 0),
                          brShelve.getBoundingRegionInfo(GenomeRegion(self._genome, self._chr, 6500, 6501)))
        self.assertRaises(OutsideBoundingRegionError, \
                          brShelve.getBoundingRegionInfo, GenomeRegion(self._genome, self._chr, 8000, 8001))
        #self.assertEquals(BoundingRegionInfo(8000, 8001, 0, 0, 0, 0),
        #                  brShelve.getBoundingRegionInfo(GenomeRegion(self._genome, self._chr, 8000, 8001)))
        self.assertEquals(BoundingRegionInfo(10000, 16000, 5000, 11000, 0, 0),
                          brShelve.getBoundingRegionInfo(GenomeRegion(self._genome, self._chr, 11000, 11001)))
        self.assertRaises(OutsideBoundingRegionError, \
                          brShelve.getBoundingRegionInfo, GenomeRegion(self._genome, self._chr, 16500, 16501))
        #self.assertEquals(BoundingRegionInfo(16500, 16501, 0, 0, 0, 0),
        #                  brShelve.getBoundingRegionInfo(GenomeRegion(self._genome, self._chr, 16500, 16501)))
    
        trackData = TrackSource().getTrackData(self._trackName, self._genome, None, False)
        self.assertListsOrDicts(['val'], trackData.keys())
        self.assertListsOrDicts((11000,), trackData['val'].shape)
    
    def runTest(self):
        pass
    
if __name__ == "__main__":
    #TestCreateFunctionTrackStat().debug()
    unittest.main()
