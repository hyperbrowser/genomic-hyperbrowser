
import urllib

import requests

from gold.gsuite import GSuiteParser


class TrackFindModule(object):
    URL = 'http://158.37.63.104/api/v1'

    STANDARD_CATEGORIES = 'experiments,studies,samples,tracks'

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

    def getMetamodelForRepository(self, repoAndHub):
        repo, hub = self.getRepoAndHub(repoAndHub)
        url = self.URL + '/metamodel/' + repo + '/' + hub + '?flat=true'

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getTopLevelAttributesForRepository(self, repoAndHub):
        repo, hub = self.getRepoAndHub(repoAndHub)
        url = self.URL + '/categories/' + repo + '/' + hub

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getSubLevelAttributesForRepository(self, repoAndHub, path):
        repo, hub = self.getRepoAndHub(repoAndHub)
        if '->' in path:
            category, path = path.split('->', 1)
            url = self.URL + '/attributes/' + repo + '/' + hub + '/' + category + '?path=' + path
        else:
            url = self.URL + '/attributes/' + repo + '/' + hub + '/' + path

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getAttributeValues(self, repoAndHub, path, searchTerm=''):
        repo, hub = self.getRepoAndHub(repoAndHub)
        if '->' in path:
            category, path = path.split('->', 1)
            url = self.URL + '/values/' + repo + '/' + hub + '/' + category + '?path=' + path
        else:
            url = self.URL + '/values/' + repo + '/' + hub + '/' + path

        if searchTerm:
            url += '&filter=' + searchTerm

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getJsonData(self, repoAndHub, attrValueMap):
        repo, hub = self.getRepoAndHub(repoAndHub)
        headers = {'Accept': 'application/json'}

        self.logRequest('json', 0)
        response = self.getData(repo, hub, attrValueMap, headers)

        return response.json()

    def getGSuite(self, repoAndHub, attrValueMap, includeExtraAttributes=False):
        repo, hub = self.getRepoAndHub(repoAndHub)
        headers = {'Accept': 'text/plain'}

        self.logRequest('gsuite', 0)
        response = self.getData(repo, hub, attrValueMap, headers, includeExtraAttributes)

        gsuite = GSuiteParser.parseFromString(response.text)

        return gsuite

    def getData(self, repo, hub, attrValueMap, headers, includeExtraAttributes=False):
        query = self.createQuery(attrValueMap)

        url = self.URL + '/search/' + repo + '/' + hub + '?query=' + query

        if not includeExtraAttributes:
            url += '&categories=' + urllib.quote(self.STANDARD_CATEGORIES)

        response = requests.get(url, headers=headers)

        self.logRequest(url, response.elapsed.total_seconds())

        return response

    def createQuery(self, attrValueMap):
        queryList = []
        #self.logRequest(str(attrValueMap), 0)

        for attribute, value in attrValueMap.iteritems():
            queryPart = attribute
            if type(value) is list:
                queryPart += urllib.quote('?| array[' + (', '.join("'{0}'".format(v) for v in value)) + ']')
            else:
                queryPart += '?' + "'{}'".format(urllib.quote(value))

            queryList.append(queryPart)

        query = (' AND '.join(queryList))

        return query

    def logRequest(self, url, time = 0):
        # logfile = open("apilog", "a", 0)
        #
        # logfile.write(str(time) + '   ' + url + '\n')
        #
        # logfile.close()
        pass

    def getRepoAndHub(self, repoHub):
        return repoHub.split(' - ')



