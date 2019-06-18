import os
import time
import humanize

from proto.CommonFunctions import isSamePath, getLoadToGalaxyHistoryURL, getFileSuffix, \
    ensurePathExists
from proto.HtmlCore import HtmlCore
from proto.StaticFile import GalaxyRunSpecificFile


FILE_BROWSER_FILENAME = 'files.html'


def generateHtmlFileBrowserForGalaxyFilesDir(crawlDataset, outputDataset,
                                             returnSeparateRootFile=False):
    """
    Generates a HTML-based file browser that provides a clickable overview of all the result files
    in the "dataset_123_files" directory connected to a Galaxy history element. This folder 
    contains all the result files except the main output (which is in the galaxyFn dataset file).
    The file browser is written into a set of files named '{}', one in each directory.
    :param crawlDataset: Path to Galaxy dataset file whose extra files directory should be crawled 
        (e.g. "/path/to/dataset_123.dat"), e.g. "galaxyFn".
    :param outputDataset: Path to Galaxy dataset file where the root file browser HTML should be 
        written, while the additional files (one per directory) will be written to the extra files
        directory. This dataset path could also be set to "galaxyFn".
    :param returnSeparateRootFile:  If True, the root HTML page will be written to a separate file
        (also named '{}') instead of the output dataset. This page is then returned.
    :return: If returnSeparateRootFile is set to True, a GalaxyRunSpecificFile object pointing 
        to the newly created root HTML page is returned. If set to False, None is 
        returned.
    """.format(FILE_BROWSER_FILENAME, FILE_BROWSER_FILENAME)

    # Helper functions

    def _addHeader(core, crawlDirPath, crawlRootDir):
        relDirPath = os.path.abspath(crawlDirPath)[len(os.path.abspath(crawlRootDir)):]
        if not relDirPath:
            relDirPath = '/'
        core.header('File browser for result directory: "{}"'.format(relDirPath))

    def _addUpOneDirLinkIfNotRoot(core, crawlDirPath, crawlRootDir, returnSeparateRootFile):
        if not isSamePath(crawlDirPath, crawlRootDir):
            if isSamePath(os.path.join(crawlDirPath, '..'), crawlRootDir):
                upOneDirPageFn = FILE_BROWSER_FILENAME if returnSeparateRootFile else ''
            else:
                upOneDirPageFn = FILE_BROWSER_FILENAME
            upOneDirLink = str(HtmlCore().link('< Up one directory', '../' + upOneDirPageFn))
            core.paragraph(upOneDirLink)

    def _addLinkToOutputDatasetIfRootAndSeparateFile(core, crawlDirPath, crawlRootDir,
                                                     returnSeparateRootFile):
        if isSamePath(crawlDirPath, crawlRootDir) and returnSeparateRootFile:
            mainDatasetLink = str(HtmlCore().link('< Back to dataset', './'))
            core.paragraph(mainDatasetLink)

    def _addTableHeader(core):
        core.tableHeader(['Name', 'Date Modified', 'Size'],
                         tableClass='auto_width colored bordered')

    def _addTableLines(core, crawlDirPath, crawlDirNames, crawlFileNames):
        filesAndDirs = sorted(zip(crawlDirNames + crawlFileNames,
                                  [True] * len(crawlDirNames) + [False] * len(crawlFileNames)))

        for i, (item, isDir) in enumerate(filesAndDirs):
            fullItemPath = os.path.join(crawlDirPath, item)
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

    def _determineOutputFilePath(outputDataset, crawlDirPath, crawlRootDir,
                                 returnSeparateRootFile):
        if isSamePath(crawlDirPath, crawlRootDir) and not returnSeparateRootFile:
            return outputDataset
        else:
            relPath = os.path.relpath(crawlDirPath, crawlRootDir)
            outputRootDir = GalaxyRunSpecificFile([], outputDataset).getDiskPath()
            outputPath = os.path.join(outputRootDir, relPath, FILE_BROWSER_FILENAME)
            ensurePathExists(outputPath)
            return outputPath

    # Main function

    differentOutputDataset = not isSamePath(crawlDataset, outputDataset)
    crawlRootDir = GalaxyRunSpecificFile([], crawlDataset).getDiskPath()

    for crawlDirPath, crawlDirNames, crawlFileNames in os.walk(crawlRootDir):
        core = HtmlCore()
        core.begin()
        _addHeader(core, crawlDirPath, crawlRootDir)
        _addUpOneDirLinkIfNotRoot(core, crawlDirPath, crawlRootDir, returnSeparateRootFile)
        _addLinkToOutputDatasetIfRootAndSeparateFile(
            core, crawlDirPath, crawlRootDir, returnSeparateRootFile
        )
        _addTableHeader(core)
        _addTableLines(core, crawlDirPath, crawlDirNames, crawlFileNames)
        core.tableFooter()
        core.end()

        outputPath = _determineOutputFilePath(
            outputDataset, crawlDirPath, crawlRootDir, returnSeparateRootFile
        )
        with open(outputPath, 'w') as outputPage:
            outputPage.write(str(core))

    return GalaxyRunSpecificFile([FILE_BROWSER_FILENAME], outputDataset) \
        if returnSeparateRootFile else None
