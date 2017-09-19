from collections import OrderedDict

from gold.track.Track import PlainTrack
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.track.TrackStructure import SingleTrackTS, FlatTracksTS
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN


def getSingleTrackTS(genome, guiSelectedTrack, title='Dummy'):

    trackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, guiSelectedTrack)

    return SingleTrackTS(PlainTrack(trackName), {'title':title})

def getFlatTracksTS(genome, guiSelectedGSuite):
    ts = FlatTracksTS()
    gsuite = getGSuiteFromGalaxyTN(guiSelectedGSuite)
    for gsTrack in gsuite.allTracks():
        track = PlainTrack(gsTrack.trackName)
        metadata = OrderedDict(title=gsTrack.title, genome=str(genome))
        metadata.update(gsTrack.attributes)
        ts[gsTrack.title] = SingleTrackTS(track, metadata)
    return ts
