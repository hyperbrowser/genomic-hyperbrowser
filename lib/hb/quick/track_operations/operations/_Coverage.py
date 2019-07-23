from collections import OrderedDict

from gold.track.TrackFormat import TrackFormatReq

from quick.track_operations.raw_operations.Coverage import coverage

from quick.track_operations.operations.Operator import Operator
from quick.track_operations.operations.Operator import KwArgumentInfo


class Coverage(Operator):

    _trackHelpList = ['Track to be calculated coverage for']
    _operationHelp = "Find the coverage of a track"
    _numTracks = 1
    _resultIsTrack = False
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        return coverage(starts, ends)

    @classmethod
    def _getKwArgumentInfoDict(cls):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', False, 'Print debug info', bool, False)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap',False,
                            'Allow overlap in the result track.', bool,
                            False)),
            ('total',
             KwArgumentInfo('total', False,
                            'Sum the coverage for all regions',
                            bool, False))])

    def printResult(self):
        """
        :return:
        """
        if self._result is not None:
            print(self._result)
        else:
            print("ERROR! Calculation not run!")
