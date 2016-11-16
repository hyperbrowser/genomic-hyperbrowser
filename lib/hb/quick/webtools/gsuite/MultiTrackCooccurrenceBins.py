from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteConstants
from gold.track.Track import Track
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.application.GalaxyInterface import GalaxyInterface
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.MultitrackSummarizedInteractionWrapperStat import MultitrackSummarizedInteractionWrapperStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.DebugMixin import DebugMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class MultiTrackCooccurrenceBins(GeneralGuiTool, GenomeMixin,
                                 UserBinMixin, DebugMixin):
    '''
    This is a template prototyping GUI that comes together with a corresponding
    web page.
    '''

    GSUITE_ALLOWED_LOCATIONS = [GSuiteConstants.LOCAL]
    GSUITE_ALLOWED_FILE_TYPES = [GSuiteConstants.PREPROCESSED]
    GSUITE_ALLOWED_TRACK_TYPES = [GSuiteConstants.SEGMENTS,
                                  GSuiteConstants.VALUED_SEGMENTS]

    # Override UserbinMixin bin selector to only allow certain choices
    UserBinMixin.getOptionsBoxCompareIn = lambda self, prevChoises: ['Genes(Ensembl)','Custom specification','Bins from history']
    UserBinMixin.getOptionsBoxBinSize = lambda self, prevChoises: "1m" if prevChoises.CompareIn == 'Custom specification' else None


    @staticmethod
    def getToolName():
        '''
        Specifies a header of the tool, which is displayed at the top of the
        page.
        '''

        #return "Determine regions where GSuite tracks co-occur more strongly"
        return "Rank genomic regions based on pairwise track co-occurrence"

    @classmethod
    def getToolDescription(cls):
        '''
        Specifies a help text in HTML that is displayed below the tool.
        '''
        from proto.hyperbrowser.HtmlCore import HtmlCore


        core = HtmlCore()

        """
        desc = 'This tool ranks specified genomic regions based on average pairwise track co-occurrence. ' + \
                'You will need to specify which regions to rank, by making a choice in the <i>Compare in</i> select box. ' + \
                'It is possible to rank according to <i>minimum</i> or <i>maximum</i> co-occurence instead of <i>average</i> by selecting another <i>summary function</i>.'
        """
        return '' # Not used anymore. Description is hacked in as a input field instead.

    @classmethod
    def getInputBoxNames(cls):
        '''
        Specifies a list of headers for the input boxes, and implicitly also
        the number of input boxes to display on the page. The returned list
        can have two syntaxes:

            1) A list of strings denoting the headers for the input boxes in
               numerical order.
            2) A list of tuples of strings, where each tuple has
               two items: a header and a key.

        The contents of each input box must be defined by the function
        getOptionsBoxK, where K is either a number in the range of 1 to the
        number of boxes (case 1), or the specified key (case 2).

        Note: the key has to be camelCase (e.g. "firstKey")
        '''

        return [    ('', 'description')] +\
                    [('GSuite file to analyse:', 'gsuite')] +\
                    cls.getInputBoxNamesForGenomeSelection() +\
                    [('Select how to concatinate the computed statistic over tracks inside a bin: ', 'summaryFunc')] +\
                    [('Choose how to select regions/bins to rank: ','CompareIn'),('Which regions/bins: (comma separated list, * means all)', 'Bins'), ('Genome region: (Example: chr1:1-20m, chr2:10m-) ','CustomRegion'),\
                            ('Bin size: (* means whole region k=Thousand and m=Million E.g. 100k)', 'BinSize'), ('Bins from history', 'HistoryBins')] +\
                    DebugMixin.getInputBoxNamesForDebug()

    @staticmethod
    def getOptionsBoxDescription():  # Alternatively: getOptionsBox1()
        desc = '<b>Description: </b> This tool ranks specified genomic regions (bins) based on average pairwise track co-occurrence. ' + \
                'You will need to specify which bins you want to rank. This will typically be done by selecting <i>Custom specification</i>' + \
                ' and choosing a main region (e.g. <i>chr1, chr2</i>) and a bin size, resulting in evenly distributed bins within those regions, all having the same size. ' +\
                '<br><br>These bins are ranked based on the average pairwise statistic between tracks inside each bin.' + \
                ' You can instead choose to rank based on the <i>maximum</i> pairwise statistic over all pairs of tracks, by selecting that option in the select menu. <br><hr><br>'
        return '__rawstr__', desc


    @staticmethod
    def getOptionsBoxGsuite(prevChoises):  # Alternatively: getOptionsBox1()
        '''
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to
        other methods. These are lists of results, one for each input box
        (in the order specified by getInputBoxOrder()).

        The input box is defined according to the following syntax:

        Selection box:          ['choice1','choice2']
        - Returns: string

        Text area:              'textbox' | ('textbox',1) | ('textbox',1,False)
        - Tuple syntax: (contents, height (#lines) = 1, read only flag = False)
        - The contents is the default value shown inside the text area
        - Returns: string

        Raw HTML code:          '__rawstr__', 'HTML code'
        - This is mainly intended for read only usage. Even though more
        advanced hacks are possible, it is discouraged.

        Password field:         '__password__'
        - Returns: string

        Genome selection box:   '__genome__'
        - Returns: string

        Track selection box:    '__track__'
        - Requires genome selection box.
        - Returns: colon-separated string denoting track name

        History selection box:
        ('__history__',) | ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting galaxy track name, as
                   specified in ExternalTrackManager.py.

        History check box list:
        ('__multihistory__', ) | ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with galaxy id as key and galaxy track name
                   as value if checked, else None.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:
        [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:
         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''
        return ('__history__',)

    # @staticmethod
    # def getOptionsBoxBinSize(prevChoices):  # Alternatively: getOptionsBox1()
    #
    #     if prevChoices.CompareIn == 'Custom specification':
    #         return ('1000000')

    @staticmethod
    def getOptionsBoxQuestion(prevChoices):  # Alternatively: getOptionsBox1()
        return ['question 6', 'question 7', 'question 8']

    @staticmethod
    def getOptionsBoxStat(prevChoices):
        return [
                'PropOfReferenceTrackInsideTargetTrackStat',
                'PropOfReferenceTrackInsideUnionStat',
                'RatioOfIntersectionToGeometricMeanStat',
                'RatioOfOverlapToUnionStat'
                ]

    @staticmethod
    def getOptionsBoxSummaryFunc(prevChoices):

        # Hack: Return raw html since this select box gives short uninformative names:
        html = "<p>Select how to combine the computed statistic over tracks:</p><p><select name='summaryFunc'>" + \
               "<option value='avg'>Take the average over all tracks</option>" + \
               "<option value='max'>Take the maximum value over all tracks</option>" + \
               "</select></p>"

        return '__rawstr__', html

        #return sorted(SummarizedInteractionWithOtherTracksStatUnsplittable.
        #              functionDict.keys())

    @staticmethod
    def getOptionsBoxPermutationStrat(prevChoices):
        '''hardcoded for now to 'PermutedSegsAndIntersegsTrack' '''
        return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than HTML,
        the output should be written to the file with path galaxyFn. If needed,
        StaticFile can be used to get a path where additional files can be put
        (e.g. generated image files). choices is a list of selections made by
        web-user in each options box.
        '''

        cls._setDebugModeIfSelected(choices)

        # Stat question 7
        core = HtmlCore()
        core.begin()
        core.divBegin(divClass='resultsExplanation')
        core.paragraph('''
             You here see all the chosen bins, ranked by co-occurrence of tracks within each bin.
            ''')
        core.divEnd()


        analysisSpec = AnalysisSpec(MultitrackSummarizedInteractionWrapperStat)
        analysisSpec.addParameter('pairwiseStatistic', 'ObservedVsExpectedStat')
        analysisSpec.addParameter('summaryFunc', choices.summaryFunc)
        analysisSpec.addParameter('multitrackSummaryFunc', choices.summaryFunc)
        gsuite = getGSuiteFromGalaxyTN(choices.gsuite)
        tracks = [Track(x.trackName) for x in gsuite.allTracks()]

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        analysisBins = GalaxyInterface._getUserBinSource(regSpec,
                                                         binSpec,
                                                         choices.genome)
        results = doAnalysis(analysisSpec, analysisBins, tracks)

        prettyResults = {}
        for key, val in results.iteritems():
            if "Result" in val.keys():
                prettyResults[key] = val["Result"]
            else:
                prettyResults[key] = "No result"

        core.header("Average of the Forbes similarity measure for pairs of tracks within each bin")
        topTrackTitle = results.keys()[0]
        """
        core.paragraph('''
            Suite data is coinciding the most in bin %s
        ''' % ('test'))
        """

        visibleRows = 20
        makeTableExpandable = len(prettyResults) > visibleRows
        core.tableFromDictionary(prettyResults, tableId='res', presorted=0,
                                 columnNames=['Bin', 'Co-occurrence within the bin'], sortable=True,
                                 expandable=makeTableExpandable, visibleRows=visibleRows)
        core.divEnd()
        core.end()

        print str(core)
        #print results



    @classmethod
    def validateAndReturnErrors(cls, choices):
        '''
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned. The
        GUI then shows this text to the user (if not empty) and greys out the
        execute button (even if the text is empty). If all parameters are
        valid, the method should return None, which enables the execute button.
        '''

        errorString = GeneralGuiTool._checkGSuiteFile(choices.gsuite)
        if errorString:
            return errorString

        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)

        errorString = GeneralGuiTool._checkGSuiteRequirements(
            gSuite,
            allowedLocations=cls.GSUITE_ALLOWED_LOCATIONS,
            allowedFileFormats=cls.GSUITE_ALLOWED_FILE_TYPES,
            allowedTrackTypes=cls.GSUITE_ALLOWED_TRACK_TYPES)

        if errorString:
            return errorString

        errorString = cls.validateUserBins(choices)
        if errorString:
            return errorString

        return None

    @staticmethod
    def isDynamic():
        '''
        Specifies whether changing the content of texboxes causes the page to
        reload.
        '''
        return True

    @staticmethod
    def isDebugMode():
        '''
        Specifies whether the debug mode is turned on.
        '''
        return True

    @staticmethod
    def getOutputFormat(choices):
        '''
        The format of the history element with the output of the tool. Note
        that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.In the latter
        case, all all print statements are redirected to the info field of the
        history item box.
        '''
        return 'customhtml'
