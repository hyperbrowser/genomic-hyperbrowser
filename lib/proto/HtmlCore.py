# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

import os
from config.Config import URL_PREFIX
#from gold.util.CustomExceptions import ShouldNotOccurError
import re

class HtmlCore(object):
    def __init__(self):
        self._str = ''

    def begin(self, extraJavaScriptFns=[], extraJavaScriptCode=None, extraCssFns=[]):
        self._str = '''
<html>
<head>
<script type="text/javascript" src="''' + URL_PREFIX + '''/static/scripts/libs/jquery/jquery.js"></script>
<script type="text/javascript" src="''' + URL_PREFIX + '''/static/scripts/sorttable.js"></script>
'''
        for javaScriptFn in extraJavaScriptFns:
            if re.match('https?://', javaScriptFn):
                self._str += '<script type="text/javascript" src="%s"></script>\n' % javaScriptFn
            else:
                self._str += '<script type="text/javascript" src="%s/static/scripts/%s"></script>\n' % (URL_PREFIX, javaScriptFn)

        if extraJavaScriptCode is not None:
            self._str += '''
<script type="text/javascript">%s</script>
''' % extraJavaScriptCode

        self._str += '''
<link href="''' + URL_PREFIX + '''/static/style/base.css" rel="stylesheet" type="text/css" />
'''

        for cssFn in extraCssFns:
            if re.match('https?://', cssFn):
                self._str += '<link href="%s" rel="stylesheet" type="text/css" />\n' % cssFn
            else:
                self._str += '<link href="%s/static/style/%s" rel="stylesheet" type="text/css" />\n'  % (URL_PREFIX, cssFn)

        self._str += '''
</head>
<body>''' + os.linesep

        return self

    def header(self, title):
        self._str += '<h3>' + title + '</h3>' + os.linesep
        return self

    def bigHeader(self, title):
        self._str += '<h1>' + title + '</h1>' + os.linesep
        return self

    def smallHeader(self, title):
        return self.highlight(title)

    def end(self):
        self._str += '''
</body>
</html>'''
        return self

    def descriptionLine(self, label, descr, indent=False, emphasize=False):
        tag = 'i' if emphasize else 'b'
        self._str += '<p%s>' % (' style="padding-left:30px;"' if indent else '') + \
            '<%s>' % tag + label + ':</%s> ' % tag + descr + '</p>' + os.linesep
        return self

    def line(self, l):
        self._str += l + '<br>' + os.linesep
        return self

    def divBegin(self, divId=None, divClass=None, style=None):
        divId = 'id="%s" '%divId if divId else ''
        divClass = 'class="%s" '%divClass if divClass else ''
        style = 'style="%s" '%style if style else ''
        self._str += '<div %s%s%s>' % (divId, divClass, style) + os.linesep
        return self

    def divEnd(self):
        self._str += '</div>'
        return self

    def format(self, val):
        from gold.util.CommonFunctions import strWithStdFormatting
        self._str += strWithStdFormatting(val, separateThousands=True)
        return self

    def paragraph(self, p, indent=False):
        #p = p.replace(os.linesep, '<br>')
        self._str += '<p%s>' % (' style="padding-left:30px;"' if indent else '') + \
                     os.linesep + p + os.linesep + '</p>' + os.linesep
        return self

    def indent(self, text):
        self._str += '<div style="padding-left:30px;">' + text + '</div>' + os.linesep
        return self

    def highlight(self, text):
        self._str += '<b>' + text + '</b>'
        return self

    def emphasize(self, text):
        self._str += '<i>' + text + '</i>'
        return self

    def tableHeader(self, headerRow, tagRow=None, firstRow=True, sortable=False, tableId=None):
        if firstRow:
            tableId = 'id="%s" '%tableId if tableId else ''
            sortable = ' sortable' if sortable else ''
            self._str += '<table %sclass="colored bordered%s" width="100%%" style="table-layout:auto; word-wrap:break-word;">' \
                % (tableId, sortable) + os.linesep

        if headerRow not in [None, []]:
            if tagRow is None:
                tagRow = [''] * len(headerRow)
            self._str += '<tr>'
            for tag,el in zip(tagRow, headerRow):
                self._str += '<th class="header"' + (' ' + tag if tag!='' else '') + '>' + str(el) + '</th>'
            self._str += '</tr>' + os.linesep

        return self

    def tableLine(self, row, rowSpanList=None):
        self._str += '<tr>'
        for i,el in enumerate(row):
            self._str += '<td' + (' rowspan=' + str(rowSpanList[i]) if rowSpanList is not None else '') + '>' + str(el) + '</td>'
        self._str += '</tr>' + os.linesep
        return self

    def tableFooter(self):
        self._str += '</table>'+ os.linesep
        return self

    def divider(self, withSpacing=False):
        self._str += '<hr %s/>' % ('style="margin-top: 20px; margin-bottom: 20px;"' if withSpacing else '') + os.linesep
        return self

    def textWithHelp(self, baseText, helpText):
        self._str += '<a title="' + helpText + '">' + baseText + '</a>'
        return self

    def link(self, text, url, popup=False, args='', withLine=True):
        self._str += '<a %s href="' % ('style="text-decoration:none;"' if not withLine else '') \
                  + url +('" target="_blank" ' if popup else '"')\
                  + '%s>' % (' ' + args if args != '' else '') + text + '</a>'
        return self

    def anchor(self, text, url, args=''):
        self._str += '<a name="' + url + '"%s>' % (' ' + args if args != '' else '') + text + '</a>'
        return self

    def formBegin(self, name=None, action=None, method=None):
        name = 'name="%s" ' % name if name else ''
        action =  'action="%s" ' % action if action else ''
        action =  'method="%s" ' % method if method else ''
        self._str += '<form %s%s%s>' % (name, action, method)
        return self

    def radioButton(self, value, name=None, event=None ):
        name = 'name="%s" ' % name if name else ''
        event = event if event else ''
        self._str += '<input type="radio" %svalue="%s" %s>%s<br>' % (name, value, event,value)
        return self

    def formEnd(self):
        self._str += '</form>'
        return self

    def unorderedList(self, strList):
        self._str += '<ul>'
        for s in strList:
            self._str += '<li> %s' % s
        self._str += '</ul>'
        return self

    def orderedList(self, strList):
        self._str += '<ol>'
        for s in strList:
            self._str += '<li> %s' % s
        self._str += '</ol>'
        return self

    def append(self, htmlStr):
        self._str += htmlStr
        return self

    def styleInfoBegin(self, styleId='', styleClass='', style='', inline=False, linesep=True):
        self._str += '<%s%s%s%s>' % ('span' if inline else 'div', \
                                    ' id="%s"' % styleId if styleId != '' else '', \
                                    ' class="%s"' % styleClass if styleClass != '' else '', \
                                    ' style="%s"' % style if style != '' else '') + \
                                    (os.linesep if linesep else '')
        return self

    def styleInfoEnd(self, inline=False):
        self._str += '</%s>' % ('span' if inline else 'div') + os.linesep
        return self

    def script(self, script):
        self._str += '<script type="text/javascript" language="javascript"> ' + script + ' </script>' + os.linesep
        return self

    def _getStyleClassOrIdItem(self, styleClass, styleId):
        if styleClass:
            return '.%s' % styleClass
        elif styleId:
            return '#%s' % styleId
        else:
            raise Exception()
            #raise ShouldNotOccurError()


    def toggle(self, text, styleClass=None, styleId=None, withDivider=False, otherAnchor=None, withLine=True):
        item = self._getStyleClassOrIdItem(styleClass, styleId)
        classOrId = styleClass if styleClass else styleId

        if withDivider:
            self._str += ' | '

        self._str += '''<a %s href="#%s" onclick="$('%s').toggle()">%s</a>''' \
                     % ('style="text-decoration:none;"' if not withLine else '', \
                        otherAnchor if otherAnchor else classOrId, \
                        item, text)

        return self

    def hideToggle(self, styleClass=None, styleId=None):
        item = self._getStyleClassOrIdItem(styleClass, styleId)
        self._str += '''
<script type="text/javascript">
    $('%s').hide()
</script>
''' % item

    def image(self, imgFn, style=None):
        self._str += '''<img%s src="%s"/>''' % \
            (' style="%s"' % style if style is not None else '', imgFn)
        return self

    def __str__(self):
        return self._str
