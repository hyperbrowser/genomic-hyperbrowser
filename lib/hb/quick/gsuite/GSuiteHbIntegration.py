from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import HbGSuiteTrack, GSuiteTrack
from gold.util.CommonFunctions import prettyPrintTrackName, cleanUpTrackType


def writeGSuiteHiddenTrackStorageHtml(galaxyFn):
    from proto.hyperbrowser.HtmlCore import HtmlCore
    from quick.application.GalaxyInterface import GalaxyInterface

    core = HtmlCore()
    core.append(GalaxyInterface.getHtmlBeginForRuns(galaxyFn))
    core.paragraph('This history element contains GSuite track data, and is hidden by default.')
    core.paragraph('If you want to access the contents of this GSuite, please use the tool: DOES_NOT_EXIST_YET')
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
