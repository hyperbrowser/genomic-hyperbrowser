from collections import OrderedDict

from gold.track.Track import PlainTrack
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.track.TrackStructure import SingleTrackTS, FlatTracksTS
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN


def getSingleTrackTS(genome, guiSelectedTrack, title='Dummy', printProgress = False):

    trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, guiSelectedTrack, printProgress=printProgress)

    return SingleTrackTS(PlainTrack(trackName), {'title':title})


def getFlatTracksTS(genome, guiSelectedGSuite):
    gsuite = getGSuiteFromGalaxyTN(guiSelectedGSuite)

    return _getFlatTracksTS(genome, gsuite)


def _getFlatTracksTS(genome, gsuite):
    ts = FlatTracksTS()
    for gsTrack in gsuite.allTracks():
        track = PlainTrack(gsTrack.trackName)
        metadata = OrderedDict(title=gsTrack.title, genome=str(genome))
        metadata.update(gsTrack.attributes)
        ts[gsTrack.title] = SingleTrackTS(track, metadata)
    return ts


def getFlatTracksTSFromGsuiteObject(genome, gsuite):
    return _getFlatTracksTS(genome, gsuite)
