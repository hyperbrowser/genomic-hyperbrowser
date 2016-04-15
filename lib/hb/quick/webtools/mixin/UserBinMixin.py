from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.util.CustomExceptions import AbstractClassError
from quick.application.GalaxyInterface import GalaxyInterface
# This is a template prototyping GUI that comes together with a corresponding
# web page.


class UserBinMixin(object):

    @staticmethod
    def getUserBinInputBoxNames():
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
        '''
        return [('Compare in','CompareIn'),('Which: (comma separated list, * means all)', 'Bins'), ('Genome region: (Example: chr1:1-20m, chr2:10m-) ','CustomRegion'),\
        ('Bin size: (* means whole region k=Thousand and m=Million E.g. 100k)', 'BinSize'), ('Bins from history', 'HistoryBins')]



    @staticmethod
    def getOptionsBoxCompareIn(prevChoices): # Alternatively: getOptionsBoxKey()
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
        - Returns: OrderedDict with galaxy track name as key and selection
                   status (bool) as value.

        Hidden field:           ('__hidden__', 'Hidden value')
        - Returns: string

        Table:                  [['header1','header2'], ['cell1_1','cell1_2'], ['cell2_1','cell2_2']]
        - Returns: None

        Check box list:         OrderedDict([('key1', True), ('key2', False), ('key3', False)])
        - Returns: OrderedDict from key to selection status (bool).
        '''

        #This code checks if the tool is in basic mode, we don't want to display user bin selection in basic mode. 
        #For this to work you must name the optionBox isBasic in your tool.
        try:
            isBasicMode = prevChoices.isBasic
        except:
            pass
        else:
            if isBasicMode:
                return None
        ########################
        
        return ['Chromosome arms','Chromosomes','Cytobands','Genes(Ensembl)','Custom specification','Bins from history']

    @staticmethod
    def getOptionsBoxBins(prevChoices):
        '''
        See getOptionsBoxCompareIn().

        '''
        if prevChoices.CompareIn in ['Chromosome arms','Chromosomes','Cytobands','Genes(Ensembl)']:
            return '*'

    @staticmethod
    def getOptionsBoxCustomRegion(prevChoices):
        '''
        See getOptionsBoxCompareIn().

        '''
        if prevChoices.CompareIn == 'Custom specification':
            return '*'


    @staticmethod
    def getOptionsBoxBinSize(prevChoices):
        '''
        See getOptionsBoxCompareIn().
        '''
        if prevChoices.CompareIn == 'Custom specification':
            return '*'


    @classmethod
    def getOptionsBoxHistoryBins(cls, prevChoices):
        if prevChoices.CompareIn == 'Bins from history':
            from gold.application.DataTypes import getSupportedFileSuffixesForBinning
            return cls.getHistorySelectionElement(*getSupportedFileSuffixesForBinning())


    @staticmethod
    def getRegsAndBinsSpec(choices):
        '''
        Returns the regSpec and binSpec for the choices made on the gui.
        '''
        regsMapper = {'Chromosome arms':'__chrArms__','Chromosomes':'__chrs__','Cytobands':'__chrBands__','Genes(Ensembl)':'__genes__'}
        
        try:
            isBasic = choices.isBasic
        except:
            pass
        else:
            if isBasic:
                return "__chrs__", "*"
        
        if choices.CompareIn == 'Custom specification':
            regSpec = choices.CustomRegion
            binSpec = choices.BinSize
        elif regsMapper.get(choices.CompareIn):
            regSpec = regsMapper[choices.CompareIn]
            binSpec = choices.Bins
        else:
            if choices.HistoryBins:
                histItem = choices.HistoryBins.split(':')
                binSpec = ExternalTrackManager.extractFnFromGalaxyTN(histItem)
                regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(histItem)
            else:
                return None, None

        return regSpec, binSpec


    @classmethod
    def validateUserBins(cls, choices):
        '''
        See getOptionsBox1().
        '''
        
        try:
            isBasic = choices.isBasic
        except:
            pass
        else:
            if isBasic:
                return None
        
        genome = cls._getGenome(choices)
        trackName1 = cls._getTrackName1(choices)
        trackName2 = cls._getTrackName2(choices)

        regSpec, binSpec = cls.getRegsAndBinsSpec(choices)
        #if not regSpec or not binSpec:
        #    return 'Please select a history element for binning.'

        errorString = GalaxyInterface._validateRegAndBinSpec(regSpec, binSpec, genome, [trackName1, trackName2])
        if errorString:
            return errorString
#
#         regsMapper = {'Chromosome arms':'__chrArms__','Chromosomes':'__chrs__','Cytobands':'__chrBands__','Genes(Ensembl)':'__genes__','ENCODE Pilot regions':'__encode__'}
#         if choices.CompareIn == 'Custom specification':
#
#             regSpec = choices.CustomRegion
#             binSpec = choices.BinSize
#             if re.match('[0-9]+[mk]?', binSpec).end() != len(binSpec):
#                 return 'Invalid Syntax for Bin size(only numbers and the characters "mk" allowed)'
#
#         elif regsMapper.get(choices.CompareIn):
#             regSpec = regsMapper[choices.CompareIn]
#             binSpec = choices.Bins
#         else:
#             histItem = choices.HistoryBins.split(':')
#             binSpec = ExternalTrackManager.extractFnFromGalaxyTN(histItem)
#             regSpec = ExternalTrackManager.extractFileSuffixFromGalaxyTN(histItem)
#
#         return regSpec, binSpec

    @staticmethod
    def _getGenome(choices):
        if hasattr(choices, 'genome'):
            return choices.genome
        else:
            raise AbstractClassError()

    @staticmethod
    def _getTrackName1(choices):
        return None

    @staticmethod
    def _getTrackName2(choices):
        return None
