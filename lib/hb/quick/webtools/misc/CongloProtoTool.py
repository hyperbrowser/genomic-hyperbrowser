from collections import OrderedDict
from itertools import product
from conglomerate.methods.giggle.giggle import Giggle
from conglomerate.tools.job import Job

#FIXME: REMOVE!!
from conglomerate.methods.stereogene.stereogene import StereoGene
from quick.application.ExternalTrackManager import ExternalTrackManager



class RestrictedAnalysisUniverse:
    pass
class RestrictedThroughExclusion(RestrictedAnalysisUniverse):
    def __init__(self, path):
        pass

from quick.webtools.GeneralGuiTool import GeneralGuiTool
import collections


class CongloProtoTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "CongloProtoTool"

    @classmethod
    def getInputBoxNames(cls):
        """
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

        Note: the key has to be camelCase and start with a non-capital letter
              (e.g. "firstKey")

        Optional method. Default return value if method is not defined: []
        """
        return [('Select the reference genome: ', 'selectReferenceGenome'),
                ('Choose a file with chromosome lengths of a custom genome build : ', 'chooseChrnLenFile'),
                ('Type of co-localization analysis: ', 'analysisType'),
                ('Choose a query track: ', 'chooseQueryTrackFile'),
                ('Choose a reference track: ', 'chooseReferenceTrackFile'),
                ('Choose a type of reference track collection', 'typeOfReferenceTrackCollection'),
                ('Choose a core data collection', 'choiceOfCoreDatabase'),
                ('Choose a custom reference track collection', 'chooseCustomTrackCollection'),
                ('Use one of the default core databases as reference collection ? ', 'optionalUseOfCoreDatabase'),
                ('Choose a query track collection: ', 'chooseQueryTrackCollection'),
                ('Choose a reference track collection: ', 'chooseReferenceTrackCollection'),
                ('Type of co-localization measure (test statistic): ', 'teststatType'),
                ('Type of overlap measure : ', 'overlapMeasure'),
                ('Type of coordinate to use when computing distance : ', 'distanceCoordinate'),
                ('Type of distance to use : ', 'distanceType'),
                ('Type of correlation metric : ', 'correlation'),
                ('Allow genomic regions to overlap within track ? ', 'allowOverlaps'),
                ('Restrict the analysis to specific parts of the genome ? ', 'restrictRegions'),
                ('Select the uploaded file to restrict the analysis space : ', 'restrictedRegionFileUpload'),
                ('Preserve local heterogeneity ? ', 'localHeterogeneity'),
                ('Method of choice to preserve local heterogeneity : ', 'localHandler'),
                ('Select the uploaded file to preserve local heterogeneity : ', 'preserveLocalFileUpload'),
                ('Preserve any clumping tendency of genomic elements ? ', 'clumping'),
                ('Handle confounding features ? ', 'confounding'),
                ('Method of choice to handle confounding features : ', 'confounderHandler'),
                ]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     """
    #     Specifies the order in which the input boxes should be displayed,
    #     as a list. The input boxes are specified by index (starting with 1)
    #     or by key. If None, the order of the input boxes is in the order
    #     specified by getInputBoxNames().
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     """
    #     Creates a visual separation of groups of consecutive option boxes
    #     from the rest (fieldset). Each such group has an associated label
    #     (string), which is shown to the user. To define groups of option
    #     boxes, return a list of BoxGroup namedtuples with the label, the key
    #     (or index) of the first and last options boxes (inclusive).
    #
    #     Example:
    #        from quick.webtool.GeneralGuiTool import BoxGroup
    #        return [BoxGroup(label='A group of choices', first='firstKey',
    #                         last='secondKey')]
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    CUSTOM_REFERENCE_GENOME = 'Custom reference genome'

    @classmethod
    def getOptionsBoxSelectReferenceGenome(cls):  # Alt: getOptionsBox1()
        return ['Human (hg19)','Human (hg38)', cls.CUSTOM_REFERENCE_GENOME]

    @classmethod
    def getOptionsBoxChooseChrnLenFile(cls, prevChoices):
        if prevChoices.selectReferenceGenome == cls.CUSTOM_REFERENCE_GENOME:
            return ('__history__',)

    TWO_TRACK_GROUPS = 'Pairwise comparison of all tracks between two track-groups'
    REFERENCE_TRACKS = 'Query track against collection of reference tracks'
    TWO_GENOMIC_TRACKS = 'Relation between two genomic tracks'

    @classmethod
    def getOptionsBoxAnalysisType(cls, prevChoices):  # Alt: getOptionsBox1()
        """
        Defines the type and contents of the input box. User selections are
        returned to the tools in the prevChoices and choices attributes to
        other methods. These are lists of results, one for each input box
        (in the order specified by getInputBoxOrder()).

        Mandatory for the first key defined in getInputBoxNames(), if any.

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

        History selection box:  ('__history__',) |
                                ('__history__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: colon-separated string denoting Galaxy dataset info, as
            described below.

        History check box list: ('__multihistory__', ) |
                                ('__multihistory__', 'bed', 'wig')
        - Only history items of specified types are shown.
        - Returns: OrderedDict with Galaxy dataset ids as key (the number YYYY
            as described below), and the associated Galaxy dataset info as the
            values, given that the history element is ticked off by the user.
            If not, the value is set to None. The Galaxy dataset info structure
            is described below.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'],
                                 ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False),
                                             ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).


        ###
        Note about the "Galaxy dataset info" data structure:
        ###

        "Galaxy dataset info" is a list of strings coding information about a
        Galaxy history element and its associated dataset, typically used to
        provide info on the history element selected by the user as input to a
        ProTo tool.

        Structure:
            ['galaxy', fileFormat, path, name]

        Optionally encoded as a single string, delineated by colon:

            'galaxy:fileFormat:path:name'

        Where:
            'galaxy' used for assertions in the code
            fileFormat (or suffix) contains the file format of the dataset, as
                encoded in the 'format' field of a Galaxy history element.
            path (or file name/fn) is the disk path to the dataset file.
                Typically ends with 'XXX/dataset_YYYY.dat'. XXX and YYYY are
                numbers which are extracted and used as an unique id  of the
                dataset in the form [XXX, YYYY]
            name is the title of the history element

        The different parts can be extracted using the functions
        extractFileSuffixFromDatasetInfo(), extractFnFromDatasetInfo(), and
        extractNameFromDatasetInfo() from the module CommonFunctions.py.
        """
        return [cls.TWO_GENOMIC_TRACKS, cls.REFERENCE_TRACKS, cls.TWO_TRACK_GROUPS]

    @classmethod
    def getOptionsBoxChooseQueryTrackFile(cls, prevChoices):
        if prevChoices.analysisType in [cls.TWO_GENOMIC_TRACKS,cls.REFERENCE_TRACKS]:
            return ('__history__',)

    @classmethod
    def getOptionsBoxChooseReferenceTrackFile(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_GENOMIC_TRACKS:
            return ('__history__',)

    CUSTOM_DATABASE = 'Use custom datasets to build a set of reference tracks'
    CORE_DATABASE = 'Use core database as the set of reference tracks'

    @classmethod
    def getOptionsBoxTypeOfReferenceTrackCollection(cls, prevChoices):
        if prevChoices.analysisType == cls.REFERENCE_TRACKS:
            return [cls.CORE_DATABASE, cls.CUSTOM_DATABASE]

    @classmethod
    def getOptionsBoxChoiceOfCoreDatabase(cls, prevChoices):
        if prevChoices.typeOfReferenceTrackCollection == cls.CORE_DATABASE:
            return ['LOLA data collection','GIGGLE data collection', 'GSuite Hyperbrowser data collection']

    @classmethod
    def getOptionsBoxChooseCustomTrackCollection(cls, prevChoices):
        if prevChoices.typeOfReferenceTrackCollection == cls.CUSTOM_DATABASE:
            return ('__history__',)

    @classmethod
    def getOptionsBoxChooseQueryTrackCollection(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_TRACK_GROUPS:
            return ('__history__',)

    @classmethod
    def getOptionsBoxOptionalUseOfCoreDatabase(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_TRACK_GROUPS:
            return ['Yes', 'No']

    @classmethod
    def getOptionsBoxChooseReferenceTrackCollection(cls, prevChoices):
        if prevChoices.optionalUseOfCoreDatabase == 'Yes':
            return ['LOLA data collection', 'GIGGLE data collection', 'GSuite Hyperbrowser data collection']
        elif prevChoices.optionalUseOfCoreDatabase == 'No':
            return ('__history__',)

    # OVERLAP_MEASURES = [COUNTS, BASES]

    FLANKING_REGIONS = 'basepair overlap including expansion of flanking regions'
    DIRECT_OVERLAP = 'direct basepair overlap between genomic regions'
    CORRELATION = 'Correlation'
    DISTANCE = 'Proximity (distance)'
    OVERLAP = 'Overlap'

    @classmethod
    def getOptionsBoxTeststatType(cls, prevChoices):  # Alt: getOptionsBox2()
        """
        See getOptionsBoxFirstKey().

        prevChoices is a namedtuple of selections made by the user in the
        previous input boxes (that is, a namedtuple containing only one element
        in this case). The elements can accessed either by index, e.g.
        prevChoices[0] for the result of input box 1, or by key, e.g.
        prevChoices.key (case 2).

        Mandatory for the subsequent keys (after the first key) defined in
        getInputBoxNames(), if any.
        """
        return OrderedDict([(cls.OVERLAP, False), (cls.DISTANCE, False), (cls.CORRELATION, False)])

    BASES = 'total number of overlapping bases'
    COUNTS = 'number of overlapping regions (counts)'

    @classmethod
    def getOptionsBoxOverlapMeasure(cls, prevChoices):
        if prevChoices.teststatType and prevChoices.teststatType[cls.OVERLAP]:
            return OrderedDict([(cls.COUNTS, False), (cls.BASES, False)])

    # @classmethod
    # def getOptionsBoxDirectOverlap(cls, prevChoices):
    #     if prevChoices.typeOfOverlap and prevChoices.typeOfOverlap[DIRECT_OVERLAP]:
    #         return OVERLAP_MEASURES
    #
    # @classmethod
    # def getOptionsBoxFlankingRegions(cls, prevChoices):
    #     if prevChoices.typeOfOverlap and prevChoices.typeOfOverlap[FLANKING_REGIONS]:
    #         return OVERLAP_MEASURES
    #
    # @classmethod
    # def getOptionsBoxFlankingSizeUpstream(cls, prevChoices):
    #     if prevChoices.flankingRegions and prevChoices.flankingRegions in OVERLAP_MEASURES:
    #         return '1000'
    #
    # @classmethod
    # def getOptionsBoxFlankingSizeDownstream(cls, prevChoices):
    #     if prevChoices.flankingRegions and prevChoices.flankingRegions in OVERLAP_MEASURES:
    #         return '1000'

    CLOSEST_COORDINATE = 'distance to closest coordinate'
    END_COORDINATE = 'distance to end coordinate'
    MIDPOINT = 'distance to midpoint'
    START_COORDINATE = 'distance to start coordinate'

    @classmethod
    def getOptionsBoxDistanceCoordinate(cls, prevChoices):
        if prevChoices.teststatType and prevChoices.teststatType[cls.DISTANCE]:
            return OrderedDict([(cls.START_COORDINATE, False), (cls.MIDPOINT, False),(cls.CLOSEST_COORDINATE, False)])

    AVERAGE_LOG_DISTANCE = 'average log distance'
    ABSOLUTE_DISTANCE = 'absolute distance'

    @classmethod
    def getOptionsBoxDistanceType(cls, prevChoices):
        if prevChoices.distanceCoordinate and any(prevChoices.distanceCoordinate.values()):
            return OrderedDict([(cls.ABSOLUTE_DISTANCE, False), (cls.AVERAGE_LOG_DISTANCE, False)])

    @classmethod
    def getOptionsBoxCorrelation(cls, prevChoices):
        if prevChoices.teststatType and prevChoices.teststatType[cls.CORRELATION]:
            return ['genome-wide kernel correlation (overall relationship)','fine-scale correlation (structure of correlation)','local correlation (genomic region-level)']

    DETERMINE_FROM_SUBMITTED_TRACKS = 'determine whether or not to allow overlap based on submitted tracks'
    MAY_OVERLAP = 'elements may overlap'
    NOT_ALLOWED = 'elements not allowed to overlap'

    @classmethod
    def getOptionsBoxAllowOverlaps(cls, prevChoices):  # Alt: getOptionsBox2()
        return OrderedDict([(cls.NOT_ALLOWED,False), (cls.MAY_OVERLAP,False), (cls.DETERMINE_FROM_SUBMITTED_TRACKS,False)])

    EXPLICIT_NEGATIVE_SET = 'Perform the analysis only in the explicit set of background regions supplied'
    EXCLUDE_SUPPLIED_BY_THE_USER = 'Yes, exclude specified regions supplied by the user'
    WHOLE_GENOME = 'No, use the whole genome'

    @classmethod
    def getOptionsBoxRestrictRegions(cls, prevChoices):  # Alt: getOptionsBox2()
        return [cls.WHOLE_GENOME, cls.EXCLUDE_SUPPLIED_BY_THE_USER, cls.EXPLICIT_NEGATIVE_SET]

    @classmethod
    def getOptionsBoxRestrictedRegionFileUpload(cls, prevChoices):
        if prevChoices.restrictRegions in [cls.EXCLUDE_SUPPLIED_BY_THE_USER, cls.EXPLICIT_NEGATIVE_SET]:
            return '__track__'


    @classmethod
    def getOptionsBoxLocalHeterogeneity(cls, prevChoices):  # Alt: getOptionsBox2()
        return ['No, distribute genomic regions across the whole genome', cls.LOCAL_HETEROGENEITY]

    FIXED_SIZE_NEIGHBOURHOOD = 'each genomic region restricted to a fixed size neighbourhood'
    SET_OF_LOCAL_REGIONS_ = 'distribute within a specified set of local regions '

    @classmethod
    def getOptionsBoxLocalHandler(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.localHeterogeneity == cls.LOCAL_HETEROGENEITY:
            return [cls.FIXED_SIZE_NEIGHBOURHOOD, cls.SET_OF_LOCAL_REGIONS_]

    @classmethod
    def getOptionsBoxPreserveLocalFileUpload(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.localHandler == cls.SET_OF_LOCAL_REGIONS_:
            return '__track__'

    PRESERVE_EMPIRIC_DISTRIBUTION = 'Yes, preserve empiric distribution of distances between genomic regions'
    UNIFORMLY_DISTRIBUTED = 'No, assume that genomic features are uniformly distributed'

    @classmethod
    def getOptionsBoxClumping(cls, prevChoices):  # Alt: getOptionsBox2()
        return OrderedDict([(cls.UNIFORMLY_DISTRIBUTED, False), (cls.PRESERVE_EMPIRIC_DISTRIBUTION, False)])

    CONFOUNDING_FEATURE = 'Yes, handle the specified confounding feature'
    LOCAL_HETEROGENEITY = 'Yes, handle local heterogeneity'

    @classmethod
    def getOptionsBoxConfounding(cls, prevChoices):  # Alt: getOptionsBox2()
        return ['No, I am not aware of any potential confounding feature for this analysis',
                cls.CONFOUNDING_FEATURE]

    @classmethod
    def getOptionsBoxConfounderHandler(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.confounding == cls.CONFOUNDING_FEATURE:
            return ['Shuffle genomic locations according to a non-homogenous Poisson process',
                    'Partial correlation', 'Stratified sampling']

    # @classmethod
    # def getInfoForOptionsBoxKey(cls, prevChoices):
    #     """
    #     If not None, defines the string content of an clickable info box
    #     beside the corresponding input box. HTML is allowed.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getDemoSelections(cls):
    #     """
    #     Defines a set of demo inputs to the option boxes in the
    #     order defined by getOptionBoxNames and getOptionsBoxOrder.
    #     If not None, a Demo button appears in the interface. Clicking the
    #     button fills the option boxed with the defined demo values.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return ['testChoice1', '..']
    #
    # @classmethod
    # def getExtraHistElements(cls, choices):
    #     """
    #     Defines extra history elements to be created when clicking execute.
    #     This is defined by a list of HistElement objects, as in the
    #     following example:
    #
    #        from proto.GeneralGuiTool import HistElement
    #        return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]
    #
    #     It is good practice to use class constants for longer strings.
    #
    #     In the execute() method, one typically needs to fetch the path to
    #     the dataset referred to by the extra history element. To fetch the
    #     path, use the dict cls.extraGalaxyFn with the defined history title
    #     as key, e.g. "cls.extraGalaxyFn[cls.HISTORY_TITLE]".
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        """
        Is called when execute-button is pushed by web-user. Should print
        output as HTML to standard out, which will be directed to a results
        page in Galaxy history. If getOutputFormat is anything else than
        'html', the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional
        files can be put (cls, e.g. generated image files). choices is a list
        of selections made by web-user in each options box.

        Mandatory unless isRedirectTool() returns True.
        """
        # ('Choose a query track: ', 'chooseQueryTrackFile'),
        # ('Choose a reference track: ', 'chooseReferenceTrackFile'),

        selections, typeOfAnalysis = cls.parseChoices(choices)

        from conglomerate.conglomerate.tools.method_compatibility import getCompatibleMethodObjects
        queryTrack = ['dummy1']
        refTracks = ['dummy2', 'dummy3']
        from conglomerate.methods.genometricorr.genometricorr import GenometriCorr
        methodClasses = [GenometriCorr, StereoGene]

        #queryTrack = cls.getFnListFromTrackChoice(choices.chooseQueryTrackFile)
        #refTracks = cls.getFnListFromTrackChoice(choices.chooseReferenceTrackFile)

        workingMethodObjects = getCompatibleMethodObjects(selections, queryTrack, refTracks, methodClasses)
        print selections
        print typeOfAnalysis
        print workingMethodObjects

    @classmethod
    def getFnListFromTrackChoice(cls, trackChoice):
        filetype = ExternalTrackManager.extractFileSuffixFromGalaxyTN(trackChoice)
        if filetype in ['bed']:
            fnList = [ExternalTrackManager.extractFnFromGalaxyTN(trackChoice)]
        elif filetype in ['gsuite']:
            gsuite = ExternalTrackManager.extractFnFromGalaxyTN(trackChoice)
            fnList = [gsTrack.path for gsTrack in gsuite.allTracks()]
        else:
            print 'ERROR: ', filetype, ExternalTrackManager.extractFnFromGalaxyTN(trackChoice)
        return fnList

    @classmethod
    def parseChoices(cls, choices):
        selections = OrderedDict()
        typeOfAnalysis = choices.analysisType
        # SELECTION BOXES:
        chrLenFnMappings = {'Human (hg19)': 'chrom_lengths.tabular'}
        genomeName = choices.selectReferenceGenome
        selections['setGenomeName'] = genomeName
        selections['setChrLenFn'] = chrLenFnMappings[genomeName]
        # mapping = {cls.WHOLE_GENOME:None,
        #            cls.EXCLUDE_SUPPLIED_BY_THE_USER:RestrictedThroughExclusion(fn)}
        if choices.restrictRegions == cls.WHOLE_GENOME:
            restrictRegions = None
        else:
            fn = ExternalTrackManager.extractFnFromGalaxyTN(choices.restrictedRegionFileUpload)
            if choices.restrictRegions == cls.EXCLUDE_SUPPLIED_BY_THE_USER:
                restrictRegions = RestrictedThroughExclusion(fn)
            if choices.restrictRegions == cls.EXPLICIT_NEGATIVE_SET:
                raise
        selections['setRestrictedAnalysisUniverse'] = ('setRestrictedAnalysisUniverse', restrictRegions)
        # import PRESERVE_HETEROGENEITY_AS_NEIGHBORHOOD ... from conglo..
        # if choices.localHandler == None:
        #     hetero = PRESERVE_HETEROGENEITY_NOT
        # elif choices.localHandler==FIXED_SIZE_NEIGHBOURHOOD:
        #      hetero = PRESERVE_HETEROGENEITY_AS_NEIGHBORHOOD
        # elif choices.localHandler==SET_OF_LOCAL_REGIONS_:
        #     fn = ExternalTrackManager.extractFnFromGalaxyTN(choices.preserveLocalFileUpload)
        #     hetero = [PRESERVE_HETEROGENEITY_WITHIN_SUPPLIED_REGIONS, fn]
        # selections['setHeterogeneityPreservation'] = hetero
        # CHECKBOXES
        choiceValueMappings = OrderedDict()
        selectionMapping = {'allowOverlaps': 'setAllowOverlaps',
                            'clumping': 'preserveClumping'}
        # TestStat
        distCoordSelected = [key for key in choices.distanceCoordinate if choices.distanceCoordinate[key]]
        distTypeSelected = [key for key in choices.distanceType if choices.distanceType[key]]
        fullDistSpecs = product(distCoordSelected, distTypeSelected)
        encodedDistSpecs = ['-'.join(spec) for spec in fullDistSpecs]
        overlapSpecs = [key for key in choices.overlapMeasure if choices.overlapMeasure[key]]
        correlationSpecs = [key for key in choices.correlation if choices.correlation[key]]
        allTsSpecs = encodedDistSpecs + overlapSpecs + correlationSpecs
        selections['setTestStatistic'] = zip(['TestStatistic'] * len(allTsSpecs), allTsSpecs)
        # distCoordSelections = cls.getSelectionsFromCheckboxParam(distCoordChoiceValueMapping, choices, 'distanceCoordinate', 'distCoord')
        # distCoordSelections = cls.getSelectionsFromCheckboxParam(distCoordChoiceValueMapping, choices, 'distanceType', 'distType')
        if choices.allowOverlaps[cls.DETERMINE_FROM_SUBMITTED_TRACKS]:
            raise
        else:
            choiceValueMappings['allowOverlaps'] = {cls.NOT_ALLOWED: False, cls.MAY_OVERLAP: True}
        choiceValueMappings['clumping'] = {cls.UNIFORMLY_DISTRIBUTED: False, cls.PRESERVE_EMPIRIC_DISTRIBUTION: True}
        for guiKey, selectionKey in selectionMapping.items():
            selections.update(
                cls.getSelectionsFromCheckboxParam(choiceValueMappings[guiKey], choices, guiKey, selectionKey))
        return selections, typeOfAnalysis

    @classmethod
    def getSelectionsFromCheckboxParam(cls, choiceValueMappings, choiceTuple, selectionName, selectionsKey):
        choices = choiceTuple._asdict()
        selections = {selectionsKey:[]}
        for choiceName, val in choiceValueMappings.items():
            if choices[selectionName][choiceName]:
                selections[selectionsKey].append((selectionsKey, val))
        return selections

    @classmethod
    def validateAndReturnErrors(cls, choices):
        """
        Should validate the selected input parameters. If the parameters are
        not valid, an error text explaining the problem should be returned.
        The GUI then shows this text to the user (if not empty) and greys
        out the execute button (even if the text is empty). If all
        parameters are valid, the method should return None, which enables
        the execute button.

        Optional method. Default return value if method is not defined: None
        """
        if choices.allowOverlaps[cls.DETERMINE_FROM_SUBMITTED_TRACKS]:
            if choices.allowOverlaps[cls.MAY_OVERLAP] or choices.allowOverlaps[cls.NOT_ALLOWED]:
                return "%s can only be selected as a single choice" % cls.DETERMINE_FROM_SUBMITTED_TRACKS
        else:
            if not choices.allowOverlaps[cls.NOT_ALLOWED] and not choices.allowOverlaps[cls.MAY_OVERLAP]:
                return "Please select whether or not to allow genomic regions to overlap within track"


            # @classmethod
    # def getSubToolClasses(cls):
    #     """
    #     Specifies a list of classes for subtools of the main tool. These
    #     subtools will be selectable from a selection box at the top of the
    #     page. The input boxes will change according to which subtool is
    #     selected.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     """
    #     Specifies whether the tool is accessible to all users. If False, the
    #     tool is only accessible to a restricted set of users as well as admin
    #     users, as defined in the galaxy.ini file.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     """
    #     Specifies whether the tool should redirect to an URL when the Execute
    #     button is clicked.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     """
    #     This method is called to return an URL if the isRedirectTool method
    #     returns True.
    #
    #     Mandatory method if isRedirectTool() returns True.
    #     """
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     """
    #     Specifies if a History item should be created when the Execute button
    #     is clicked.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     """
    #     Specifies if this tool could be run from batch using the batch. The
    #     batch run line can be fetched from the info box at the bottom of the
    #     tool.
    #
    #     Optional method. Default return value if method is not defined:
    #         same as isHistoryTool()
    #     """
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     """
    #     Specifies whether changing the content of textboxes causes the page
    #     to reload. Returning False stops the need for reloading the tool
    #     after each input, resulting in less lags for the user.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     """
    #     Specifies a list of input boxes which resets the subsequent stored
    #     choices previously made. The input boxes are specified by index
    #     (starting with 1) or by key.
    #
    #     Optional method. Default return value if method is not defined: True
    #     """
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     """
    #     Specifies a help text in HTML that is displayed below the tool.
    #
    #     Optional method. Default return value if method is not defined: ''
    #     """
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     """
    #     Specifies an id used by StaticFile.py to reference an illustration
    #     file on disk. The id is a list of optional directory names followed
    #     by a filename. The base directory is STATIC_PATH as defined by
    #     Config.py. The full path is created from the base directory
    #     followed by the id.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     """
    #     Specifies an URL to an example page that describes the tool, for
    #     instance a Galaxy page.
    #
    #     Optional method. Default return value if method is not defined: None
    #     """
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     """
    #     Specifies whether the debug mode is turned on. Debug mode is
    #     currently mostly used within the Genomic HyperBrowser and will make
    #     little difference in a plain Galaxy ProTo installation.
    #
    #     Optional method. Default return value if method is not defined: False
    #     """
    #     return False
    #
    # @classmethod
    # def getOutputFormat(cls, choices):
    #     """
    #     The format of the history element with the output of the tool. Note
    #     that if 'html' is returned, any print statements in the execute()
    #     method is printed to the output dataset. For text-based output
    #     (e.g. bed) the output dataset only contains text written to the
    #     galaxyFn file, while all print statements are redirected to the info
    #     field of the history item box.
    #
    #     Note that for 'html' output, standard HTML header and footer code is
    #     added to the output dataset. If one wants to write the complete HTML
    #     page, use the restricted output format 'customhtml' instead.
    #
    #     Optional method. Default return value if method is not defined:
    #     'html'
    #     """
    #     return 'html'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
    #     """
    #     The title (name) of the main output history element.
    #
    #     Optional method. Default return value if method is not defined:
    #     the name of the tool.
    #     """
