from collections import OrderedDict

from gold.track.Track import PlainTrack
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.track.TrackStructure import SingleTrackTS, MultipleTracksTS
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN


def getSingleTrackTS(genome, guiSelectedTrack, title='Dummy'):

    track = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, guiSelectedTrack)
    return SingleTrackTS(track, {'title':title})

def getMultipleTracksTS(genome, guiSelectedGSuite):
    ts = MultipleTracksTS()
    gsuite = getGSuiteFromGalaxyTN(guiSelectedGSuite)
    for gsTrack in gsuite.allTracks():
        track = PlainTrack(gsTrack.trackName)
        metadata = OrderedDict(title=gsTrack.title, genome=genome)
        metadata.update(gsTrack.attributes)
        ts[gsTrack.title] = SingleTrackTS(track, metadata)
    return ts
