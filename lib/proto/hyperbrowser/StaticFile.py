from proto.StaticFile import StaticFile, StaticImage, PickleStaticFile, RunSpecificPickleFile
from proto.StaticFile import GalaxyRunSpecificFile as ProtoGalaxyRunSpecificFile


class GalaxyRunSpecificFile(ProtoGalaxyRunSpecificFile):
    def getExternalTrackName(self):
        from quick.application.ExternalTrackManager import ExternalTrackManager
        name = ExternalTrackManager.extractNameFromHistoryTN(self._galaxyFn)
        return ExternalTrackManager.createStdTrackName(self.getId(), name)
