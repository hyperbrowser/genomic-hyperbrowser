from proto.tools.hyperbrowser.GeneralGuiTool import GeneralGuiTool
from quick.webtools.projectsPageTemplate.WelcomePageHtmlFunctions import WelcomePageHtmlFunctions, RgbColors, NecessaryInforForWelcomePage, CreateCss
from config.Config import GALAXY_STATIC_PATH, HB_SOURCE_DATA_BASE_DIR, DATA_FILES_PATH
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from collections import OrderedDict
import os, errno

class CreateTemplateForWelcomePageTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Create template for welcome page"

    @classmethod
    def getInputBoxNames(cls):
        return [('Project title', 'projectTitle'),
                ('Project description', 'projectDesc'),
                ('Project contact information', 'projectContact'),
                ("Project description which will be in the project's list", 'prDesc'),
                ("Project's instance name", 'prInstance'),
                ('Color of template (look below)', 'color'),
                ('Do you want to overwrite content of html code in welcome page (default: yes)', 'saveWelcomePageToHtml'),
                (
                'How many extra tabs do you want to have (you have always 2: Projects lists and About, max 2)',
                'tabsNum'),
                ('Title of tab 1', 'tabTitle1'),
                ('Title of tab 2', 'tabTitle2'),
                ('Title of tab 3', 'tabTitle3'),
                ('How many rows do you want to have in tab 1 (default 1, max 3): ',
                 'selectRowTemplate1'),
                ('Select column number for row 1: ', 'selectRow1ColumnTemplate1'),
                #default tab
                ('Select element 1 for column 1: ', 'selectRow1ColumnTemplate1Col1Element1'),
                ('Select element 1 for column 2: ', 'selectRow1ColumnTemplate1Col2Element1'),
                ('Select element 1 for column 3: ', 'selectRow1ColumnTemplate1Col3Element1'),
                ('Select column number for row 2: ', 'selectRow2ColumnTemplate1'),
                ('Select element 1 for column 1: ', 'selectRow2ColumnTemplate1Col1Element1'),
                ('Select element 1 for column 2: ', 'selectRow2ColumnTemplate1Col2Element1'),
                ('Select element 1 for column 3: ', 'selectRow2ColumnTemplate1Col3Element1'),
                ('Select column number for row 3: ', 'selectRow3ColumnTemplate1'),
                ('Select element 1 for column 1: ', 'selectRow3ColumnTemplate1Col1Element1'),
                ('Select element 1 for column 2: ', 'selectRow3ColumnTemplate1Col2Element1'),
                ('Select element 1 for column 3: ', 'selectRow3ColumnTemplate1Col3Element1'),
                ('How many rows do you want to have in tab 2 (default 1, max 3): ',
                 'selectRowTemplate2'),
                ('Select column number for row 1: ', 'selectRow1ColumnTemplate2'),
                ('Select element 1 for column 1: ', 'selectRow1ColumnTemplate2Col1Element1'),
                ('Select element 1 for column 2: ', 'selectRow1ColumnTemplate2Col2Element1'),
                ('Select element 1 for column 3: ', 'selectRow1ColumnTemplate2Col3Element1'),
                ('Select column number for row 2: ', 'selectRow2ColumnTemplate2'),
                ('Select element 1 for column 1: ', 'selectRow2ColumnTemplate2Col1Element1'),
                ('Select element 1 for column 2: ', 'selectRow2ColumnTemplate2Col2Element1'),
                ('Select element 1 for column 3: ', 'selectRow2ColumnTemplate2Col3Element1'),
                ('Select column number for row 3: ', 'selectRow3ColumnTemplate2'),
                ('Select element 1 for column 1: ', 'selectRow3ColumnTemplate2Col1Element1'),
                ('Select element 1 for column 2: ', 'selectRow3ColumnTemplate2Col2Element1'),
                ('Select element 1 for column 3: ', 'selectRow3ColumnTemplate2Col3Element1'),
                ]

    @classmethod
    def getOptionsBoxProjectTitle(cls):
        return ''

    @classmethod
    def getOptionsBoxProjectDesc(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxProjectContact(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxPrDesc(cls, prevChoices):
        return ''

    @classmethod
    def getOptionsBoxPrInstance(cls, prevChoices):
        return ''

    @classmethod
    def getOptionsBoxColor(cls, prevChoices):
        return ''

    @classmethod
    def getOptionsBoxSaveWelcomePageToHtml(cls, prevChoices):
        return ['yes', 'no']

    @classmethod
    def getOptionsBoxTabsNum(cls, prevChoices):
        return ['1', '2', '3']

    @classmethod
    def getOptionsBoxTabTitle1(cls, prevChoices):
        if int(prevChoices.tabsNum) >=  1:
            return ''

    @classmethod
    def getOptionsBoxTabTitle2(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2:
            return ''

    @classmethod
    def getOptionsBoxTabTitle3(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 3:
            return ''

    #template 1

    @classmethod
    def getOptionsBoxSelectRowTemplate1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1:
            return ['1', '2', '3']

    # row1
    @classmethod
    def getOptionsBoxSelectRow1ColumnTemplate1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >=1:
            return ['1', '2', '3']


    @classmethod
    def getOptionsBoxSelectRow1ColumnTemplate1Col1Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 1 and int(
                prevChoices.selectRow1ColumnTemplate1) >= 1:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow1ColumnTemplate1Col1Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 1 and int(
    #             prevChoices.selectRow1ColumnTemplate1) >= 1:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow1ColumnTemplate1Col2Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 1 and int(
                prevChoices.selectRow1ColumnTemplate1) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow1ColumnTemplate1Col2Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 1 and int(
    #             prevChoices.selectRow1ColumnTemplate1) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow1ColumnTemplate1Col3Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 1 and int(
                prevChoices.selectRow1ColumnTemplate1) >= 3:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow1ColumnTemplate1Col3Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 1 and int(
    #             prevChoices.selectRow1ColumnTemplate1) >= 3:
    #         return GeneralGuiTool.getHistorySelectionElement()

    #row2
    @classmethod
    def getOptionsBoxSelectRow2ColumnTemplate1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >=2:
            return ['1', '2', '3']

    @classmethod
    def getOptionsBoxSelectRow2ColumnTemplate1Col1Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 2 and int(
                prevChoices.selectRow2ColumnTemplate1) >= 1:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow2ColumnTemplate1Col1Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 2 and int(
    #             prevChoices.selectRow2ColumnTemplate1) >= 1:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow2ColumnTemplate1Col2Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 2 and int(
                prevChoices.selectRow2ColumnTemplate1) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow2ColumnTemplate1Col2Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 2 and int(
    #             prevChoices.selectRow2ColumnTemplate1) >= 2:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow2ColumnTemplate1Col3Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 2 and int(
                prevChoices.selectRow2ColumnTemplate1) >= 3:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow2ColumnTemplate1Col3Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 2 and int(
    #             prevChoices.selectRow2ColumnTemplate1) >= 3:
    #         return GeneralGuiTool.getHistorySelectionElement()

    #row 3
    @classmethod
    def getOptionsBoxSelectRow3ColumnTemplate1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >=3:
            return ['1', '2', '3']

    @classmethod
    def getOptionsBoxSelectRow3ColumnTemplate1Col1Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 3 and int(
                prevChoices.selectRow3ColumnTemplate1) >= 1:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow3ColumnTemplate1Col1Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 3 and int(
    #             prevChoices.selectRow3ColumnTemplate1) >= 1:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow3ColumnTemplate1Col2Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 3 and int(
                prevChoices.selectRow3ColumnTemplate1) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow3ColumnTemplate1Col2Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 3 and int(
    #             prevChoices.selectRow3ColumnTemplate1) >= 2:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow3ColumnTemplate1Col3Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 3 and int(
                prevChoices.selectRow3ColumnTemplate1) >= 3:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow3ColumnTemplate1Col3Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 1 and int(prevChoices.selectRowTemplate1) >= 3 and int(
    #             prevChoices.selectRow3ColumnTemplate1) >= 3:
    #         return GeneralGuiTool.getHistorySelectionElement()

    #template 2



    @classmethod
    def getOptionsBoxSelectRowTemplate2(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2:
            return ['1', '2', '3']

    #row 1
    @classmethod
    def getOptionsBoxSelectRow1ColumnTemplate2(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 1:
            return ['1', '2', '3']

    @classmethod
    def getOptionsBoxSelectRow1ColumnTemplate2Col1Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 1 and int(
                prevChoices.selectRow1ColumnTemplate2) >= 1:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow1ColumnTemplate2Col1Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 1 and int(
    #             prevChoices.selectRow1ColumnTemplate2) >= 1:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow1ColumnTemplate2Col2Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 1 and int(
                prevChoices.selectRow1ColumnTemplate2) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow1ColumnTemplate2Col2Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 1 and int(
    #             prevChoices.selectRow1ColumnTemplate2) >= 2:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow1ColumnTemplate2Col3Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 1 and int(
                prevChoices.selectRow1ColumnTemplate2) >= 3:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow1ColumnTemplate2Col3Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 1 and int(
    #             prevChoices.selectRow1ColumnTemplate2) >= 3:
    #         return GeneralGuiTool.getHistorySelectionElement()

    #row 2
    @classmethod
    def getOptionsBoxSelectRow2ColumnTemplate2(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 2:
            return ['1', '2', '3']

    @classmethod
    def getOptionsBoxSelectRow2ColumnTemplate2Col1Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 2 and int(
                prevChoices.selectRow2ColumnTemplate2) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow2ColumnTemplate2Col1Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 2 and int(
    #             prevChoices.selectRow2ColumnTemplate2) >= 2:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow2ColumnTemplate2Col2Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 2 and int(
                prevChoices.selectRow2ColumnTemplate2) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow2ColumnTemplate2Col2Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 2 and int(
    #             prevChoices.selectRow2ColumnTemplate2) >= 2:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow2ColumnTemplate2Col3Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 2 and int(
                prevChoices.selectRow2ColumnTemplate2) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow2ColumnTemplate2Col3Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 2 and int(
    #             prevChoices.selectRow2ColumnTemplate2) >= 2:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow3ColumnTemplate2(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 3:
            return ['1', '2', '3']

    @classmethod
    def getOptionsBoxSelectRow3ColumnTemplate2Col1Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 3 and int(
                prevChoices.selectRow3ColumnTemplate2) >= 1:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow3ColumnTemplate2Col1Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 3 and int(
    #             prevChoices.selectRow3ColumnTemplate2) >= 1:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow3ColumnTemplate2Col2Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 3 and int(
                prevChoices.selectRow3ColumnTemplate2) >= 2:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow3ColumnTemplate2Col2Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 3 and int(
    #             prevChoices.selectRow3ColumnTemplate2) >= 2:
    #         return GeneralGuiTool.getHistorySelectionElement()

    @classmethod
    def getOptionsBoxSelectRow3ColumnTemplate2Col3Element1(cls, prevChoices):
        if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 3 and int(
                prevChoices.selectRow3ColumnTemplate2) >= 3:
            return GeneralGuiTool.getHistorySelectionElement()

    # @classmethod
    # def getOptionsBoxSelectRow3ColumnTemplate2Col3Element2(cls, prevChoices):
    #     if int(prevChoices.tabsNum) >= 2 and int(prevChoices.selectRowTemplate2) >= 3 and int(
    #             prevChoices.selectRow3ColumnTemplate2) >= 3:
    #         return GeneralGuiTool.getHistorySelectionElement()





    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        projectTitle = choices.projectTitle
        projectDesc = choices.projectDesc
        prDesc = choices.prDesc
        prInstance = choices.prInstance
        tabsNum = int(choices.tabsNum)
        colorProject = choices.color
        projectContact = choices.projectContact

        if choices.saveWelcomePageToHtml == 'yes':
            optionForSavingResult = True
        else:
            optionForSavingResult = False


        cls.fillTabsAndBuildWelcomeHTML(choices, projectContact, projectDesc, projectTitle,
                                        tabsNum, prInstance, optionForSavingResult)

        cls.addProjectIntoProjectsList(colorProject, prDesc, prInstance, projectTitle)

        cls.buildCssProjectFile(colorProject)

        nifwp = NecessaryInforForWelcomePage()
        htmlCore = HtmlCore()
        htmlCore.paragraph(nifwp.addInfoAboutRestartingGalaxy())
        htmlCore.paragraph(nifwp.addInfoAboutAddingLineToMakeNewWelcomePageVisibleFOrEveryone())

        print htmlCore

    @classmethod
    def buildCssProjectFile(cls, colorProject):
        colorProjectShade, colorProjectTint = cls.getTintAndShadeColor(colorProject)
        cc = CreateCss(colorProject, colorProjectTint, colorProjectShade)
        pageCss = cc.addCss()
        pathToCssWelcomeProjectFile = GALAXY_STATIC_PATH + '/welcome_project.css'
        with open(pathToCssWelcomeProjectFile, 'w') as f:
            f.write(pageCss)
        f.close()

    @classmethod
    def addProjectIntoProjectsList(cls, colorProject, prDesc, prInstance, projectTitle):

        if prInstance != '':

            pathToWelcomeProjectDescFile = HB_SOURCE_DATA_BASE_DIR + '/' + 'welcome_project_' + str(
                prInstance) + '.txt'

            header = ['Title', 'Description', 'Instance', 'Color']
            desc = [str(projectTitle), str(prDesc), str(prInstance), str(colorProject)]
            with open(pathToWelcomeProjectDescFile, 'w') as f:
                f.write('\t'.join(header) + '\n')
                f.write('\t'.join(desc) + '\n')
            f.close()



            #create a link to welcome_project_PAGE
            file1 = pathToWelcomeProjectDescFile
            file2 = os.path.join(DATA_FILES_PATH, 'projects', 'welcome_project_' + str(
                prInstance) + '.txt')

            try:
                os.symlink(file1, file2)
            except OSError, e:
                if e.errno == errno.EEXIST:
                    os.remove(file2)
                    os.symlink(file1, file2)

    @classmethod
    def fillTabsAndBuildWelcomeHTML(cls, choices, projectContact, projectDesc, projectTitle,
                                    tabsNum, prInstance, optionForSavingResult):
        selectTemplateRow, tabsTitle = cls.getAllDataFromChoicesAndAddToTabs(choices, tabsNum)
        if projectDesc != '':
            projectDesc = cls.openAndReadFile(projectDesc)
        if projectContact != '':
            projectContact = cls.openAndReadFile(projectContact)
        prList = cls.getAllProjects(prInstance)

        wphf = WelcomePageHtmlFunctions(selectTemplateRow, projectTitle, projectDesc,
                                        projectContact, prList)
        page = ''
        page += wphf.pageHeader('welcome_project.css')
        page += wphf.pageBodyStart()
        page += wphf.addTabs(tabsNum, tabsTitle)
        page += wphf.pageBodyAndHtmlEnd()

        if optionForSavingResult == True:
            pathToWelcomeProjectFile = GALAXY_STATIC_PATH + '/welcome_project.html'
            with open(pathToWelcomeProjectFile, 'w') as f:
                f.write(page)
            f.close()

    @classmethod
    def getTintAndShadeColor(cls, colorProject):
        # create lighter and darker colors based on selected colors user
        rc = RgbColors()
        r, g, b = rc.hex_to_rgb(colorProject)
        rT, gT, bT = rc.rgbToTint(r, g, b, 0.3)
        colorProjectTint = rc.rgb_to_hex(rT, gT, bT)
        rS, gS, bS = rc.rgbToShade(r, g, b, 0.4)
        colorProjectShade = rc.rgb_to_hex(rS, gS, bS)
        return colorProjectShade, colorProjectTint

    @classmethod
    def getAllDataFromChoicesAndAddToTabs(cls, choices, tabsNum):
        tabsTitle = []
        selectTemplateRow = OrderedDict()
        if tabsNum >= 1:
            selectTemplateRow[1] = OrderedDict()
            tabsTitle.append(choices.tabTitle1)
            cls.getTemplateRow(choices, selectTemplateRow[1], choices.selectRowTemplate1,
                               choices.selectRow1ColumnTemplate1,
                               choices.selectRow2ColumnTemplate1,
                               choices.selectRow3ColumnTemplate1,
                               choices.selectRow1ColumnTemplate1Col1Element1,
                               choices.selectRow1ColumnTemplate1Col2Element1,
                               choices.selectRow1ColumnTemplate1Col3Element1,
                               choices.selectRow2ColumnTemplate1Col1Element1,
                               choices.selectRow2ColumnTemplate1Col2Element1,
                               choices.selectRow2ColumnTemplate1Col3Element1,
                               choices.selectRow3ColumnTemplate1Col1Element1,
                               choices.selectRow3ColumnTemplate1Col2Element1,
                               choices.selectRow3ColumnTemplate1Col3Element1,
                               )
        if tabsNum >= 2:
            tabsTitle.append(choices.tabTitle2)
            selectTemplateRow[2] = OrderedDict()
            cls.getTemplateRow(choices, selectTemplateRow[2], choices.selectRowTemplate2,
                               choices.selectRow1ColumnTemplate2,
                               choices.selectRow2ColumnTemplate2,
                               choices.selectRow3ColumnTemplate2,
                               choices.selectRow1ColumnTemplate2Col1Element1,
                               choices.selectRow1ColumnTemplate2Col2Element1,
                               choices.selectRow1ColumnTemplate2Col3Element1,
                               choices.selectRow2ColumnTemplate2Col1Element1,
                               choices.selectRow2ColumnTemplate2Col2Element1,
                               choices.selectRow2ColumnTemplate2Col3Element1,
                               choices.selectRow3ColumnTemplate2Col1Element1,
                               choices.selectRow3ColumnTemplate2Col2Element1,
                               choices.selectRow3ColumnTemplate2Col3Element1
                               )
        return selectTemplateRow, tabsTitle

    @classmethod
    def checkIfSomeoneUsedThatColorBefore(cls, yourColor, prInstance):
        allPath = os.path.join(DATA_FILES_PATH, 'projects')


        #code to show project list need to be in JavaScript

        for fileName in os.listdir(allPath):
            if fileName != 'welcome_project_' + str(
                    prInstance) + '.txt' and fileName != 'welcome_project_.txt':
                pathToFileName = os.path.join(allPath, fileName)
                with open(pathToFileName, 'r') as f:
                    line = f.readlines()[1].strip().split('\t')
                    usedColor = line[-1]
                    if usedColor == yourColor:
                        return True

        return False


    @classmethod
    def getAllProjects(cls, prInstance):
        # get all data which are used in list project
        allPath = os.path.join(DATA_FILES_PATH, 'projects')
        prList = []
        for fileName in os.listdir(allPath):
            if fileName != 'welcome_project_' + str(prInstance) + '.txt' and fileName != 'welcome_project_.txt':
                pathToFileName = os.path.join(allPath, fileName)
                with open(pathToFileName, 'r') as f:
                    prList.append(f.readlines()[1].strip().split('\t'))
        return prList

    @classmethod
    def openAndReadFile(cls, fileName):

        with open(ExternalTrackManager.extractFnFromGalaxyTN(fileName.split(':')), 'r') as f:
            data = ''.join(f.readlines())

        f.closed
        return data

    @classmethod
    def getTemplateRow(cls, choices, selectTemplateRow, temp, tempCol1, tempCol2, tempCol3,
                       tempR1Col1El1, tempR1Col2El1, tempR1Col3El1,
                       tempR2Col1El1, tempR2Col2El1, tempR2Col3El1,
                       tempR3Col1El1, tempR3Col2El1, tempR3Col3El1):

        temp1Row = int(temp)

        #tem1Row - how many rows

        for r in range(1, temp1Row+1):
            if not r in selectTemplateRow.keys():
                selectTemplateRow[r] = OrderedDict()

        if temp1Row >= 1:
            cls.getDataForAllColumn(selectTemplateRow, 1, tempCol1,
                                    tempR1Col1El1, tempR1Col2El1, tempR1Col3El1)
        if temp1Row >= 2:
            cls.getDataForAllColumn(selectTemplateRow, 2, tempCol2,
                                    tempR2Col1El1, tempR2Col2El1, tempR2Col3El1)
        if temp1Row >= 3:
            cls.getDataForAllColumn(selectTemplateRow, 3, tempCol3,
                                    tempR3Col1El1, tempR3Col2El1, tempR3Col3El1)


        return selectTemplateRow

    @classmethod
    def getDataForAllColumn(cls, selectTemplateRow, temp1Row, tempCol1,
                            tempR1Col1El1, tempR1Col2El1, tempR1Col3El1):
        if tempCol1 != '' and int(tempCol1) >= 1:
            cls.getColumnDataPerRow(selectTemplateRow, temp1Row, 1, tempR1Col1El1)
        if tempCol1 != '' and int(tempCol1) >= 2:
            cls.getColumnDataPerRow(selectTemplateRow, temp1Row, 2, tempR1Col2El1)
        if tempCol1 != '' and int(tempCol1) >= 3:
            cls.getColumnDataPerRow(selectTemplateRow, temp1Row, 3, tempR1Col3El1)

        return selectTemplateRow

    @classmethod
    def getColumnDataPerRow(cls, selectTemplateRow, temp1Row, tempCol1, tempCol1El1):
        cls.addDataToRowAndColumn(selectTemplateRow, temp1Row, tempCol1El1, tempCol1)
        return selectTemplateRow

    @classmethod
    def addDataToRowAndColumn(cls, selectTemplateRow, temp1Row, tempCol1El1,
                              number):

        if not number in selectTemplateRow[temp1Row].keys():
            selectTemplateRow[temp1Row][number] = ''

        if tempCol1El1 != '':
            selectTemplateRow[temp1Row][number] += cls.openAndReadFile(tempCol1El1)
        else:
            selectTemplateRow[temp1Row][number] += ''

        return selectTemplateRow

    #<a href="../u/hb-superuser/h/chromatin-accessibility-dnase-across-cell-types" target="_blank">

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if choices.color and choices.prInstance:
            yourColor = choices.color
            prInstance = choices.prInstance
            response = cls.checkIfSomeoneUsedThatColorBefore(yourColor, prInstance)
            if response == True:
                return 'Somoene else is using that color, you need to choose another one'


        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    @classmethod
    def getToolDescription(cls):

        rc = RgbColors()
        colorsDict = rc.getPossibleColorList()

        tab = ''


        for key in colorsDict.keys():
            tab += '<p>' + str(key) + '</p>'
            tab += '<table>'
            i=0
            for it in colorsDict[key]:

                if i == 0:
                    tab += '<tr>'
                elif i % 5 == 0:
                    tab += '</tr>'
                    tab += '<tr>'
                tab += '<td style="background-color:' + str(it) + '">' + str(it) + '</td>'

                i+=1
            tab += '</tr>'
            tab += '</table>'


        return tab
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False
    #
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
