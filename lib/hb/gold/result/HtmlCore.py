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
from gold.util.CommonConstants import THOUSANDS_SEPARATOR
from gold.util.CustomExceptions import ShouldNotOccurError
import re
from collections import OrderedDict

class HtmlCore(object):
    def __init__(self):
        self._str = ''

    def begin(self, extraJavaScriptFns=[], extraJavaScriptCode=None, extraCssFns=[], redirectUrl=None, reloadTime=None):
        self._str = '''
<html>
<head>'''
        
        if redirectUrl:
            self._str += '''
<meta http-equiv="refresh" content="0; url=%s" />''' % redirectUrl

        if reloadTime:
            self._str += '''
<script type="text/javascript">
    var done = false;
    setTimeout("if (!done) document.location.reload(true);", %s);
</script>
''' % (reloadTime * 1000)

        self._str += '''
<script type="text/javascript" src="''' + URL_PREFIX + '''/static/scripts/libs/jquery/jquery.js"></script>
<script type="text/javascript" src="''' + URL_PREFIX + '''/static/scripts/sorttable.js"></script>
<script type="text/javascript" src="''' + URL_PREFIX + '''/static/scripts/google_analytics_1.js"></script>
<script type="text/javascript" src="''' + URL_PREFIX + '''/static/scripts/google_analytics_2.js"></script>
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

    def end(self, stopReload=False):
        if stopReload:
            self._str += '''
<script type="text/javascript">
    done = true;
</script>'''
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
    
    def addInstruction(self, tableName = 'tab0'):
        
        tableName = str(tableName).replace('"','')
        
        
        strText = """ 
        <br \><div  style="margin-bottom:10px;" class="infomessage"><div class='""" + str(tableName) + """clickmeTable'>Show instructions for table</div></div>
        """
        
        strText += """
        <div id ='""" + str(tableName) + """table'  style='display:none;min-width:400px;margin-top:10px;margin-bottom:10px;border:1px solid #000033;padding:10px;color:#181818' >
            <div id ='guideLine'  style='font-weght:bold;text-transform:uppercase;margin-bottom:5px;'>
            Guidelines for table:
            </div>
            
            <div id ='option1d'  style='font-weght:bold;margin-bottom:5px;margin-top:5px;'>
            Sorting:
            </div>
            - To sort the table by a column, click on the column header. <br \>

            <div id ='option1d'  style='font-weght:bold;margin-bottom:5px;margin-top:5px;'>
            Show/Hide plots:
            </div>
            - To generate a bar plot for a specific column check the box (when there is one) next to the column header. The sorting in the table is also reflected in the plots.
            
            
        </div>
        
        """
        
        strText += """
        <script>
        
        $('.""" + str(tableName) + """clickmeTable').on('click', function(e) {
                //console.log('#""" + str(tableName) + """Table');
                $('#""" + str(tableName) + """table').slideToggle('fast');
                
            });
        
        </script>
        
        
        """
        
        return strText
    def tableHeader(self, headerRow, tagRow=None, firstRow=True, sortable=False, tableId=None, addInstruction=False, tableClass=''):
        
        if firstRow:
            if addInstruction==True:
                if tableId=='':
                    tableId='tab0'
                self._str += self.addInstruction(tableName=tableId)
            tableId = 'id="%s" '%tableId if tableId else ''
            sortable = ' sortable' if sortable else ''
            self._str += '<table %sclass="colored bordered%s %s" width="100%%" style="table-layout:auto; word-wrap:break-word;">' \
                % (tableId, sortable, tableClass) + os.linesep

        if headerRow not in [None, []]:
            if tagRow is None:
                tagRow = [''] * len(headerRow)
            self._str += '<tr>'
            for tag,el in zip(tagRow, headerRow):
                self._str += '<th class="header"' + (' ' + tag if tag != '' else '') + '>' + str(el) + '</th>'
            self._str += '</tr>' + os.linesep

        return self
    
    def tableHeaderWithClass(self, headerRow, tableClass=None, tagRow=None, firstRow=True, sortable=False, addInstruction=False, tableId=None):
        if firstRow:
            if addInstruction==True:
                if tableId=='':
                    tableId='tab0'
                self._str += self.addInstruction(tableName=tableId)
            tableId = 'id="%s" '%tableId if tableId else ''
            styleClass = 'class="%s'% tableClass if tableClass else ''
            if sortable:
                if styleClass:
                    styleClass += ' sortable"'
                else:
                    styleClass = 'class="sortable'
            if styleClass:
                styleClass +='"'
            self._str += '<table %s %s width="100%%" style="table-layout:auto; word-wrap:break-word;">' \
                % (tableId, styleClass) + os.linesep

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
            # self._str += '<td' + (' rowspan=' + str(rowSpanList[i]) if rowSpanList is not None else '') + '>' + str(el) + '</td>'
            rowSpan = rowSpanList[i] if rowSpanList else None
            self.tableCell(str(el), rowSpan=rowSpan)
        self._str += '</tr>' + os.linesep
        return self
    
    def tableRowBegin(self, rowClass=None):
        self._str += '<tr'
        if rowClass:
            self._str += ' class=%s' % rowClass
        self._str += '>'
        return self
    
    def tableRowEnd(self):
        self._str += '</tr>' + os.linesep
        return self
    
    def tableCell(self, content, cellClass=None, style=None, rowSpan=None, colSpan=None):
        self._str += '<td'
        try:
            contNoSpaces = content.replace(THOUSANDS_SEPARATOR, '')
            float(contNoSpaces)
            self._str += ' sorttable_customkey="' + contNoSpaces + '"'
        except:
            pass
        if cellClass:
            self._str += ' class=%s' % cellClass
        if style:
            self._str += ' style=%s' % style
        if rowSpan:
            self._str += ' rowspan=' + str(rowSpan)
        if colSpan:
            self._str += ' colspan=' + str(colSpan)
        self._str += '>' + content + '</td>'

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
            raise ShouldNotOccurError()


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

    def fieldsetBegin(self, title=None):
        self._str += '<fieldset>' + os.linesep
        if title:
            self._str += '<legend>%s</legend>' % title + os.linesep
        return self

    def fieldsetEnd(self):
        self._str += '</fieldset>' + os.linesep
        return self

    def image(self, imgFn, style=None):
        self._str += '''<img%s src="%s"/>''' % \
            (' style="%s"' % style if style is not None else '', imgFn)
        return self
    
    def tableFromDictionary(self, dataDict, columnNames=None, sortable=True, tableId=None, expandable=False, visibleRows=6, presorted=None, addInstruction=None):
        """Render a table from data in dataDict. Each key in dataDict is a row title,
        each value is a list of values, each corresponding to the column given with columnNames.

        If presorted is set to a number and tableId != None and sortable == True, that column will be presorted (using a hacky solution using jquery.
        """

        #transfom dicts with a single value to a dict of lists for easier sorting and html table generation
        dataDictOfLists = OrderedDict()
        for key, val in dataDict.iteritems():
            if isinstance(val, list):
                dataDictOfLists[key] = val
            elif isinstance(val, tuple):
                dataDictOfLists[key] = list(val)
            else:
                dataDictOfLists[key] = [val]

        if presorted is not None and presorted > -1:
            assert isinstance(presorted, int), 'presorted must be int'
            from quick.util import CommonFunctions
            dataDictOfLists = CommonFunctions.smartSortDictOfLists(dataDictOfLists, sortColumnIndex=presorted)

        if expandable:
            assert tableId is not None, 'Table ID must be set for expandable tables.'
            self.tableHeaderWithClass(headerRow=columnNames, sortable=sortable, tableId=tableId, tableClass='colored bordered expandable', addInstruction=addInstruction)
        else:
            self.tableHeader(headerRow=columnNames, sortable=sortable, tableId=tableId, addInstruction=addInstruction)

        # for key, val in dataDict.iteritems():
        for key, val in dataDictOfLists.iteritems():
            if isinstance(val, list):
                self.tableLine([key] + val)
            else:
                self.tableLine([key] + [val])

        self.tableFooter()

        # if tableId != None and sortable and presorted:
        #     # Javascript code for clicking on the column (so that it is sorted client side)
        #     # Hacky solution: Emulates a click on the header with a 500 ms delay so that sorttable.js is done first
        #     self._str += "<script>$(document).ready(function(){ setTimeout(function(){ $('#" + tableId + " .header')[" + str(presorted) + "].click();}, 500) })</script>"

        if expandable and len(dataDict) > visibleRows:
            self._tableExpandButton(tableId, len(dataDict), visibleRows=visibleRows)

        return self

    def tableFromDictOfDicts(self, dataDict, firstColName='', sortable=True, tableId=None, expandable=False, visibleRows=6, presorted=None):
        ''' it is assumed that dataDict is a full matrix, i.e. each element in the dict is a dict of the same size.'''
        assert isinstance(dataDict, OrderedDict) and all(isinstance(x, OrderedDict) for x in dataDict.values()),\
            'dataDict must be an OrderedDict of OrderedDicts'
        colNames = []
        convertedDataDict = OrderedDict()
        for key1, val1 in dataDict.iteritems():
            if not colNames:
                colNames = [firstColName] + val1.keys()
            convertedDataDict[key1] = val1.values()
            
        return self.tableFromDictionary(convertedDataDict, columnNames=colNames, sortable=sortable, tableId=tableId, expandable=expandable, visibleRows=visibleRows, presorted=presorted)
                

    def _tableExpandButton(self, tableId, totalRows, visibleRows=6):
        
        self.script('''
        
            function expandTable(tableId) {
                tblId = "#" + tableId;
                $(tblId).find("tr").show();
                btnDivId = "#toggle_table_" + tableId;
                $(btnDivId).find("input").toggle();
            }
        
            function collapseTable(tableId, visibleRows) {
                tblId = "#" + tableId;
                trScltr = tblId + " tr:nth-child(n + " + visibleRows + ")";
                $(trScltr).hide();
                btnDivId = "#toggle_table_" + tableId;
                $(btnDivId).find("input").toggle();
            }
            
            $(document).ready(function(){
                hiddenRowsSlctr = "table.expandable tr:nth-child(n + %s)";
                $(hiddenRowsSlctr).hide();
            }
            );
            
        ''' % str(visibleRows+2)) # '+2' for some reason (one of life's great mysteries)
        
        
        self._str += '''<div id="toggle_table_%s" class="toggle_table_btn">
                        <input type="button" value="Expand table (now showing %s of %s rows)..." id="expand_table_btn" style="background: #F5F5F5;" onclick="expandTable('%s')"/>
                        <input type="button" value="Collapse table (now showing %s of %s rows)" id="collapse_table_btn" style="background: #F5F5F5; display: none;" onclick="collapseTable('%s', %s)"/>
                        ''' % (tableId, visibleRows, totalRows, tableId, totalRows, totalRows, tableId, visibleRows+1)
        
    def __str__(self):
        return self._str
