from collections import OrderedDict

from proto.hyperbrowser.StaticFile import StaticFile


class WelcomePageHtmlFunctions():

    def __init__(self, selectTemplateRow, projectTitle, projectDesc, projectContact, prList):
        self.selectTemplateRow = selectTemplateRow
        self.projectTitle = projectTitle
        self.projectDesc = projectDesc
        self.projectContact = projectContact
        self.prList = prList

    def pageHeader(self, ownCss):
        header = "<!DOCTYPE html>"
        header += "<html>"
        header += "<head>"
        header += self.addJSlibraries()
        header += self.addOwnCss(ownCss)
        header += "<meta charset='UTF-8'>"
        header += "<title>" + str(self.projectTitle) + "</title>"
        header += "</head>"

        return header


    def addOwnCss(self, ownCss):
        css = ''
        css += '<link rel="stylesheet" href="' + str(ownCss) + '">'

        return css


    def addJSlibraries(self):
        lib = ''
        lib += '<meta name="viewport" content="width=device-width, initial-scale=1">'
        lib += '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">'
        lib += '<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>'
        lib += '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>'

        return lib


    def pageBodyStart(cls):
        body = "<body>"
        body += "<div class='content'>"
        return body

    def pageBodyAndHtmlEnd(cls):
        body = ''
        body += '</div>'
        body += "</body>"
        body += "</html>"
        return body

    def addTabs(cls, howManyExtraTabs, tabsTitle):
        tabs = ''
        tabs += '<div class ="tabs"> '
        tabs += '<ul class ="nav nav-tabs" id="tab-links">'

        for i in range(0, howManyExtraTabs):
            extra = ''
            if i == 0:
                extra = 'class="active"'
            tabs = cls.createElementOfTab(i, tabs, tabsTitle[i], extra)

        #always tab with Project list
        projectListsNum = howManyExtraTabs
        tabs = cls.createElementOfTab(projectListsNum, tabs, "List of other projects")
        # always tab with About
        projectAbout = howManyExtraTabs + 1
        tabs = cls.createElementOfTab(projectAbout, tabs, "About")

        tabs += '</ul>'
        tabs += '</div> '

        tabs += cls.createContentForTabs(howManyExtraTabs)

        return tabs

    def createElementOfTab(self, i, tabs, tabsTitle, extra=''):

        tabs += '<li ' + str(extra) + ' value="tab' + str(i) + '">'
        tabs += '<a data-toggle="tab" href="#menu' + str(i) + '">'
        tabs += tabsTitle
        tabs += '</a></li>'
        return tabs

    def createContentForTabs(self, howManyExtraTabs):

        cscfp = CreateStaticContentForPages(prList=self.prList)

        content = ''
        content += '<div class="tab-content">'
        for i in range(0, howManyExtraTabs+2):
            extra = ''
            if i == 0:
                extra = ' in active'
            content += '<div id="menu'+ str(i) +'" class="tab-pane fade ' + str(extra) + '">'


            if i < howManyExtraTabs:
                content += self.createTemplate(self.selectTemplateRow[i+1], i)
                content += self.createTemplateFooter()

            if i == howManyExtraTabs:
                #get list of project from file
                content += cscfp.createContentForProjectPage()
            if i == howManyExtraTabs + 1:
                content += cscfp.createContentForAboutPage()

            content += '</div>'
        content += '</div>'

        return content

    def createTemplateFooter(self):
        footer =''
        footer += """
            <div class="footer">
                """ + str(self.projectContact) + """
            </div>
        """
        return footer

    def createTemplate(self, selectTab, numTab):

        template = ''
        template += """<div class="container">
                            <div class="rowSpecial">
                                <div class="colAll">"""

        if numTab == 0:
            template += '<h2 class="projectTitle">' + str(self.projectTitle) + '</h2>'
            template += str(self.projectDesc)
        else:
            template += "Content for column 1 and row 1"

        template += """</div> </div></div>"""

        #rows
        for row in selectTab.keys():

            template += """
                        <div class="containerNext">
                            <div class="rowSpecialWithGap">"""

            howManyCol = len(selectTab[row].keys())

            if howManyCol == 1:
                template += """
                          <div class="colAll"> """ + str(selectTab[row][1]) + """</div>

                """
            if howManyCol == 2:
                template += """

                          <div class="colHalfLeft"> """ + str(selectTab[row][1]) + """</div>
                          <div class="colHalfRight"> """ + str(selectTab[row][2]) + """</div>

            """
            if howManyCol == 3:
                template += """

                          <div class="colOneThirdLeft"> """ + str(selectTab[row][1]) + """</div>
                          <div class="colOneThirdMiddle">  """ + str(selectTab[row][2]) + """</div>
                          <div class="colOneThirdRight">  """ + str(selectTab[row][3]) + """</div>

            """


            template += """
                            </div>
                        </div>
                        """




                # howManyCol = len(selectTab[row][col])
                # print 'col', col
                # print 'howManyCol', howManyCol
                # print 'selectTab[row][col]', selectTab[row][col]




        return template




class NecessaryInforForWelcomePage():

    @classmethod
    def addInfoAboutRestartingGalaxy(cls):

        info = 'Clear cache and reload the main page'

        return '<div class = "info">' + info + '</div>'

    @classmethod
    def addInfoAboutAddingLineToMakeNewWelcomePageVisibleFOrEveryone(cls):

        info = "Your page is in '/static/welcome_project.html' <br>"
        info += ""
        info += ""

        return '<div class = "info">' + info + '</div>'



class CreateCss():

    def __init__(self, colorProject, colorProjectTint, colorProjectShade):
        self.colorProject = colorProject
        self.colorProjectTint = colorProjectTint
        self.colorProjectShade = colorProjectShade

    def addCss(self):
        css = ''
        css += self.addBody()
        css += self.addContainer()
        css += self.addCssToTab()
        css += self.addTabMain()
        css += self.addInfo()
        css += self.addStaticPage()
        css += self.addContent()

        return css


    def addCssToTab(self):
        return """
        .nav {
            padding-bottom:1px;
        }
        .nav-tabs {
            border-bottom: 1px solid """ + str(self.colorProject) + """;
        }
        .nav-tabs > li {
            background-color: #66635B;
            border-bottom: none;
        }
        .nav-tabs > li.active > a, .nav-tabs > li.active > a:focus, .nav-tabs > li.active > a:hover {
            color: #222;
            cursor: default;
            background-color: """ + str(self.colorProject) + """;
            border: 1px solid """ + str(self.colorProject) + """;
            border-bottom-color: transparent;
        }
        .nav-tabs > li > a {
            margin-right: 2px;
            line-height: 1.42857143;
            border-radius: 4px 4px 0 0;
            border: 1px solid """ + str(self.colorProject) + """;
            border-bottom-color:transparent ;
            color: #fff;
        }
        .nav-tabs > li > a:hover {
            color: #000000;
            background-color: """ + str(self.colorProjectTint) + """;
            border: 1px solid """ + str(self.colorProject) + """;
            border-bottom-color:transparent;
        }
        .nav > li > a {
            position: relative;
            display: block;
            padding: 10px 15px;
        }
        .nav > li {
            padding-right:2px;
        }
       """

    def addContainer(self):
        return """
        .content {
            padding-right: 15px;
            padding-left: 15px;
            margin-right: auto;
            margin-left: auto;
        }
        """

    def addBody(self):
        return """
        body {
            font-size:12px;
            background-color: #66635B;
            padding: 10px;
            font-family: "Lucida Grande",verdana,arial,helvetica,sans-serif;
            }
        """

    def addTabMain(self):
        return """
        .container{
            color: #222;
            width: 100%;
            background-color: """ + str(self.colorProject) + """;
            margin-bottom:10px;
        }

        .footer {
            text-align:center;
            padding: 10px;
            width: 100%;
            background-color: """ + str(self.colorProject) + """;
            margin-top: 20px;
            border-radius: 0px 0px 4px 4px;
        }

        .projectTitle {
            border-bottom: 1px dotted #333333;
        }

        containerNext{
            color: #222;
            width: 100%;
        }

        .rowSpecial{
            overflow: hidden;
            background-color: """ + str(self.colorProject) + """;
            margin-top: 20px;
            padding-bottom: 10px;
        }
        .rowSpecialWithGap{
            display: flex;
            overflow: hidden;
            background-color: #66635B;
            margin-top: 20px;
        }
        .colHalfLeft{
            background-color: """ + str(self.colorProject) + """;
            float: left;
            width:50%;
            padding:15px;
        }
        .colHalfRight{
            float: left;
            background-color: """ + str(self.colorProject) + """;
            width:50%;
            padding:15px;
            border-left: 10px solid #66635B;
        }

        .colAll{
            padding:15px;
            width:100%;
            background-color: """ + str(self.colorProject) + """;
        }
        .colAllProjectList{
            padding:5px;
            padding-left: 15px;
            padding-right: 15px;
            width:100%;
            background-color: """ + str(self.colorProject) + """;
        }
        .colOneThirdLeft{
            background-color: """ + str(self.colorProject) + """;
            float:left;
            padding:15px;
            width:33.3333333%;
        }
        .colOneThirdMiddle{
            background-color: """ + str(self.colorProject) + """;
            float:left;
            padding:15px;
            width:33.3333333%;
            border-left: 10px solid #66635B;
        }
        .colOneThirdRight{
            background-color: """ + str(self.colorProject) + """;
            float:left;
            padding:15px;
            width:33.3333333%;
            border-left: 10px solid #66635B;
        }




        .colAllProjectList div   {
            margin-bottom:10px;
        }

        p {
            padding: 5px;
        }

        a {
            color: """ + str(self.colorProjectShade) + """
        }

        a:hover {
            color: """ + str(self.colorProjectTint) + """
        }

        """

    def addInfo(self):
        return """
            .info
            {
                width: 300px;
            }
        """

    def addContent(self):
        return """
            .example
            {
                border: 1px dotted #333333;
                padding: 10px;
                margin-bottom:10px;
            }
            .example p
            {
                border:none;
                font-weight: bold;
            }
            .exampleDesc a
            {
                text-decoration: underline;
                color: #000000;
            }
            .exampleDesc a:hover
            {
                text-decoration: none;
                color: """ + str(self.colorProjectShade) + """;
            }
            .exampleDesc p{
                font-weight:normal;
            }

            .project, .description
            {
                padding: 2px;
            }
            .project p, .description p
            {
                border:none;
            }
            .projectTitle p
            {
                font-size:14px;
            }

            .project a, .description a
            {
                text-decoration: underline;
                color: #000000;
            }
            .project a:hover, .description a:hover
            {
                text-decoration: none;
                color: """ + str(self.colorProjectShade) + """;
            }
            .descriptionTitle {
                border-bottom: 1px dotted #474747;
                padding-bottom: 5px;
            }
            .description p.paragraph
            {

            }

            .contactInfo
            {
                padding: 2px;
            }
            .contactInfo p
            {
                border:none;
            }
            .contactInfo a
            {
                text-decoration: underline;
                color: #000000;
            }
            .contactInfo a:hover
            {
                text-decoration: none;
                color: """ + str(self.colorProjectShade) + """;
            }


            .imgzoom img {
            max-width: 100%;
            display: block;
        }

        .imgzoom {

        }

        .imgzoom .imageL, .imgzoom .imageC, .imgzoom .imageR {
            width: 30%;
            height: 100%;
            float:left;
            margin-left:5px;
            margin-right:5px;
        }
        .img-thumbnail{

        }

        .imgzoom .imageL img, .imgzoom .imageC img, .imgzoom .imageR img {
            -webkit-transition: all 1s ease; /* Safari and Chrome */
            -moz-transition: all 1s ease; /* Firefox */
            -o-transition: all 1s ease; /* IE 9 */
            -ms-transition: all 1s ease; /* Opera */
            transition: all 1s ease;

        }

        .imgzoom .imageL:hover img {
            -webkit-transform:scale(1.5); /* Safari and Chrome */
            -moz-transform:scale(1.5); /* Firefox */
            -ms-transform:scale(1.5); /* IE 9 */
            -o-transform:scale(1.5); /* Opera */
             transform:scale(1.5);
            margin-left: 30%;

        }
        .imgzoom .imageC:hover img {
            -webkit-transform:scale(1.5); /* Safari and Chrome */
            -moz-transform:scale(1.5); /* Firefox */
            -ms-transform:scale(1.5); /* IE 9 */
            -o-transform:scale(1.5); /* Opera */
             transform:scale(1.5);

        }
        .imgzoom .imageR:hover img {
            -webkit-transform:scale(1.5); /* Safari and Chrome */
            -moz-transform:scale(1.5); /* Firefox */
            -ms-transform:scale(1.5); /* IE 9 */
            -o-transform:scale(1.5); /* Opera */
             transform:scale(1.5);
            margin-right: 100%;

        }



        """

    def addStaticPage(self):
        return """
        .contact, .infoAboutHB {
            padding: 10px;
            margin-top: 10px;
            margin-bottom:10px;
        }
        .contact a, .infoAboutHB a{
            color: #999;
        }

        .contact a:hover, .infoAboutHB a:hover{
            color: #66635B;
        }




        """

class RgbColors():

    @classmethod
    def hex_to_rgb(cls, value):
        value = value.lstrip('#')
        lv = len(value)

        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    @classmethod
    def rgb_to_hex(cls, red, green, blue):

        return '#%02x%02x%02x' % (red, green, blue)

    @classmethod
    def rgbToShade(cls, currentR, currentG, currentB, shade_factor):
        newR = currentR * (1 - shade_factor)
        newG = currentG * (1 - shade_factor)
        newB = currentB * (1 - shade_factor)

        return newR, newG, newB

    @classmethod
    def rgbToTint(cls, currentR, currentG, currentB, tint_factor):
        newR = currentR + (255 - currentR) * tint_factor
        newG = currentG + (255 - currentG) * tint_factor
        newB = currentB + (255 - currentB) * tint_factor

        return newR, newG, newB


    @classmethod
    def getPossibleColorList(cls):

        #create dict of all possible colors in the projects instance
        colorsDict = OrderedDict()

        colorsDict['Whites/Pastels'] = []
        colorsDict['Grays'] = []
        colorsDict['Blues'] = []
        colorsDict['Greens'] = []
        colorsDict['Yellows'] = []
        colorsDict['Browns'] = []
        colorsDict['Oranges'] = []
        colorsDict['Pinks/Violets'] = []

        colorsDict['Whites/Pastels'] = ["#fffafa", "#eee9e9", "#cdc9c9", "#8b8989", "#f8f8ff",
                                        "#f5f5f5", "#dccdc", "#fffaf0", "#fdf5e6", "#faf0e6",
                                        "#faebd7", "#eedfcc", "#cdc0b0", "#8b8378", "#ffefd5",
                                        "#ffebcd", "#ffe4c4", "#eed5b7", "#cdb79e", "#8b7d6b",
                                        "#ffdab9", "#eecbad", "#cdaf95", "#8b7765", "#ffdead",
                                        "#ffe4b5", "#fff8dc", "#eee8dc", "#cdc8b1", "#8b8878",
                                        "#fffff0", "#eeeee0", "#cdcdc1", "#8b8b83", "#fffacd",
                                        "#fff5ee", "#eee5de", "#cdc5bf", "#8b8682", "#f0fff0",
                                        "#e0eee0", "#c1cdc1", "#838b83", "#f5fffa",
                                        "#f0ffff""#f0f8ff", "#e6e6fa", "#fff0f5", "#ffe4e1",
                                        "#ffffff"]
        colorsDict['Grays'] = ["#000000", "#2f4f4f", "#696969", "#708090", "#778899", "#bebebe",
                               "#d3d3d3"]

        colorsDict['Blues'] = ["#191970", "#000080", "#6495ed", "#483d8b", "#6a5acd", "#7b68ee",
                               "#8470ff", "#0000cd", "#41690", "#0000ff", "#1e90ff", "#00bfff",
                               "#87ceeb", "#87cefa", "#4682b4", "#b0c4de", "#add8e6", "#b0e0e6",
                               "#afeeee", "#00ced1", "#48d1cc", "#40e0d0", "#00ffff", "#e0ffff",
                               "#5f9ea0"]

        colorsDict['Greens'] = ["#66cdaa", "#7fffd4", "#006400", "#556b2f", "#8fbc8f", "#2e8b57",
                                "#3cb371", "#20b2aa", "#98fb98", "#00ff7f", "#7cfc00", "#7fff00",
                                "#00fa9a", "#adff2f", "#32cd32", "#9acd32", "#228b22", "#6b8e23",
                                "#bdb76b", "#f0e68c"]

        colorsDict['Yellows'] = ["#eee8aa", "#fafad2", "#ffffe0", "#ffff00", "#ffd700", "#eedd82",
                                 "#daa520", "#b8860b"]

        colorsDict['Browns'] = ["#bc8f8f", "#cd5c5c", "#8b4513", "#a0522d", "#cd853f", "#deb887",
                                "#f5f5dc", "#f5deb3", "#f4a460", "#d2b48c", "#d2691e", "#b22222",
                                "#a52a2a"]

        colorsDict['Oranges'] = ["#e9967a", "#fa8072", "#ffa07a", "#ffa500", "#ff8c00", "#ff7f50",
                                 "#f08080", "#ff6347", "#ff4500", "#ff0000"]

        colorsDict['Pinks/Violets'] = ["#ff69b4", "#ff1493", "#ffc0cb", "#ffb6c1", "#db7093",
                                       "#b03060", "#c71585", "#d02090", "#ee82ee", "#dda0dd",
                                       "#da70d6", "#ba55d3", "#9932cc", "#9400d3", "#8a2be2",
                                       "#a020f0", "#9370db", "#d8bfd8"]


        return colorsDict



class CreateStaticContentForPages():

    def __init__(self, prList):
        self.prList = prList


    def createContentForProjectPage(self):

        pathToFolder = StaticFile(['files', 'projects', 'projects_' + self.prList + '.txt'])
        pathToFolderUrl = pathToFolder.getURL()

        #tempSolution
        pathToFolderUrl = '/dianadom_dev/static/hyperbrowser/files/projects/'+'projects_' + self.prList + '.txt'


        project =  '''

            <div class="container">
                <div class="rowSpecial">
                    <div class="colAllProjectList">

                          <div id ='content'></div>
                                <script>
                                $("#content").load("''' + str(pathToFolderUrl) + '''");
                                </script>
                    </div>
                </div>
            </div>
            '''

        return project


    def createContentForAboutPage(self):

        return """
        <div class="container">


				<div class="contact">

				    <b>Note:</b>
                        <p>
                        This is a specialized version of The Genomic Hyperbrowser,
                        focusing on new functionality for analyzing collections of genomic track.
                        More information on the general HyperBrowser functionality can be
                        found on the <a href="https://hyperbrowser.uio.no/hb/" target="_blank">main project site</a>.
                        </p>
				    <b>Contact information</b>
                        <p>
                        If you have any questions, requests or comments, please use our discussion forum (available from the <a minsizehint="-1" href="https://sites.google.com/site/hyperbrowserhelp/?tool_id=hb_help">Help</a> menu) or send us an email to <a href="#" onclick="this.href='mailto:'+ this.innerHTML.split('').reverse().join('')" class="codedirection">hyperbrowser-requests@usit.uio.no</a>&#x200E;. We are happy to respond and welcome collaborative projects that help further develop our system. If you encounter any bugs, please let us know via an email to
                        <a href="#" onclick="this.href='mailto:'+ this.innerHTML.split('').reverse().join('')" class="codedirection">hyperbrowser-requests@usit.uio.no</a>.
                       </p>

				        <p>If you register as a user, you will be able to subscribe to the <a href="#" onclick="this.href='mailto:'+ this.innerHTML.split('').reverse().join('')" class="codedirection">hyperbrowser-requests@usit.uio.no</a> mailing list, which serves for distribution of system-related announcements and administrative messages.
				         A backlog of announcements is available from the Help menu. The Help menu also contains citation information.
				        </p>

				</div>

		</div>

        <div class="containerNext">
            <div class="rowSpecial">
                <div class ="infoAboutHB">
                <p class="blocktext">
                This project is being developed by the Norwegian bioinformatics community as an open-source project under the GPL  license v3,
                supported by various national and local bodies.
                </p>
                <p class="blocktext">
                  For further information on Norwegian bioinformatics, please visit <a href="http://www.bioinfo.no">www.bioinfo.no</a>.
                </p>
         </div>
          </div>
		</div>

        <div class="footer">
                <div class="section">
                  <img src="hyperbrowser/images/logo/HB_support.png" class="center">
                </div>
        </div>




        """


