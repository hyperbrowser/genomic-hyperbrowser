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
from gold.track.TrackStructure import MultipleTracksTS




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

    def testMakeTreeSegregatedByCategory(self):
        # TODO Lonneke; clean up & investigate border cases
        st1 = SingleTrackTS(Track('1'), dict())
        st2 = SingleTrackTS(Track('2'), dict())
        st3 = SingleTrackTS(Track('3'), dict())
        st4 = SingleTrackTS(Track('4'), dict())

        root = MultipleTracksTS()
        root['A1'] = MultipleTracksTS()
        root['A1']['B1'] = st1
        root['A1']['B2'] = st2
        root['A2'] = MultipleTracksTS()
        root['A2']['B3'] = st3
        root['A2']['B4'] = st4

        correctOutput = MultipleTracksTS()
        correctOutput['B1'] = MultipleTracksTS()
        correctOutput['B1']['A1'] = st1
        correctOutput['B1']['A2'] = MultipleTracksTS()
        correctOutput['B1']['A2']['B3'] = st3
        correctOutput['B1']['A2']['B4'] = st4
        correctOutput['B2'] = MultipleTracksTS()
        correctOutput['B2']['A1'] = st2
        correctOutput['B2']['A2'] = MultipleTracksTS()
        correctOutput['B2']['A2']['B3'] = st3
        correctOutput['B2']['A2']['B4'] = st4

        realOutput = root.makeTreeSegregatedByCategory(root['A1'])
        self._isEqualTrackStructure(correctOutput, realOutput)





if __name__ == "__main__":
    unittest.main()



