import sys
from gold.application.GalaxyInterface import GalaxyInterface
from collections import OrderedDict
from proto.hyper_gui import *
from proto.BaseToolController import *

class HyperBrowserToolController(BaseToolController):

    def getTrackElement(self, id, label, history=False, ucsc=False, tracks=None):
        datasets = []
        if history:
            try:
                datasets = self.galaxy.getHistory(GalaxyInterface.getSupportedGalaxyFileFormats())
            except Exception, e:
                print e
        element = TrackWrapper(id, GalaxyInterface, [], self.galaxy, datasets, self.getGenome(), ucscTracks=ucsc)
        if tracks is not None:
            element.tracks = tracks
        else:
            element.fetchTracks()
        element.legend = label
        return element
