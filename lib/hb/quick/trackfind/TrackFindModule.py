
import urllib

import requests

from gold.gsuite import GSuiteParser
import datetime

import logging
log = logging.getLogger( __name__ )


class TrackFindModule(object):
    URL = 'http://trackfind.elixir.no/api/v1'

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

    def getCategoriesForRepository(self, repoAndHub):
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

    def getAttributeValues(self, repoAndHub, path, searchTerm='', attrValueMap=None):
        repo, hub = self.getRepoAndHub(repoAndHub)
        if '->' in path:
            category, path = path.split('->', 1)
            url = self.URL + '/values/' + repo + '/' + hub + '/' + category + '?path=' + path
        else:
            url = self.URL + '/values/' + repo + '/' + hub + '/' + path

        if searchTerm:
            if '?' in url:
                url += '&filter=' + searchTerm
            else:
                url += '?filter=' + searchTerm

        if attrValueMap:
            query = self.createQuery(attrValueMap)
            if '?' in url:
                url += '&query=' + query
            else:
                url += '?query=' + query

        response = requests.get(url)
        self.logRequest(url, response.elapsed.total_seconds())

        return response.json()

    def getGSuite(self, repoAndHub, attrValueMap, includeExtraAttributes=False, attrFilter=None):
        repo, hub = self.getRepoAndHub(repoAndHub)
        headers = {'Accept': 'text/plain'}

        self.logRequest('gsuite', 0)
        response = self.getSearchResults(repo, hub, attrValueMap, headers, includeExtraAttributes, attrFilter)

        #log.debug('before gsuite parsing ' + str(datetime.datetime.now()))
        gsuite = GSuiteParser.parseFromString(response.text)
        #log.debug('after gsuite parsing ' + str(datetime.datetime.now()))

        return gsuite

    def getSearchResults(self, repo, hub, attrValueMap, headers, includeExtraAttributes=False, attrFilter=None):
        query = self.createQuery(attrValueMap)

        url = self.URL + '/search/' + repo + '/' + hub + '?query=' + query

        if attrFilter:
            attrs = self.convertFilterAttributesToQueryForm(attrFilter)
            url += '&attributes=' + attrs

        if not includeExtraAttributes:
            url += '&categories=' + urllib.quote(self.STANDARD_CATEGORIES)

        response = requests.get(url, headers=headers)

        self.logRequest(url, response.elapsed.total_seconds())

        return response

    @classmethod
    def convertFilterAttributesToQueryForm(cls, attrFilter):
        convertedAttrs = []
        for attrList in attrFilter:
            convertedAttr = [attrList[0] + '.content']
            for attr in attrList[1:]:
                convertedAttr.append("'{}'".format(attr))
            convertedAttrs.append('->'.join(convertedAttr))

        return ','.join(convertedAttrs)



    def createQuery(self, attrValueMap):
        queryList = []

        for attribute, value in attrValueMap.iteritems():
            if value is None:
                continue
            queryPart = attribute
            if type(value) is list:
                queryPart += urllib.quote('?| array[' + (', '.join("'{0}'".format(v) for v in value)) + ']')
            else:
                queryPart += '?' + "'{}'".format(urllib.quote(value))

            queryList.append(queryPart)

        query = (' AND '.join(queryList))

        return query

    def logRequest(self, url, time = 0):
        logfile = open("apilog-new", "a", 0)

        logfile.write(str(time) + '   ' + url + '\n')

        logfile.close()
        pass

    def getRepoAndHub(self, repoHub):
        return repoHub.split(' - ')



