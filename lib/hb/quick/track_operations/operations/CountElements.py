from collections import OrderedDict

from gtrackcore.track.format.TrackFormat import TrackFormatReq

from quick.track_operations.raw_operations.CountElements import \
    countElements

from quick.track_operations.operations.Operator import Operator
from quick.track_operations.operations.Operator import KwArgumentInfo

class CountElements(Operator):

    _trackHelpList = ['Track to be count elements on']
    _operationHelp = "Count number of elements in each region of a track"
    _numTracks = 1
    _resultIsTrack = False
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()

        nr = countElements(starts, ends)
        return nr

    @classmethod
    def _getKwArgumentInfoDict(self):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap','o',
                            'Allow overlap in the result track.', bool,
                            False)),
            ('total',
             KwArgumentInfo('total', 't',
                            'Sum the coverage for all regions',
                            bool, False))])
