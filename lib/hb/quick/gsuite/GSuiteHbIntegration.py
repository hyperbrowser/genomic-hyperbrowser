import re

from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import HbGSuiteTrack, GSuiteTrack
from gold.util.CommonFunctions import prettyPrintTrackName, cleanUpTrackType, \
    extractNameFromDatasetInfo

GSUITE_HISTORY_OUTPUT_NAME_DICT = {
    'progress': 'Progress (%s)',
    'remote': 'GSuite (%s) - ready for download',
    'primary': 'GSuite (%s) - ready for manipulation or preprocessing',
    'preprocessed': 'GSuite (%s) - ready for analysis',
    'nodownload': 'GSuite (%s) - files that failed to download (select in '
                  '"Convert GSuite tracks from remote to primary" to retry)',
    'nopreprocessed': 'GSuite (%s) - files that failed preprocessing (select '
                      'in "Preprocess a GSuite for analysis" to retry)',
    'nomanipulate': 'GSuite (%s) - files that failed manipulation (select '
                    'in "Modify primary tracks referred to in a GSuite" to retry)',
    'nointersect': 'GSuite (%s) - files that failed intersection (in most cases due '
                   'to lack of segments in the intersection regions)',
    'storage': 'GSuite (%s) - track storage'
}


def getGSuiteHistoryOutputName(type, description='', datasetInfo=None):
    """
    :param type: one of 'progress', 'remote', 'primary', 'preprocessed', 'nodownload',
        'nopreprocess', or 'storage'.
    :param description: a string containing a description.
    :param datasetInfo: a datasetInfo list of a input history element, which will be parsed in
        order to extract a file description. If it contains parentheses, the method
        assumes it has also been produced by getGSuiteHistoryOutputName(), and extracts
        the content within the parentheses. If no parentheses is found, the full name is used.
        If both a datasetInfo and a description parameter is used, the value of the description
        is added to the end of the file description from the datasetInfo parameter.
    :return: string containing the name of an output history element
    """
    assert type == 'same' or type in GSUITE_HISTORY_OUTPUT_NAME_DICT.keys()
    if type == 'same':
        assert datasetInfo is not None

    if datasetInfo:
        datasetName = extractNameFromDatasetInfo(datasetInfo)

        match = re.search('\(.+\)', datasetName)
        if match:
            lastDesc = match.group(0)[1:-1]
        else:
            lastDesc = datasetName

        if description:
            description = lastDesc + description
        else:
            description = lastDesc

        if type == 'same':
            datasetName = re.sub('^[0-9]+ - ', '', datasetName)
            return datasetName.replace(lastDesc, description)

    return GSUITE_HISTORY_OUTPUT_NAME_DICT[type] % description


def writeGSuiteHiddenTrackStorageHtml(galaxyFn):
    from proto.hyperbrowser.HtmlCore import HtmlCore
    from quick.application.GalaxyInterface import GalaxyInterface

    core = HtmlCore()
    core.append(GalaxyInterface.getHtmlBeginForRuns(galaxyFn))
    core.paragraph('This history element contains GSuite track data, and is hidden by default.')
    core.paragraph('If you want to access the contents of this GSuite, please use the tool: '
                   '"Export primary tracks from a GSuite to your history", selecting '
                   'a primary GSuite history element that refers to the files contained '
                   'in this storage.')
    core.end()
    core.append(GalaxyInterface.getHtmlEndForRuns())

    with open(galaxyFn, 'w') as outputFile:
        outputFile.write(str(core))


def getAnalysisQuestionInfoHtml(bmQid):
    '''
    Builds the div element that contains the appropriate basic mode analysis question.
    '''
    from quick.toolguide import BasicModeQuestionCatalog
    from proto.hyperbrowser.HtmlCore import HtmlCore

    if bmQid:
        htmlCore = HtmlCore()
        htmlCore.divBegin(divClass='analysis-info')
        prgrph = '''
    <b>Your question of interest was: %s<b>
    ''' % BasicModeQuestionCatalog.Catalog[bmQid]
        htmlCore.paragraph(prgrph)
        htmlCore.divEnd()
        return htmlCore


def getSubtracksAsGSuite(genome, parentTrack, username=''):
    from gold.description.TrackInfo import TrackInfo
    from quick.application.GalaxyInterface import GalaxyInterface
    from quick.application.ProcTrackNameSource import ProcTrackNameSource

    fullAccess = GalaxyInterface.userHasFullAccess(username)
    procTrackNameSource = ProcTrackNameSource(genome, fullAccess=fullAccess,
                                              includeParentTrack=False)

    gSuite = GSuite()
    for trackName in procTrackNameSource.yielder(parentTrack):
        trackType = TrackInfo(genome, trackName).trackFormatName.lower()
        trackType = cleanUpTrackType(trackType)
        uri = HbGSuiteTrack.generateURI(trackName=trackName)
        title = prettyPrintTrackName(trackName)
        if title.startswith("'") and title.endswith("'") and len(title) > 1:
            title = title[1:-1]
        gSuite.addTrack(GSuiteTrack(uri, title=title, trackType=trackType, genome=genome))

    return gSuite
