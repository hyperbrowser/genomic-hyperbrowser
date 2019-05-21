
import requests

from proto.hyperbrowser.StaticFile import StaticFile
from gold.gsuite import GSuiteParser


class TrackFindModule:
    #URL = 'http://insilico.hpc.uio.no:8888/api/v1/'
    URL = 'http://158.37.63.104/api/v1'

    def __init__(self):
        pass

    def getRepositories(self):
        url = self.URL + '/repositories'

        response = requests.get(url)

        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()
    
    def getHubs(self, repository):
        url = self.URL + '/hubs/' + repository

        response = requests.get(url)

        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getAttributesForRepository(self, repo, hub):
        url = self.URL + '/' + repo + '/' + hub + '/attributes?raw=true'

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getTopLevelAttributesForRepository(self, repo, hub):
        url = self.URL + '/categories/' + repo + '/' + hub

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getSubLevelAttributesForRepository(self, repo, hub, category, path):
        if path:
            url = self.URL + '/attributes/' + repo + '/' + hub + '/' + category + '?path=' + path
        else:
            url = self.URL + '/attributes/' + repo + '/' + hub + '/' + category

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getAttributeValues(self, repo, hub, category, path, searchTerm=''):
        if path:
            url = self.URL + '/values/' + repo + '/' + hub + '/' + category + '?path=' + path
        else:
            url = self.URL + '/values/' + repo + '/' + hub + '/' + category

        if searchTerm:
            url += '&filter=' + searchTerm

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getJsonData(self, repo, hub, attrValueMap):
        headers = {'Accept': 'application/json'}

        response = self.getData(repo, hub, attrValueMap, headers)

        return response.json()

    def getGSuite(self, repo, hub, attrValueMap):
        headers = {'Accept': 'text/plain'}

        response = self.getData(repo, hub, attrValueMap, headers)

        gsuite = GSuiteParser.parseFromString(response.text)

        #self.logRequest(str(gsuite))

        return gsuite

    def getData(self, repo, hub, attrValueMap, headers):
        query = self.createQuery(attrValueMap)

        url = self.URL + '/search/' + repo + '/' + hub + '?query=' + query + '&limit=10'

        response = requests.get(url, headers=headers)

        self.logRequest(url, response.elapsed.total_seconds())

        return response

    def createQuery(self, attrValueMap):
        queryList = []

        for attribute, value in attrValueMap.iteritems():
            queryPart = attribute
            if type(value) is list:
                queryPart += ' IN (' + (', '.join("'{0}'".format(v) for v in value)) + ')'
            else:
                queryPart += '?' + "'{}'".format(value)

            queryList.append(queryPart)

        query = (' AND '.join(queryList))

        return query

    def logRequest(self, url, time = 0):
        logfile = open("apilog", "a", 0)

        logfile.write(str(time) + '   ' + url + '\n')

        logfile.close()
        pass



