from quick.application.ExternalTrackManager import ExternalTrackManager
import csv
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

class HGsuite:

    @classmethod
    def __init__(cls):
        pass

    @classmethod
    def parseCvsFileHeader(cls, fileName):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for r in reader:
                return r

    @classmethod
    def parseCvsAndGetLineNumbers(cls, fileName):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            lineNum = -1 #excluding header
            for r in reader:
                lineNum+=1
        return lineNum

    @classmethod
    def parseGSuiteAndGetLineNumbers(cls, gsuite):
        gsuite = getGSuiteFromGalaxyTN(gsuite)
        return gsuite.numTracks()

    @classmethod
    def parseCvsFileBasedOnColumsNumber(cls, fileName, colNum):

        separateColumnList = []
        dataCollection=[]
        i=0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for r in reader:
                if i==0:
                    header = r
                else:
                    dataCollectionPart=[]
                    for c in colNum:
                        if r[c] != '':
                            h = header[c]
                            dataCollectionPart.append(h)

                    if len(dataCollectionPart) == 0:
                        dataCollectionPart = [None]

                    if len(dataCollectionPart) >= 2:
                        for dcp in dataCollectionPart:
                            if not dcp in separateColumnList:
                                separateColumnList.append(dcp)
                                print separateColumnList, i

                    dataCollection.append(dataCollectionPart)
                i+=1

        print separateColumnList

        if len(separateColumnList) == 0:
            return dataCollection
        else:
            #do column separation
            #return dataCollection
            pass


    @classmethod
    def parseColumnResponse(cls, selectedColumns):

        cols = selectedColumns.strip().split(',')
        colNum = []
        for cc in cols:
            try:
                c = int(cc)
                colNum.append(c-1)
            except:
                for i in range(int(cc.split('-')[0]) -1 , int(cc.split('-')[1])):
                    colNum.append(i)
        return colNum
