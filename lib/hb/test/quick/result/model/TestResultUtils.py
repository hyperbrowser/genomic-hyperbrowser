from gold.track.Track import Track
from gold.track.TrackStructure import TrackStructureV2, FlatTracksTS, SingleTrackTS
from quick.result.model.ResultUtils import getTrackTitleToResultDictFromFlatPairedTrackStructure
from test.util.Asserts import TestCaseWithImprovedAsserts
from mock import MagicMock as Mock

class TestResultUtils(TestCaseWithImprovedAsserts):

    def setUp(self):

        stsRef1 = SingleTrackTS(Mock(spec=Track), dict(title="trackA"))

        ts1 = FlatTracksTS()
        ts1["reference"] = stsRef1
        ts1.result = 0.5
        ts1["query"] = Mock(spec=SingleTrackTS)

        stsRef2 = SingleTrackTS(Mock(spec=Track), dict(title="trackB"))

        ts2 = FlatTracksTS()
        ts2["reference"] = stsRef2
        ts2.result = 1.2
        ts2["query"] = Mock(spec=SingleTrackTS)

        self.resultTS = TrackStructureV2()
        self.resultTS['0'] = ts1
        self.resultTS['1'] = ts2


    def test_getTrackTitleToResultDictFromFlatPairedTrackStructure(self):
        expectedResultDict = dict(trackA=0.5, trackB=1.2)
        resDict = getTrackTitleToResultDictFromFlatPairedTrackStructure(self.resultTS)

        self.assertDictEqual(expectedResultDict, resDict)


if __name__ == '__main__':
    TestCaseWithImprovedAsserts.main()