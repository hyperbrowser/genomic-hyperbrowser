
from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from quick.track_operations.raw_operations.AverageLength import \
    averageLength

from quick.track_operations.operations.Operator import Operator
from quick.track_operations.operations.Operator import KwArgumentInfo

class AverageLength(Operator):

    _trackHelpList = ['Track to find the average element length on']
    _operationHelp = "Finds the average length of the elements"
    _numTracks = 1
    _resultIsTrack = False
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        nr = averageLength(starts, ends, self._customAverageFunction)
        return nr

    @classmethod
    def _getKwArgumentInfoDict(cls):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('customAverageFunction',
             KwArgumentInfo('customAverageFunction','c',
                            'Use a custom average function', None, None))])
