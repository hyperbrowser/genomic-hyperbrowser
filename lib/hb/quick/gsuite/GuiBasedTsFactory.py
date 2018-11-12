from collections import OrderedDict

from gold.track.Track import PlainTrack
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.track.TrackStructure import SingleTrackTS, FlatTracksTS
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN


def getSingleTrackTS(genome, guiSelectedTrack, title='Dummy'):
    trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, guiSelectedTrack)
    return SingleTrackTS(PlainTrack(trackName), {'title': title})


def getFlatTracksTS(genome, guiSelectedGSuite):
    ts = FlatTracksTS()
    gsuite = getGSuiteFromGalaxyTN(guiSelectedGSuite)

    for gsTrack in gsuite.allTracks():
        assert gsTrack.trackName is not None, "Gstrack name is None %s" % gsTrack
        track = PlainTrack(gsTrack.trackName)
        metadata = OrderedDict(title=gsTrack.title, genome=str(genome))
        metadata.update(gsTrack.attributes)
        assert track is not None
        assert metadata is not None
        ts[gsTrack.title] = SingleTrackTS(track, metadata)
    return ts
