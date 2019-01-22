import os
import time
import humanize

from proto.CommonFunctions import isSamePath, getLoadToGalaxyHistoryURL, getFileSuffix
from proto.HtmlCore import HtmlCore
from proto.StaticFile import GalaxyRunSpecificFile


FILE_BROWSER_FILENAME = 'files.html'


def generateHtmlFileBrowserForGalaxyFilesDir(galaxyFn, writeRootPageToGalaxyFn=False):
    """
    Generates a HTML-based file browser that provides a clickable overview of all the result files
    in the "dataset_123_files" directory connected to a Galaxy history element. This folder 
    contains all the result files except the main output (which is in the galaxyFn dataset file).
    The file browser is written into a set of files named '{}', one in each directory.
    :param galaxyFn: Path to Galaxy dataset file (e.g. "/path/to/dataset_123.dat").
    :param writeRootPageToGalaxyFn: If True, write root HTML page to main dataset file (galaxyFn).
    :return: GalaxyRunSpecificFile object pointing to the newly created root HTML page (named 
        '{}'). If writeRootPageToGalaxyFn is set to True, None is returned.
    """.format(FILE_BROWSER_FILENAME, FILE_BROWSER_FILENAME)

    # Helper functions

    def _addHeader(core, dirPath, rootDir):
        relDirPath = os.path.abspath(dirPath)[len(os.path.abspath(rootDir)):]
        if not relDirPath:
            relDirPath = '/'
        core.header('File browser for result directory: "{}"'.format(relDirPath))

    def _addUpOneDirLinkIfNotRoot(core, dirPath, rootDir, writeRootPageToGalaxyFn):
        if not isSamePath(dirPath, rootDir):
            if isSamePath(os.path.join(dirPath, '..'), rootDir):
                upOneDirPageFn = FILE_BROWSER_FILENAME if not writeRootPageToGalaxyFn else ''
            else:
                upOneDirPageFn = FILE_BROWSER_FILENAME
            upOneDirLink = str(HtmlCore().link('< Up one directory', '../' + upOneDirPageFn))
            core.paragraph(upOneDirLink)

    def _addLinkToMainDatasetIfRootAndSeparateFile(core, dirPath,
                                                   rootDir, writeRootPageToGalaxyFn):
        if isSamePath(dirPath, rootDir) and not writeRootPageToGalaxyFn:
            mainDatasetLink = str(HtmlCore().link('< Back to main dataset', '/.'))
            core.paragraph(mainDatasetLink)

    def _addTableHeader(core):
        core.tableHeader(['Name', 'Date Modified', 'Size'],
                         tableClass='auto_width colored bordered')

    def _addTableLines(core, dirPath, dirNames, fileNames):
        filesAndDirs = sorted(zip(dirNames + fileNames,
                                  [True] * len(dirNames) + [False] * len(fileNames)))

        for i, (item, isDir) in enumerate(filesAndDirs):
            fullItemPath = os.path.join(dirPath, item)
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

    def _determineOutputFilePath(galaxyFn, dirPath, rootDir, writeRootPageToGalaxyFn):
        if isSamePath(dirPath, rootDir) and writeRootPageToGalaxyFn:
            return galaxyFn
        else:
            return os.path.abspath(os.path.join(dirPath, FILE_BROWSER_FILENAME))


    # Main function

    rootDir = GalaxyRunSpecificFile([], galaxyFn).getDiskPath()

    for dirPath, dirNames, fileNames in os.walk(rootDir):
        core = HtmlCore()
        core.begin()
        _addHeader(core, dirPath, rootDir)
        _addUpOneDirLinkIfNotRoot(core, dirPath, rootDir, writeRootPageToGalaxyFn)
        _addLinkToMainDatasetIfRootAndSeparateFile(core, dirPath, rootDir,
                                                   writeRootPageToGalaxyFn)
        _addTableHeader(core)
        _addTableLines(core, dirPath, dirNames, fileNames)
        core.tableFooter()
        core.end()

        outputPath = _determineOutputFilePath(galaxyFn, dirPath, rootDir, writeRootPageToGalaxyFn)
        with open(outputPath, 'w') as outputPage:
            outputPage.write(str(core))

    return GalaxyRunSpecificFile([FILE_BROWSER_FILENAME], galaxyFn) \
        if not writeRootPageToGalaxyFn else None
