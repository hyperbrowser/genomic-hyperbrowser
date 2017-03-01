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

        t1 = SingleTrackTS(Track('t1'), {"field 1": "value 1"})
        t2 = SingleTrackTS(Track('t2'), {"field 1": "value 2", "field 2": 6})
        t3 = SingleTrackTS(Track('t3'), {"field 1": "value 3", "field 3": None})

        self.inputTree = TrackStructureV2()
        self.inputTree['A'] = TrackStructureV2()
        self.inputTree['A']['C'] = t1
        self.inputTree['B'] = TrackStructureV2()
        self.inputTree['B']['D'] = t2
        self.inputTree['B']['E'] = t3

        # correct result of the input tree splitted on node A
        self.splitOnA = TrackStructureV2()
        self.splitOnA['C'] = TrackStructureV2()
        self.splitOnA['C']['A'] = t1
        self.splitOnA['C']['B'] = TrackStructureV2()
        self.splitOnA['C']['B']['D'] = t2
        self.splitOnA['C']['B']['E'] = t3

        # correct result of the input tree splitted on node B
        self.splitOnB = TrackStructureV2()
        self.splitOnB['D'] = TrackStructureV2()
        self.splitOnB['D']['A'] = TrackStructureV2()
        self.splitOnB['D']['A']['C'] = t1
        self.splitOnB['D']['B'] = t2
        self.splitOnB['E'] = TrackStructureV2()
        self.splitOnB['E']['A'] = TrackStructureV2()
        self.splitOnB['E']['A']['C'] = t1
        self.splitOnB['E']['B'] = t3

        self.pairwiseCombinations = TrackStructureV2()
        self.pairwiseCombinations["t1_t2"] = TrackStructureV2()
        self.pairwiseCombinations["t1_t2"]["query"] = t1
        self.pairwiseCombinations["t1_t2"]["reference"] = t2
        self.pairwiseCombinations["t1_t3"] = TrackStructureV2()
        self.pairwiseCombinations["t1_t3"]["query"] = t1
        self.pairwiseCombinations["t1_t3"]["reference"] = t3

        self.flatTs = FlatTracksTS()
        self.flatTs['A'] = t1
        self.flatTs['B'] = t2
        self.flatTs['C'] = t3

    def setUp(self):
        self._buildTestTrees()

    def _isEqualTrackStructure(self, correct, output):
        self.assertEqual(correct.keys(), output.keys())
        for key, value in correct.items():
            self._isEqualTrackStructure(correct[key], output[key])
            self.assertIsInstance(output, TrackStructureV2)
            if isinstance(correct[key], SingleTrackTS):
                self.assertEqual(correct[key], output[key])

    def testMakeTreeSegregatedByCategory(self):
        # test splitting on a node that has a single category
        singleCategoryOutput = self.inputTree.makeTreeSegregatedByCategory(self.inputTree['A'])
        self._isEqualTrackStructure(singleCategoryOutput, self.splitOnA)

        # test splitting on a node that has multiple categories
        singleCategoryOutput = self.inputTree.makeTreeSegregatedByCategory(self.inputTree['B'])
        self._isEqualTrackStructure(singleCategoryOutput, self.splitOnB)

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
        self.assertItemsEqual(("field 1", "field 2", "field 3"), self.flatTs.getMetadataFields())

    def testGetAllValuesForMetadataField(self):
        self.assertItemsEqual(("value 1", "value 2", "value 3",), self.flatTs.getAllValuesForMetadataField("field 1"))
        self.assertItemsEqual((6,), self.flatTs.getAllValuesForMetadataField("field 2"))
        self.assertItemsEqual((None,), self.flatTs.getAllValuesForMetadataField("field 3"))


if __name__ == "__main__":
    unittest.main()



