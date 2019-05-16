import urllib2

from gold.gsuite.GSuiteEditor import concatenateGSuitesAddingCategories
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

        gSuiteList = [getGSuiteFromGalaxyTN(galaxyTn) for galaxyTn in \
                      cls._getSelectedGsuiteGalaxyTNsInOrder(choices)]

        if choices.categorize == 'No':
            concatenatedGSuite = concatenateGSuites(gSuiteList)
        else:
            categoryList = [getattr(choices, 'categoryEntry%s' % i).strip().encode('utf-8')
                            for i in xrange(len(gSuiteList))]
            concatenatedGSuite = concatenateGSuitesAddingCategories(gSuiteList, choices.columnTitle, categoryList)

        composeToFile(concatenatedGSuite, galaxyFn)