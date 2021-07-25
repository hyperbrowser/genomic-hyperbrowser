from gold.application.GalaxyInterface import GalaxyInterface
from gold.application.LogSetup import usageAndErrorLogging, logException
from proto.hyperbrowser.StaticFile import StaticImage
from proto.hyperbrowser.hyper_gui import TrackWrapper


class HyperBrowserControllerMixin(object):
    STATIC_IMAGE_CLS = StaticImage

    def _init(self):
        if hasattr(super(HyperBrowserControllerMixin, self), '_init'):
            super(HyperBrowserControllerMixin, self)._init()

        self.trackElements = {}
        self.batchline = ''

    @usageAndErrorLogging
    def _executeTool(self, toolClassName, choices, galaxyFn, username):
        if hasattr(super(HyperBrowserControllerMixin, self), '_executeTool'):
            super(HyperBrowserControllerMixin, self)._executeTool(
                toolClassName, choices, galaxyFn, username)

    def getInputValueForTrack(self, id, name, fileTree='preprocessed'):
        assert fileTree in ['preprocessed', 'standardized', 'collected', 'parsing error', 'preprocessed_history']
        try:
            # assert False
            cachedTracks = self.getCacheData(id)
            track = self.getTrackElement(id, name, fileTree=fileTree, tracks=cachedTracks)
        except:
            print 'track cache is empty'
            track = self.getTrackElement(id, name, fileTree=fileTree)
            self.putCacheData(id, track.tracks)

        self.trackElements[id] = track
        tn = track.definition(False)
        GalaxyInterface.cleanUpTrackName(tn)
        val = ':'.join(tn)
        # val = track.asString()
        return val

    def decodeChoice(self, opts, id, choice):
        if opts == '__track__':
            tn = str(choice).split(':')
            GalaxyInterface.cleanUpTrackName(tn)
            choice = ':'.join(tn)
        else:
            choice = super(HyperBrowserControllerMixin, self).decodeChoice(opts, id, choice)
        return choice

    def getBatchLine(self):
        if len(self.subClasses) == 0 and self.prototype.isBatchTool():
            self.batchline = '$Tool[%s](%s)' % (self.toolId, '|'.join([repr(c) for c in self.choices]))
            return self.batchline
        return None

    def _getAllGenomes(self):
        return [('----- Select -----', '', False)] + GalaxyInterface.getAllGenomes(self.galaxy.getUserName())
        
    def getTrackElement(self, id, label, fileTree='preprocessed', tracks=None):
        assert fileTree in ['preprocessed', 'standardized', 'collected', 'parsing error', 'preprocessed_history']
        datasets = []
        if fileTree == 'preprocessed_history':
            try:
                datasets = self.galaxy.getHistory(GalaxyInterface.getSupportedGalaxyFileFormats())
            except Exception, e:
                logException(e)
            fileTree = 'preprocessed'
        element = TrackWrapper(id, GalaxyInterface, [], self.galaxy, datasets, self.getGenome(), fileTree=fileTree)
        if tracks is not None:
            element.tracks = tracks
        else:
            element.fetchTracks()
        element.legend = label
        return element

    @staticmethod
    def _getStdOutToHistoryDatatypes():
        return ['html', 'customhtml', 'hbfunction']

