import urllib
from collections import OrderedDict

from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class JoinTwoTabularFilesBySpecificFieldTool(GeneralGuiTool):
    MAX_NUM_OF_TAB_FILES = 10

    @classmethod
    def getToolName(cls):
        return "Join two tabular files"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select tabular file from history', 'selFile1'),
                ('Select column', 'selCol1'),
                ('Select tabular file from history', 'selFile2'),
                ('Select column', 'selCol2'),
                ('Add information about files to header', 'addHeaderInfo')]

    @classmethod
    def getOptionsBoxSelFile1(cls):
        return GeneralGuiTool.getHistorySelectionElement('tabular')

    @classmethod
    def getOptionsBoxSelCol1(cls, prevChoices):
        if prevChoices.selFile1:
            return cls.returnColFile(prevChoices.selFile1)

    @classmethod
    def getOptionsBoxSelFile2(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('tabular')

    @classmethod
    def getOptionsBoxSelCol2(cls, prevChoices):
        if prevChoices.selFile2 and prevChoices.selCol1!=None:
            return cls.returnColFile(prevChoices.selFile2)

    @classmethod
    def getOptionsBoxAddHeaderInfo(cls, prevChoices):
        return ['yes', 'no']

    @classmethod
    def returnColFile(cls, selFile2):
        with open(ExternalTrackManager.extractFnFromGalaxyTN(selFile2.split(':')),
                  'r') as f:
            header = f.readline()
            header = header.strip('\n').split('\t')
            return [None] + header

    @classmethod
    def openFile(cls, fileName, colName, addHeaderInfo):
        allData = OrderedDict()
        fN = fileName.split(':')
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fN), 'r') as f:
            i=0
            for line in f:
                l = line.strip('\n').split('\t')
                if i == 0:
                    selColNum = l.index(colName)
                    if addHeaderInfo == 'yes':
                        header = [(ll+urllib.unquote(fN[-1])).encode('utf-8') for ll in l]
                    else:
                        header = l
                    inxColName = l.index(colName)

                else:
                    if l != ['']:
                        allData[l[inxColName]] = l
                i+=1
        return header, allData, selColNum

    @classmethod
    def openAllFile(cls, fileName, addHeaderInfo):
        allData = []
        fN = fileName.split(':')
        with open(ExternalTrackManager.extractFnFromGalaxyTN(fN), 'r') as f:
            i = 0
            for line in f:
                l = line.strip('\n').split('\t')
                if i == 0:
                    if addHeaderInfo == 'yes':
                        header = [(ll + urllib.unquote(fN[-1])).encode('utf-8') for ll in l]
                    else:
                        header = l
                else:
                    if l != ['']:
                        allData.append(l)
                i += 1
        return header, allData

    @classmethod
    def combainFiles(cls, allData, header, selCol):
        d = OrderedDict()

        for key in set(allData[0].keys() + allData[1].keys()):
            try:
                d.setdefault(key, []).append(allData[0][key])
            except KeyError:
                lList = [0 for el in header[1]]
                lList[selCol[0]] = key
                d.setdefault(key, []).append(lList)

            try:
                d.setdefault(key, []).append(allData[1][key])
            except KeyError:
                lList = [0 for el in header[0]]
                lList[selCol[1]] = key
                d.setdefault(key, []).append(lList)

        return d


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        selFile1 = choices.selFile1
        selCol1 = choices.selCol1
        selFile2 = choices.selFile2

        addHeaderInfo = choices.addHeaderInfo

        if selCol1 == 'None':
            header1, allData1 = cls.openAllFile(selFile1, addHeaderInfo)
            header2, allData2 = cls.openAllFile(selFile2, addHeaderInfo)

            header=[header1, header2]

            maxLenNum = 0
            minLenNum = 0
            if len(allData1) >= len(allData2):
                maxLenNum = len(allData1)
                minLenNum = len(allData2)
            else:
                maxLenNum = len(allData2)
                minLenNum = len(allData1)


            # header
            hList = []
            for hf in header:
                hList += hf

            outputFile = open(cls.makeHistElement(galaxyExt='tabular', title='combained file'),
                              'w')
            outputFile.write('\t'.join(hList) + '\n')

            for m in range(0, minLenNum):
                allDL = allData1[m] + allData2[m]
                outputFile.write('\t'.join([str(c) for c in allDL]) + '\n')
            for m in range(minLenNum, maxLenNum):
                if len(allData1) >= len(allData2):
                    allDL = allData1[m] + ['' for h in header2]
                else:
                    allDL = ['' for h in header1] + allData2[m]
                outputFile.write('\t'.join([str(c) for c in allDL]) + '\n')

            outputFile.close()

        else:
            selCol1 = selCol1.encode('utf-8')
            selCol2 = choices.selCol2
            selCol2 = selCol2.encode('utf-8')

            header1, allData1, selColNum1 = cls.openFile(selFile1, selCol1, addHeaderInfo)
            header2, allData2, selColNum2 = cls.openFile(selFile2, selCol2, addHeaderInfo)

            header = [header1, header2]
            allData = [allData1, allData2]
            selCol = [selColNum1, selColNum2]

            combainFilesDict = cls.combainFiles(allData, header, selCol)

            #header
            hList = []
            for hf in header:
                hList += hf

            outputFile = open(cls.makeHistElement(galaxyExt='tabular', title='combained file'), 'w')
            outputFile.write('\t'.join(hList) + '\n')

            #rest rows
            for cf in combainFilesDict.itervalues():
                cList = []
                for c in cf:
                    cList += c
                outputFile.write('\t'.join([str(c) for c in cList]) + '\n')

            outputFile.close()









    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     """
    #     Specifies a list of classes for subtools of the main tool. These
    #     subtools will be selectable from a selection box at the top of the
    #     page. The input boxes will change according to which subtool is
    #     selected.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     """
    #     Specifies whether the tool is accessible to all users. If False, the
    #     tool is only accessible to a restricted set of users as well as admin
    #     users, as defined in the galaxy.ini file.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     """
    #     Specifies whether the tool should redirect to an URL when the Execute
    #     button is clicked.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     """
    #     This method is called to return an URL if the isRedirectTool method
    #     returns True.
    #
    #     Mandatory method if isRedirectTool() returns True.
    #     """
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     """
    #     Specifies if a History item should be created when the Execute button
    #     is clicked.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     """
    #     Specifies if this tool could be run from batch using the batch. The
    #     batch run line can be fetched from the info box at the bottom of the
    #     tool.
    #
    #     Optional method. Default return value if method is not defined:
    #         same as isHistoryTool()
    #     """
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     """
    #     Specifies whether changing the content of textboxes causes the page
    #     to reload. Returning False stops the need for reloading the tool
    #     after each input, resulting in less lags for the user.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     """
    #     Specifies a list of input boxes which resets the subsequent stored
    #     choices previously made. The input boxes are specified by index
    #     (starting with 1) or by key.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     """
    #     Specifies a help text in HTML that is displayed below the tool.
    #
    #     Optional method. Default return value if method is not defined: ''
    #     """
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     """
    #     Specifies an id used by StaticFile.py to reference an illustration
    #     file on disk. The id is a list of optional directory names followed
    #     by a filename. The base directory is STATIC_PATH as defined by
    #     Config.py. The full path is created from the base directory
    #     followed by the id.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     """
    #     Specifies an URL to an example page that describes the tool, for
    #     instance a Galaxy page.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     """
    #     Specifies whether the debug mode is turned on. Debug mode is
    #     currently mostly used within the Genomic HyperBrowser and will make
    #     little difference in a plain Galaxy ProTo installation.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     """
    #     The format of the history element with the output of the tool. Note
    #     that if 'html' is returned, any print statements in the execute()
    #     method is printed to the output dataset. For text-based output
    #     (e.g. bed) the output dataset only contains text written to the
    #     galaxyFn file, while all print statements are redirected to the info
    #     field of the history item box.
    #
    #     Note that for 'html' output, standard HTML header and footer code is
    #     added to the output dataset. If one wants to write the complete HTML
    #     page, use the restricted output format 'customhtml' instead.
    #
    #     Optional method. Default return value if method is not defined:
    #     'html'
    #     """
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
    #     """
    #     The title (name) of the main output history element.
    #
    #     Optional method. Default return value if method is not defined:
    #     the name of the tool.
    #     """

    @staticmethod
    def isPublic():
        return True