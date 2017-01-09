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
import quick.application.ExternalTrackManager

class GSuiteTestWithMockEncodingFuncs(unittest.TestCase):
    def setUp(self):
        @staticmethod
        def getEncodedDatasetIdFromGalaxyFn(galaxyFn):
            return str(hash(galaxyFn))

        @staticmethod
        def getGalaxyFnFromEncodedDatasetId(datasetId):
            return '/path/to/dataset_%s.dat' % datasetId

        @staticmethod
        def getGalaxyFilesFnFromEncodedDatasetId(datasetId):
            return '/path/to/dataset_%s_files' % datasetId

        self.oldGetEncodeDatasetIdFunc = \
            quick.application.ExternalTrackManager.ExternalTrackManager.getEncodedDatasetIdFromGalaxyFn
        quick.application.ExternalTrackManager.ExternalTrackManager.getEncodedDatasetIdFromGalaxyFn = \
            getEncodedDatasetIdFromGalaxyFn

        self.oldGetGalaxyFnFunc = \
            quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFnFromEncodedDatasetId
        quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFnFromEncodedDatasetId = \
            getGalaxyFnFromEncodedDatasetId

        self.oldGetGalaxyFilesFnFunc = \
            quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFilesFnFromEncodedDatasetId
        quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFilesFnFromEncodedDatasetId = \
            getGalaxyFilesFnFromEncodedDatasetId

    def tearDown(self):
        quick.application.ExternalTrackManager.ExternalTrackManager.getEncodedDatasetIdFromGalaxyFn = \
            self.oldGetEncodeDatasetIdFunc
        quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFnFromEncodedDatasetId = \
            self.oldGetGalaxyFnFunc
        quick.application.ExternalTrackManager.ExternalTrackManager.getGalaxyFilesFnFromEncodedDatasetId = \
            self.oldGetGalaxyFilesFnFunc
