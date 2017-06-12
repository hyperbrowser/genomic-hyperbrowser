from proto.tools.hyperbrowser.GeneralGuiTool import GeneralGuiTool
from quick.util.CommonFunctions import ensurePathExists
from quick.application.ExternalTrackManager import ExternalTrackManager
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile

class CreateExampleContentTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Create content for welcome page"

    @classmethod
    def getInputBoxNames(cls):

        return [
                ("Which element do you want to create:", 'elementType'),
                ("Title", 'exampleTitle'),
                ("Select element for description part's", 'elementDesc'),
                ("Description part 1", 'exampleDesc1'),
                ("Description part 2", 'exampleDesc2'),
                ("Do you want to add link", 'addLink'),
                ("Type of url url:", 'urlEI'),
                ("Which element are you adding:", 'elementPL'),
                ("Url title", 'exampleUrlTitle'),
                ("Url (look at description) or email address", 'exampleUrl'),
                ("Description part 3", 'exampleDesc3'),
                ("Description part 4", 'exampleDesc4'),
                ]

    @classmethod
    def getOptionsBoxElementType(cls):
        return ['project description', 'project contact', 'description', 'example']

    @classmethod
    def getOptionsBoxExampleTitle(cls, prevChoices):
        return ''

    @classmethod
    def getOptionsBoxElementDesc(cls, prevChoices):
        return ['all in one line', 'paragraph']

    @classmethod
    def getOptionsBoxExampleDesc1(cls, prevChoices):
        return ''

    @classmethod
    def getOptionsBoxExampleDesc2(cls, prevChoices):
        return ''

    @classmethod
    def getOptionsBoxAddLink(cls, prevChoices):
        return ['no', 'yes']

    @classmethod
    def getOptionsBoxUrlEI(cls, prevChoices):
        if prevChoices.addLink == 'yes':
            return ['internal', 'external', 'email']


    @classmethod
    def getOptionsBoxElementPL(cls, prevChoices):
        if prevChoices.addLink == 'yes':
            if prevChoices.urlEI == 'internal':
                return ['link', 'page']


    @classmethod
    def getOptionsBoxExampleUrlTitle(cls, prevChoices):
        if prevChoices.addLink == 'yes':
            return ''

    @classmethod
    def getOptionsBoxExampleUrl(cls, prevChoices):
        if prevChoices.addLink == 'yes':
            return ''

    @classmethod
    def getOptionsBoxExampleDesc3(cls, prevChoices):
        return ''

    @classmethod
    def getOptionsBoxExampleDesc4(cls, prevChoices):
        return ''


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        elementType = choices.elementType
        exampleTitle = choices.exampleTitle
        exampleDesc1 = choices.exampleDesc1
        exampleDesc2 = choices.exampleDesc2
        addLink = choices.addLink
        urlEI = choices.urlEI
        exampleUrlTitle = choices.exampleUrlTitle
        exampleUrl = choices.exampleUrl
        exampleDesc3 = choices.exampleDesc3
        exampleDesc4 = choices.exampleDesc4

        elementDesc = choices.elementDesc





        if elementType == 'example':
            typeClass = 'example'

        if elementType == 'project description':
            typeClass = 'project'

        if elementType == 'description':
            typeClass = 'description'

        if elementType == 'project contact':
            typeClass = 'contactInfo'


        buildExample = ""
        buildExample += "<div class = '" + str(typeClass) + "'>"

        if exampleTitle != '':
            buildExample += "<h4 class = '" + str(typeClass) + 'Title' + "'>" + str(exampleTitle) + "</h4>"
        if exampleDesc1 != '':
            buildExample += "<div class = '" + str(typeClass) + "Desc'>"
            buildExample += cls.buildDesc(elementDesc, exampleDesc1)

        if exampleDesc2 != '':
            buildExample += cls.buildDesc(elementDesc, exampleDesc2)

        if addLink == 'yes':

            if exampleUrlTitle != '' and exampleUrl != '':
                if urlEI == 'internal':
                    if choices.elementPL == 'page':
                        urlPart = '../u/hb-superuser/p/'
                    else:
                        urlPart = '../u/hb-superuser/h/'
                    urlPath = str(urlPart) + str(exampleUrl)
                if urlEI == 'external':
                    urlPath = str(exampleUrl)

                if urlEI == 'internal' or urlEI == 'external':
                    buildExample += "<a href = '" + str(urlPath) + "' >" + str(exampleUrlTitle) + "</a>"
                if urlEI == 'email':
                    urlPath = exampleUrl
                    buildExample += "<a href='mailto:" + str(urlPath) + "' target='_top'>" + str(exampleUrlTitle) + "</a>"


        if exampleDesc3 != '':
            buildExample += cls.buildDesc(elementDesc, exampleDesc3)

        if exampleDesc4 != '':
            buildExample += cls.buildDesc(elementDesc, exampleDesc4)
            buildExample += "</div>"
        else:
            buildExample += "</div>"

        buildExample += '</div>'

        #outputFile = open(cls.makeHistElement(galaxyExt='txt', title=str(elementType)), 'w')
        # outputFile = GalaxyRunSpecificFile(['elementType' + '.' + 'txt'], galaxyFn)
        # ensurePathExists(outputFile.getDiskPath())
        # with(open(outputFile.getDiskPath(ensurePath=True)), 'w'):
        #     outputFile.write(buildExample)
        # outputFile.close()

        #print>> open(galaxyFn, 'w'), "<xmp style='padding:0px;margin:0px;white-space:nowrap'> " + buildExample + " </xmp>"
        print>> open(galaxyFn, 'w'), buildExample

    @classmethod
    def buildDesc(cls, elementDesc, exampleDesc3):
        buildExample=''
        if elementDesc == 'paragraph':
            buildExample += '<p class="paragraph">'
        buildExample += str(exampleDesc3)
        if elementDesc == 'paragraph':
            buildExample += '</p>'
        return buildExample



    @classmethod
    def validateAndReturnErrors(cls, choices):

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

        desc = "Url is started from '../u/hb-superuser/h/' if it is a link to history"
        desc += "Url is started from '../u/hb-superuser/p/' if it is a page"
        desc += "so if you are adding en example, then add just last name"




        return desc
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
    @classmethod
    def getOutputFormat(cls, choices):
        return 'txt'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
