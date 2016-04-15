#from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.GeneralGuiTool import MultiGeneralGuiTool

from quick.webtools.restricted.ChromCoord import ChromCoord
from quick.webtools.restricted.TrackFileImport import TrackFileImport
from quick.webtools.restricted.TrackFileImport1 import TrackFileImport1
from quick.webtools.restricted.TrackFileImport2 import TrackFileImport2

# This is a template prototyping GUI that comes together with a corresponding
# web page.
##########################################################################
class AbdulrahmansTool1(MultiGeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Test tools Developed by Abdulrahman Azab"
    @staticmethod
    def getSubToolClasses():
        return [ChromCoord,TrackFileImport1]
#########################################################################
#
#


