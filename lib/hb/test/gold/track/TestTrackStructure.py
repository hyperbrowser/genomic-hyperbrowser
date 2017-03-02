#Unit test for aspects/methods in TrackStructureV2
#To be filled in by various team members - according to different tasks in Trello list:
#  "Finalize first statistic using new TS (branch:first_new_ts_stat)"
#See one of the other tests for how to make a unit test - e.g. TestTrackFormat.py
#I (GKS) don't know which git process will be the easiest here -
# I expect the easiest might be to just develop in the branch first_new_ts_stat and commit often,
# but another possibility may be to make separate feature branches and merge in again..

import unittest
from gold.track.Track import Track
from gold.track.TrackStructure import TrackStructureV2
from gold.track.TrackStructure import SingleTrackTS
from gold.track.TrackStructure import FlatTracksTS
from gold.track.TrackStructure import CategoricalTS




class TestTrackStructure(unittest.TestCase):
    def _buildTestTrees(self):
        #  inputTree      splitOnA         splitOnB           pairwise (A vs B)
        #    /  \             |              /   \              /  \
        #   A    B            C             D     E         t1_t2  t1_t3
        #   |   / \          /  \          /\     /\         / \    / \
        #   C   D   E       A    B        A  B   A  B       Q   R  Q   R
        #   |   |   |       |   / \       |  |   |  |       |   |  |   |
        #   t1  t2  t3      t1 D   E      C  t2  C  t3      t1  t2 t1  t2
        #                      |   |      |      |
        #                      t2  t3     t1     t1

        self.t1 = SingleTrackTS(Track('t1'), {"field 1": "value 1"})
        self.t2 = SingleTrackTS(Track('t2'), {"field 1": "value 2", "field 2": 6})
        self.t3 = SingleTrackTS(Track('t3'), {"field 1": "value 2", "field 3": None})

        self.inputTree = TrackStructureV2()
        self.inputTree['A'] = TrackStructureV2()
        self.inputTree['A']['C'] = self.t1
        self.inputTree['B'] = TrackStructureV2()
        self.inputTree['B']['D'] = self.t2
        self.inputTree['B']['E'] = self.t3

        # correct result of the input tree splitted on node A
        self.splittedOnNodeA = TrackStructureV2()
        self.splittedOnNodeA['C'] = TrackStructureV2()
        self.splittedOnNodeA['C']['A'] = self.t1
        self.splittedOnNodeA['C']['B'] = TrackStructureV2()
        self.splittedOnNodeA['C']['B']['D'] = self.t2
        self.splittedOnNodeA['C']['B']['E'] = self.t3

        # correct result of the input tree splitted on node B
        self.splittedOnNodeB = TrackStructureV2()
        self.splittedOnNodeB['D'] = TrackStructureV2()
        self.splittedOnNodeB['D']['A'] = TrackStructureV2()
        self.splittedOnNodeB['D']['A']['C'] = self.t1
        self.splittedOnNodeB['D']['B'] = self.t2
        self.splittedOnNodeB['E'] = TrackStructureV2()
        self.splittedOnNodeB['E']['A'] = TrackStructureV2()
        self.splittedOnNodeB['E']['A']['C'] = self.t1
        self.splittedOnNodeB['E']['B'] = self.t3

        self.pairwiseCombinations = TrackStructureV2()
        self.pairwiseCombinations["t1_t2"] = TrackStructureV2()
        self.pairwiseCombinations["t1_t2"]["query"] = self.t1
        self.pairwiseCombinations["t1_t2"]["reference"] = self.t2
        self.pairwiseCombinations["t1_t3"] = TrackStructureV2()
        self.pairwiseCombinations["t1_t3"]["query"] = self.t1
        self.pairwiseCombinations["t1_t3"]["reference"] = self.t3

        self.flatTrackStructure = FlatTracksTS()
        self.flatTrackStructure['A'] = self.t1
        self.flatTrackStructure['B'] = self.t2
        self.flatTrackStructure['C'] = self.t3

    def setUp(self):
        self._buildTestTrees()

    def _assertEqualTrackStructure(self, correct, output):
        self.assertEqual(correct.keys(), output.keys())
        for key, value in correct.items():
            self._assertEqualTrackStructure(correct[key], output[key])
            self.assertIsInstance(output[key], correct[key].__class__)
            self.assertIsInstance(output, TrackStructureV2)
            if isinstance(correct[key], SingleTrackTS):
                self.assertEqual(correct[key], output[key])

    def testMakeTreeSegregatedByCategory(self):
        # test splitting on a node that has a single category
        singleCategoryOutput = self.inputTree.makeTreeSegregatedByCategory(self.inputTree['A'])
        self._assertEqualTrackStructure(singleCategoryOutput, self.splittedOnNodeA)

        # test splitting on a node that has multiple categories
        singleCategoryOutput = self.inputTree.makeTreeSegregatedByCategory(self.inputTree['B'])
        self._assertEqualTrackStructure(singleCategoryOutput, self.splittedOnNodeB)

        # test splitting on a node without categories (should return an error)
        with self.assertRaises(AssertionError):
            self.inputTree.makeTreeSegregatedByCategory(self.inputTree['A']['C'])

        # TODO lonneke test with root as input
        # should this return the same structure as the input?
        # should metadata be moved around?
        # should the new structure be different from input and have more levels?

    def testMakePairwiseCombinations(self):
        pairwiseOutput = self.inputTree['A'].makePairwiseCombinations(self.inputTree['B'])
        self.assertEqual(pairwiseOutput, self.pairwiseCombinations)

        # combination between empty TrackStructures should result in just an empty TrackStructure
        empty = TrackStructureV2()
        empty.makePairwiseCombinations(empty)
        self.assertEqual(empty.makePairwiseCombinations(empty), empty)

        # TODO Lonneke add more border cases?

    def testGetMetadataField(self):
        self.assertItemsEqual(("field 1", "field 2", "field 3"), self.flatTrackStructure.getMetadataFields())

    def testGetAllValuesForMetadataField(self):
        self.assertItemsEqual(("value 1", "value 2",), self.flatTrackStructure.getAllValuesForMetadataField("field 1"))
        self.assertItemsEqual((6,), self.flatTrackStructure.getAllValuesForMetadataField("field 2"))
        self.assertItemsEqual((None,), self.flatTrackStructure.getAllValuesForMetadataField("field 3"))

    def testGetFlattenedTS(self):
        getFlattenedTsResult = FlatTracksTS()
        getFlattenedTsResult['t1'] = self.t1
        getFlattenedTsResult['t1 (2)'] = self.t1
        getFlattenedTsResult['t2'] = self.t2
        getFlattenedTsResult['t3'] = self.t3
        self._assertEqualTrackStructure(getFlattenedTsResult, self.splittedOnNodeB.getFlattenedTS())

    def testGetSplittedByCategoryTS(self):
        splitByField1 = CategoricalTS()
        field1value1 = FlatTracksTS()
        field1value2 = FlatTracksTS()
        splitByField1['value 1'] = field1value1
        splitByField1['value 1']['A'] = self.t1
        splitByField1['value 2'] = field1value2
        splitByField1['value 2']['B'] = self.t2
        splitByField1['value 2']['C'] = self.t3

        self._assertEqualTrackStructure(splitByField1, self.flatTrackStructure.getSplittedByCategoryTS("field 1"))

        splitByField2 = CategoricalTS()
        field2val6 = FlatTracksTS()
        splitByField2[6] = field2val6
        splitByField2[6]['B'] = self.t2

        self._assertEqualTrackStructure(splitByField2, self.flatTrackStructure.getSplittedByCategoryTS("field 2"))

        splitByField3 = CategoricalTS()
        field3None = FlatTracksTS()
        splitByField3[None] = field3None
        splitByField3[None]['C'] = self.t3

        self._assertEqualTrackStructure(splitByField3, self.flatTrackStructure.getSplittedByCategoryTS("field 3"))





        self.flatTrackStructure.getSplittedByCategoryTS("field 3")
        self.flatTrackStructure.getSplittedByCategoryTS("field does not exist")

    def testGetTrackSubsetTS(self):
        subsetField1Value2 = FlatTracksTS()
        subsetField1Value2['B'] = self.t2
        subsetField1Value2['C'] = self.t3
        self._assertEqualTrackStructure(subsetField1Value2, self.flatTrackStructure.getTrackSubsetTS("field 1", "value 2"))

        subsetField3None = FlatTracksTS()
        subsetField3None['C'] = self.t3
        self._assertEqualTrackStructure(subsetField3None, self.flatTrackStructure.getTrackSubsetTS("field 3", None))

        empty = FlatTracksTS()
        self._assertEqualTrackStructure(empty, self.flatTrackStructure.getTrackSubsetTS("field does not exist", "value"))
        self._assertEqualTrackStructure(empty, self.flatTrackStructure.getTrackSubsetTS("field 1", "val does not exist"))







if __name__ == "__main__":
    unittest.main()



