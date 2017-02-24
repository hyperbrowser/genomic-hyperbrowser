from proto.ProtoToolRegister import getProtoToolList
from proto.config.Config import PROTO_TOOL_DIR
from proto.tools.GeneralGuiTool import MultiGeneralGuiTool


class ExploreToolsTool(MultiGeneralGuiTool):
    # For subclass override
    TOOL_DIR = PROTO_TOOL_DIR

    @staticmethod
    def getToolName():
        return "ProTo tool explorer"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select tool -----"

    @staticmethod
    def useSubToolPrefix():
        return True

    @classmethod
    def getSubToolClasses(cls):
        tool_list = getProtoToolList(toolDir=cls.TOOL_DIR)[1]
        return sorted(tool_list, key=lambda c: c.__module__)

    @staticmethod
    def getToolDescription():
        from proto.HtmlCore import HtmlCore
        core = HtmlCore()
        core.smallHeader("General description")
        core.paragraph("This tool is used to try out ProTo tools that have "
                       "not been installed as separate tools in the tool "
                       "menu. This is typically used for development "
                       "purposes, so that one can polish the tool until it"
                       "is finished for deployment in the tool menu. "
                       "When a tool is installed into the menu, the tool "
                       "disappears from the tool list in this tool."
                       "The logic for inclusion in the list is that there "
                       "exists a Python module with a class that inherits "
                       "from GeneralGuiTool, without there existing "
                       "a Galaxy xml file for the tool.")
        return str(core)
