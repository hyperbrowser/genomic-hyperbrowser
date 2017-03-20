from quick.application.ExternalTrackManager import ExternalTrackManager
import csv
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
import copy
import itertools
from collections import OrderedDict

class HGsuite:

    MERGED_SIGN = ' - '

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
    def _checkContains(cls, listA, listB):
        diff = set(listA) - set(listB)

        retrunList = []
        for l in listA:
            lTF = False
            for d in diff:
                if d == l:
                    lTF = True
                    dd = d
            if lTF == True:
                retrunList.append(dd)
            else:
                retrunList.append(None)

        return retrunList



    @classmethod
    def checkWhichColumnNeedToBeSplitted(cls, dataCollection, headerSelected):

        uniqueDataCollectionModified = cls.getUniqueCombinationsOfAllColumns(dataCollection)
        print 'uniqueDataCollectionModified', uniqueDataCollectionModified

        uniqueDataCollectionModified = cls.appendAllUniqueColumnsBySingleData(dataCollection, uniqueDataCollectionModified)
        print 'uniqueDataCollectionModified', uniqueDataCollectionModified

        groupColumn = cls.buildGroupedColumn(uniqueDataCollectionModified)
        print 'groupColumn', groupColumn


        exit()

        return groupColumn

    @classmethod
    def buildGroupedColumn(cls, uniqueDataCollectionModified):

        uniqueDataCollectionModifiedDesc = sorted(uniqueDataCollectionModified, key=len)

        groupColumn = {}
        groupColumn['single'] = []
        groupColumn['together'] = []
        partData = []
        for udEl in uniqueDataCollectionModifiedDesc:
            if len(udEl) == 1:
                partData.append(udEl[0])
            else:
                if len(partData) != 0:
                    partData.append(udEl[0])
                    groupColumn['together'].append(partData)
                    count = 1
                    partData = []
                else:
                    count = 0
                for elN in range(count, len(udEl)):
                    groupColumn['single'].append(udEl[elN])

        return groupColumn

    @classmethod
    def appendAllUniqueColumnsBySingleData(cls, dataCollection, uniqueDataCollectionModified):
        uniqueDataCollectionSingle = [list(x) if len(x) == 1 else '' for x in
                                      set(tuple(x) for x in dataCollection)]
        for s in uniqueDataCollectionSingle:
            if s != '' and s[0] != None:
                checkTF = False
                for u in uniqueDataCollectionModified:
                    if s[0] in u:
                        checkTF = True
                if checkTF == False:
                    if not s in uniqueDataCollectionModified:
                        uniqueDataCollectionModified.append(s)
        return uniqueDataCollectionModified

    @classmethod
    def getUniqueCombinationsOfAllColumns(cls, dataCollection):
        uniqueDataCollection = [list(x) if len(x) > 1 else '' for x in
                                set(tuple(x) for x in dataCollection)]
        # print 'uniqueDataCollection', uniqueDataCollection
        # print 'uniqueDataCollectionSingle', uniqueDataCollectionSingle
        uniqueDataCollectionModified = []
        for el1Num in range(0, len(uniqueDataCollection)):
            el1 = uniqueDataCollection[el1Num]

            ll = el1
            llCount = 0
            for el2Num in range(el1Num + 1, len(uniqueDataCollection)):
                el2 = uniqueDataCollection[el2Num]
                if el1 != '' and el2 != '':
                    if len(el1) > 1 and len(el2) > 1:
                        if len(list(set(ll).intersection(el2))) > 0:
                            ll = list(set(ll + el2))
                            uniqueDataCollection[el1Num] = ''
                            uniqueDataCollection[el2Num] = ''
                            llCount += 1

            if len(ll) > 0:
                chTF = False
                for el in uniqueDataCollectionModified:
                    if set(el) == set(ll):
                        chTF = True

                if chTF == False:
                    uniqueDataCollectionModified.append(list(set(ll)))

        return uniqueDataCollectionModified

    @classmethod
    def parseCvsFileBasedOnColumsNumber(cls, fileName, colNum):

        headerSelected, dataCollection, separateColumnList = cls.readCsvFile(colNum, fileName)

        if len(separateColumnList) == 0:
            headerMod = ['-'.join(headerSelected)]

            message = 'The selected column consist of data which are fully independent, so all column were merged successfully.'
            return dataCollection, headerMod, message
        else:
            #do column separation and support the next category

            #check which column have to be splitted
            groupColumn = cls.checkWhichColumnNeedToBeSplitted(dataCollection, headerSelected)
            headerGroup, dataCollectionGroup = cls.readCsvFileWithGroup(colNum, fileName, groupColumn)

            headerGroupMessage = ', '.join([el for el in headerGroup])
            message = 'The selected column consist of data which are not independent, ' \
                      'so the following columns were merged together: ' + str(headerGroupMessage)


            return dataCollectionGroup, headerGroup, message

    @classmethod
    def readCsvFileWithGroup(cls, colNum, fileName, groupColumn):

        headerGroup = []
        dataCollectionGroup = OrderedDict()

        separateColumnList = []
        dataCollection = []
        i = 0

        # groupColumn =
        # {
        # 'single': [['Adult'], ['Primary Immune cells'], ['Fetal']],
        # 'together': [['ES/derived ', 'Brain']]
        # }

        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for r in reader:
                if i == 0:
                    header = r

                    for g in groupColumn['single']:
                        headerGroup.append(g)
                        if not g in dataCollectionGroup.keys():
                            dataCollectionGroup[g] = []

                    if len(groupColumn['together']) > 0:
                        for gctNum in range(0, len(groupColumn['together'])):
                            joinedPartGC = HGsuite.MERGED_SIGN.join(groupColumn['together'][gctNum])

                            headerGroup.append(joinedPartGC)
                            if not joinedPartGC in dataCollectionGroup.keys():
                                dataCollectionGroup[joinedPartGC] = []
                else:
                    for g in groupColumn['single']:
                        indexG = header.index(g)
                        if r[indexG] == '':
                            dataCollectionGroup[g].append(None)
                        else:
                            dataCollectionGroup[g].append(g)
                    if len(groupColumn['together']) > 0:
                        for gctNum in range(0, len(groupColumn['together'])):
                            joinedPartGC = HGsuite.MERGED_SIGN.join(groupColumn['together'][gctNum])
                            for g in groupColumn['together'][gctNum]:
                                indexG = header.index(g)
                                if r[indexG] == '':
                                    dataCollectionGroup[joinedPartGC].append(g)
                                    wasTF = True
                            if wasTF == False:
                                dataCollectionGroup[joinedPartGC].append(None)


                i += 1

        # for t, i in dataCollectionGroup.iteritems():
        #     print t, len(i)
        # exit()

        return headerGroup, dataCollectionGroup

    @classmethod
    def readCsvFile(cls, colNum, fileName):

        separateColumnList = []
        dataCollection = []
        i = 0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for r in reader:
                if i == 0:
                    header = r
                    headerSelected = []
                    for c in colNum:
                        headerSelected.append(header[c])
                else:
                    dataCollectionPart = []
                    for c in colNum:
                        if r[c] != '':
                            dataCollectionPart.append(header[c])

                    if len(dataCollectionPart) == 0:
                        dataCollectionPart = [None]

                    if len(dataCollectionPart) >= 2:
                        for dcp in dataCollectionPart:
                            if not dcp in separateColumnList:
                                separateColumnList.append(dcp)

                    dataCollection.append(dataCollectionPart)
                i += 1
        return headerSelected, dataCollection, separateColumnList

    @classmethod
    def parseColumnResponse(cls, selectedColumns):

        #since the column number were user friendly, now we need to minus 1 everywhere

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
