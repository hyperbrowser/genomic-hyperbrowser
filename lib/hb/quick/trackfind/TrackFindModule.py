

import requests
import ast


class TrackFindModule:
    def __init__(self):
        pass

    def getRepositories(self):
        url = 'http://insilico.hpc.uio.no:8888/api/v1/providers'

        response = requests.get(url)

        repos = list(map(str, ast.literal_eval(response.text)))

        return repos

    def getAttributesForRepository(self, repository):
        url = 'http://insilico.hpc.uio.no:8888/api/v1/' + repository + '/attributes'

        response = requests.get(url)

        attributes = list(map(str, ast.literal_eval(response.text)))

        return attributes

    def getAttributeValues(self, repository, attribute):
        url = 'http://insilico.hpc.uio.no:8888/api/v1/' + repository + '/' + attribute + '/values'

        response = requests.get(url)

        values = list(map(str, ast.literal_eval(response.text)))

        return values

    def getData(self, repository, attribute, value):
        url = 'http://insilico.hpc.uio.no:8888/api/v1/' + repository + '/search?query=' + attribute + ':' + value + '&limit=10'

        response = requests.get(url)

        return response.text

