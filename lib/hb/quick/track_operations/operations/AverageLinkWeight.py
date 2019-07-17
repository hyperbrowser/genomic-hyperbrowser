
from collections import OrderedDict

from gold.track.TrackFormat import TrackFormatReq

from quick.track_operations.raw_operations.AverageLinkWeight import \
    averageLinkWeight

from quick.track_operations.operations.Operator import Operator
from quick.track_operations.operations.Operator import KwArgumentInfo

class AverageLinkWeight(Operator):
    """
    Find the average weight of the links in a track.
    """

    _trackHelpList = ['Track to find the average link weight on']
    _operationHelp = "Find the average link weight of a track"
    _numTracks = 1
    _resultIsTrack = False
    # TODO: Add a requirement for weight and support multiple types..
    _trackRequirements = [TrackFormatReq(linked=True)]

    def _calculate(self, region, tv):
        weights = tv.weightsAsNumpyArray()
        ret = averageLinkWeight(weights, self._customAverageFunction)
        return ret

    @classmethod
    def _getKwArgumentInfoDict(cls):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('customAverageFunction',
             KwArgumentInfo('customAverageFunction','c',
                            'Use a custom average function', None, None))])
