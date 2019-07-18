
from collections import OrderedDict

from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackFormat import TrackFormat

from quick.track_operations.raw_operations.Complement import complement

from quick.track_operations.operations.Operator import Operator
from quick.track_operations.operations.Operator import KwArgumentInfo

from quick.track_operations.operations.Merge import Merge

from quick.track_operations.utils.TrackHandling import \
    createRawResultTrackView

class Complement(Operator):
    """
    Creates a complementing track.
    """

    _trackHelpList = ['Track to create a complement track from']
    _operationHelp = "Create a track that is the complement to the input track"
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False)]

    # By definition there cannot be any overlap.
    _resultAllowOverlaps = False

    def _calculate(self, region, tv):
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()

        if self._useStrands and strands is not None:
            assert strands is not None
        else:
            self._useStrands = False
            strands = None

        # Get genome size.
        regionSize = len(region)
        ret = complement(starts, ends, strands, regionSize,
                         useStrands=self._useStrands,
                         treatMissingAsNegative=self._treatMissingAsNegative)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3
            # We do not care about info from the base track..
            # the new track will only contain the starts and ends

            starts = ret[0]
            ends = ret[1]
            strands = ret[2]
            tv = createRawResultTrackView(None, region, None,
                                          self._resultAllowOverlaps,
                                          newStarts=starts, newEnds=ends,
                                          newStrands=strands)

            return tv
        else:
            return None

    def _postCalculation(self):
        track = self._tracks[0]
        merged = Merge(track, useStrands=self._useStrands,
                       treatMissingAsNegative=self._treatMissingAsNegative,
                       debug=self._debug)
        self._tracks = [merged]

    def _setResultTrackFormat(self):
        """
        Create the correct TrackFormat for the output track.
        :return:
        """
        # The result will always be a segment track.
        self._resultTrackFormat = TrackFormat(strandList=[], endList=[])

    @classmethod
    def getKwArgumentInfoDict(cls):
        return OrderedDict([
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False)),
            ('useStrands',
             KwArgumentInfo('useStrands', 's', 'Follow the strand direction',
                            bool, True)),
            ('treatMissingAsNegative',
             KwArgumentInfo('treatMissingAsNegative', 'n',
                            'Treat any missing strand as if they are '
                            'negative. The default is to treat them as positive',
                            bool, False))])
