from gold.gsuite.GSuiteEditor import addColumnToGSuite
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.gsuite.ConcatenateGSuitesTool import ConcatenateGSuitesTool


class ContacenateTwoOrMoreHGsuitesTool(ConcatenateGSuitesTool):
    @classmethod
    def getToolName(cls):
        return "Concatenate two or more hGsuites"


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        from gold.gsuite.GSuiteEditor import concatenateGSuites
        from gold.gsuite.GSuiteComposer import composeToFile


        gSuiteList = [getGSuiteFromGalaxyTN(galaxyTn) for galaxyTn in \
                      cls._getSelectedGsuiteGalaxyTNsInOrder(choices)]
        for currentGSuite in gSuiteList:
            addColumnToGSuite(currentGSuite, attrName='source', trackTitleToColumnValueDict='NOT DONE YET')

        concatenatedGSuite = concatenateGSuites(gSuiteList)
        composeToFile(concatenatedGSuite, galaxyFn)

