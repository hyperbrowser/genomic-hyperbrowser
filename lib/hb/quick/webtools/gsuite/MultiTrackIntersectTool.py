import gold.gsuite.GSuiteConstants as GSuiteConstants
from quick.webtools.GeneralGuiTool import GeneralGuiTool


# This is a template prototyping GUI that comes together with a corresponding
# web page.

class MultiTrackIntersectTool(GeneralGuiTool):
    FROM_HISTORY_TEXT = 'From history'
    FROM_HYPERBROWSER_TEXT = 'From HyperBrowser repository'

    WITH_OVERLAPS = 'Allow multiple overlapping points/segments within the same track'
    NO_OVERLAPS = 'Merge any overlapping points/segments within the same track'

    GSUITE_ALLOWED_FILE_FORMATS = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.POINTS,
                                  GSuiteConstants.VALUED_POINTS,
                                  GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]
    GSUITE_DISALLOWED_GENOMES = [GSuiteConstants.UNKNOWN,
                                 GSuiteConstants.MULTIPLE]

    OUTPUT_TRACKS_SUFFIX = 'bed'
    GSUITE_OUTPUT_LOCATION = GSuiteConstants.LOCAL
    GSUITE_OUTPUT_FILE_FORMAT = GSuiteConstants.PREPROCESSED
    GSUITE_OUTPUT_TRACK_TYPE = GSuiteConstants.SEGMENTS

    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''
        return "Intersect preprocessed tracks in GSuite with a single track"

    @staticmethod
    def getInputBoxNames():
        '''
        Specifies a list of headers for the input boxes, and implicitly also the
        number of input boxes to display on the page. The returned list can have
        two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''
        return [('Select genome buid:', 'genome'),
                ('Select GSuite file from history:', 'gSuite'),
                ('Select source of filtering track:', 'trackSource'),
                ('Select track from history:', 'trackHistory'),
                ('Select track:', 'track'),
                ('Overlap handling:', 'withOverlaps')]

    #@staticmethod
    #def getInputBoxOrder():
    #    '''
    #    Specifies the order in which the input boxes should be displayed, as a
    #    list. The input boxes are specified by index (starting with 1) or by
    #    key. If None, the order of the input boxes is in the order specified by
    #    getInputBoxNames.
    #    '''
    #    return None

    @staticmethod
    def getOptionsBoxGenome(): # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to other
        methods. These are lists of results, one for each input box (in the
        order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:  ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list: ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return '__genome__'

    @classmethod
    def getOptionsBoxGSuite(cls, prevChoices): # Alternatively: getOptionsBox2()
        '''
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).
        '''
        return cls.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxTrackSource(cls, prevChoices):
        return [cls.FROM_HISTORY_TEXT, cls.FROM_HYPERBROWSER_TEXT]

    @classmethod
    def getOptionsBoxTrackHistory(cls, prevChoices):
        if prevChoices.trackSource == cls.FROM_HISTORY_TEXT:
            from gold.application.DataTypes import getSupportedFileSuffixesForPointsAndSegments
            return cls.getHistorySelectionElement(*getSupportedFileSuffixesForPointsAndSegments())

    @classmethod
    def getOptionsBoxTrack(cls, prevChoices):
        if prevChoices.trackSource == cls.FROM_HYPERBROWSER_TEXT:
            return cls.TRACK_SELECT_ELEMENT

    @classmethod
    def getOptionsBoxWithOverlaps(cls, prevChoices):
        if prevChoices.trackHistory or prevChoices.track:
            return [cls.NO_OVERLAPS, cls.WITH_OVERLAPS]

    #@staticmethod
    #def getInfoForOptionsBoxKey(prevChoices):
    #    '''
    #    If not None, defines the string content of an clickable info box beside
    #    the corresponding input box. HTML is allowed.
    #    '''
    #    return None

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def getExtraHistElements(cls, choices):
        from quick.webtools.GeneralGuiTool import HistElement
        fileList = []

        if choices.gSuite:
            try:
                from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
                gSuite = getGSuiteFromGalaxyTN(choices.gSuite)

                for track in gSuite.allTracks():
                    fileList.append( HistElement(track.title, cls.OUTPUT_TRACKS_SUFFIX, hidden=True) )

            except:
                pass

        return fileList

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results page
        in Galaxy history. If getOutputFormat is anything else than HTML, the
        output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        import gold.gsuite.GSuiteComposer as GSuiteComposer
        from gold.gsuite.GSuite import GSuite
        from gold.gsuite.GSuiteTrack import GSuiteTrack, HbGSuiteTrack
        from gold.origdata.TrackGenomeElementSource import TrackViewListGenomeElementSource
        from gold.origdata.FileFormatComposer import getComposerClsFromFileSuffix
        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        from quick.application.ExternalTrackManager import ExternalTrackManager
        from quick.application.GalaxyInterface import GalaxyInterface
        from quick.application.UserBinSource import UserBinSource
        from quick.extra.TrackExtractor import TrackExtractor

        genome = choices.genome
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)

        if choices.withOverlaps == cls.NO_OVERLAPS:
            if choices.trackSource == cls.FROM_HISTORY_TEXT:
                filterTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, choices.trackHistory)
            else:
                filterTrackName = choices.track.split(':')
        else:
            if choices.trackSource == cls.FROM_HISTORY_TEXT:
                regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(choices.trackHistory)
                binSpec = ExternalTrackManager.extractFnFromGalaxyTN(choices.trackHistory)
            else:
                regSpec = 'track'
                binSpec = choices.track

            userBinSource = UserBinSource(regSpec, binSpec, genome)

        outGSuite = GSuite()

        analysisDef = '-> TrackIntersectionStat'
#         analysisDef = '-> TrackIntersectionWithValStat'
        for track in gSuite.allTracks():
            histFileName = cls.extraGalaxyFn[track.title]
            galaxyTN = ExternalTrackManager.constructGalaxyTnFromSuitedFn(
                histFileName, fileEnding=cls.OUTPUT_TRACKS_SUFFIX, name=track.title)

            if choices.withOverlaps == cls.NO_OVERLAPS:
                res = GalaxyInterface.runManual([track.trackName, filterTrackName], analysisDef, '*', '*',
                                                 genome=genome, galaxyFn=galaxyFn, username=username)

                trackViewList = [res[key]['Result'] for key in sorted(res.keys())]

                tvGeSource = TrackViewListGenomeElementSource(genome, trackViewList, galaxyTN)

                composerCls = getComposerClsFromFileSuffix(cls.OUTPUT_TRACKS_SUFFIX)
                composerCls(tvGeSource).composeToFile(histFileName)
                #BedComposer(tvGeSource).composeToFile(histFileName)
                #BedGraphComposer(tvGeSource).composeToFile(histFileName)
            else:
                TrackExtractor.extractOneTrackManyRegsToOneFile( \
                    track.trackName, userBinSource, histFileName, fileFormatName=cls.OUTPUT_TRACKS_SUFFIX, \
                    globalCoords=True, asOriginal=False, allowOverlaps=True)

            # Temporary hack until better solution for empty result tracks have been implemented

            from gold.origdata.GenomeElementSource import GenomeElementSource
            geSource = GenomeElementSource(histFileName, genome=genome, suffix=cls.OUTPUT_TRACKS_SUFFIX)

            try:
                geSource.parseFirstDataLine()
            except: # Most likely empty file
                continue

            #
            
            stdTrackName = ExternalTrackManager.getPreProcessedTrackFromGalaxyTN(genome, galaxyTN)

            uri = HbGSuiteTrack.generateURI(trackName=stdTrackName)
            outGSuite.addTrack(GSuiteTrack(uri, title=track.title, trackType=cls.GSUITE_OUTPUT_TRACK_TYPE,
                                           genome=genome, attributes=track.attributes))

        GSuiteComposer.composeToFile(outGSuite, galaxyFn)


    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are not
        valid, an error text explaining the problem should be returned. The GUI
        then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are valid,
        the method should return None, which enables the execute button.
        '''
        errorStr = cls._checkGenome(choices.genome)
        if errorStr:
            return errorStr

        errorStr = cls._checkGSuiteFile(choices.gSuite)
        if errorStr:
            return errorStr

        from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)

        errorStr = cls._checkGSuiteTrackListSize(gSuite)
        if errorStr:
            return errorStr

        errorStr = cls._checkGenomeEquality(choices.genome, gSuite.genome)
        if errorStr:
            return errorStr

        errorStr = cls._checkGSuiteRequirements(
            gSuite,
            allowedFileFormats = cls.GSUITE_ALLOWED_FILE_FORMATS,
            allowedLocations = cls.GSUITE_ALLOWED_LOCATIONS,
            allowedTrackTypes = cls.GSUITE_ALLOWED_TRACK_TYPES,
            disallowedGenomes = cls.GSUITE_DISALLOWED_GENOMES)
        if errorStr:
            return errorStr

        if choices.trackSource == cls.FROM_HISTORY_TEXT:
            trackChoice = 'trackHistory'
        else:
            trackChoice = 'track'

        errorStr = cls._checkTrack(choices, trackChoice, 'genome')
        if errorStr:
            return errorStr

        errorStr = cls._checkBasicTrackType(choices, cls.GSUITE_ALLOWED_TRACK_TYPES,
                                                  trackChoice, 'genome')
        if errorStr:
            return errorStr

    #@staticmethod
    #def getSubToolClasses():
    #    '''
    #    Specifies a list of classes for subtools of the main tool. These
    #    subtools will be selectable from a selection box at the top of the page.
    #    The input boxes will change according to which subtool is selected.
    #    '''
    #    return None
    #
    @staticmethod
    def isPublic():
        '''
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as defined in
        LocalOSConfig.py.
        '''
        return True
    #
    #@staticmethod
    #def isRedirectTool():
    #    '''
    #    Specifies whether the tool should redirect to an URL when the Execute
    #    button is clicked.
    #    '''
    #    return False
    #
    #@staticmethod
    #def getRedirectURL(choices):
    #    '''
    #    This method is called to return an URL if the isRedirectTool method
    #    returns True.
    #    '''
    #    return ''
    #
    #@staticmethod
    #def isHistoryTool():
    #    '''
    #    Specifies if a History item should be created when the Execute button is
    #    clicked.
    #    '''
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    '''
    #    Specifies whether changing the content of texboxes causes the page to
    #    reload.
    #    '''
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    '''
    #    Specifies a list of input boxes which resets the subsequent stored
    #    choices previously made. The input boxes are specified by index
    #    (starting with 1) or by key.
    #    '''
    #    return []
    #
    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.paragraph('Loops through all the tracks in the selected GSuite file and intersects all '
                       'tracks with the specified single filtering track. Only the parts of the '
                       'segments that are intersecting with the filtering track are kept.')

        cls._addGSuiteFileDescription(core,
                                      allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
                                      allowedFileFormats=cls.GSUITE_ALLOWED_FILE_FORMATS,
                                      allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES,
                                      disallowedGenomes=cls.GSUITE_DISALLOWED_GENOMES,
                                      outputLocation=cls.GSUITE_OUTPUT_LOCATION,
                                      outputFileFormat=cls.GSUITE_OUTPUT_FILE_FORMAT,
                                      outputTrackType=cls.GSUITE_OUTPUT_TRACK_TYPE)

        return str(core)
    #
    #@staticmethod
    #def getToolIllustration():
    #    '''
    #    Specifies an id used by StaticFile.py to reference an illustration file
    #    on disk. The id is a list of optional directory names followed by a file
    #    name. The base directory is STATIC_PATH as defined by Config.py. The
    #    full path is created from the base directory followed by the id.
    #    '''
    #    return None
    #
    # @staticmethod
    # def getFullExampleURL():
    #     return 'u/hb-superuser/p/compile-gsuite-from-hyperbrowser-repository--intersect-preprocessed-tracks-in-gsuite-with-a-single-track---example'
    #
    #@classmethod
    #def isBatchTool(cls):
    #    '''
    #    Specifies if this tool could be run from batch using the batch. The
    #    batch run line can be fetched from the info box at the bottom of the
    #    tool.
    #    '''
    #    return cls.isHistoryTool()
    #
    #@staticmethod
    #def isDebugMode():
    #    '''
    #    Specifies whether debug messages are printed.
    #    '''
    #    return False
    #
    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'gsuite'
