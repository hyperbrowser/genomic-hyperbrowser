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
    def allCombinations(cls, headerSelected, includingSingleElement=False):
        # all combination of elements in list

        if includingSingleElement == False:
            singleVal = 1
        if includingSingleElement == True:
            singleVal = 0

        allComb = []
        for L in range(0, len(headerSelected) + 1):
            for subset in itertools.combinations(headerSelected, L):
                if len(subset) > singleVal:
                    allComb.append(list(subset))
        return allComb

    @classmethod
    def checkWhichColumnNeedToBeSplitted(cls, dataCollection, headerSelected):
   #
        mapOfPossibleCombinationDict = cls.getMapOfPossibleCombinations(dataCollection, headerSelected)
        # print 'mapOfPossibleCombinationDict', mapOfPossibleCombinationDict, '<br />'
        #
        mapOfPossibleCombinationDescList = cls.getAllPossibilitiesForInitialData(mapOfPossibleCombinationDict, headerSelected)
        # # print 'mapOfPossibleCombinationDescList', mapOfPossibleCombinationDescList, '<br />'
        #
        groupColumn = cls.buildGroupedColumn(mapOfPossibleCombinationDescList, headerSelected)
        # # print 'groupColumn', groupColumn, '<br />'

        return groupColumn

    @classmethod
    def buildGroupedColumn(cls, mapOfPossibleCombinationDescList, headerSelected):

        groupColumn = {}
        groupColumn['single'] = []
        groupColumn['together'] = []
        copyHeaderSelected = copy.copy(headerSelected)

        # addFirstEl
        elM = mapOfPossibleCombinationDescList[0]
        if len(elM) > 1:
            groupColumn['together'].append(elM)
        else:
            groupColumn['single'].append(elM[0])
        whatLeft = list(set(copyHeaderSelected) - set(elM))
        whatLeftComb = sorted(cls.allCombinations(whatLeft, includingSingleElement=True), key=len,
                              reverse=True)
        mapOfPossibleCombinationDescList = [el if len(el) <= len(whatLeft) else '' for el in
                                            mapOfPossibleCombinationDescList]
        # print 'new mapOfPossibleCombinationDescList', mapOfPossibleCombinationDescList

        # groupColum - final collection of data
        # whatLeft - which elements need to be found
        # mapOfPossibleCombinationDescList - possible combinations of elements

        #check the rest of elements
        cls.checkRestPossibilities(groupColumn, whatLeft, whatLeftComb,
                              mapOfPossibleCombinationDescList)

        return groupColumn

    @classmethod
    def checkRestPossibilities(cls, groupColumn, whatLeft, whatLeftComb,
                              mapOfPossibleCombinationDescList):
        #     print 'groupColumn', groupColumn
        #     print 'whatLeft', whatLeft
        #     print 'whatLeftComb', whatLeftComb
        #     print 'mapOfPossibleCombinationDescList', mapOfPossibleCombinationDescList
        for wl1Num in range(0, len(whatLeftComb)):
            #         print '---', wl1Num, whatLeftComb[wl1Num], len(whatLeftComb)
            elWL = whatLeftComb[wl1Num]
            for wl2Num in range(0, len(mapOfPossibleCombinationDescList)):
                elM = mapOfPossibleCombinationDescList[wl2Num]
                if elM != '':
                    if set(elWL) == set(elM):

                        if len(elM) == 1:
                            for elSingleNum in range(wl1Num, len(whatLeftComb)):
                                elNM = whatLeftComb[elSingleNum]
                                if not elNM[0] in groupColumn['single']:
                                    groupColumn['single'].append(elNM[0])
                        else:
                            if len(elM) > 1:
                                if not elM in groupColumn['together']:
                                    groupColumn['together'].append(elM)

                        whatLeft = list(set(whatLeft) - set(elM))

                        if len(whatLeft) > 1:
                            whatLeftComb = sorted(
                                cls.allCombinations(whatLeft, includingSingleElement=True),
                                key=len, reverse=True)
                            mapOfPossibleCombinationDescList = [
                                el if len(el) <= len(whatLeft) else '' for el in
                                mapOfPossibleCombinationDescList]

                            return cls.checkRestPossibilities(groupColumn, whatLeft, whatLeftComb,
                                                         mapOfPossibleCombinationDescList)
                        elif len(whatLeft) == 1:
                            if not whatLeft[0] in groupColumn['single']:
                                groupColumn['single'].append(whatLeft[0])

                        else:
                            return True


        return groupColumn

    @classmethod
    def getAllPossibilitiesForInitialData(cls, mapOfPossibleCombinationDict, headerSelected):


        mapOfPossibleCombinationList = []
        for h in headerSelected:
            allPossibleComb = cls.allCombinations(mapOfPossibleCombinationDict[h]['initialData'])
            for el1Num in range(0, len(allPossibleComb)):
                countIfTheCombIsPossible = 0
                for el2Num in range(0, len(allPossibleComb[el1Num])):
                    singleH = allPossibleComb[el1Num][el2Num]
                    if singleH in mapOfPossibleCombinationDict.keys():
                        intersectedOtherEl = mapOfPossibleCombinationDict[singleH]['initialData']
                        wholeList = allPossibleComb[el1Num]
                        if set(wholeList) == set(intersectedOtherEl).intersection(wholeList):
                            countIfTheCombIsPossible += 1
                    else:
                        countIfTheCombIsPossible += 1

                if countIfTheCombIsPossible == len(allPossibleComb[el1Num]):
                    checkTF = False
                    for mp in mapOfPossibleCombinationList:
                        if set(mp) == set(allPossibleComb[el1Num]):
                            checkTF = True
                    if checkTF == False:
                        mapOfPossibleCombinationList.append(list(set(allPossibleComb[el1Num])))

        mapOfPossibleCombinationDescList = sorted(mapOfPossibleCombinationList, key=len,
                                                  reverse=True) + [[h] for h in headerSelected]

        return mapOfPossibleCombinationDescList

    @classmethod
    def getMapOfPossibleCombinations(cls, dataCollection, headerSelected):
        uniqueDataCollection = [list(x) if len(x) > 1 else '' for x in
                                set(tuple(x) for x in dataCollection)]

        mapOfPossibleCombinationDict = {}
        for h in headerSelected:
            mapOfPossibleCombinationDict[h] = {}
            mapOfPossibleCombinationDict[h]['initialData'] = []

            combainDataForHeaderElement = []
            for el1Num in range(0, len(uniqueDataCollection)):
                el1 = uniqueDataCollection[el1Num]
                if el1 != '' and h in el1:
                    combainDataForHeaderElement = list(set(el1 + combainDataForHeaderElement))

            mapOfPossibleCombinationDict[h]['initialData'] = [h] + list(
                set(headerSelected) - set(combainDataForHeaderElement))

        return mapOfPossibleCombinationDict

    # @classmethod
    # def parseCvsFileBasedOnColumsNumber(cls, fileName, colNum):
    #
    #     headerSelected, dataCollection, separateColumnList = cls.readCsvFile(colNum, fileName)
    #
    #     if len(separateColumnList) == 0:
    #         headerMod = ['-'.join(headerSelected)]
    #
    #         message = 'The selected column consist of data which are fully independent, so all column were merged successfully.'
    #
    #         return dataCollection, headerMod, message
    #     else:
    #         #do column separation and support the next category
    #
    #         #check which column have to be splitted
    #         groupColumn = cls.checkWhichColumnNeedToBeSplitted(dataCollection, headerSelected)
    #         headerGroup, dataCollectionGroup = cls.readCsvFileWithGroup(colNum, fileName, groupColumn)
    #
    #         headerGroupMessage = ', '.join([el for el in headerGroup])
    #         message = 'The selected column consist of data which are not independent, ' \
    #                   'so the following columns (written with " - ") were merged together: ' + str(headerGroupMessage)
    #
    #
    #         return dataCollectionGroup, headerGroup, message

    @classmethod
    def parseGSuiteFileBasedOnColumsNumber(cls, gSuite, colNum):

        headerSelected, dataCollection, separateColumnList, allData = cls.readGSuiteFile(colNum, gSuite)

        if len(separateColumnList) == 0:
            headerMod = ['-'.join(headerSelected)]

            message = 'The selected column consist of data which are fully independent, so all column were merged successfully.'

            return dataCollection, headerMod, message
        else:
            # do column separation and support the next category

            # check which column have to be splitted
            groupColumn = cls.checkWhichColumnNeedToBeSplitted(dataCollection, headerSelected)


            headerGroup, dataCollectionGroup = cls.readGSuiteFileWithGroup(colNum, gSuite,
                                                                        groupColumn, allData, headerSelected)

            headerGroupMessage = ', '.join([el for el in headerGroup])
            message = 'The selected column consist of data which are not independent, ' \
                      'so the following columns (written with " - ") were merged together: ' + str(
                headerGroupMessage)

            return dataCollectionGroup, headerGroup, message


    @classmethod
    def readGSuiteFileWithGroup(cls, colNum, gSuite, groupColumn, allData, headerSelected):

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



        for g in groupColumn['single']:
            headerGroup.append(g)
            if not g in dataCollectionGroup.keys():
                dataCollectionGroup[g] = []

        if len(groupColumn['together']) > 0:
            for gctNum in range(0, len(groupColumn['together'])):
                joinedPartGC = HGsuite.MERGED_SIGN.join(
                    groupColumn['together'][gctNum])

                headerGroup.append(joinedPartGC)
                if not joinedPartGC in dataCollectionGroup.keys():
                    dataCollectionGroup[joinedPartGC] = []


        for r in allData:

            for g in groupColumn['single']:
                indexG = headerSelected.index(g)
                if r[indexG] == None:
                    dataCollectionGroup[g].append(None)
                else:
                    dataCollectionGroup[g].append(g)
            if len(groupColumn['together']) > 0:
                for gctNum in range(0, len(groupColumn['together'])):
                    joinedPartGC = HGsuite.MERGED_SIGN.join(
                        groupColumn['together'][gctNum])
                    for g in groupColumn['together'][gctNum]:
                        indexG = headerSelected.index(g)
                        if r[indexG] == None:
                            dataCollectionGroup[joinedPartGC].append(g)
                            wasTF = True
                    if wasTF == False:
                        dataCollectionGroup[joinedPartGC].append(None)


        # for t, i in dataCollectionGroup.iteritems():
        #     print t, len(i)
        # exit()

        return headerGroup, dataCollectionGroup



    @classmethod
    def readGSuiteFile(cls, colNum, gSuite):

        separateColumnList = []
        dataCollection = []
        i = 0

        allGSuiteAttributes = gSuite.attributes
        headerSelected = [allGSuiteAttributes[c] for c in colNum]

        allAttrVal = []
        for h in headerSelected:
            allAttrValPart = []
            for r in gSuite.getAttributeValueList(h):
                allAttrValPart.append(r)
            allAttrVal.append(allAttrValPart)

        allData = zip(*allAttrVal)

        for r in allData:
            dataCollectionPart = []
            for c in range(0, len(r)):
                if r[c] != None:
                    dataCollectionPart.append(headerSelected[c])

            if len(dataCollectionPart) == 0:
                dataCollectionPart = [None]

            if len(dataCollectionPart) >= 2:
                for dcp in dataCollectionPart:
                    if not dcp in separateColumnList:
                        separateColumnList.append(dcp)

            dataCollection.append(dataCollectionPart)

        return headerSelected, dataCollection, separateColumnList, allData

    # @classmethod
    # def readCsvFile(cls, colNum, gSuite):
    #
    #     separateColumnList = []
    #     dataCollection = []
    #     i = 0
    #     with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
    #         reader = csv.reader(f, delimiter=';')
    #         for r in reader:
    #             if i == 0:
    #                 header = r
    #                 headerSelected = []
    #                 for c in colNum:
    #                     headerSelected.append(header[c])
    #             else:
    #                 dataCollectionPart = []
    #                 for c in colNum:
    #                     if r[c] != '':
    #                         dataCollectionPart.append(header[c])
    #
    #                 if len(dataCollectionPart) == 0:
    #                     dataCollectionPart = [None]
    #
    #                 if len(dataCollectionPart) >= 2:
    #                     for dcp in dataCollectionPart:
    #                         if not dcp in separateColumnList:
    #                             separateColumnList.append(dcp)
    #
    #                 dataCollection.append(dataCollectionPart)
    #             i += 1
    #     return headerSelected, dataCollection, separateColumnList

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
