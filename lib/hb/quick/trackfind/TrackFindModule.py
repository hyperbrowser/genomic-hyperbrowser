
import requests

from proto.hyperbrowser.StaticFile import StaticFile
from gold.gsuite import GSuiteParser


class TrackFindModule:
    #URL = 'http://insilico.hpc.uio.no:8888/api/v1/'
    URL = 'http://158.39.77.99/api/v1/'

    def __init__(self):
        pass

    def getRepositories(self):
        url = self.URL + 'providers'

        response = requests.get(url)

        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getAttributesForRepository(self, repository):
        url = self.URL + repository + '/attributes?raw=true'

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getTopLevelAttributesForRepository(self, repository):
        url = self.URL + repository + '/attributes?raw=true&top=true'

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getSubLevelAttributesForRepository(self, repository, attribute):
        url = self.URL + repository + '/' + attribute + '/subattributes?raw=true'

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getAttributeValues(self, repository, attribute, searchTerm=''):
        url = self.URL + repository + '/' + attribute + '/values?raw=true'

        if searchTerm:
            url += '&filter=' + searchTerm

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getData(self, repository, attrValueMap):
        query = self.createQuery(attrValueMap)

        url = self.URL + repository + '/search?query=' + query #+ '&limit=10'

        response = requests.get(url)

        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getGSuite(self, repository, attrValueMap):

        self.logRequest("getting gsuite \n")

        filepath = StaticFile(
            ['files', 'trackfind', 'trackfind-export-example.gsuite']).getDiskPath()
        gsuite = GSuiteParser.parse(filepath)

        return gsuite

    def createQuery(self, attrValueMap):
        queryList = []

        for attribute, value in attrValueMap.iteritems():
            queryPart = 'curated_content->' + attribute
            if type(value) is list:
                queryPart += ' IN (' + (', '.join("'{0}'".format(v) for v in value)) + ')'
            else:
                queryPart += ' = ' + "'{}'".format(value)

            queryList.append('->>'.join(queryPart.rsplit('->', 1)))

        query = (' AND '.join(queryList))

        return query

    def logRequest(self, url, time = 0):
        logfile = open("apilog", "a")

        logfile.write(str(time) + '   ' + url + '\n')

        logfile.close()

