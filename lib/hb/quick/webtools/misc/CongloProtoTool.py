from collections import OrderedDict
from itertools import product

from conglomerate.methods.intervalstats.intervalstats import IntervalStats
from conglomerate.methods.lola.lola import LOLA
from conglomerate.tools.method_compatibility import getCompatibleMethodObjects, getCollapsedConfigurationsPerMethod

import pkg_resources

from conglomerate.methods.genometricorr.genometricorr import GenometriCorr
from conglomerate.methods.giggle.giggle import Giggle
from conglomerate.methods.interface import ColocMeasureOverlap, RestrictedAnalysisUniverse, RestrictedThroughExclusion, \
    RestrictedThroughInclusion
from conglomerate.tools.job import Job

from conglomerate.methods.stereogene.stereogene import StereoGene
from conglomerate.tools.runner import runAllMethodsInSequence
from conglomerate.methods.interface import RestrictedThroughPreDefined, ColocMeasureCorrelation
from conglomerate.tools.constants import VERBOSE_RUNNING
from proto.HtmlCore import HtmlCore
from proto.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
#from quick.congloproto.HBCongloMethod import HBCongloMethod
#from quick.congloproto import HBCongloMethod
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN

ALL_METHOD_CLASSES = [GenometriCorr, StereoGene, Giggle, IntervalStats, LOLA]#, HBCongloMethod]
#[GenometriCorr, LOLA, StereoGene, Giggle, IntervalStats, HBCongloMethod]
#debug3
from quick.webtools.GeneralGuiTool import GeneralGuiTool

class CongloProtoTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "coloc-stats"

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
        return [('Select the running mode : ', 'selectRunningMode'),
                ('Select the reference genome: ', 'selectReferenceGenome'),
                ('Upload your own genome chromosome lenghts file', 'missingGenome'),
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
                ('Analyse against background regions? (optional)','analyseInBackground'),
                ('Select the uploaded file of background regions','backgroundRegionFileUpload'),
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
                ('Compatible methods : ', 'compatibleMethods')
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

    ADVANCED = 'Advanced mode: unified specification of individual parameters'
    SIMPLE_WITH_SHARED_DEFAULTS = 'Simple mode: based on shared parameter settings'
    SIMPLE_WITH_DEFAULTS = 'Simple mode: based on tool-specific defaults'

    @classmethod
    def getOptionsBoxSelectRunningMode(cls):  # Alt: getOptionsBox1()
        return [cls.SIMPLE_WITH_DEFAULTS, cls.SIMPLE_WITH_SHARED_DEFAULTS, cls.ADVANCED]

    @classmethod
    def getInfoForOptionsBoxSelectRunningMode(cls):
        text = 'Simple mode with tool-specific defaults performs co-localization analysis with six different tools with default settings.'
        text += '<br>'
        text += 'Simple mode with shared defaults runs the co-localization analysis tools with similar or same parameters/settings to allow comparison between the findings of the tools.'
        text += '<br>'
        text += 'Advanced mode allows the selection of co-localization analysis tools/methods based on detailed choices of parameters and methodological assumptions.'
        return text

    CUSTOM_REFERENCE_GENOME = 'Custom reference genome'

    @classmethod
    def getOptionsBoxSelectReferenceGenome(cls,prevChoices):  # Alt: getOptionsBox1()
        return ['Human (hg19)','Human (hg38)', 'Mouse (mm10)', cls.CUSTOM_REFERENCE_GENOME]
        #return '__genome__'

    @classmethod
    def getInfoForOptionsBoxSelectReferenceGenome(cls, prevChoices):
        text = 'Currently supports only hg19, hg18, hg38, mm10 and mm9.'
        text += '<br>'
        text += 'Please upload the chromosome lengths file of a reference genome of your choice, if the default options are not suitable for your analysis.'
        return text

    @classmethod
    def getOptionsBoxMissingGenome(cls, prevChoices):
        return False

    @classmethod
    def getOptionsBoxChooseChrnLenFile(cls, prevChoices):
        if prevChoices.missingGenome:
            return ('__history__',)

    @classmethod
    def getInfoForOptionsBoxChooseChrnLenFile(cls, prevChoices):
        text = 'Upload the chromosome lengths file of a reference genome of your choice, if the default reference genomes are not suitable for your analysis.'
        text += '<br>'
        text += 'The file should be tab separated with two fields; the first field should contain the chromosome name (e.g. chr22) and the second field should contain the length of the chromosome (e.g., 123456).'
        return text


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
        #return [cls.TWO_GENOMIC_TRACKS, cls.REFERENCE_TRACKS, cls.TWO_TRACK_GROUPS]
        #Not including TWO GROUPS for now, for running time reasons.. (also not handled for now, but easy to do)
        return [cls.TWO_GENOMIC_TRACKS, cls.REFERENCE_TRACKS]

    @classmethod
    def getInfoForOptionsBoxAnalysisType(cls, prevChoices):
        text = 'Here you can choose to perform the co-localization analysis either between a pair of genomic tracks or analyse a single genomic track against a large collection of genomic tracks.' \
               'The large collection of genomic tracks can further be a core database, where one could for example perform the analysis against ENCODE or Roadmap Epigenomics data including ' \
               'transcription factor binding sites, DNAse hypersensitive sites and so on. See the articles [1,2,3] for the reference track collections they curated.'
        text += '<br>'
        text += '[1] https://doi.org/10.1186/gb-2010-11-12-r121'
        text += '<br>'
        text += '[2]https://doi.org/10.1101/157735'
        text += '<br>'
        text += '[3] 10.1093/bioinformatics/btv612'
        return text

    @classmethod
    def getOptionsBoxChooseQueryTrackFile(cls, prevChoices):
        if prevChoices.analysisType in [cls.TWO_GENOMIC_TRACKS,cls.REFERENCE_TRACKS]:
            return ('__history__','bed')

    @classmethod
    def getInfoForOptionsBoxChooseQueryTrackFile(cls, prevChoices):
        text = 'For now, only BED files are supported.' \
               'Upload files through the upload button on the top left corner under the tools menu. ' \
               'The file will appear under the galaxy history in the right menu panel. '
        text += '<br>'
        text += 'It is strongly advised to adhere to the BED file format specifications.'
        text += 'If you have a different file format other than BED, you can use the tool on the left-hand menu to convert between file formats.'
        text += 'Please see under the tools menu "Format and convert tracks".'
        return text

    @classmethod
    def getOptionsBoxChooseReferenceTrackFile(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_GENOMIC_TRACKS:
            return ('__history__','bed')

    @classmethod
    def getInfoForOptionsBoxChooseReferenceTrackFile(cls, prevChoices):
        text = 'For now, only BED files are supported.' \
               'Upload files through the upload button on the top left corner under the tools menu. ' \
               'The file will appear under the galaxy history in the right menu panel. '
        text += '<br>'
        text += 'It is strongly advised to adhere to the BED file format specifications.'
        text += 'If you have a different file format other than BED, you can use the tool on the left-hand menu to convert between file formats.'
        text += 'Please see under the tools menu "Format and convert tracks".'
        return text


    CUSTOM_DATABASE = 'Use custom datasets to build a set of reference tracks'
    CORE_DATABASE = 'Use core database as the set of reference tracks'

    @classmethod
    def getOptionsBoxTypeOfReferenceTrackCollection(cls, prevChoices):
        if prevChoices.analysisType == cls.REFERENCE_TRACKS:
            return [cls.CORE_DATABASE, cls.CUSTOM_DATABASE]

    @classmethod
    def getInfoForOptionsBoxTypeOfReferenceTrackCollection(cls, prevChoices):
        text = 'The large collection of genomic tracks can be a core database, ' \
               'where one could for example perform the analysis against ENCODE ' \
               'or Roadmap Epigenomics data including transcription factor binding sites, ' \
               'DNAse hypersensitive sites and so on. See the articles [1,2,3] ' \
               'for the reference track collections they curated.'
        text += '<br>'
        text += 'Alternatively, one could build a custom collection of reference tracks.' \
                'For this, one can upload a bunch of BED files through the upload functionality ' \
                '(drag and drop works) or a tar file containing several BED files ' \
                '- further one can build a collection of genomic tracks (which we refer to as GSuite).'
        text += '<br>'
        text += '[1] https://doi.org/10.1186/gb-2010-11-12-r121'
        text += '<br>'
        text += '[2]https://doi.org/10.1101/157735'
        text += '<br>'
        text += '[3] 10.1093/bioinformatics/btv612'
        return text

    LOLA_COLLECTION = 'LOLA data collection'
    GIGGLE_COLLECTION = 'GIGGLE data collection'
    HB_COLLECTION = 'GSuite Hyperbrowser data collection'

    @classmethod
    def getOptionsBoxChoiceOfCoreDatabase(cls, prevChoices):
        if prevChoices.typeOfReferenceTrackCollection == cls.CORE_DATABASE:
            return [cls.LOLA_COLLECTION, cls.GIGGLE_COLLECTION, cls.HB_COLLECTION]

    @classmethod
    def getOptionsBoxChooseCustomTrackCollection(cls, prevChoices):
        if prevChoices.typeOfReferenceTrackCollection == cls.CUSTOM_DATABASE:
            return ('__history__','gsuite')

    @classmethod
    def getInfoForOptionsBoxChooseCustomTrackCollection(cls, prevChoices):
        text = 'Select the custom reference track collection. One could upload a bunch of BED files through the upload functionality' \
                '(drag and drop works) or a tar file containing several BED files' \
                '- further one can build a collection of genomic tracks (which we refer to as GSuite).'
        return text


    @classmethod
    def getOptionsBoxChooseQueryTrackCollection(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_TRACK_GROUPS:
            return ('__history__','gsuite')

    @classmethod
    def getOptionsBoxOptionalUseOfCoreDatabase(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_TRACK_GROUPS:
            return ['Yes', 'No']

    @classmethod
    def getOptionsBoxChooseReferenceTrackCollection(cls, prevChoices):
        if prevChoices.optionalUseOfCoreDatabase == 'Yes':
            return ['LOLA data collection', 'GIGGLE data collection', 'GSuite Hyperbrowser data collection']
        elif prevChoices.optionalUseOfCoreDatabase == 'No':
            return ('__history__','gsuite')

    # OVERLAP_MEASURES = [COUNTS, BASES]


    EXPLICIT_NEGATIVE_SET = 'Perform the analysis only in the explicit set of background regions supplied'
    EXCLUDE_SUPPLIED_BY_THE_USER = 'Yes, exclude specified regions supplied by the user'
    WHOLE_GENOME = 'No, use the whole genome'


    @classmethod
    def getOptionsBoxAnalyseInBackground(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.selectRunningMode in [cls.SIMPLE_WITH_DEFAULTS, cls.SIMPLE_WITH_SHARED_DEFAULTS]:
            return [cls.WHOLE_GENOME, cls.EXPLICIT_NEGATIVE_SET]

    @classmethod
    def getInfoForOptionsBoxAnalyseInBackground(cls, prevChoices):
        text = 'The genomic regions in a genomic track file are typically a result of some form of genomic assay ' \
               'analysed on a high throughput sequencing or genotyping platform, where some predefined regions ' \
               'of the genome are assayed (e.g., all the SNPs, transcripts, exonic regions and so on). The genomic ' \
               'regions found based on such assays are thus restricted to the regions queried on the technology platform. ' \
               'The statistical test (null model) should ideally restrict the analysis space to the regions queried on the ' \
               'technology platform. Some tools provide the possibility to restrict the analysis to background set of regions, ' \
               'by either excluding the regions supplied by the user or by performing the analysis only against an explicit set ' \
               'of background regions supplied by the user. Only BED files are supported for now.'
        text += '<br>'
        return text


    @classmethod
    def getOptionsBoxBackgroundRegionFileUpload(cls, prevChoices):
        if prevChoices.analyseInBackground == cls.EXPLICIT_NEGATIVE_SET:
            return ('__history__','bed')

    @classmethod
    def getInfoForOptionsBoxBackgroundRegionFileUpload(cls, prevChoices):
        text = 'Some tools provide the possibility to restrict the analysis to background set of regions, ' \
               'by either excluding the regions supplied by the user or by performing the analysis only against an explicit set ' \
               'of background regions supplied by the user. Upload an explicit set of background regions; the analysis will be restricted to the regions defined in the file. Only BED files are supported for now.'
        text += '<br>'
        return text

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
        if prevChoices.selectRunningMode == cls.ADVANCED:
            return OrderedDict([(cls.OVERLAP, False), (cls.DISTANCE, False), (cls.CORRELATION, False)])

    BASES = 'total number of overlapping bases'
    COUNTS = 'number of overlapping regions (counts)'

    @classmethod
    def getInfoForOptionsBoxTeststatType(cls, prevChoices):
        text = 'Choose at least one or many co-localization measures (test statistic). ' \
               'Selection of a test statistic shows further options to choose from. ' \
               'Overlap measure can use counts (total number of overlapping intervals ' \
               'between two files) or size (total number of overlapping base pairs between ' \
               'two files). Proximity (distance) can be computed to either start or midpoint ' \
               'or the closest coordinate.  A correlation metric can be obtained genome-wide ' \
               '(overall relationship), at a fine-scale, or a local correlation (region-level). ' \
               'For more information about the test statistics, see the original articles ' \
               '[1,2,3,4,5,6,7,8]'
        text += '<br>'
        text += '[1] https://doi.org/10.1186/gb-2010-11-12-r121'
        text += '<br>'
        text += '[2]https://doi.org/10.1371/journal.pcbi.1002529'
        text += '<br>'
        text += '[3] 10.1093/bioinformatics/btv612'
        text += '<br>'
        text += '[4] https://doi.org/10.1093/bioinformatics/btx379'
        text += '<br>'
        text += '[5] https://doi.org/10.1101/157735'
        text += '<br>'
        text += '[6] 10.1093/bioinformatics/bts009'
        text += '<br>'
        text += '[7] 10.1016/j.ajhg.2015.05.016'
        text += '<br>'
        text += '[8] 10.1093/gigascience/gix032'
        return text

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
        if prevChoices.selectRunningMode == cls.ADVANCED:
            return OrderedDict([(cls.NOT_ALLOWED,False), (cls.MAY_OVERLAP,False), (cls.DETERMINE_FROM_SUBMITTED_TRACKS,False)])


    @classmethod
    def getOptionsBoxRestrictRegions(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.selectRunningMode == cls.ADVANCED:
            return [cls.WHOLE_GENOME, cls.EXCLUDE_SUPPLIED_BY_THE_USER, cls.EXPLICIT_NEGATIVE_SET]

    @classmethod
    def getOptionsBoxRestrictedRegionFileUpload(cls, prevChoices):
        if prevChoices.restrictRegions in [cls.EXCLUDE_SUPPLIED_BY_THE_USER, cls.EXPLICIT_NEGATIVE_SET]:
            return '__history__'


    @classmethod
    def getOptionsBoxLocalHeterogeneity(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.selectRunningMode == cls.ADVANCED:
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
        if prevChoices.selectRunningMode == cls.ADVANCED:
            return OrderedDict([(cls.UNIFORMLY_DISTRIBUTED, False), (cls.PRESERVE_EMPIRIC_DISTRIBUTION, False)])

    CONFOUNDING_FEATURE = 'Yes, handle the specified confounding feature'
    LOCAL_HETEROGENEITY = 'Yes, handle local heterogeneity'

    @classmethod
    def getOptionsBoxConfounding(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.selectRunningMode == cls.ADVANCED:
            return ['No, I am not aware of any potential confounding feature for this analysis',
                cls.CONFOUNDING_FEATURE]

    @classmethod
    def getOptionsBoxConfounderHandler(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.confounding == cls.CONFOUNDING_FEATURE:
            return ['Shuffle genomic locations according to a non-homogenous Poisson process',
                    'Partial correlation', 'Stratified sampling']

    @classmethod
    def getOptionsBoxCompatibleMethods(cls, prevChoices):
        if cls.validateAndReturnErrors(prevChoices) is not None:
            return None

        workingMethodObjects = cls.getWorkingMethodObjects(prevChoices)
        if workingMethodObjects is None:
            return None
        methodChoices = getCollapsedConfigurationsPerMethod(workingMethodObjects)
        if len(methodChoices)==0:
            return None
        else:
            return OrderedDict( zip(methodChoices, [True]*len(methodChoices)) )

    @classmethod
    def getWorkingMethodObjects(cls, prevChoices):
        selections = cls.determine_selections(prevChoices)
        # typeOfAnalysis = prevChoices.analysisType
        queryTrack = cls.getQueryTracksFromChoices(prevChoices)
        refTracks = cls.getRefTracksFromChoices(prevChoices)
        if queryTrack is None or refTracks is None:
            return None
        workingMethodObjects = getCompatibleMethodObjects(selections.values(), queryTrack, refTracks,
                                                          ALL_METHOD_CLASSES)
        return workingMethodObjects

    @classmethod
    def determine_selections(cls, prevChoices):
        if prevChoices.selectRunningMode == cls.SIMPLE_WITH_SHARED_DEFAULTS:

            selections = {'setColocMeasure': [('setColocMeasure', ColocMeasureOverlap(**{'includeFlanks':False, 'countWholeIntervals':True, 'flankSizeUpstream':0, 'flankSizeDownstream':0})),
                                              ('setColocMeasure', ColocMeasureCorrelation(typeOfCorrelation='genome-wide'))],
                          'setRestrictedAnalysisUniverse':  [('setRestrictedAnalysisUniverse',None)]}
            if prevChoices.backgroundRegionFileUpload != None:
                              selections['setRestrictedAnalysisUniverse'].append(
                                  ('setRestrictedAnalysisUniverse',RestrictedThroughInclusion(prevChoices.backgroundRegionFileUpload)) )

        elif prevChoices.selectRunningMode == cls.SIMPLE_WITH_DEFAULTS:
            selections = {'setRestrictedAnalysisUniverse':  [('setRestrictedAnalysisUniverse',None)]}
            if prevChoices.backgroundRegionFileUpload != None:
                              selections['setRestrictedAnalysisUniverse'].append(
                                  ('setRestrictedAnalysisUniverse',RestrictedThroughInclusion(prevChoices.backgroundRegionFileUpload)) )
        elif prevChoices.selectRunningMode == cls.ADVANCED:
            selections = cls.parseAdvancedChoices(prevChoices)
        else:
            raise
        chrLenFnMappings = {'hg19': pkg_resources.resource_filename('conglomerate_resources', 'hg19.chrom.sizes'),
                            'hg18': pkg_resources.resource_filename('conglomerate_resources', 'hg18.chrom.sizes'),
                            'hg38': pkg_resources.resource_filename('conglomerate_resources', 'hg38.chrom.sizes'),
                            'mm9': pkg_resources.resource_filename('conglomerate_resources', 'mm9.chrom.sizes'),
                            'mm10': pkg_resources.resource_filename('conglomerate_resources', 'mm10.chrom.sizes'),
                            }
        genomeName = prevChoices.selectReferenceGenome.split('(')[-1].split(')')[0]
        selections['setGenomeName'] = [('setGenomeName', genomeName)]
        selections['setChromLenFileName'] = [('setChromLenFileName',chrLenFnMappings[genomeName])]

        return selections

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
        # import conglomerate.tools.constants as const
        # const.CATCH_METHOD_EXCEPTIONS = False
        selections = cls.determine_selections(choices)


        #TEMP, for transferring to local computer..
        # print ''
        # print 'selections = ', repr(selections)
        # print ''
        queryTrack = cls.getQueryTracksFromChoices(choices)
        refTracks = cls.getRefTracksFromChoices(choices)
        typeOfAnalysis = choices.analysisType

        workingMethodObjects = getCompatibleMethodObjects(selections.values(), queryTrack, refTracks, ALL_METHOD_CLASSES)
        methodSelectionStatus = dict([(extendedMethodName.split(' ')[0], selectionStatus) for extendedMethodName,selectionStatus in choices.compatibleMethods.items()])
        keptWmos = [wmo for wmo in workingMethodObjects if methodSelectionStatus[wmo._methodCls.__name__] ]

        if VERBOSE_RUNNING:
            print choices.compatibleMethods
            print selections
            print typeOfAnalysis
            print 'Working methods:'
            print [wmo._methodCls.__name__ for wmo in keptWmos]
            for wmo in keptWmos:
                print '**', wmo._methodCls.__name__, '**'
                print wmo._methods[0]._params
                print '****'
                print ' '

        runAllMethodsInSequence(keptWmos)

        unionOfParamKeys = set([paramKey for wmo in keptWmos for paramKey in wmo.annotatedChoices.keys()])
        # print(unionOfParamKeys)
        keysWithVariation = []
        for key in unionOfParamKeys:
            numDifferentKeyValues = len(set([wmo.annotatedChoices.get(key) \
                                                 if not isinstance(wmo.annotatedChoices.get(key), list) \
                                                 else tuple(wmo.annotatedChoices.get(key)) \
                                             for wmo in keptWmos]))
            if numDifferentKeyValues > 1:
                keysWithVariation.append(key)
        keysWithVariation.sort()

        core = HtmlCore()
        core.tableHeader(
            ['Method name', 'Query track', 'reference track'] + keysWithVariation + ['P-value', 'Test statistic',
            'Detailed results'])

        if VERBOSE_RUNNING:
            print 'Success states: ', [wmo.ranSuccessfully() for wmo in keptWmos]

        for i, wmo in enumerate(keptWmos):
            if VERBOSE_RUNNING:
                print 'Stdout of tool: ', wmo.getResultFilesDictList()
            if not wmo.ranSuccessfully():
                if VERBOSE_RUNNING:
                    print 'skipping result output for method', wmo
                continue

            allPvals = wmo.getPValue()
            allTestStats = wmo.getTestStatistic()
            # print 'TEMP18: ', wmo._methodCls.__name__, allTestStats
            allFullResults = wmo.getFullResults()
            assert len(allPvals)>0, allPvals

            assert len(allPvals) == len(allTestStats), (allPvals, allTestStats)
            for j, trackCombination in enumerate(allPvals.keys()):
                fullResultStaticFile = GalaxyRunSpecificFile(['details' + str(i) + '_' + str(j) + '.html'], galaxyFn)
                fullResult = allFullResults[trackCombination]
                fullResultStaticFile.writeTextToFile(fullResult)
                pval = allPvals[trackCombination]
                ts = allTestStats[trackCombination]
                # prettyTrackComb = '-'.join([track.split('/')[-1] for track in trackCombination])
                prettyTracks = [track.split('/')[-1] for track in trackCombination]
                # print 'TEMP14', [wmo._methodCls.__name__, prettyTrackComb] + [wmo.annotatedChoices.get(key) for key in keysWithVariation] + [str(pval), str(ts), fullResultStaticFile.getLink('Full results')]
                core.tableLine(
                    [wmo._methodCls.__name__] + prettyTracks + [wmo.annotatedChoices.get(key) for key in
                                                                keysWithVariation] + [str(pval), str(ts),
                                                                                      fullResultStaticFile.getLink(
                                                                                          'Full results')])
        core.tableFooter()

        # not wmo.ranSuccessfully()
        if not all(wmo.ranSuccessfully() for wmo in keptWmos):
            core.tableHeader(['Method name', 'Tool error'])
            for i, wmo in enumerate(keptWmos):
                if wmo.ranSuccessfully():
                    continue
                errorStaticFile = GalaxyRunSpecificFile(['errors' + str(i) + '.html'], galaxyFn)
                errorStaticFile.writeTextToFile(wmo.getErrorDetails())
                # print 'TEMP18: ', wmo.getErrorDetails()
                core.tableLine([wmo._methodCls.__name__, errorStaticFile.getLink('Tool error output')])
            core.tableFooter()

        print core

    @classmethod
    def getQueryTracksFromChoices(cls, choices):
        queryTrack = cls.getFnListFromTrackChoice(choices.chooseQueryTrackFile)
        return queryTrack

    @classmethod
    def getRefTracksFromChoices(cls, choices):
        typeOfAnalysis = choices.analysisType
        if typeOfAnalysis == cls.TWO_GENOMIC_TRACKS:
            referenceTrackChoice = choices.chooseReferenceTrackFile
            refTracks = cls.getFnListFromTrackChoice(referenceTrackChoice)
        elif typeOfAnalysis == cls.REFERENCE_TRACKS:
            if choices.choiceOfCoreDatabase!=None:
                assert choices.chooseCustomTrackCollection in [None,''], choices.chooseCustomTrackCollection
                if choices.choiceOfCoreDatabase == cls.LOLA_COLLECTION:
                    return ['prebuilt','LOLACore_170206']
                else:
                    raise Exception("Not supported: " + str(choices.choiceOfCoreDatabase))
            else:
                assert choices.choiceOfCoreDatabase is None, choices.choiceOfCoreDatabase
                referenceTrackChoice = choices.chooseCustomTrackCollection
        else:
            raise Exception('Invalid typeOfAnalysis: ' + str(typeOfAnalysis))
        refTracks = cls.getFnListFromTrackChoice(referenceTrackChoice)
        #raise Exception(str(refTracks))
        return refTracks

    @classmethod
    def getFnListFromTrackChoice(cls, trackChoice):
        if trackChoice is None or trackChoice.strip()=='':
            return None

        filetype = ExternalTrackManager.extractFileSuffixFromGalaxyTN(trackChoice, allowUnsupportedSuffixes=True)
        if filetype in ['bed']:
            fnList = [ExternalTrackManager.extractFnFromGalaxyTN(trackChoice)]
        elif filetype in ['gsuite']:
            gsuite = getGSuiteFromGalaxyTN(trackChoice)

            fnList = [gsTrack.path for gsTrack in gsuite.allTracks()]
        else:
            print 'ERROR: ', filetype, ExternalTrackManager.extractFnFromGalaxyTN(trackChoice)
        return fnList

    @classmethod
    def parseAdvancedChoices(cls, choices):
        selections = OrderedDict()
        # SELECTION BOXES:
        # mapping = {cls.WHOLE_GENOME:None,
        #            cls.EXCLUDE_SUPPLIED_BY_THE_USER:RestrictedThroughExclusion(fn)}
        if choices.restrictRegions in [cls.WHOLE_GENOME,None]:
            restrictRegions = None
        else:
            fn = ExternalTrackManager.extractFnFromGalaxyTN(choices.restrictedRegionFileUpload)
            if choices.restrictRegions == cls.EXCLUDE_SUPPLIED_BY_THE_USER:
                restrictRegions = RestrictedThroughExclusion(fn)
            if choices.restrictRegions == cls.EXPLICIT_NEGATIVE_SET:
                raise
        selections['setRestrictedAnalysisUniverse'] = [('setRestrictedAnalysisUniverse', restrictRegions)]
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
                            #'choiceOfCoreDatabase': 'setPredefinedTrackIndexAndCollection'}
        # TestStat
        distCoordSelected = [key for key in choices.distanceCoordinate if choices.distanceCoordinate[key]] \
                            if choices.distanceCoordinate is not None else []
        distTypeSelected = [key for key in choices.distanceType if choices.distanceType[key]] \
                            if choices.distanceType is not None else[]
        fullDistSpecs = product(distCoordSelected, distTypeSelected)
        encodedDistSpecs = ['-'.join(spec) for spec in fullDistSpecs]
        tsMapping = {cls.COUNTS : ColocMeasureOverlap(False, True,0,0),
                                cls.BASES : ColocMeasureOverlap(False, False,0,0)}
        overlapSpecs = [tsMapping[key] for key in choices.overlapMeasure if choices.overlapMeasure[key]] \
                        if choices.overlapMeasure is not None else []

        correlationSpecs = [key for key in choices.correlation if choices.correlation[key]] \
                            if choices.correlation is not None else[]
        allTsSpecs = encodedDistSpecs + overlapSpecs + correlationSpecs
        selections['setColocMeasure'] = zip(['setColocMeasure'] * len(allTsSpecs), allTsSpecs)
        # distCoordSelections = cls.getSelectionsFromCheckboxParam(distCoordChoiceValueMapping, choices, 'distanceCoordinate', 'distCoord')
        # distCoordSelections = cls.getSelectionsFromCheckboxParam(distCoordChoiceValueMapping, choices, 'distanceType', 'distType')
        if choices.allowOverlaps and choices.allowOverlaps[cls.DETERMINE_FROM_SUBMITTED_TRACKS]:
            raise
        else:
            choiceValueMappings['allowOverlaps'] = {cls.NOT_ALLOWED: False, cls.MAY_OVERLAP: True}
        choiceValueMappings['clumping'] = {cls.UNIFORMLY_DISTRIBUTED: False, cls.PRESERVE_EMPIRIC_DISTRIBUTION: True}
        #choiceValueMappings['choiceOfCoreDatabase'] = {cls.LOLA_COLLECTION: {'trackIndex':'LOLACore_170206', 'trackCollection':'codex'} }
        for guiKey, selectionKey in selectionMapping.items():
            currSelection = cls.getSelectionsFromCheckboxParam(choiceValueMappings[guiKey], choices, guiKey, selectionKey)
            assert len(currSelection.values()[0])>0, (guiKey, selectionKey, currSelection)
            selections.update(currSelection)
        return selections

    @classmethod
    def getSelectionsFromCheckboxParam(cls, choiceValueMappings, choiceTuple, selectionName, selectionsKey):
        choices = choiceTuple._asdict()
        # if choices[selectionName] is None:
        #     return {selectionsKey:None}
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
        #return str(choices.choiceOfCoreDatabase)
        if choices.allowOverlaps and choices.allowOverlaps[cls.DETERMINE_FROM_SUBMITTED_TRACKS]:
            if choices.allowOverlaps[cls.MAY_OVERLAP] or choices.allowOverlaps[cls.NOT_ALLOWED]:
                return "%s can only be selected as a single choice" % cls.DETERMINE_FROM_SUBMITTED_TRACKS
        else:
            if choices.allowOverlaps and not choices.allowOverlaps[cls.NOT_ALLOWED] and not choices.allowOverlaps[cls.MAY_OVERLAP]:
                return "Please select whether or not to allow genomic regions to overlap within track"
        if choices.clumping and not any(choices.clumping.values()):
            return "Please select whether or not to handle clumping"

        if cls.getQueryTracksFromChoices(choices) is None:
            return "Please select query track"
        if cls.getRefTracksFromChoices(choices) is None:
            return "Please select reference tracks"

        workingMethodObjects = cls.getWorkingMethodObjects(choices)
        if workingMethodObjects is None:
            return "Unresolved error"
        elif len(workingMethodObjects)==0:
            return "No method is compatible with current selections - please make further selections"

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
    @classmethod
    def isPublic(cls):
        """
        Specifies whether the tool is accessible to all users. If False, the
        tool is only accessible to a restricted set of users as well as admin
        users, as defined in the galaxy.ini file.

        Optional method. Default return value if method is not defined: False
        """
        return True
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
