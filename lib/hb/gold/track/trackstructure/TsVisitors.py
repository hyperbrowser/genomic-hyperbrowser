import copy
from abc import ABCMeta

from proto.generictool import getClassName
from third_party.Visitor import Visitor


class TrackStructureVisitor(Visitor):
    __metaclass__ = ABCMeta

    def visitAllNodesAndReturnModifiedCopyOfTS(self, trackStructure, *args, **kwArgs):
        newCopy = copy.copy(trackStructure)
        self.visit(newCopy, *args, **kwArgs)
        for key in newCopy.keys():
            newCopy[key] = self.visitAllNodesAndReturnModifiedCopyOfTS(newCopy[key],
                                                                       *args, **kwArgs)
        return newCopy

    def visitAllNodesWithLevelAndKeyArg(self, trackStructure, level, key, *args, **kwArgs):
        retStr = self.visit(trackStructure, level, key, *args, **kwArgs)
        for key in trackStructure.keys():
            retStr += self.visitAllNodesWithLevelAndKeyArg(trackStructure[key], level+1, key,
                                                           *args, **kwArgs)
        return retStr

    def genericVisit(self, tsNode, *args, **kwArgs):
        pass


class TsSwapOrigWithRandomTracksVisitor(TrackStructureVisitor):
    @staticmethod
    def visitSingleTrackTS(tsNode, randTvProvider, randIndex=0):
        from gold.track.TsBasedRandomizedTrack import TsBasedRandomizedTrack
        from gold.track.RandomizedTrack import OrigTrackWrapper
        assert not isinstance(tsNode.track, OrigTrackWrapper), \
            'Different TrackStructureV2 copies needs to be provided as original and ' \
            'randomized track structures to a TrackViewProvider.'
        tsNode.track = TsBasedRandomizedTrack(tsNode.track, randTvProvider, randIndex)


class TsWrapOrigTracksVisitor(TrackStructureVisitor):
    @staticmethod
    def visitSingleTrackTS(tsNode, trackRandomizer):
        from gold.track.RandomizedTrack import OrigTrackWrapper
        tsNode.track = OrigTrackWrapper(tsNode.track, trackRandomizer)


class TsTreeWriterVisitor(TrackStructureVisitor):
    def genericVisit(self, tsNode, level, key):
        retStr = ' ' * level
        if key:
            retStr += '|_ {}: '.format(key)
        retStr += getClassName(tsNode)
        retStr += '\n'
        return retStr

    def _formatTrack(self, track):
        from gold.track.RandomizedTrack import OrigTrackWrapper
        from gold.track.RandomizedTrack import RandomizedTrack

        if any(isinstance(track, cls) for cls in [OrigTrackWrapper, RandomizedTrack]):
            return '{}({})'.format(getClassName(track), self._formatTrack(track._origTrack))
        else:
            return '{} [{}]'.format(':'.join(track.trackName), track.trackTitle)

    def visitSingleTrackTS(self, tsNode, level, key):
        retStr = self.genericVisit(tsNode, level, key)
        retStr += '{}|_ track: {} {}\n'.format(' ' * (level+1),
                                               self._formatTrack(tsNode.track),
                                               repr(tsNode.metadata))
        return retStr
