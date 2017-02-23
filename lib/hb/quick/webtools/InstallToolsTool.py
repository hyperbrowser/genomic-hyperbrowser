from proto.tools.InstallToolsTool import InstallToolsTool as ProtoInstallToolsTool


class InstallToolsTool(ProtoInstallToolsTool):
    @classmethod
    def getOptionsBoxToolType(cls, prevchoices):
        return ['hb', 'proto']
