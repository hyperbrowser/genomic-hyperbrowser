import urllib2

from gold.gsuite.GSuiteEditor import addColumnToGSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack
from quick.multitrack.MultiTrackCommon import getGSuiteFromGSuiteFile
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.gsuite.ConcatenateGSuitesTool import ConcatenateGSuitesTool


class ContacenateTwoOrMoreHGsuitesTool(ConcatenateGSuitesTool):
    @classmethod
    def getToolName(cls):
        return "Concatenate two or more hGsuites with extra source field"


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        from gold.gsuite.GSuiteEditor import concatenateGSuites
        from gold.gsuite.GSuiteComposer import composeToFile

        gSuiteList = []
        for galaxyTn in cls._getSelectedGsuiteGalaxyTNsInOrder(choices):
            currentGSuite = getGSuiteFromGalaxyTN(galaxyTn)
            gSuiteTitle = urllib2.unquote(galaxyTn.split(':')[-1])
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn)
            outGsuite = addColumnToGSuite(currentGSuite, uri, attrName='source', gSuiteTitle=gSuiteTitle)
            gSuiteList.append(outGsuite)

        concatenatedGSuite = concatenateGSuites(gSuiteList)
        composeToFile(concatenatedGSuite, galaxyFn)

