#!/usr/bin/env python
import ast
import unittest
import os
import sys
from collections import OrderedDict
from copy import deepcopy

import numpy

from config.Config import DebugConfig
from gold.description.TrackInfo import TrackInfo
from gold.track.Track import Track
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackSource import TrackSource
from gold.util.CommonFunctions import createDirPath
from gold.origdata.GenomeElementSource import BoundingRegionTuple
from gold.track.GenomeRegion import GenomeRegion
from gold.util.CustomExceptions import PreprocessError
from quick.origdata.CustomTrackGenomeElementSource import CustomTrackGenomeElementSource
from quick.util.GenomeInfo import GenomeInfo
from gold.track.TrackView import AutonomousTrackElement, TrackView
from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob, PreProcessCustomTrackJob
from test.gold.origdata.common.TestWithGeSourceData import TestWithGeSourceData
from test.integration.GalaxyIntegrationTest import GalaxyIntegrationTest


class TestTrackPreProcessor(GalaxyIntegrationTest, TestWithGeSourceData):
    GENOME = 'TestGenome'

    def setUp(self):
        super(TestTrackPreProcessor, self).setUp()
        self._prevPassOnPreprocessExceptions = DebugConfig.PASS_ON_PREPROCESS_EXCEPTIONS
        DebugConfig.PASS_ON_PREPROCESS_EXCEPTIONS = True

    def tearDown(self):
        super(TestTrackPreProcessor, self).tearDown()
        DebugConfig.PASS_ON_PREPROCESS_EXCEPTIONS = self._prevPassOnPreprocessExceptions

    def _preProcess(self, subTrackName, noOverlapsFileCount=None, withOverlapsFileCount=None,
                    noOverlapsChrElCount=None, withOverlapsChrElCount=None):
        trackName = self.TRACK_NAME_PREFIX + subTrackName

        self._removePreprocessedTrackData(trackName)

        # aeval = Interpreter()
        # aeval.symtable.update({'PreProcessAllTracksJob': PreProcessAllTracksJob})
        # cmd = "PreProcessAllTracksJob(" + repr(self.GENOME) + "," + \
        #       repr(trackName) + ", username='Test').process()"
        # aeval(cmd)
        PreProcessAllTracksJob(self.GENOME, trackName, username='Test').process()

        self._assertCounts(trackName, noOverlapsFileCount, withOverlapsFileCount, noOverlapsChrElCount,
                           withOverlapsChrElCount)

        self._assertHasTrackFormatHash(trackName)

        # self._storeProfile()

    def _preProcessCustomTracks(self, subTrackName, regionList, getGeSourceCallBackFunc,
                                noOverlapsFileCount=None, withOverlapsFileCount=None,
                                noOverlapsChrElCount=None, withOverlapsChrElCount=None,
                                **callBackArgs):
        trackName = self.TRACK_NAME_PREFIX + subTrackName

        for mergeChrFolders in [False, True]:
            self._removePreprocessedTrackData(trackName)
            print 'mergeChrFolders: {}'.format(mergeChrFolders)
            PreProcessCustomTrackJob(self.GENOME, trackName, regionList, getGeSourceCallBackFunc, username='Test',
                                     preProcess=True, finalize=False, mergeChrFolders=mergeChrFolders,
                                     **callBackArgs).process()
            PreProcessCustomTrackJob(self.GENOME, trackName, regionList, getGeSourceCallBackFunc, username='Test',
                                     preProcess=False, finalize=True, mergeChrFolders=mergeChrFolders,
                                     **callBackArgs).process()

            if not mergeChrFolders:
                if noOverlapsFileCount:
                    noOverlapsFileCount = (noOverlapsFileCount - 1) * len(regionList)
                if withOverlapsFileCount:
                    withOverlapsFileCount = (withOverlapsFileCount - 1) * len(regionList)

            self._assertCounts(trackName, noOverlapsFileCount, withOverlapsFileCount,
                               noOverlapsChrElCount, withOverlapsChrElCount)

    def _assertCounts(self, trackName, noOverlapsFileCount, withOverlapsFileCount,
                      noOverlapsChrElCount, withOverlapsChrElCount):
        noOverlapsPath, withOverlapsPath = self._getDirPaths(trackName)
        if noOverlapsFileCount is not None:
            self.assertEquals(noOverlapsFileCount, self._countFiles(noOverlapsPath))
        if withOverlapsFileCount is not None:
            self.assertEquals(withOverlapsFileCount, self._countFiles(withOverlapsPath))
        if noOverlapsChrElCount is not None:
            self._assertChrElCounts(trackName, noOverlapsChrElCount, False)
        if withOverlapsChrElCount is not None:
            self._assertChrElCounts(trackName, withOverlapsChrElCount, True)

    @staticmethod
    def _countFiles(dir):
        numFiles = 0
        for path, dirs, files in os.walk(dir):
            numFiles += len([_ for _ in files if not _.startswith('.')])
        return numFiles

    def _getDirPaths(self, trackName):
        noOverlapsPath = createDirPath(trackName, self.GENOME, allowOverlaps=False)
        withOverlapsPath = createDirPath(trackName, self.GENOME, allowOverlaps=True)
        return noOverlapsPath, withOverlapsPath

    def _assertChrElCounts(self, trackName, chrElCountDict, allowOverlaps):
        allChrs = chrElCountDict.keys()
        for chr in allChrs:
            self.assertEquals(chrElCountDict[chr], self._getNumTrackElements(trackName, chr, allowOverlaps))
        self.assertEquals(sum(chrElCountDict.values()),
                          self._getTotalNumTrackElementsFromMemmap(trackName, allChrs, allowOverlaps))
        self.assertEquals(sum(chrElCountDict.values()),
                          self._getTotalNumTrackElementsFromTrackInfo(trackName, allowOverlaps))

    def _getNumTrackElements(self, trackName, chr, allowOverlaps):
        trackSource = TrackSource()
        trackData = trackSource.getTrackData(trackName, self.GENOME, chr, allowOverlaps)
        brShelve = trackData.boundingRegionShelve
        if brShelve:
            chrBoundingRegions = brShelve.getAllBoundingRegionsForChr(chr)
            numTrackElements = sum(self._getTrackView(trackName, br, allowOverlaps).getNumElements()
                                   for br in chrBoundingRegions)
            assert numTrackElements == brShelve.getTotalElementCountForChr(chr)
        else:  # chr-specific folders have not been merged
            numTrackElements = self._getNumTrackElementsFromMemmap(trackName, chr, allowOverlaps)

        return numTrackElements

    def _getTotalNumTrackElementsFromMemmap(self, trackName, allChrs, allowOverlaps):
        totalNumTrackElements = 0
        for chr in allChrs + [None]:  # Count both chr-specific directories and merged files
            try:
                totalNumTrackElements += self._getNumTrackElementsFromMemmap(trackName, chr, allowOverlaps)
            except OSError:  # Trying to access chr-specific dir that does not exist
                continue

        return totalNumTrackElements

    def _getNumTrackElementsFromMemmap(self, trackName, chr, allowOverlaps):
        trackSource = TrackSource()
        trackData = trackSource.getTrackData(trackName, self.GENOME, chr, allowOverlaps, forceChrFolders=True)
        allArrayLenghts = [memmap.getShape()[0] for name, memmap in trackData.iteritems()
                           if name not in ['leftIndex', 'rightIndex']]
        if len(allArrayLenghts) > 0:
            assert all(arrayLen == allArrayLenghts[0] for arrayLen in allArrayLenghts)
            return allArrayLenghts[0]
        else:
            return 0

    def _getTotalNumTrackElementsFromTrackInfo(self, trackName, allowOverlaps):
        ti = TrackInfo(self.GENOME, trackName)
        return ti.origElCount if allowOverlaps else ti.clusteredElCount

    def _assertHasTrackFormatHash(self, trackName):
        ti = TrackInfo(self.GENOME, trackName)
        assert ti.trackFormatHash

    def _getTrackView(self, trackName, region, allowOverlaps):
        track = Track(trackName)
        track.addFormatReq(TrackFormatReq(allowOverlaps=allowOverlaps))
        return track.getTrackView(region)

    def _getBoundingRegionTupleList(self, case, sortedAssertElList):
        boundingRegions = [br for br in sorted(case.boundingRegionsAssertList) if br.region.chr is not None]
        if len(boundingRegions) > 0:
            return [BoundingRegionTuple(GenomeRegion(self.GENOME, chr=br.region.chr,
                                                     start=br.region.start if br.region.start is not None else 0,
                                                     end=br.region.end if br.region.end is not None else \
                                                         GenomeInfo.getChrLen(self.GENOME, br.region.chr)), br.elCount)
                    for br in boundingRegions]
        else:
            totChrList = [ge.chr for ge in sortedAssertElList]
            chrBrList = OrderedDict( [ (i, totChrList.count(i)) for i in sorted(set(totChrList)) ] )
            return [BoundingRegionTuple(GenomeRegion(self.GENOME, chr=chr, start=0,
                                                     end=GenomeInfo.getChrLen(self.GENOME, chr)), elCount) \
                    for chr, elCount in chrBrList.iteritems()]

    def _getCaseTrackView(self, case, br, allowOverlaps):
        return self._getTrackView(self.TRACK_NAME_PREFIX + case.trackName,
                                  GenomeRegion(genome=self.GENOME, chr=br.chr, start=br.start, end=br.end),
                                  allowOverlaps=allowOverlaps)

    def _assertGenomeAndTrackElementEqual(self, ge, te, teChr, teOffset):
        self.assertEqual(ge.chr, teChr)

        if ge.start is not None:
            self.assertEqual(ge.start, te.start() + teOffset)
        if ge.end is not None:
            self.assertEqual(ge.end, te.end() + teOffset)
        if ge.edges is not None:
            self.assertListsOrDicts(ge.edges, te.edges()[te.edges()!=''])
        if ge.weights is not None:
            self.assertListsOrDicts(ge.weights, te.weights()[te.edges()!=''])

        for attr in ['val', 'strand', 'id']:
            self.assertListsOrDicts(getattr(ge, attr), getattr(te, attr)())
        for attr in ge.orderedExtraKeys:
            self.assertListsOrDicts(ge.extra[attr], getattr(te, attr)())

    def _testTrackReading(self, case, allowOverlaps):
        allAssertEls = []
        allTrackEls = []
        trackElChrs = []
        trackElOffsets = []
        prevAssertElCount = 0

        sortedAssertElList = sorted(case.assertElementList, key=lambda el:[el.chr, el.start, el.end])

        if case.targetClass._isSliceSource:
            expandedAssertElList = []
            for assertEl in sortedAssertElList:
                for prefix in case.prefixList:
                    contents = getattr(assertEl, prefix)
                    for i in range(len(contents)):
                        el = deepcopy(assertEl)
                        setattr(el, prefix, contents[i])
                        expandedAssertElList.append(el)
            sortedAssertElList = expandedAssertElList

        for brTuple in self._getBoundingRegionTupleList(case, sortedAssertElList):
            if 'end' in case.prefixList and not 'start' in case.prefixList: #GP, SF, LGP, LSF
                assertElStartIdx = prevAssertElCount + 1
            else:
                assertElStartIdx = prevAssertElCount
            assertElEndIdx = prevAssertElCount + brTuple.elCount
            assertEls = sortedAssertElList[assertElStartIdx:assertElEndIdx]

            tv = self._getCaseTrackView(case, brTuple.region, allowOverlaps)
            self.assertEqual(len(assertEls), tv.getNumElements())

            allAssertEls += assertEls
            allTrackEls += [AutonomousTrackElement(trackEl=x) for x in tv]
            trackElChrs += [brTuple.region.chr for x in tv]
            trackElOffsets += [tv.genomeAnchor.start for x in tv]
            prevAssertElCount += brTuple.elCount

        for i, ge in enumerate(allAssertEls):
            self._assertGenomeAndTrackElementEqual(ge, allTrackEls[i], trackElChrs[i], trackElOffsets[i])


class TestGESourceTestsPreprocessing(TestTrackPreProcessor):
    TRACK_NAME_PREFIX = ['TestGenomeElementSource']

    def testAll(self):
        testGESource = self._commonSetup()

        for caseName in testGESource.cases:
            print caseName
            case = testGESource.cases[caseName]
            if caseName.endswith('_no_hb'):
                print 'Test case skipped...'
                continue

            self._writeTestFile(case)
            self._preProcess(case.trackName)

            allowOverlaps = True if ('start' in case.prefixList) and '_no_overlaps' not in caseName else False
            self._testTrackReading(case, allowOverlaps=allowOverlaps)

        self._removeAllTrackData(self.TRACK_NAME_PREFIX)

    def _preProcessUnpackException(self, trackName):
        try:
            self._preProcess(trackName)
        except PreprocessError as e:
            raise e.__context__

    def testAllExceptions(self):
        testGESource = self._commonSetup()

        for caseName in testGESource.exceptionCases:
            print caseName
            case = testGESource.exceptionCases[caseName]
            if caseName.endswith('_no_hb'):
                print 'Test case skipped...'
                continue

            self._writeTestFile(case)
            self.assertRaises(case.exceptionClass, self._preProcessUnpackException, case.trackName)

        self._removeAllTrackData(self.TRACK_NAME_PREFIX)


class TestCustomTrackPreprocessing(TestTrackPreProcessor):
    TRACK_NAME_PREFIX = ['CustomTracks']

    def testPreprocessCustomTrack(self):
        class SlicedCustomTrackGenomeElementSource(CustomTrackGenomeElementSource):
            _isSliceSource = True

            def getValDataType(self):
                return 'int32'

        class RangeTrackViewSource(object):
            def __init__(self, region):
                self._region = region

            def __iter__(self):
                for region in [self._region]:
                    valArray = numpy.arange(len(region), dtype='int32')
                    yield TrackView(self._region, valList=valArray, allowOverlaps=False)

        def _getGeSourceCallBackFunction(genome, trackName, region, func):
            rangeTvSource = RangeTrackViewSource(region)
            return SlicedCustomTrackGenomeElementSource(rangeTvSource, genome, trackName, region.chr, func)

        def inverseRange(trackView):
            return len(trackView) - trackView.valsAsNumpyArray()

        regionList = [GenomeRegion(self.GENOME, 'chr21', 0, 10000),
                      GenomeRegion(self.GENOME, 'chrM', 0, 16571)]
        self._preProcessCustomTracks(
            ['CustomFunctionSlice'], regionList,
            getGeSourceCallBackFunc=_getGeSourceCallBackFunction, noOverlapsFileCount=2, withOverlapsFileCount=None,
            noOverlapsChrElCount={'chr21': 10000, 'chrM': 16571}, withOverlapsChrElCount=None,
            func=inverseRange
        )


class TestGESourceTracksPreprocessing(TestTrackPreProcessor):
    TRACK_NAME_PREFIX = ['GESourceTracks']

    def testPreProcessBed(self):
        self._preProcess(['BedGenomeElementSource'],
                         noOverlapsFileCount=14,
                         withOverlapsFileCount=14,
                         noOverlapsChrElCount={'chr21': 242, 'chrM': 11},
                         withOverlapsChrElCount={'chr21': 828, 'chrM': 11})

    def testPreProcessBedPoint(self):
        self._preProcess(['PointBedGenomeElementSource'],
                         noOverlapsFileCount=7,
                         withOverlapsFileCount=7,
                         noOverlapsChrElCount={'chr21': 139, 'chrM': 8},
                         withOverlapsChrElCount={'chr21': 139, 'chrM': 8})

    def testPreProcessBedCategory(self):
        self._preProcess(['BedCategoryGenomeElementSource'],
                         noOverlapsFileCount=6,
                         withOverlapsFileCount=6,
                         noOverlapsChrElCount={'chr21': 38, 'chrM': 0},
                         withOverlapsChrElCount={'chr21': 87, 'chrM': 0})

    def testPreProcessBedValued(self):
        self._preProcess(['BedValuedGenomeElementSource'],
                         noOverlapsFileCount=8,
                         withOverlapsFileCount=8,
                         noOverlapsChrElCount={'chr21': 38, 'chrM': 0},
                         withOverlapsChrElCount={'chr21': 87, 'chrM': 0})

    def testPreProcessFasta(self):
        self._preProcess(['FastaGenomeElementSource'],
                         noOverlapsFileCount=2,
                         withOverlapsFileCount=None,
                         noOverlapsChrElCount={'chr21': 9804, 'chrM': 0},
                         withOverlapsChrElCount=None)

    def testPreProcessGff(self):
        self._preProcess(['GffGenomeElementSource'],
                         noOverlapsFileCount=12,
                         withOverlapsFileCount=12,
                         noOverlapsChrElCount={'chr21': 3076, 'chrM': 0},
                         withOverlapsChrElCount={'chr21': 5260, 'chrM': 0})

    def testPreProcessMicroarray(self):
        self._preProcess(['MicroarrayGenomeElementSource'],
                         noOverlapsFileCount=7,
                         withOverlapsFileCount=7,
                         noOverlapsChrElCount={'chr21': 2, 'chrM': 0},
                         withOverlapsChrElCount={'chr21': 2, 'chrM': 0})

    def testPreProcessBedGraph(self):
        self._preProcess(['BedGraphGenomeElementSource'],
                         noOverlapsFileCount=6,
                         withOverlapsFileCount=6,
                         noOverlapsChrElCount={'chr21': 10000, 'chrM': 0},
                         withOverlapsChrElCount={'chr21': 10000, 'chrM': 0})

    def testPreProcessBedGraphTargetControl(self):
        self._preProcess(['BedGraphTargetControlGenomeElementSource'],
                         noOverlapsFileCount=6,
                         withOverlapsFileCount=6,
                         noOverlapsChrElCount={'chr21': 2, 'chrM': 1},
                         withOverlapsChrElCount={'chr21': 2, 'chrM': 1})

    def testPreProcessHBFunction(self):
        self._preProcess(['HBFunctionGenomeElementSource'],
                         noOverlapsFileCount=2,
                         withOverlapsFileCount=None,
                         noOverlapsChrElCount=None,
                         withOverlapsChrElCount=None)

    def testPreProcessPoisitionIter(self):
        self._preProcess(['PositionIterGESource'],
                         noOverlapsFileCount=4,
                         withOverlapsFileCount=None,
                         noOverlapsChrElCount={'chr21': 139, 'chrM': 8},
                         withOverlapsChrElCount=None)

    def runTest(self):
        pass


if __name__ == "__main__":
    if len(sys.argv) == 2:
        TestTrackPreProcessor.debugMode = sys.argv[1]
        sys.argv = sys.argv[:-1]
    # TestTrackPreProcessor().run()
    # TestTrackPreProcessor().debug()
    unittest.main()
