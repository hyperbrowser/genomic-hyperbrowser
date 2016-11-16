import os
from proto.HtmlCore import HtmlCore
from proto.TableCoreMixin import TableCoreMixin


class TextCore(TableCoreMixin):
    HTML_CORE_CLS = HtmlCore

    def __init__(self):
        self._str = ''

    def __getattr__(self, item):
        if getattr(self.HTML_CORE_CLS, item):
            return self._default
        else:
            raise AttributeError('TextCore does not contain member "%s".' % item)

    def _default(self, *args, **kwargs):
        return self

    def header(self, title):
        self._str += '#' + title + os.linesep + os.linesep
        return self

    def bigHeader(self, title):
        self._str += '#' + title.upper() + os.linesep + os.linesep
        return self
        
    def descriptionLine(self, label, descr, indent=False):
        self._str += ('\t' if indent else '' ) + label + ': ' + descr + os.linesep
        return self
    
    def line(self, l):
        self._str += l + os.linesep
        return self
        
    def format(self, val):
        from gold.util.CommonFunctions import strWithStdFormatting
        self._str += strWithStdFormatting(val, separateThousands=False)
        return self
        
    def paragraph(self, p, indent=False):
        self._str += ('\t' if indent else '' ) + p + os.linesep + os.linesep
        return self
    
    def indent(self, text):
        self._str += '\t' + text
        return self
    
    def highlight(self, text):
        self._str += text
        return self

    def emphasize(self, text):
        self._str += text
        return self

    def tableHeader(self, headerRow, **kwargs):
        self._str += '\t'.join([str(el).upper() for el in headerRow])
        self._str += os.linesep
        return self

    def tableLine(self, row, rowSpanList=None, **kwargs):
        self._str += '\t'.join(['' if rowSpanList is not None and rowSpanList[i]==0 \
                                else str(el) for i,el in enumerate(row)])
        self._str += os.linesep
        return self

    def tableFooter(self, **kwargs):
        self._str += os.linesep        
        return self

    def divider(self, withSpacing=False):
        self._str += (os.linesep if withSpacing else '') + os.linesep + \
                     '---------------' + os.linesep + os.linesep
        return self

    def textWithHelp(self, baseText, helpText):
        self._str += baseText
        return self
        
    def link(self, text, url, popup=False, args='', withLine=True):
        self._str += text + ('(' + url +')' if url not in ['', '#'] else '')
        return self
    
    def unorderedList(self, strList):
        for s in strList:
            self._str += '* %s' % s + os.linesep
        self._str += os.linesep
        return self

    def orderedList(self, strList):
        for i, s in enumerate(strList):
            self._str += '%i. %s' % (i, s) + os.linesep
        self._str += os.linesep
        return self

    def append(self, str):
        self._str += str
        return self

    def __str__(self):
        return self._str
