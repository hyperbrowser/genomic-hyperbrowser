import os
import time
import humanize

from proto.CommonFunctions import isSamePath, getLoadToGalaxyHistoryURL, getFileSuffix
from proto.HtmlCore import HtmlCore
from proto.StaticFile import GalaxyRunSpecificFile


FILE_BROWSER_FILENAME = 'files.html'


def generateHtmlFileBrowserRootPage(galaxyFn, rootPageFileName):

    # Helper functions

    def _addHeader(core, dirpath, rootDir):
        reldirpath = os.path.abspath(dirpath)[len(os.path.abspath(rootDir)):]
        if not reldirpath:
            reldirpath = '/'
        core.header('File browser for result directory: "{}"'.format(reldirpath))

    def _addUpOneDirLinkIfNotRoot(core, dirpath, rootDir, rootPageFileName):
        if not isSamePath(dirpath, rootDir):
            if isSamePath(os.path.join(dirpath, '..'), rootDir):
                upOneDirPageFn = rootPageFileName
            else:
                upOneDirPageFn = FILE_BROWSER_FILENAME
            upOneDirLink = str(HtmlCore().link('< Up one directory', '../' + upOneDirPageFn))
            core.paragraph(upOneDirLink)

    def _addTableHeader(core):
        core.tableHeader(['Name', 'Date Modified', 'Size'],
                         tableClass='auto_width colored bordered')

    def _addTableLines(core, dirpath, dirnames, filenames):
        filesAndDirs = sorted(zip(dirnames + filenames,
                                  [True] * len(dirnames) + [False] * len(filenames)))

        for i, (item, isDir) in enumerate(filesAndDirs):
            fullItemPath = os.path.join(dirpath, item)
            core.tableLine(
                [_getNameContent(isDir, item, fullItemPath),
                 _getLastModifiedDateContent(fullItemPath),
                 _getSizeContent(fullItemPath, isDir)],
                rowClass=None if i % 2 == 0 else 'odd_row')

    def _getNameContent(isDir, item, fullItemPath):
        if isDir:
            return HtmlCore().link(item, item + '/' + FILE_BROWSER_FILENAME)
        else:
            loadToHistoryUrl = getLoadToGalaxyHistoryURL(
                fullItemPath,
                galaxyDataType='txt',
                histElementName=item
            )
            return HtmlCore().link(item, loadToHistoryUrl)

    def _getLastModifiedDateContent(fullItemPath):
        return time.ctime(os.path.getmtime(fullItemPath))

    def _getSizeContent(fullItemPath, isDir):
        return '&lt;dir&gt;' if isDir else humanize.naturalsize(os.path.getsize(fullItemPath))

    def _writeCoreToFileBrowserFile(core, dirpath):
        htmlPagePath = os.path.abspath(os.path.join(dirpath, FILE_BROWSER_FILENAME))
        with open(htmlPagePath, 'w') as htmlPage:
            htmlPage.write(str(core))

    # Main function

    rootDir = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()

    for dirpath, dirnames, filenames in os.walk(rootDir):
        core = HtmlCore()
        core.begin()
        _addHeader(core, dirpath, rootDir)
        _addUpOneDirLinkIfNotRoot(core, dirpath, rootDir, rootPageFileName)
        _addTableHeader(core)
        _addTableLines(core, dirpath, dirnames, filenames)
        core.tableFooter()
        core.end()

        if not isSamePath(dirpath, rootDir):
            _writeCoreToFileBrowserFile(core, dirpath)
        else:
            rootContents = str(core)

    return rootContents
