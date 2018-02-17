import os
from collections import OrderedDict, defaultdict

from config.Config import GALAXY_TOOL_DATA_PATH
from conglomerate.core.config import VERBOSE_RUNNING, CATCH_METHOD_EXCEPTIONS
from conglomerate.core.types import TrackFile
from conglomerate.methods.interface import (ColocMeasureCorrelation, ColocMeasureOverlap,
                                            RestrictedThroughExclusion, RestrictedThroughInclusion,
                                            ColocMeasureProximity, InvalidSpecification)
from conglomerate.tools.WorkingMethodObjectParser import WorkingMethodObjectParser, ALL_CONGLOMERATE_METHOD_CLASSES
from conglomerate.tools.method_compatibility import (getCompatibleMethodObjects,
                                                     getCollapsedConfigurationsPerMethod)
from conglomerate.tools.runner import runAllMethodsInSequence
from proto.CommonFunctions import (createGalaxyToolURL, getGalaxyUploadLinkOnclick, createToolURL,
                                   getGalaxyFilesDir)
from proto.HtmlCore import HtmlCore
from proto.StaticFile import GalaxyRunSpecificFile
from proto.TextCore import TextCore
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.congloproto.HBCongloMethod import HyperBrowser
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.util.CommonFunctions import silenceRWarnings
from quick.webtools.GeneralGuiTool import GeneralGuiTool

#ALL_METHOD_CLASSES = [GenometriCorr, Giggle, IntervalStats, LOLA, HyperBrowser]
ALL_METHOD_CLASSES = ALL_CONGLOMERATE_METHOD_CLASSES + [HyperBrowser]
# [GenometriCorr, LOLA, StereoGene, Giggle, IntervalStats, HyperBrowser]
# debug3


class CongloProtoTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return ""

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
        return [("", 'toolDescTop'),
                ('Running mode: ', 'selectRunningMode'),
                ("", 'divider'),
                ("", 'toolDescMiddle'),
                ('Reference genome: ', 'selectReferenceGenome'),
                ('Upload your own genome chromosome lengths file', 'missingGenome'),
                ('Choose a file with chromosome lengths of a custom genome build : ', 'chooseChrnLenFile'),
                ('Type of co-localization analysis: ', 'analysisType'),
                ('Choose a query track: ', 'chooseQueryTrackFile'),
                ('Choose a reference track: ', 'chooseReferenceTrackFile'),
                ('Type of reference track collection', 'typeOfReferenceTrackCollection'),
                ('Choose a core data collection', 'choiceOfCoreDatabase'),
                ('Choose a custom reference track collection', 'chooseCustomTrackCollection'),
                ('Use one of the default core databases as reference collection ? ', 'optionalUseOfCoreDatabase'),
                ('Choose a query track collection: ', 'chooseQueryTrackCollection'),
                ('Choose a reference track collection: ', 'chooseReferenceTrackCollection'),
                ('Analyse against background regions? (optional)', 'analyseInBackground'),
                ('Select the uploaded file of background regions', 'backgroundRegionFileUpload'),
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
                ('Runtime mode : ', 'runtimeMode'),
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

    @classmethod
    def getOptionsBoxToolDescTop(cls):
        core = HtmlCore()
        core.bigHeader('coloc-stats')
        core.smallHeader('- a unified web interface to perform co-localization analysis of genomic features')
        core.divider()
        return '__rawStr__', str(core)

    @classmethod
    def getOptionsBoxDivider(cls, prevChoices):
        core = HtmlCore()
        core.divider()
        return '__rawStr__', str(core)

    @classmethod
    def getOptionsBoxToolDescMiddle(cls, prevChoices):
        if prevChoices.selectRunningMode == cls.ADVANCED:
            return

        core = HtmlCore()
        core.paragraph(
            'Below is a unified interface to multiple previously published methods for statistical co-localization analysis. '
            'All the methods can be used to analyze a <b> query track </b> against either a single <b> reference track </b> or a <b> reference track collection </b>. '
            'Supported inputs are single datasets or collections of datasets. It can be run in a basic mode with default settings '
            'or in an advanced mode that allows further customization. <br><p></p> For each selection box, <b> click on the information button </b> for further explanation.')
        core.divider()
        core.fieldsetBegin("Get data")
        linkUpload = str(HtmlCore().link('<span style="color: maroon;"><b>Upload data</b></span>',
                   createGalaxyToolURL('upload1'),
                   args='onclick="{}"'.format(getGalaxyUploadLinkOnclick())))
        linkImport = str(HtmlCore().link('<span style="color: maroon;"><b>Import sample data</b></span>',
                   createToolURL('hb_conglo_import_sample_files_tool')))
        core.paragraph('If you have not uploaded data already, you can %s or %s'%(linkUpload, linkImport))
        core.fieldsetEnd()
        return '__rawstr__', str(core)

    ADVANCED = 'Advanced mode: unified selection of specific parameters'
    SIMPLE_WITH_SHARED_DEFAULTS = 'Simple mode: based on shared parameter settings'
    SIMPLE_WITH_DEFAULTS = 'Basic mode: partly based on tool-specific defaults'

    @classmethod
    def getOptionsBoxSelectRunningMode(cls, prevChoices):  # Alt: getOptionsBox1()
        # return [cls.SIMPLE_WITH_DEFAULTS, cls.SIMPLE_WITH_SHARED_DEFAULTS, cls.ADVANCED]
        return [cls.SIMPLE_WITH_DEFAULTS, cls.ADVANCED]

    @classmethod
    def getInfoForOptionsBoxSelectRunningMode(cls):
        text = 'Basic mode with partly tool-specific defaults performs co-localization analysis with six different tools using partly their default settings. Only a few main selections need to be made by the user.'
        text += '<br>'
        text += 'Advanced mode allows the selection of co-localization analysis tools/methods based on detailed choices of parameters and methodological assumptions. After selecting one or many specific parameter values, a list of compatible tools will be shown.'
        return text
        # text += 'Simple mode with shared defaults runs the co-localization analysis tools with similar or same parameters/settings to allow comparison between the findings of the tools.'
        # text += '<br>'

    HG19_CHR20 = 'Human chromosome 20 (hg19_chr20) [for testing]'
    CUSTOM_REFERENCE_GENOME = 'Custom reference genome'

    @classmethod
    def getOptionsBoxSelectReferenceGenome(cls, prevChoices):  # Alt: getOptionsBox1()
        return ['Human (hg19)', 'Human (hg38)', 'Mouse (mm9)', 'Mouse (mm10)',
                cls.HG19_CHR20, cls.CUSTOM_REFERENCE_GENOME]
        # return '__genome__'

    @classmethod
    def getInfoForOptionsBoxSelectReferenceGenome(cls, prevChoices):
        text = 'Support for hg19, hg38, mm9 and mm10 is integrated in the system.'
        text += '<br>'
        text += 'Analysis can be performed on other reference genomes by uploading a custom chromosome lengths file.'
        return text

    @classmethod
    def getOptionsBoxMissingGenome(cls, prevChoices):
        return None
        # return False

    @classmethod
    def getOptionsBoxChooseChrnLenFile(cls, prevChoices):
        # if prevChoices.missingGenome:
        if prevChoices.selectReferenceGenome == cls.CUSTOM_REFERENCE_GENOME:
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
        # return [cls.TWO_GENOMIC_TRACKS, cls.REFERENCE_TRACKS, cls.TWO_TRACK_GROUPS]
        # Not including TWO GROUPS for now, for running time reasons.. (also not handled for now, but easy to do)
        return [cls.TWO_GENOMIC_TRACKS, cls.REFERENCE_TRACKS]

    @classmethod
    def getInfoForOptionsBoxAnalysisType(cls, prevChoices):
        text = 'Here you can choose to perform the co-localization analysis either between a pair of genomic tracks or analyse a single genomic track against a large collection of genomic tracks.' \
                'For more information about co-localization analysis, refer the following citations:'
        text += '<br>'
        text += '[1] https://doi.org/10.1186/gb-2010-11-12-r121'
        text += '<br>'
        text += '[2]https://doi.org/10.1101/157735'
        text += '<br>'
        text += '[3] 10.1093/bioinformatics/btv612'
        return text

    @classmethod
    def getOptionsBoxChooseQueryTrackFile(cls, prevChoices):
        if prevChoices.analysisType in [cls.TWO_GENOMIC_TRACKS, cls.REFERENCE_TRACKS]:
            return ('__history__', 'bed')

    @classmethod
    def getInfoForOptionsBoxChooseQueryTrackFile(cls, prevChoices):
        text = 'Upload files through the upload button on the top left corner under the tools menu. ' \
               'The file will appear under the galaxy history in the right menu panel. ' \
               'For now, only BED files are supported.'
        text += '<br>'
        text += 'It is strongly advised to adhere to the BED file format specifications.'
        text += 'If you have a different file format other than BED, you can use the tool on the left-hand menu to convert between file formats.'
        text += 'Please see under the tools menu "Format and convert tracks".'
        return text

    @classmethod
    def getOptionsBoxChooseReferenceTrackFile(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_GENOMIC_TRACKS:
            return ('__history__', 'bed')

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
            return [cls.CUSTOM_DATABASE, cls.CORE_DATABASE]

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
            return [cls.LOLA_COLLECTION]
            # return [cls.LOLA_COLLECTION, cls.GIGGLE_COLLECTION, cls.HB_COLLECTION]

    @classmethod
    def getOptionsBoxChooseCustomTrackCollection(cls, prevChoices):
        if prevChoices.typeOfReferenceTrackCollection == cls.CUSTOM_DATABASE:
            return ('__history__', 'gsuite')

    @classmethod
    def getInfoForOptionsBoxChooseCustomTrackCollection(cls, prevChoices):
        text = 'Select the custom reference track collection. One could upload a bunch of BED files through the upload functionality' \
               '(drag and drop works) or a tar file containing several BED files' \
               '- further one can build a collection of genomic tracks (which we refer to as GSuite).'
        return text

    @classmethod
    def getOptionsBoxChooseQueryTrackCollection(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_TRACK_GROUPS:
            return ('__history__', 'gsuite')

    @classmethod
    def getOptionsBoxOptionalUseOfCoreDatabase(cls, prevChoices):
        if prevChoices.analysisType == cls.TWO_TRACK_GROUPS:
            return ['Yes', 'No']

    @classmethod
    def getOptionsBoxChooseReferenceTrackCollection(cls, prevChoices):
        if prevChoices.optionalUseOfCoreDatabase == 'Yes':
            return [cls.LOLA_COLLECTION]
            # return ['LOLA data collection', 'GIGGLE data collection', 'GSuite Hyperbrowser data collection']
        elif prevChoices.optionalUseOfCoreDatabase == 'No':
            return ('__history__', 'gsuite')

    # OVERLAP_MEASURES = [COUNTS, BASES]


    SIMPLEMODE_ONLY_WHOLE_GENOME = 'No, use only methods that can use the whole genome as background'
    SIMPLEMODE_OPTIONALLY_EXPLICIT_BG = 'Yes, provide an explicit set of background regions to tools that can take it as input (using whole genome for others)'
    SIMPLEMODE_ONLY_EXPLICIT_BG = 'Yes, use only methods that can take an explicit set of background regions as input'

    EXPLICIT_NEGATIVE_SET = 'Perform the analysis only in the explicit set of background regions supplied'
    EXCLUDE_SUPPLIED_BY_THE_USER = 'Yes, exclude specified regions supplied by the user'
    WHOLE_GENOME = 'No, use the whole genome'

    @classmethod
    def getOptionsBoxAnalyseInBackground(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.selectRunningMode in [cls.SIMPLE_WITH_DEFAULTS, cls.SIMPLE_WITH_SHARED_DEFAULTS]:
            return [cls.SIMPLEMODE_ONLY_WHOLE_GENOME, cls.SIMPLEMODE_ONLY_EXPLICIT_BG,
                    cls.SIMPLEMODE_OPTIONALLY_EXPLICIT_BG]

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
        if prevChoices.analyseInBackground in [cls.SIMPLEMODE_OPTIONALLY_EXPLICIT_BG, cls.SIMPLEMODE_ONLY_EXPLICIT_BG]:
            return ('__history__', 'bed')

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
        return None
        # if prevChoices.teststatType and prevChoices.teststatType[cls.DISTANCE]:
        #     return OrderedDict([(cls.START_COORDINATE, False), (cls.MIDPOINT, False),(cls.CLOSEST_COORDINATE, False)])

    AVERAGE_LOG_DISTANCE = 'average log distance'
    ABSOLUTE_DISTANCE = 'absolute distance'

    @classmethod
    def getOptionsBoxDistanceType(cls, prevChoices):
        return None
        # if prevChoices.distanceCoordinate and any(prevChoices.distanceCoordinate.values()):
        #     return OrderedDict([(cls.ABSOLUTE_DISTANCE, False), (cls.AVERAGE_LOG_DISTANCE, False)])

    @classmethod
    def getOptionsBoxCorrelation(cls, prevChoices):
        return None
        # if prevChoices.teststatType and prevChoices.teststatType[cls.CORRELATION]:
        #     return ['genome-wide kernel correlation (overall relationship)','fine-scale correlation (structure of correlation)','local correlation (genomic region-level)']

    DETERMINE_FROM_SUBMITTED_TRACKS = 'determine whether or not to allow overlap based on submitted tracks'
    MAY_OVERLAP = 'elements may overlap'
    NOT_ALLOWED = 'elements not allowed to overlap'

    @classmethod
    def getOptionsBoxAllowOverlaps(cls, prevChoices):  # Alt: getOptionsBox2()
        return None
        # if prevChoices.selectRunningMode == cls.ADVANCED:
        #     return OrderedDict([(cls.NOT_ALLOWED,False), (cls.MAY_OVERLAP,False), (cls.DETERMINE_FROM_SUBMITTED_TRACKS,False)])

    @classmethod
    def getOptionsBoxRestrictRegions(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.selectRunningMode == cls.ADVANCED:
            # return [cls.WHOLE_GENOME, cls.EXCLUDE_SUPPLIED_BY_THE_USER, cls.EXPLICIT_NEGATIVE_SET]
            return [cls.WHOLE_GENOME, cls.EXPLICIT_NEGATIVE_SET]

    @classmethod
    def getOptionsBoxRestrictedRegionFileUpload(cls, prevChoices):
        if prevChoices.restrictRegions in [cls.EXCLUDE_SUPPLIED_BY_THE_USER, cls.EXPLICIT_NEGATIVE_SET]:
            return ('__history__', 'bed')

    @classmethod
    def getOptionsBoxLocalHeterogeneity(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.selectRunningMode == cls.ADVANCED:
            # return ['No, distribute genomic regions across the whole genome', cls.LOCAL_HETEROGENEITY]
            return ['No, distribute genomic regions across the whole genome']

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
            return ['No, I am not aware of any potential confounding feature for this analysis']
            # return ['No, I am not aware of any potential confounding feature for this analysis',cls.CONFOUNDING_FEATURE]

    @classmethod
    def getOptionsBoxConfounderHandler(cls, prevChoices):  # Alt: getOptionsBox2()
        if prevChoices.confounding == cls.CONFOUNDING_FEATURE:
            return ['Shuffle genomic locations according to a non-homogenous Poisson process',
                    'Partial correlation', 'Stratified sampling']

    @classmethod
    def getOptionsBoxRuntimeMode(cls, prevChoices):
        return ['quick', 'medium', 'accurate']

    @classmethod
    def getInfoForOptionsBoxRuntimeMode(cls, prevChoices):
        text = 'Depending upon the analysis choices and the run times of corresponding compatible methods, the run time can vary from minutes to hours.' \
                'Choosing a quick mode reduces the run time of the compatible methods,for instance, by reducing the number of permutations.'
        text += '<br>'
        return text


    @classmethod
    def getOptionsBoxCompatibleMethods(cls, prevChoices):
        if cls.getValidationText(prevChoices) is not None:
            return None

        #workingMethodObjects = cls.getWorkingMethodObjects(prevChoices)
        queryTrack, refTracks, selectionValues = cls.extractFromChoices(prevChoices)
        workingMethodObjects = WorkingMethodObjectParser(queryTrack, refTracks, selectionValues, ALL_METHOD_CLASSES).getWorkingMethodObjects()

        if workingMethodObjects is None:
            return None
        methodChoices = getCollapsedConfigurationsPerMethod(workingMethodObjects)
        if len(methodChoices) == 0:
            return None
        else:
            return OrderedDict(zip(sorted(methodChoices), [True] * len(methodChoices)))

    @classmethod
    def extractFromChoices(cls, choices):
        selections = cls.determine_selections(choices)
        queryTrack = ReferenceTrackParser.getFnListFromTrackChoice(choices.chooseQueryTrackFile)
        refTrackParser = ReferenceTrackParser.createFromGUIChoices(choices)
        refTracks = refTrackParser.getRefTracksFromChoices()
        return queryTrack, refTracks, selections.values()

    # @classmethod
    # def getWorkingMethodObjects(cls, choices):
    #     selections = cls.determine_selections(choices)
    #     queryTrack = ReferenceTrackParser.getFnListFromTrackChoice(choices.chooseQueryTrackFile)
    #     refTrackParser = ReferenceTrackParser.createFromGUIChoices(choices)
    #     refTracks = refTrackParser.getRefTracksFromChoices()
    #     wmoParser = WorkingMethodObjectParser(queryTrack, refTracks, selections.values())
    #     return wmoParser.getWorkingMethodObjects()

    @classmethod
    def determine_selections(cls, prevChoices):
        if prevChoices.selectRunningMode == cls.SIMPLE_WITH_SHARED_DEFAULTS:

            selections = {'setColocMeasure': [('setColocMeasure', ColocMeasureOverlap(
                **{'includeFlanks': False, 'countWholeIntervals': True, 'flankSizeUpstream': 0,
                   'flankSizeDownstream': 0})),
                                              ('setColocMeasure',
                                               ColocMeasureCorrelation(typeOfCorrelation='genome-wide'))]}

            selections['setRestrictedAnalysisUniverse'] = cls.parseSimpleModeBgOptions(prevChoices)

        elif prevChoices.selectRunningMode == cls.SIMPLE_WITH_DEFAULTS:
            selections = {}
            selections['setRestrictedAnalysisUniverse'] = cls.parseSimpleModeBgOptions(prevChoices)

        elif prevChoices.selectRunningMode == cls.ADVANCED:
            selections = cls.parseAdvancedChoices(prevChoices)
        else:
            raise Exception()
        chrLenFnMappings = {'hg19': cls._getCongloResourcePath('hg19.chrom.sizes'),
                            'hg18': cls._getCongloResourcePath('hg18.chrom.sizes'),
                            'hg38': cls._getCongloResourcePath('hg38.chrom.sizes'),
                            'mm9': cls._getCongloResourcePath('mm9.chrom.sizes'),
                            'mm10': cls._getCongloResourcePath('mm10.chrom.sizes'),
                            'hg19_chr20': cls._getCongloResourcePath('hg19_chr20.chrom.sizes'),
                            }
        if prevChoices.selectReferenceGenome == cls.CUSTOM_REFERENCE_GENOME:
            genomeName = 'Custom'
            chrLenFn = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.chooseChrnLenFile) \
                if prevChoices.chooseChrnLenFile is not None \
                else None

        else:
            genomeName = prevChoices.selectReferenceGenome.split('(')[-1].split(')')[0]
            chrLenFn = chrLenFnMappings[genomeName]

        selections['setGenomeName'] = [('setGenomeName', genomeName)]
        selections['setChromLenFileName'] = [('setChromLenFileName', chrLenFn)]
        selections['setRuntimeMode'] = [('setRuntimeMode', prevChoices.runtimeMode)]
        return selections

    @classmethod
    def _getCongloResourcePath(cls, resourceFn):
        return os.path.join(*[GALAXY_TOOL_DATA_PATH, 'conglomerate', 'resources', resourceFn])

    @classmethod
    def parseSimpleModeBgOptions(cls, prevChoices):
        bgOptions = []
        if prevChoices.analyseInBackground in [cls.SIMPLEMODE_ONLY_WHOLE_GENOME,
                                               cls.SIMPLEMODE_OPTIONALLY_EXPLICIT_BG]:
            bgOptions.append(('setRestrictedAnalysisUniverse', None))
        if prevChoices.analyseInBackground in [cls.SIMPLEMODE_ONLY_EXPLICIT_BG, cls.SIMPLEMODE_OPTIONALLY_EXPLICIT_BG]:
            if prevChoices.backgroundRegionFileUpload in [None, '']:
                spec = InvalidSpecification('No background region file selected in GUI.')
            else:
                bgFns = TrackParser.getFnListFromTrackChoice(prevChoices.backgroundRegionFileUpload)
                assert len(bgFns) == 1
                spec = RestrictedThroughInclusion(bgFns[0])
            bgOptions.append(
                ('setRestrictedAnalysisUniverse', spec))
        return bgOptions

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
        if not VERBOSE_RUNNING:
            silenceRWarnings()

        print HtmlCore().begin(reloadTime=5)
        # TODO: REMOVE
        # LOAD_PICKLES = True
        #
        # if LOAD_PICKLES:
        #     pickleFn = '/hyperbrowser/staticFiles/div/trackComb_oneMany_v2.pickle'
        #     trackCombResults = load(open(pickleFn))
        #     if not type(trackCombResults)==TrackCombResultList:
        #         trackCombResults = TrackCombResultList(trackCombResults)
        #     #CongloProtoTool.outputResults(trackCombResults, [], None, [],galaxyFn)
        #     crg = CongloResultsGenerator(trackCombResults, [], [],galaxyFn)
        #     crg.outputResults()
        #     return
        # TODO: /REMOVE

        print '<h1>Result page for coloc-stats analysis</h1>'

        print HtmlCore().toggle('Show/Hide progress', styleId='progress', withDivider=True)
        print HtmlCore().divBegin(divId="progress", style="display: block; background-color: lightgray; border-style: ridge; padding: 8px;")
        print HtmlCore().paragraph('Analysis in progress (may take from minutes to hours - depending on selected datasets, tools and parameters)')
        if VERBOSE_RUNNING:
            print '<pre>'

        #workingMethodObjects = cls.getWorkingMethodObjects(choices)
        queryTrack, refTracks, selectionValues = cls.extractFromChoices(choices)
        print 'FOR TEST TRANSFER - queryTrack, refTracks, selectionValues: ', '<br>', repr(queryTrack), '<br>', repr(refTracks), '<br>', selectionValues, '<br><br>'
        workingMethodObjects = WorkingMethodObjectParser(queryTrack, refTracks, selectionValues,ALL_METHOD_CLASSES).getWorkingMethodObjects()
        print 'FOR TEST TRANSFER - compatible methods classes:', set([wmo.getMethodName() for wmo in workingMethodObjects]), '<br><br>'
        methodSelectionStatus = dict(
            [(extendedMethodName.split(' ')[0], selectionStatus) for extendedMethodName, selectionStatus in
             choices.compatibleMethods.items()])
        keptWmos = [wmo for wmo in workingMethodObjects if methodSelectionStatus[wmo._methodCls.__name__]]

        if VERBOSE_RUNNING:
            cls._printWmoInfo(keptWmos)

        jobOutputDir = os.path.join(getGalaxyFilesDir(galaxyFn), 'cwl_output')
        runAllMethodsInSequence(keptWmos, jobOutputDir=jobOutputDir)
        print HtmlCore().divEnd()
        if VERBOSE_RUNNING:
            print 'Success states: ', [wmo.ranSuccessfully() for wmo in keptWmos]
            print '</pre><br>'
        keysWithVariation = cls.determineKeysWithVariation(keptWmos)
        print '<h2>Results for each dataset and tool configuration</h2>'
        succeedingMethods, failingMethods = [[wmo for wmo in keptWmos if wmo.ranSuccessfully()==state]
                                          for state in [True,False]]
        # TODO: Adding galaxyFn is a temporary hack to allow full HyperBrowser output
        trackCombResults = cls.extractResultsFromWorkingMethodList(succeedingMethods, galaxyFn)
        trackCombErrors = cls.extractErrorFromFailingMethodList(failingMethods)

        # TODO: REMOVE
        # sf = GalaxyRunSpecificFile(['trackComb.pickle'], galaxyFn)
        # path = sf.getDiskPath(ensurePath=True)
        # dump(trackCombResults, open(path, 'w'))
        # print sf.getLink('Pickles')
        # TODO: /REMOVE

        print '''Your analysis has been completed and your results are available below.
                You can see the parameters used for the run (in the originally GUI layout) by clicking the "rerun" icon on this history element'''

        crg = CongloResultsGenerator(trackCombResults, trackCombErrors, keysWithVariation, galaxyFn)
        crg.outputResults()

        print HtmlCore().end(stopReload=True)



    @classmethod
    def _printWmoInfo(cls, keptWmos):
        print 'Kept methods (after manual GUI subselection):', [wmo._methodCls.__name__ for wmo in keptWmos]
        for wmo in keptWmos:
            print '**', wmo._methodCls.__name__, '**'
            print wmo._methods[0]._params, '\n****\n'


    # @classmethod
    # def createRankTable(cls, keptWmos, keysWithVariation):
    #     core = HtmlCore()
    #     rankTableDict = defaultdict(dict)
    #     for i, wmo in enumerate(keptWmos):
    #         if not wmo.ranSuccessfully():
    #             continue
    #
    #         wmoLabel = wmo._methodCls.__name__  # + '(' + ','.join([key + ':' + wmo.annotatedChoices.get(key) for key in
    #         #                 keysWithVariation]) + ')'
    #         allTestStats = wmo.getTestStatistic()
    #         tsVals = [(trackCombination[1].split('/')[-1], allTestStats[trackCombination]) \
    #                   for trackCombination in allTestStats.keys()]
    #         # tsRanks = dict([(track, 1+sum(v>val for t,v in tsVals)) for track, val in tsVals])
    #         for trackName, val in tsVals:
    #             rankTableDict[trackName][wmoLabel] = 1 + sum(v > val for t, v in tsVals)
    #     if len(rankTableDict) > 1:  # More than 1 ref track
    #         allTrackNames = rankTableDict.keys()
    #         # allWmoLabels = rankTableDict.values()[0].keys()
    #         # assert all([row.keys() == allWmoLabels for row in rankTableDict.values()]), (allWmoLabels, [row.keys() for row in rankTableDict.values()])
    #         allWmoLabels = list(set([wmoLabel for row in rankTableDict.values() for wmoLabel in row.keys()]))
    #         core.tableHeader([' '] + allWmoLabels + ['Mean rank'], sortable=True)
    #         for trackName in rankTableDict:
    #             ranksInRow = [rankTableDict[trackName][wmoLabel] if wmoLabel in rankTableDict[trackName] else 'N/A' \
    #                           for wmoLabel in allWmoLabels]
    #             nonNAranks = [rankTableDict[trackName][wmoLabel] for wmoLabel in allWmoLabels if
    #                           wmoLabel in rankTableDict[trackName]]
    #             meanRank = '%.1f' % (reduce(lambda x, y: x * y, nonNAranks) ** (1.0 / len(nonNAranks)))
    #             core.tableLine([trackName] + [str(x) for x in ranksInRow] + [meanRank])
    #         core.tableFooter()
    #     return core



    @classmethod
    def determineKeysWithVariation(cls, keptWmos):
        unionOfParamKeys = set([paramKey for wmo in keptWmos for paramKey in wmo.annotatedChoices.keys()])
        keysWithVariation = []
        for key in unionOfParamKeys:
            numDifferentKeyValues = len(set([wmo.annotatedChoices.get(key) \
                                                 if not isinstance(wmo.annotatedChoices.get(key), list) \
                                                 else tuple(wmo.annotatedChoices.get(key)) \
                                             for wmo in keptWmos]))
            if numDifferentKeyValues > 1:
                keysWithVariation.append(key)
        keysWithVariation.sort()
        return keysWithVariation

    @classmethod
    def extractErrorFromFailingMethodList(cls, wmoList):
        if len(wmoList)>0:
            return reduce(lambda x,y:x+y, [cls.extractErrorFromFailingMethod(wmo) for wmo in wmoList])
        else:
            return []

    @classmethod
    def extractErrorFromFailingMethod(cls, wmo):
        try:
            methodName = wmo._methodCls.__name__  # TODO: Make public method
            return [TrackCombError(wmo.getErrorDetails(), methodName)]
        except:
            if not CATCH_METHOD_EXCEPTIONS:
                raise
            return []

    @classmethod
    def extractResultsFromWorkingMethodList(cls, wmoList, galaxyFn):
        return TrackCombResultList(reduce(lambda x,y:x+y, [cls.extractResultsFromWorkingMethod(wmo, galaxyFn) for wmo in wmoList]))

    @classmethod
    def extractResultsFromWorkingMethod(cls, wmo, galaxyFn):
        try:
            if VERBOSE_RUNNING:
                print 'Stdout of tool: ', wmo.getResultFilesDictList()
            if not wmo.ranSuccessfully():
                if VERBOSE_RUNNING:
                    print 'skipping result output for method', wmo
                return
            allPvals = wmo.getPValue()
            allTestStats = wmo.getTestStatistic()
            # TODO: temporary hack
            if wmo._methodCls.__name__ == 'HyperBrowser':
                allFullResults = wmo.getFullResults(galaxyFn)
            else:
                allFullResults = wmo.getFullResults()
            assert len(allPvals) > 0, allPvals
            assert len(allPvals) == len(allTestStats), (allPvals, allTestStats)
            trackCombinations = allPvals.keys()

            results = []
            for trackCombination in trackCombinations:
                fullResult = allFullResults[trackCombination]
                pval = allPvals[trackCombination]
                testStat = allTestStats[trackCombination]
                methodName = wmo._methodCls.__name__ #TODO: Make public method
                annotatedChoices = wmo.annotatedChoices
                results.append(TrackCombResult(testStat, pval, fullResult, trackCombination, methodName, annotatedChoices))
            return results
        except:
            if not CATCH_METHOD_EXCEPTIONS:
                raise
            return []

    # @classmethod
    # def createMainTable(cls, galaxyFn, keptWmos, keysWithVariation):
    #
    #     def _produceTable(core, tableDict=None, columnNames=None, tableId=None, **kwArgs):
    #         return core.tableFromDictionary(
    #             tableDict, columnNames=columnNames, tableId=tableId, addInstruction=True, **kwArgs)
    #
    #     core = HtmlCore()
    #     tableData = OrderedDict()
    #     colNames = ['Method name', 'Query track', 'reference track'] + keysWithVariation + ['P-value',
    #                                                                                         'Co-localization enrichment',
    #                                                                                         'Detailed results']
    #
    #     for i, wmo in enumerate(keptWmos):
    #         if VERBOSE_RUNNING:
    #             print 'Stdout of tool: ', wmo.getResultFilesDictList()
    #         if not wmo.ranSuccessfully():
    #             if VERBOSE_RUNNING:
    #                 print 'skipping result output for method', wmo
    #             continue
    #
    #         allPvals = wmo.getPValue()
    #         allTestStats = wmo.getTestStatistic()
    #         allFullResults = wmo.getFullResults()
    #         assert len(allPvals) > 0, allPvals
    #
    #         assert len(allPvals) == len(allTestStats), (allPvals, allTestStats)
    #         for j, trackCombination in enumerate(allPvals.keys()):
    #             fullResultStaticFile = GalaxyRunSpecificFile(['details' + str(i) + '_' + str(j) + '.html'], galaxyFn)
    #             fullResult = allFullResults[trackCombination]
    #             fullResultStaticFile.writeTextToFile(fullResult)
    #             pval = allPvals[trackCombination]
    #             ts = allTestStats[trackCombination]
    #             prettyTracks = [track.split('/')[-1] for track in trackCombination]
    #             # tableData[wmo._methodCls.__name__] = prettyTracks + [wmo.annotatedChoices.get(key) for key in
    #             #                                                 keysWithVariation] + [str(pval), str(ts),
    #             #                                                                       fullResultStaticFile.getLink(
    #             #                                                                           'Full results')]
    #             keyCols = (wmo._methodCls.__name__,) + tuple(prettyTracks) + tuple(
    #                 [wmo.annotatedChoices.get(key) for key in
    #                  keysWithVariation])
    #             furtherCols = [str(pval), str(ts), fullResultStaticFile.getLink('Full results')]
    #             tableData[keyCols] = furtherCols
    #
    #     tableId = 'resultsTable'
    #     tableFile = GalaxyRunSpecificFile([tableId, 'main_table.tsv'], galaxyFn)
    #     tabularHistElementName = 'Raw main results'
    #
    #     core.tableWithTabularImportButton(tabularFile=True, tabularFn=tableFile.getDiskPath(),
    #                                       tabularHistElementName=tabularHistElementName,
    #                                       produceTableCallbackFunc=_produceTable,
    #                                       tableDict=tableData,
    #                                       columnNames=colNames, tableId=tableId, sortable=True)
    #     return core


    @classmethod
    def parseAdvancedChoices(cls, choices):
        selections = OrderedDict()
        # SELECTION BOXES:
        # mapping = {cls.WHOLE_GENOME:None,
        #            cls.EXCLUDE_SUPPLIED_BY_THE_USER:RestrictedThroughExclusion(fn)}
        if choices.restrictRegions in [cls.WHOLE_GENOME, None]:
            restrictRegions = None
        else:
            if choices.restrictedRegionFileUpload in [None, '', []]:
                fn = None
            else:
                fn = TrackFile(ExternalTrackManager.extractFnFromGalaxyTN(choices.restrictedRegionFileUpload), '')

            if choices.restrictRegions == cls.EXCLUDE_SUPPLIED_BY_THE_USER:
                restrictRegions = RestrictedThroughExclusion(fn)
            if choices.restrictRegions == cls.EXPLICIT_NEGATIVE_SET:
                restrictRegions = RestrictedThroughInclusion(fn)
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
        selectionMapping = {'clumping': 'preserveClumping'}
        # 'allowOverlaps': 'setAllowOverlaps',
        # 'choiceOfCoreDatabase': 'setPredefinedTrackIndexAndCollection'}
        # TestStat
        # distCoordSelected = [key for key in choices.distanceCoordinate if choices.distanceCoordinate[key]] \
        #                     if choices.distanceCoordinate is not None else []
        # distTypeSelected = [key for key in choices.distanceType if choices.distanceType[key]] \
        #                     if choices.distanceType is not None else[]
        # fullDistSpecs = product(distCoordSelected, distTypeSelected)
        # encodedDistSpecs = ['-'.join(spec) for spec in fullDistSpecs]
        if choices.teststatType is not None and choices.teststatType[cls.DISTANCE] == True:
            encodedDistSpecs = [ColocMeasureProximity(None, None)]
        else:
            encodedDistSpecs = []

        tsMapping = {cls.COUNTS: ColocMeasureOverlap(False, True, 0, 0),
                     cls.BASES: ColocMeasureOverlap(False, False, 0, 0)}
        overlapSpecs = [tsMapping[key] for key in choices.overlapMeasure if choices.overlapMeasure[key]] \
            if choices.overlapMeasure is not None else []

        # correlationSpecs = [key for key in choices.correlation if choices.correlation[key]] \
        #                     if choices.correlation is not None else[]
        if choices.teststatType is not None and choices.teststatType[cls.CORRELATION] == True:
            correlationSpecs = [ColocMeasureCorrelation(None)]
        else:
            correlationSpecs = []

        allTsSpecs = encodedDistSpecs + overlapSpecs + correlationSpecs
        selections['setColocMeasure'] = zip(['setColocMeasure'] * len(allTsSpecs), allTsSpecs)
        # distCoordSelections = cls.getSelectionsFromCheckboxParam(distCoordChoiceValueMapping, choices, 'distanceCoordinate', 'distCoord')
        # distCoordSelections = cls.getSelectionsFromCheckboxParam(distCoordChoiceValueMapping, choices, 'distanceType', 'distType')

        # if choices.allowOverlaps and choices.allowOverlaps[cls.DETERMINE_FROM_SUBMITTED_TRACKS]:
        #     raise
        # else:
        #     choiceValueMappings['allowOverlaps'] = {cls.NOT_ALLOWED: False, cls.MAY_OVERLAP: True}

        choiceValueMappings['clumping'] = {cls.UNIFORMLY_DISTRIBUTED: False, cls.PRESERVE_EMPIRIC_DISTRIBUTION: True}
        # choiceValueMappings['choiceOfCoreDatabase'] = {cls.LOLA_COLLECTION: {'trackIndex':'LOLACore_170206', 'trackCollection':'codex'} }
        for guiKey, selectionKey in selectionMapping.items():
            currSelection = cls.getSelectionsFromCheckboxParam(choiceValueMappings[guiKey], choices, guiKey,
                                                               selectionKey)
            assert len(currSelection.values()[0]) > 0, (guiKey, selectionKey, currSelection)
            selections.update(currSelection)
        return selections

    @classmethod
    def getSelectionsFromCheckboxParam(cls, choiceValueMappings, choiceTuple, selectionName, selectionsKey):
        choices = choiceTuple._asdict()
        # if choices[selectionName] is None:
        #     return {selectionsKey:None}
        selections = {selectionsKey: []}
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
        return cls.getValidationText(choices)

    @classmethod
    def getValidationText(cls, choices):
        if choices.allowOverlaps and choices.allowOverlaps[cls.DETERMINE_FROM_SUBMITTED_TRACKS]:
            if choices.allowOverlaps[cls.MAY_OVERLAP] or choices.allowOverlaps[cls.NOT_ALLOWED]:
                return "%s can only be selected as a single choice" % cls.DETERMINE_FROM_SUBMITTED_TRACKS
        else:
            if choices.allowOverlaps and not choices.allowOverlaps[cls.NOT_ALLOWED] and not choices.allowOverlaps[
                cls.MAY_OVERLAP]:
                return "Please select whether or not to allow genomic regions to overlap within track"
        if choices.clumping and not any(choices.clumping.values()):
            return "Please select whether or not to handle clumping"

        if TrackParser.getFnListFromTrackChoice(choices.chooseQueryTrackFile) is None:
            return "Please select query track"
        try:
            refTrackParser = ReferenceTrackParser.createFromGUIChoices(choices)
            if refTrackParser.getRefTracksFromChoices() is None:
                return "Please select reference tracks"
        except Exception, e:
            return e.message

        #workingMethodObjects = cls.getWorkingMethodObjects(choices)
        queryTrack, refTracks, selectionValues = cls.extractFromChoices(choices)
        workingMethodObjects = WorkingMethodObjectParser(queryTrack, refTracks, selectionValues,ALL_METHOD_CLASSES).getWorkingMethodObjects()

        if workingMethodObjects is None:
            return "Unresolved error"
        elif len(workingMethodObjects) == 0:
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
    @classmethod
    def getOutputFormat(cls, choices):
        """
        The format of the history element with the output of the tool. Note
        that if 'html' is returned, any print statements in the execute()
        method is printed to the output dataset. For text-based output
        (e.g. bed) the output dataset only contains text written to the
        galaxyFn file, while all print statements are redirected to the info
        field of the history item box.

        Note that for 'html' output, standard HTML header and footer code is
        added to the output dataset. If one wants to write the complete HTML
        page, use the restricted output format 'customhtml' instead.

        Optional method. Default return value if method is not defined:
        'html'
        """
        return 'customhtml'
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


def dump_args_and_more(func):
    '''This decorator dumps out the arguments passed to a function before calling it,
    as well as return value or any exception'''
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name

    def echo_func(*args,**kwargs):
        print fname, ":", ', '.join(
            '%s=%r' % entry
            for entry in zip(argnames,args) + kwargs.items())
        try:
            result = func(*args, **kwargs)
            print "-> ", result
            return result
        except:
            print '-> raised exception:'
            import traceback
            traceback.print_exc()
            raise


    return echo_func


class TrackParser:
    @classmethod
    def getFnListFromTrackChoice(cls, trackChoice):
        if trackChoice is None or trackChoice.strip() == '':
            return None

        filetype = ExternalTrackManager.extractFileSuffixFromGalaxyTN(trackChoice, allowUnsupportedSuffixes=True)
        if filetype in ['bed']:
            fnList = [TrackFile(ExternalTrackManager.extractFnFromGalaxyTN(trackChoice), \
                                ExternalTrackManager.extractNameFromHistoryTN(trackChoice))]

        elif filetype in ['gsuite']:
            gsuite = getGSuiteFromGalaxyTN(trackChoice)
            if gsuite.isPreprocessed():
                raise Exception("Please select gsuite in primary format (a gsuite referring to a set of bed files)")
            fnList = [TrackFile(gsTrack.path, gsTrack.title) for gsTrack in gsuite.allTracks()]
        else:
            print 'ERROR: ', filetype, ExternalTrackManager.extractFnFromGalaxyTN(trackChoice)
        return fnList

class ReferenceTrackParser(TrackParser):
    @classmethod
    def createFromGUIChoices(cls, choices):
        return ReferenceTrackParser(choices.analysisType, choices.choiceOfCoreDatabase, \
                                    choices.chooseReferenceTrackFile, choices.typeOfReferenceTrackCollection, \
                                    choices.chooseCustomTrackCollection)

    def __init__(self, analysisType, choiceOfCoreDatabase, chooseReferenceTrackFile, typeOfReferenceTrackCollection, chooseCustomTrackCollection):
        self._analysisType = analysisType
        self._choiceOfCoreDatabase = choiceOfCoreDatabase
        self._chooseReferenceTrackFile = chooseReferenceTrackFile
        self._typeOfReferenceTrackCollection = typeOfReferenceTrackCollection
        self._chooseCustomTrackCollection = chooseCustomTrackCollection

    def getRefTracksFromChoices(self):
        if self._analysisType == CongloProtoTool.REFERENCE_TRACKS and self._choiceOfCoreDatabase == CongloProtoTool.LOLA_COLLECTION:
            return ['prebuilt', 'LOLACore_170206']

        referenceTrackChoice = self._getRefTrackChoice()
        refTracks = self.getFnListFromTrackChoice(referenceTrackChoice)
        if len(refTracks) == 0:
            raise Exception('Please select non-empty gsuite')
        return refTracks

    def _getRefTrackChoice(self):
        typeOfAnalysis = self._analysisType
        choiceOfCoreDatabase = self._choiceOfCoreDatabase
        assert not (typeOfAnalysis == CongloProtoTool.REFERENCE_TRACKS and choiceOfCoreDatabase == CongloProtoTool.LOLA_COLLECTION)
        if typeOfAnalysis == CongloProtoTool.TWO_GENOMIC_TRACKS:
            referenceTrackChoice = self._chooseReferenceTrackFile
        elif typeOfAnalysis == CongloProtoTool.REFERENCE_TRACKS:
            if self._typeOfReferenceTrackCollection == CongloProtoTool.CORE_DATABASE:
                raise Exception("Not supported: " + str(self._choiceOfCoreDatabase))
            elif self._typeOfReferenceTrackCollection == CongloProtoTool.CUSTOM_DATABASE:
                referenceTrackChoice = self._chooseCustomTrackCollection
            else:
                raise Exception()
        else:
            raise Exception('Invalid typeOfAnalysis: ' + str(typeOfAnalysis))
        return referenceTrackChoice


class TrackList:
    pass

class TrackCombResultList(list):
    # def __init__(self):
    #     list.__init__(self)

    def getSetOfAllRefTracks(self):
        return set([res.trackCombination[1] for res in self])

    def getResultsForSpecifiedRefTrack(self, refTrack):
        return TrackCombResultList([res for res in self if res.trackCombination[1]==refTrack])

    def getResultsForSpecifiedMethodName(self, methodName):
        return TrackCombResultList([res for res in self if res.methodName==methodName])


class TrackCombResult:
    def __init__(self, testStat, pval, fullResult, trackCombination, methodName, annotatedChoices):
        self.testStat = testStat
        self.pval = pval
        self.fullResult = fullResult
        assert len(trackCombination)==2, trackCombination
        self.trackCombination = trackCombination
        self.methodName = methodName
        self.annotatedChoices = annotatedChoices

    def getPrettyTrackNames(self):
        return [track.split('/')[-1] for track in self.trackCombination]

class TrackCombError:
    def __init__(self, errorStr, methodName):
        self.errorStr = errorStr
        self.methodName = methodName

class CongloResultsGenerator:
    def __init__(self, trackCombResults, trackCombErrors, keysWithVariation, galaxyFn):
        self._trackCombResults = trackCombResults
        self._trackCombErrors = trackCombErrors
        self._keysWithVariation = keysWithVariation
        self._galaxyFn = galaxyFn
        self._subPageStaticFiles = {}

    def outputResults(self):
        refTrackSet = self._trackCombResults.getSetOfAllRefTracks()
        if len(refTrackSet)>1:
            print str(self._generateOneVsManyResults())
        else:
            print str(self._generateOneVsOneResults(self._trackCombResults))

        if len(self._trackCombErrors)>0:
            print str(self._createErrorTable())

    def _generateOneVsOneResults(self, trackCombResults):
        core = HtmlCore()
        core.append(str(self.createMainTable(trackCombResults)))
        try:
            #pass
            core.paragraph(str(self.plotPvals(trackCombResults)))
        except Exception as e:
            if not CATCH_METHOD_EXCEPTIONS:
                raise
            #core.smallHeader('Pval plotting error:')
            #core.preformatted(e)
        core.paragraph(self.getSimplisticPvalIndication(trackCombResults))
        core.paragraph('Relevant FAQ (see under FAQ tab on homepage): Why are the p-values of different methods different, when they are analysing the same research question?')
        return str(core)

    def plotPvals(self, trackCombResults):
        from proto.RSetup import r
        r(R_PLOTTING_CODE)
        pvals = [res.pval.numericResult for res in trackCombResults]
        methods = [res.methodName for res in trackCombResults]
        sf = GalaxyRunSpecificFile(['pvalPlot.png'],self._galaxyFn)
        #sf.openRFigure()
        rpvals = r.unlist(pvals)
        r.plot_pvals(rpvals, methods,sf.getDiskPath(ensurePath=True))
        #sf.closeRFigure()

        return str(HtmlCore().image(os.path.basename(sf.getDiskPath()),style='height:400px;width:auto'))
        #return sf.getLink('Pvalue-plot')

    def getSimplisticPvalIndication(self, trackCombResults):
        intro = '<b>Simplistic indication: </b>'
        coreText = self._produceCorePvalIndication(trackCombResults)
        if coreText is None:
            return ''
        else:
            return intro+coreText

    def _produceCorePvalIndication(self, trackCombResults):
        pvals = [res.pval.numericResult for res in trackCombResults]
        total = len(pvals)
        strong = len([p for p in pvals if p is not None and p <= 0.01])
        weak = len([p for p in pvals if p is not None and 0.01 < p <= 0.05])
        accept = len([p for p in pvals if p is not None and p > 0.05])
        nondef = len([p for p in pvals if p is None])
        if nondef == total:
            return "None of the selected tools provided a p-value for the relation between these two datasets"

        if (strong + nondef == total) and strong >= 2:
            return "There is a %sconsensus among the tools on concluding on a statistically significant association between the query and reference track" % (
            'clear' if strong >= 3 else '')
        if (accept + nondef == total) and accept >= 2:
            return "There is a %sconsensus among the tools that there is <b>no</b> statistical support for an association between the query and reference track" % (
            'clear' if strong >= 3 else '')

        if total - nondef == 1:
            return self._getOneConclusionPvalFormulation(accept, weak, strong)

        if nondef > 0 and total - nondef == 1:
            return "Only one of the selected tools provided a p-value, which suggests that: " + self._getOneConclusionPvalFormulation(accept, weak, strong)

        if accept == 0 and strong == 0 and weak>=2:
            return "There is a consensus among tools of a weak indication of an association between the query and reference track"
        if accept == 1 and weak == 0 and strong >= 3:
            return "The majority of tools conclude on a statistically significant association between the query and reference track, but there is some disagreement between tools"
        elif accept == 0 and weak == 1 and strong >= 3:
            return "The majority of tools conclude on a statistically significant association between the query and reference track, but some at only weak levels of significance"
        elif accept == 0 and weak > 0 and strong > 0:
            return "All tools provide some indication of statistically significant association between the query and reference track, but with a mix of strong and weak levels of significance"
        elif accept+weak>0 and strong > 0:
            return "There is no clear consensus among tools regarding the presence of any statistically significant association between the query and reference track"

        return None

    def _getOneConclusionPvalFormulation(self, accept, weak, strong):
        if strong == 1:
            return 'The data indicate a statistically significant association between the query and reference track.'
        if weak == 1:
            return 'The data provide a weak indication (p-value between 0.01 and 0.05) for a statistically significant association between the query and reference track.'
        if accept == 1:
            return 'There is <b>no</b> statistical support for an association between the query and reference track.'

    def _generateOneVsManyResults(self):
        refTrackSet = self._trackCombResults.getSetOfAllRefTracks()
        for refTrack in refTrackSet:
            resultsSubset = self._trackCombResults.getResultsForSpecifiedRefTrack(refTrack)
            self._subPageStaticFiles[refTrack] = GalaxyRunSpecificFile(['oneVsOne'+'_'+refTrack+'.html'],self._galaxyFn)
            subPageHtml = HtmlCore()
            subPageHtml.begin()
            subPageHtml.append(self._generateOneVsOneResults(resultsSubset))
            subPageHtml.end()
            self._subPageStaticFiles[refTrack].writeTextToFile(str(subPageHtml))

        core = HtmlCore()
        core.append(str(self.createRankTable()))
        core.append(str(self.createTestStatTable()))
        core.append(str(self.createPvalTable()))

        core.append(str(self.createDetailedResultsLinkTable()))
        return core

    def createDetailedResultsLinkTable(self):
        core = HtmlCore()
        core.bigHeader('Full results')
        core.paragraph('The table below provides the full results for each reference track, '
                       'obtained through all the methods/configurations chosen. '
                       'Click on the reference track, which will redirect to a new page containing '
                       'detailed results and visualizations.')

        core.tableHeader(['Detailed results per reference track'])
        for refTrack in self._trackCombResults.getSetOfAllRefTracks():
            refTrackLink = self._subPageStaticFiles[refTrack].getLink(refTrack)
            core.tableLine([refTrackLink])
        core.tableFooter()
        return core

    def createRankTable(self):
        if len(self._trackCombResults)==0:
            return ''
        someResult = self._trackCombResults[0]
        core = HtmlCore()
        core.bigHeader('Ranking of reference tracks')
        #by degree of co-localization according to each tool
        core.paragraph('''The table below shows the reference tracks ordered by the magnitude of their co-localization enrichment with the query track. 
        Ranks are given to each reference track based on the co-localization enrichment determined by each individual tool/configuration chosen. 
        A consensus rank is then obtained as a geometric mean of the individual ranks.The table can also be sorted based on method-specific rankings 
        to see the individual ranks. The test statistic (co-localization enrichment), p-values, and full results of individual tools are shown further in the tables below.''')
        core.paragraph('<b>Query track tested for co-localization:</b> ' + someResult.trackCombination[0].split('/')[-1])
        rankTableDict = defaultdict(dict)
        tsVals = [(res, res.testStat.numericResult) for res in self._trackCombResults]

        for res, val in tsVals:
            trackName = res.trackCombination[1].split('/')[-1]
            resultsForSameMethod = self._trackCombResults.getResultsForSpecifiedMethodName(res.methodName)
            rankTableDict[trackName][res.methodName] = 1 + sum(r.testStat.numericResult > val for r in resultsForSameMethod)

        assert len(rankTableDict) > 1  # More than 1 ref track
        allWmoLabels = list(set([wmoLabel for row in rankTableDict.values() for wmoLabel in row.keys()]))
        core.tableHeader(['Reference track'] + allWmoLabels + ['Consensus rank'], sortable=True)
        for trackName in rankTableDict:
            ranksInRow = [rankTableDict[trackName][wmoLabel] if wmoLabel in rankTableDict[trackName] else 'N/A' \
                          for wmoLabel in allWmoLabels]
            nonNAranks = [rankTableDict[trackName][wmoLabel] for wmoLabel in allWmoLabels if
                          wmoLabel in rankTableDict[trackName]]
            meanRank = '%.1f' % (reduce(lambda x, y: x * y, nonNAranks) ** (1.0 / len(nonNAranks)))
            #trackNameLink = self._subPageStaticFiles[trackName].getLink(trackName)
            core.tableLine([trackName] + [str(x) for x in ranksInRow] + [meanRank])
        core.tableFooter()
        return core

    def createPvalTable(self):
        return self.createTableOfExtractedResultAttribute('pval', 'P-value of co-localization enrichment for each reference track and tool')

    def createTestStatTable(self):
        return self.createTableOfExtractedResultAttribute('testStat', 'Co-localization enrichment for each reference track and tool')

    def createTableOfExtractedResultAttribute(self, attribute, headerLine):
        assert attribute in ['pval', 'testStat']
        tableDict = defaultdict(dict)
        for res in self._trackCombResults:
            trackName = res.trackCombination[1].split('/')[-1]
            #tableDict[trackName][res.methodName] = res.pval
            tableDict[trackName][res.methodName] = getattr(res,attribute)


        core = HtmlCore()
        core.bigHeader(headerLine)
        if attribute == 'pval':
            core.paragraph('The table below shows the reference tracks and their p-values for co-localization with query track, '
                           'obtained through each individual method/configuration chosen. The reference tracks are <b> not ordered </b> by any column. '
                           'However, the table cab be sorted based on the findings of each individual tool to get tool-specific orderings.')
        elif attribute == 'testStat':
            core.paragraph('The table below shows the reference tracks and their co-localization enrichment (effect size) obtained '
                           'through each individual method/configuration chosen. The reference tracks are <b> not ordered </b> by any column, '
                           'because the definition of test statistics varies in each individual tool and thus best not compared across tools. '
                           'However, the table cab be sorted based on the findings of each individual tool to get tool-specific orderings.')
        if len(tableDict) > 1:  # More than 1 ref track
            allWmoLabels = list(set([wmoLabel for row in tableDict.values() for wmoLabel in row.keys()]))
            if attribute=='testStat':
                allWmoClasses = [globals()[label] for label in allWmoLabels]
                allWmoDescr = [wmo.getTestStatDescr() for wmo in allWmoClasses]
                allWmoLabAndDescr = [label+'<br>('+descr+')' for label,descr in zip(allWmoLabels,allWmoDescr)]
            else:
                allWmoLabAndDescr = allWmoLabels
            core.tableHeader(['Reference track'] + allWmoLabAndDescr, sortable=True)
            for trackName in tableDict:
                valuesInRow = [tableDict[trackName][wmoLabel] if wmoLabel in tableDict[trackName] else 'N/A' \
                               for wmoLabel in allWmoLabels]
                #trackNameLink = self._subPageStaticFiles[trackName].getLink(trackName)
                core.tableLine([trackName] + [str(x) for x in valuesInRow])
            core.tableFooter()
        return core

    def _createErrorTable(self):
        core = HtmlCore()
        core.bigHeader('Tools that returned errors')
        core.tableHeader(['Method name', 'Tool error'])
        for i, error in enumerate(self._trackCombErrors):
            errorStaticFile = GalaxyRunSpecificFile(['errors' + str(i) + '.html'], self._galaxyFn)
            errorStaticFile.writeTextToFile(error.errorStr)
            core.tableLine([error.methodName, errorStaticFile.getLink('Tool error output')])
        core.tableFooter()
        return core

    def createMainTable(self, trackCombResults):

        def _produceTable(core, tableDict=None, columnNames=None, tableId=None, **kwArgs):
            if isinstance(core, TextCore):
                from third_party.mstripper import strip_tags
                newTableDict = OrderedDict([(key, [strip_tags(v) for v in val])
                                            for key, val in tableDict.iteritems()])
            else:
                newTableDict = tableDict
            return core.tableFromDictionary(
                newTableDict, columnNames=columnNames, tableId=tableId, addInstruction=True, **kwArgs)
        if len(trackCombResults)==0:
            return ''
        someResult = trackCombResults[0]
        prettyTracks = someResult.getPrettyTrackNames()
        core = HtmlCore()
        core.bigHeader('Detailed results of each tool and configuration')
        core.paragraph('Query track: ' + prettyTracks[0])
        core.paragraph('Reference track: ' + prettyTracks[1])

        tableData = OrderedDict()
        colNames = ['Method name'] + self._keysWithVariation + \
                   ['P-value','Co-localization enrichment', 'Detailed results']
        for j, res in enumerate(trackCombResults):
            fullResultStaticFile = GalaxyRunSpecificFile([ '_'.join(['details', prettyTracks[1], str(j), '.html']) ], self._galaxyFn)
            fullResultStaticFile.writeTextToFile(res.fullResult)
            keyCols = (res.methodName,) + \
                      tuple([res.annotatedChoices.get(key) for key in
                             self._keysWithVariation])
            furtherCols = [str(res.pval), str(res.testStat), fullResultStaticFile.getLink('Full results')]
            tableData[keyCols] = furtherCols

        tableId = 'resultsTable'
        tableFile = GalaxyRunSpecificFile([tableId, 'main_table.tsv'], self._galaxyFn)
        tabularHistElementName = 'Raw main results'

        core.tableWithTabularImportButton(tabularFile=True, tabularFn=tableFile.getDiskPath(),
                                          tabularHistElementName=tabularHistElementName,
                                          produceTableCallbackFunc=_produceTable,
                                          tableDict=tableData,
                                          columnNames=colNames, tableId=tableId, sortable=True)
        return core


# def runResultOutputFromPickle(): #TODO: Temporary
#     pickleFn = '/Users/sandve/Downloads/trackComb.pickle'
#     trackCombResults = load(open(pickleFn))
#     CongloProtoTool.outputResults(trackCombResults, None, [], '/software/galaxy/personal/geirksa/galaxy_dev/database/files/000/dataset_886.dat')

#runResultOutputFromPickle()


R_PLOTTING_CODE = '''
## the libraries ggplot2 and ggthemes should be installed
## install.packages('ggplot2')
## install.packages('ggthemes')
## input is a list of p-values and a list of corresponding tools/methods that produced the p-values.

plot_pvals <- function(pvals_list,methods_list,fn){
  library(ggplot2)
  library(ggthemes)
  pvals_list <- as.numeric(pvals_list)
  if(!all(!is.na(pvals_list))){
    methods_list <- methods_list[-which(is.na(pvals_list))]
    pvals_list <- pvals_list[-which(is.na(pvals_list))]
  }
  plot_data <- data.frame(pvals_list,methods_list)
  plot_object <- ggplot(data=plot_data,aes(x=methods_list,y=-log10(pvals_list)))
  final_plot <- plot_object+geom_bar(stat = 'identity',width=0.2)+coord_flip()+xlab('')+ylab('-log10(p-val)')+theme_minimal()
  ggsave(filename=fn,plot=final_plot,dpi = 300)  
}
'''
