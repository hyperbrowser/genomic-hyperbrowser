from collections import OrderedDict

from test.util.Asserts import TestCaseWithImprovedAsserts

class TestGSuiteStatUtils(TestCaseWithImprovedAsserts):

    def setUp(self):
        self._sourceDict = OrderedDict()
        self._sourceDict["Track 1"] = OrderedDict([("stat 1", "1"), ("stat 2", "2"), ("stat 1", "3"), ("stat 2", "4")])
        self._sourceDict["Track 2"] = OrderedDict([("stat 1", "5"), ("stat 2", "6"), ("stat 1", "7"), ("stat 2", "8")])

        self._mockStatToPrettyNameDict = {'stat 1':'pretty stat 1'}


    def test_prettifyKeysInDict(self):
        expectedDict = OrderedDict()
        expectedDict["Track 1"] = OrderedDict([("pretty stat 1", "1"), ("stat 2", "2"), ("pretty stat 1", "3"), ("stat 2", "4")])
        expectedDict["Track 2"] = OrderedDict([("pretty stat 1", "5"), ("stat 2", "6"), ("pretty stat 1", "7"), ("stat 2", "8")])

        from quick.gsuite.GSuiteStatUtils import prettifyKeysInDict
        resDict = prettifyKeysInDict(self._sourceDict, prettyDict=self._mockStatToPrettyNameDict)

        self.assertDictEqual(expectedDict, resDict)


if __name__ == '__main__':
    TestCaseWithImprovedAsserts.main()
