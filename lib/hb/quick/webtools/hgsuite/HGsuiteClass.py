from quick.application.ExternalTrackManager import ExternalTrackManager
import csv
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
import copy
import itertools
from collections import OrderedDict

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
    def getPossibleColumnsConcatenation(cls, copyHeader, copyHeaderNumbersList):
        groupColumn = OrderedDict()

        for chNum in range(0, len(copyHeader)):
            # check if the columnName has some value for the element
            headerChNum = copyHeader[chNum]
            #     print 'for which element', chNum, copyHeader[chNum]

            # if sum is equal 0 it means that elemnt fits to every of the combination
            if sum(copyHeaderNumbersList[chNum]) > 0:

                if not headerChNum in groupColumn.keys():
                    groupColumn[headerChNum] = []

                for elNum1 in range(0, len(copyHeaderNumbersList)):
                    if elNum1 == chNum:
                        #                 print 'equal for which we count', copyHeaderNumbersList[elNum1]
                        for elNum2 in range(0, len(copyHeaderNumbersList[elNum1])):
                            if chNum == elNum2:
                                groupColumn[headerChNum].append(headerChNum)
                            else:
                                inxEl = copyHeaderNumbersList[elNum1][elNum2]
                                headerInxEl = copyHeader[elNum2]
                                # element need to be equal zero
                                if inxEl == 0:
                                    # if the elment is not in groupColumn
                                    if headerInxEl not in groupColumn[headerChNum]:
                                        groupColumn[headerChNum].append(headerInxEl)
        return groupColumn

    @classmethod
    def checkWhichColumnNeedToBeSplitted(cls, dataCollection, headerSelected):

        print 'headerSelected=' + str(headerSelected)
        print '<br/>','<br/>','<br/>'
        print 'dataCollection=' + str(dataCollection)
        print '<br/>', '<br/>', '<br/>'

        copyHeader = copy.copy(headerSelected)
        copyHeaderNumbersList = cls.getUniqueCombinationOfColumns(copyHeader, dataCollection)
        groupColumn = cls.getPossibleColumnsConcatenation(copyHeader, copyHeaderNumbersList)

        print 'copyHeaderNumbers', copyHeaderNumbersList, '<br/>'




        #response is the list - that one which have the same number need to be separate
        #that one which have different number and it is only one then the columns can be combained




        uniqueValue = list(set(copyHeaderNumbers))

        print 'uniqueValue', '<br/>'

        groupColumn = {}
        groupColumn['different'] = []
        groupColumn['together'] = []
        for uv in uniqueValue:
            if uv != '*':
                uvNum = copyHeaderNumbers.count(uv)
                if uvNum == 1:
                    groupColumn['together'].append(headerSelected[copyHeaderNumbers.index(uv)])
                else:
                    differentList = [i for i, x in enumerate(copyHeaderNumbers) if x == uv]
                    for d in differentList:
                        groupColumn['different'].append(headerSelected[d])
            else:
                groupColumn['different'].append(headerSelected[copyHeaderNumbers.index(uv)])

        #different  - which one need to be separate
        #together - which one can be together
        print 'groupColumn', groupColumn, '<br/>'

        exit()

        return groupColumn

    @classmethod
    def getUniqueCombinationOfColumns(cls, copyHeader, dataCollection):

        uniqueDataCollection = [list(x) if len(list(x)) > 1 else '' for x in
                                set(tuple(x) for x in dataCollection)]
        print 'set', uniqueDataCollection

        copyHeaderNumbers = [0 for i in range(0, len(copyHeader))]
        copyHeaderNumbersList = []

        for ch in copyHeader:
            copyHeaderNumbersList.append([0 for i in range(0, len(copyHeader))])
        for acc in uniqueDataCollection:
            i = 0
            for a in acc:
                if i == 0:
                    indexA = copyHeader.index(a)
                    copyHeaderNumbersList[indexA][indexA] += 1
                else:
                    indexB = copyHeader.index(a)
                    copyHeaderNumbersList[indexA][indexB] += 1
                    copyHeaderNumbersList[indexB][indexA] += 1
                    copyHeaderNumbersList[indexB][indexB] += 1
                i += 1
        return copyHeaderNumbersList

    @classmethod
    def parseCvsFileBasedOnColumsNumber(cls, fileName, colNum):

        headerSelected, dataCollection, separateColumnList = cls.readCsvFile(colNum, fileName)

        if len(separateColumnList) == 0:
            headerMod = ['-'.join(headerSelected)]
            return dataCollection, headerMod
        else:
            #do column separation and support the next category

            #check which column have to be splitted
            groupColumn = cls.checkWhichColumnNeedToBeSplitted(dataCollection, headerSelected)
            cls.readCsvFileWithGroup(colNum, fileName, groupColumn)

            exit()

            #all columns are splitted
            dataCollectionModified = []
            for dcNum in range(0, len(dataCollection)):
                if len(dataCollection[dcNum]) == 1 and dataCollection[dcNum] == [None]:
                    dcmList = []
                    for hsNum in range(0, len(headerSelected)):
                        dcmList.append(None)
                    dataCollectionModified.append(dcmList)
                if len(dataCollection[dcNum]) != len(headerSelected):
                    dataCollectionModified.append(dataCollection[dcNum])
                else:
                    dataCollectionModified.append(cls.checkContains(headerSelected, dataCollection[dcNum]))

            return dataCollection, headerSelected

    @classmethod
    def readCsvFileWithGroup(cls, colNum, fileName, groupColumn):

        headerGroup = []
        dataCollectionGroup = OrderedDict()

        separateColumnList = []
        dataCollection = []
        i = 0
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
            reader = csv.reader(f, delimiter=';')
            for r in reader:
                if i == 0:
                    header = r

                    for g in groupColumn['different']:
                        headerGroup.append(g)
                        if not g in dataCollectionGroup.keys():
                            dataCollectionGroup[g] = []

                    if len(groupColumn['together']) > 0:
                        joinedPartGC = '-'.join(groupColumn['together'])

                        headerGroup.append(joinedPartGC)
                        if not joinedPartGC in dataCollectionGroup.keys():
                            dataCollectionGroup[joinedPartGC] = []
                else:
                    for g in groupColumn['different']:
                        indexG = header.index(g)
                        if r[indexG] == '':
                            dataCollectionGroup[g].append(None)
                        else:
                            dataCollectionGroup[g].append(g)
                    if len(groupColumn['together']) > 0:
                        joinedPartGC = '-'.join(groupColumn['together'])
                        for g in groupColumn['together']:
                            indexG = header.index(g)
                            if r[indexG] == '':
                                dataCollectionGroup[joinedPartGC].append(g)
                                wasTF = True
                        if wasTF == False:
                            dataCollectionGroup[joinedPartGC].append(None)


                i += 1

        for t, i in dataCollectionGroup.iteritems():
            print t, len(i)
        exit()

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
