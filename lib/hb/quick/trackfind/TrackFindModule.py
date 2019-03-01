
import requests

from proto.hyperbrowser.StaticFile import StaticFile
from gold.gsuite import GSuiteParser


class TrackFindModule:
    #URL = 'http://insilico.hpc.uio.no:8888/api/v1/'
    URL = 'http://158.37.63.104/api/v1/'

    def __init__(self):
        pass

    def getRepositories(self):
        url = self.URL + 'hubs?active=true'

        response = requests.get(url)

        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getAttributesForRepository(self, repository):
        repo, hub = self.getRepoAndHub(repository)
        url = self.URL + '/' + repo + '/' + hub + '/attributes?raw=true'

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getTopLevelAttributesForRepository(self, repository):
        repo, hub = self.getRepoAndHub(repository)
        url = self.URL + '/' + repo + '/' + hub + '/attributes?raw=true&top=true'

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getSubLevelAttributesForRepository(self, repository, attribute):
        repo, hub = self.getRepoAndHub(repository)
        url = self.URL + '/' + repo + '/' + hub + '/' + attribute + '/subattributes?raw=true'

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getAttributeValues(self, repository, attribute, searchTerm=''):
        repo, hub = self.getRepoAndHub(repository)
        url = self.URL + '/' + repo + '/' + hub + '/' + attribute + '/values?raw=true'

        if searchTerm:
            url += '&filter=' + searchTerm

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getJsonData(self, repository, attrValueMap):
        headers = {'Accept': 'application/json'}

        response = self.getData(repository, attrValueMap, headers)

        return response.json()

    def getGSuite(self, repository, attrValueMap):
        headers = {'Accept': 'text/plain'}

        response = self.getData(repository, attrValueMap, headers)

        gsuite = GSuiteParser.parseFromString(response.text)

        return gsuite

    def getData(self, repository, attrValueMap, headers):
        repo, hub = self.getRepoAndHub(repository)
        query = self.createQuery(attrValueMap)

        url = self.URL + '/' + repo + '/' + hub + '/search?query=' + query + '&limit=10'

        response = requests.get(url, headers=headers)

        self.logRequest(url, response.elapsed.total_seconds())

        return response

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
        # logfile = open("apilog", "a", 0)

        # logfile.write(str(time) + '   ' + url + '\n')

        # logfile.close()
        pass

    def getRepoAndHub(self, repository):
        repo, hub = [s.strip() for s in repository.split('-')]

        return repo, hub


