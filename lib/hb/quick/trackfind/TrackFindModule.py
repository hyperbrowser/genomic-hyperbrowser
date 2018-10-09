

import requests
import ast


class TrackFindModule:
    #URL = 'http://insilico.hpc.uio.no:8888/api/v1/'
    URL = 'http://158.39.77.99/api/v1/'

    def __init__(self):
        pass

    def getRepositories(self):
        url = self.URL + 'providers'

        response = requests.get(url)

        repos = list(map(str, ast.literal_eval(response.text)))

        return repos

    def getAttributesForRepository(self, repository):
        url = self.URL + repository + '/attributes?raw=true'

        response = requests.get(url)

        attributes = list(map(str, ast.literal_eval(response.text)))

        return attributes

    def getAttributeValues(self, repository, attribute):
        url = self.URL + repository + '/' + attribute + '/values?raw=true'

        response = requests.get(url)

        values = list(map(str, ast.literal_eval(response.text)))

        return values

    def getData(self, repository, attrValueMap):
        query = self.createQuery(attrValueMap)

        print query

        url = self.URL + repository + '/search?query=' + query + '&limit=10'

        response = requests.get(url)

        return response.text, query

    def createQuery(self, attrValueMap):
        queryList = []

        for attribute, value in attrValueMap.iteritems():
            print type(value)
            if type(value) is list:
                queryList.append('curated_content->>' + "'{}'".format(attribute) + ' IN (' + (', '.join("'{0}'".format(v) for v in value)) + ')')
            else:
                queryList.append('curated_content->>' + "'{}'".format(attribute) + ' = ' + "'{}'".format(value))

        print queryList

        query = (' AND '.join(queryList))

        return query

