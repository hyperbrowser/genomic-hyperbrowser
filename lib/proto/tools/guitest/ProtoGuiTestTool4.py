from proto.tools.GeneralGuiTool import MultiGeneralGuiTool


class ProtoGuiTestTool4(MultiGeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "Multitool: Test tool #4 for Galaxy ProTo GUI"

    @staticmethod
    def getToolSelectionName():
        return "-----  Select ProTo GUI test tool -----"

    @staticmethod
    def getSubToolSelectionTitle():
        return 'Select ProTo GUI test #4 subtool:'

    @classmethod
    def getSubToolClasses(cls):
        """
        Specifies a list of classes for subtools of the main tool. These
        subtools will be selectable from a selection box at the top of the
        page. The input boxes will change according to which subtool is
        selected.

        Optional method. Default return value if method is not defined: None
        """
        from proto.tools.guitest.ProtoGuiTestTool1 import ProtoGuiTestTool1
        from proto.tools.guitest.ProtoGuiTestTool2 import ProtoGuiTestTool2
        from proto.tools.guitest.ProtoGuiTestTool3 import ProtoGuiTestTool3
        return [ProtoGuiTestTool1, ProtoGuiTestTool2, ProtoGuiTestTool3]

    @classmethod
    def isPublic(cls):
        """
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as well as admin
        users, as defined in the galaxy.ini file.

        Optional method. Default return value if method is not defined: False
        """
        return True
