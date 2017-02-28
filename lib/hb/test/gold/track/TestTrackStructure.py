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
    def setUp(self):
        pass

    def _isEqualTrackStructure(self, correct, output):
        self.assertEqual(correct.keys(), output.keys())
        for key, value in correct.items():
            self._isEqualTrackStructure(correct[key], output[key])
            self.assertIsInstance(output, TrackStructureV2)
            if isinstance(correct[key], SingleTrackTS):
                self.assertEqual(correct[key], output[key])

    def _testWithSingleCategory(self):
        # root                    root
        #  / \                      |
        # A   B                     C
        # |   |  split on node B   / \
        # t1  C  -------------->  A   B
        #     |                   |   |
        #     t2                  t1  t2


        t1 = SingleTrackTS(Track('t1'), dict())
        t2 = SingleTrackTS(Track('t2'), dict())

        inputStructure = TrackStructureV2()
        inputStructure['A'] = t1
        inputStructure['B'] =  TrackStructureV2()
        inputStructure['B']['C'] = t2

        correctOutput = TrackStructureV2()
        correctOutput['C'] = TrackStructureV2()
        correctOutput['C']['A'] = t1
        correctOutput['C']['B'] = t2

        realOutput = inputStructure.makeTreeSegregatedByCategory(inputStructure['B'])
        self._isEqualTrackStructure(correctOutput, realOutput)

    def _testWithMultipleCategories(self):
        #  root                         root
        #  /  \                         /  \
        # A    B                       C    D
        # |   / \   split on node B   /\    /\
        # t1 C   D  -------------->  A  B  A  B
        #    |   |                   |  |  |  |
        #    t2  t3                  t1 t2 t1 t3

        t1 = SingleTrackTS(Track('t1'), dict())
        t2 = SingleTrackTS(Track('t2'), dict())
        t3 = SingleTrackTS(Track('t3'), dict())

        inputStructure = TrackStructureV2()
        inputStructure['A'] = t1
        inputStructure['B'] =  TrackStructureV2()
        inputStructure['B']['C'] = t2
        inputStructure['B']['D'] = t3

        correctOutput = TrackStructureV2()
        correctOutput['C'] = TrackStructureV2()
        correctOutput['D'] = TrackStructureV2()
        correctOutput['C']['A'] = t1
        correctOutput['C']['B'] = t2
        correctOutput['D']['A'] = t1
        correctOutput['D']['B'] = t3

        realOutput = inputStructure.makeTreeSegregatedByCategory(inputStructure['B'])
        self._isEqualTrackStructure(correctOutput, realOutput)

    def _testWithWrongInput(self):
        # root
        #  / \
        # A   B  Splitting on node A or B should fail
        # |   |
        # t1  t2

        inputStructure = TrackStructureV2()
        inputStructure['A'] = SingleTrackTS(Track('t1'), dict())
        inputStructure['B'] = SingleTrackTS(Track('t2'), dict())

        with self.assertRaises(AssertionError):
            inputStructure.makeTreeSegregatedByCategory(inputStructure['A'])
            inputStructure.makeTreeSegregatedByCategory(inputStructure['B'])

    def testMakeTreeSegregatedByCategory(self):
        self._testWithSingleCategory()
        self._testWithMultipleCategories()
        self._testWithWrongInput()









if __name__ == "__main__":
    unittest.main()



