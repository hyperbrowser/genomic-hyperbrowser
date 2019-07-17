
import logging

from collections import OrderedDict
from collections import namedtuple

from gtrackcore.track.core.TrackView import TrackView
from gold.track.TrackFormat import TrackFormat
from gold.track.TrackFormat import TrackFormatReq

from quick.track_operations.operations.Operator import Operator
from quick.track_operations.operations.Operator import KwArgumentInfo

from quick.track_operations.operations.Merge import Merge

from quick.track_operations.raw_operations.Flank import flank

class Flank(Operator):
    """
    Creates a new track of flanking segments.
    """
    _trackHelpList = ['Track to create flank track from']
    _operationHelp = "Create a flanking track from a given track"
    _numTracks = 1
    _resultIsTrack = True
    _trackRequirements = [TrackFormatReq(dense=False)]

    def _calculate(self, region, tv):
        # Remove RawOperationsContent
        logging.debug("Start call! region:{0}".format(region))
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        strands = tv.strandsAsNumpyArray()

        if self._useStrands:
            if strands is None or strands.size == 0:
                # Track has no strand information, ignoring strands.
                self._useStrands = False

        # Get region size.
        regionSize = len(region)

        print("useStrands: {}".format(self._useStrands))

        ret = flank(starts, ends, regionSize, strands=strands,
                    downstream=self._downstream, upstream=self._upstream,
                    both=self._both, useStrands=self._useStrands,
                    useFraction=self._useFraction,
                    treatMissingAsNegative=self._treatMissingAsNegative,
                    debug=self._debug)

        if ret is not None and len(ret[0]) != 0:
            assert len(ret) == 3
            # We do not care about info from the base track..
            # the new track will only contain starts, ends and (strands if
            # present.

            starts = ret[0]
            ends = ret[1]
            strands = ret[2]

            if self._debug:
                print("------------------")
                print("res _calculate")
                print("starts: {}".format(starts))
                print("ends: {}".format(ends))
                print("strands: {}".format(strands))
                print("------------------")

            tv = TrackView(region, starts, ends, None, strands, None,
                           None, None, borderHandling='crop',
                           allowOverlaps=True)
            return tv
        else:
            return None

    def _postCalculation(self):
        if not self._resultAllowOverlap:
            track = self._result
            # Overlap not allowed in the result. Using merge to remove it
            m = Merge(track, useStrands=self._useStrands,
                      treatMissingAsNegative=self._treatMissingAsNegative)
            res = m.calculate()
            self._result = res

    def _setResultTrackFormat(self):
        """
        Create the correct TrackFormat for the output track.
        TODO, do this dynamic
        :return:
        """
        self._resultTrackFormat = TrackFormat(startList=[], endList=[])

    @classmethod
    def _getKwArgumentInfoDict(cls):
        return OrderedDict([
            ('both',
             KwArgumentInfo('both', 'b', 'Creating flank in both directions.',
                            float, None)),
            ('upstream',
             KwArgumentInfo('upstream', 'u',
                            'Size of the upstream flank. In number of base '
                            'pairs', float, None)),
            ('downstream',
             KwArgumentInfo('downstream', 'w',
                            'Size of the downstream flank. In number of base '
                            'pairs', float, None)),
            ('resultAllowOverlap',
             KwArgumentInfo('resultAllowOverlap','o',
                            'Allow overlap in the result track.', bool,
                            False)),
            ('useFraction',
             KwArgumentInfo('useFraction', 'f',
                            'Interpret flak size as a fraction of the '
                            'element size', bool, False)),
            ('useStrands',
             KwArgumentInfo('useStrands', 's', 'Follow the strand direction',
                            bool, True)),
            ('treatMissingAsNegative',
             KwArgumentInfo('treatMissingAsNegative', 'n',
                            'Treat any missing strand as if they are '
                            'negative. The default is to treat them as positive',
                            bool, False)),
            ('debug',
             KwArgumentInfo('debug', 'd', 'Print debug info', bool, False))
            ])
