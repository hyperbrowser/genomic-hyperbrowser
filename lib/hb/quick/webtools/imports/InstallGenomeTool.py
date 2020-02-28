import ast
import os
from collections import OrderedDict, Counter
from copy import copy
from datetime import datetime

from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.extra.GenomeImporter import GenomeImporter
from quick.genome.GenomeCommonFunctions import STANDARDIZED_TRACKS, PARSING_ERROR_TRACKS, \
    NMER_CHAINS, TRACKS_NO_OVERLAPS, TRACKS_WITH_OVERLAPS, removeGenomeData, installGenome
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class InstallGenomeTool(GeneralGuiTool):
    
    NON_UNIQUE_CHROMOSOME_NAME_TEXT= "NON_UNIQUE_NAME_NUMBER"

    TRACK_FOLDERS = [STANDARDIZED_TRACKS, PARSING_ERROR_TRACKS, NMER_CHAINS, TRACKS_NO_OVERLAPS, TRACKS_WITH_OVERLAPS]

    NO = 'No'
    YES = 'Yes'
    ALL = 'All'
    FROM_CHROMOSOME_LIST = 'From chromosome list'
    FROM_SELECTION = 'From selection'
    ALL_PREV_SELECTED = 'All previously selected'
    
    @staticmethod
    def getToolName():
        return "Install uploaded genome"

    @staticmethod
    def getInputBoxNames():
        return [('Select genome from history', 'selectGenome'), #1
                ('', 'tempChrNames'),
                ('Edit chromosome names?', 'editChrNames'), #2
                ('Chromosome names found in fasta file(s)', 'chrNamesFound'), #3
                ('Edit all chromosome names using regular expression?', 'editChrNamesWithRegExp'), #4
                ('Regular expression used to edit chromosome names', 'regExp'), #5
                ('Chromosome name prefix', 'chrNamePrefix'), #6
                ('Chromosome name delimeter', 'chrNameDelimiter'), #7
                ('Chromosome name suffix', 'chrNameSuffix'),#8
                ('Use which chromosomes?', 'chrSelectionType'),#9
                ('', 'renamedChrs'),
                ('Select chromosomes', 'selectChrs'), #10
                ('Select chromosomes (delete the ones to not use)', 'chrList'),#11
                ('Use which chromosomes as standard chromosomes (i.e. should always be displayed)?', 'standardChrSelectionType'),#12
                ('Select standard chromosomes', 'selectStandardChrs'), #13
                ('Select standard chromosomes (delete the ones to not use)', 'standardChrList')#14
                 ]

    @staticmethod
    def getOptionsBoxSelectGenome():
        "Returns a list of options to be displayed in the first options box"
        return '__history__', 'hbgenome'

    @classmethod
    def getOptionsBoxTempChrNames(cls, prevChoices):
        if prevChoices.selectGenome is not None:
            tempInfoFile = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices.selectGenome)
            tempChrNames = GenomeImporter.getChromosomeNames(tempInfoFile)

            return '__hidden__', tempChrNames
    
    @classmethod
    def getOptionsBoxEditChrNames(cls, prevChoices):
        if prevChoices.selectGenome is not None:
            return [cls.NO, cls.YES]
    
    @classmethod
    def getOptionsBoxChrNamesFound(cls, prevChoices):
        if prevChoices.selectGenome is not None and prevChoices.editChrNames == cls.YES:
            tempChrsList = cls._getTempChromosomeNamesList(prevChoices)
            tempChrs = os.linesep.join(sorted(tempChrsList))
            return tempChrs, len(tempChrsList)
        return None
    
    @classmethod
    def getOptionsBoxEditChrNamesWithRegExp(cls, prevChoices):
        if prevChoices.selectGenome is not None:
            return [cls.NO, cls.YES]
        
    @classmethod
    def getOptionsBoxRegExp(cls, prevChoices):
        return '.*' if prevChoices.editChrNamesWithRegExp == cls.YES else None
    
    @classmethod
    def getOptionsBoxChrNamePrefix(cls, prevChoices):
        return '' if prevChoices.editChrNamesWithRegExp == cls.YES else None
    
    @classmethod
    def getOptionsBoxChrNameDelimiter(cls, prevChoices):
        return '_' if prevChoices.editChrNamesWithRegExp == cls.YES else None
    
    @classmethod
    def getOptionsBoxChrNameSuffix(cls, prevChoices):
        return '' if prevChoices.editChrNamesWithRegExp == cls.YES else None

    @classmethod
    def getOptionsBoxRenamedChrs(cls, prevChoices):
        if prevChoices.selectGenome is not None:
            renamedChrs = cls._getRenamedChrDict(prevChoices)

            return '__hidden__', renamedChrs
    
    @classmethod
    def getOptionsBoxChrSelectionType(cls, prevChoices):
        if prevChoices.selectGenome is not None:
            return [cls.ALL, cls.FROM_SELECTION, cls.FROM_CHROMOSOME_LIST]

    @classmethod
    def getOptionsBoxSelectChrs(cls, prevChoices):
        if prevChoices.chrSelectionType == cls.FROM_SELECTION:
            chrList = cls._getRenamedChrListFromCache(prevChoices)
            chrList.sort()

            return OrderedDict([(chrName, True) for chrName in chrList])

    @classmethod
    def getOptionsBoxChrList(cls, prevChoices):
        if prevChoices.chrSelectionType == cls.FROM_CHROMOSOME_LIST:
            chrList = cls._getRenamedChrListFromCache(prevChoices)
            chrList.sort()
            return os.linesep.join(chrList), len(chrList), False
    
    @classmethod
    def getOptionsBoxStandardChrSelectionType(cls, prevChoices):
        if prevChoices.selectGenome is not None:
            return [cls.ALL_PREV_SELECTED, cls.FROM_SELECTION, cls.FROM_CHROMOSOME_LIST]
    
    @classmethod
    def getOptionsBoxSelectStandardChrs(cls, prevChoices):
        if prevChoices.standardChrSelectionType == cls.FROM_SELECTION:
            availableChrsList = cls._getSelectedChrs(prevChoices, 'chrSelectionType', 'selectChrs', 'chrList')

            return OrderedDict([(chrName, True) for chrName in availableChrsList])
            
    @classmethod
    def getOptionsBoxStandardChrList(cls, prevChoices):
        if prevChoices.standardChrSelectionType == cls.FROM_CHROMOSOME_LIST:
            availableChrsList = cls._getSelectedChrs(prevChoices, 'chrSelectionType', 'selectChrs', 'chrList')

            return os.linesep.join(availableChrsList), len(availableChrsList), False

    @classmethod
    def _getSelectedChrs(cls, choices, selectionTypeBoxName, selectionBoxName, listBoxName):
        if getattr(choices, selectionTypeBoxName) == cls.FROM_SELECTION:
            selectedChrs = [ch for ch, selected in getattr(choices, selectionBoxName).iteritems() if selected]
        elif getattr(choices, selectionTypeBoxName) == cls.FROM_CHROMOSOME_LIST:
            selectedChrs = [x.strip() for x in getattr(choices, listBoxName).strip().split(os.linesep)]
        else:
            chrList = cls._getRenamedChrListFromCache(choices)
            selectedChrs = sorted(chrList)

        return selectedChrs

    @classmethod
    def _getSelectedChrsFromList(cls, choices, selectionTypeBoxName, listBoxName):
        if getattr(choices, selectionTypeBoxName) == cls.FROM_CHROMOSOME_LIST:
            selectedChrs = [x.strip() for x in getattr(choices, listBoxName).strip().split(os.linesep)]

            return selectedChrs

    @classmethod
    def _getRenamedChrDict(cls, prevChoices):
        chrResultList = []
        renamedChrsDict = {}

        tempChrNamesList = cls._getTempChromosomeNamesList(prevChoices)
        if prevChoices.editChrNames == cls.NO:
            chrNamesList = tempChrNamesList
        else:
            chrNamesList = [ch.strip() for ch in prevChoices.chrNamesFound.split(os.linesep)]

        if chrNamesList:
            if prevChoices.editChrNamesWithRegExp == cls.NO:
                chrResultList = copy(chrNamesList)
            else:
                prefix = prevChoices.chrNamePrefix
                delimeter = prevChoices.chrNameDelimiter
                suffix = prevChoices.chrNameSuffix
                import re
                try:
                    pattern = re.compile(prevChoices.regExp.strip())
                except:
                    return []

                for ch in chrNamesList:
                    if prevChoices.regExp.strip() != '.*':
                        match = pattern.search(ch)
                        if match is not None:
                            groupdict = match.groupdict()
                            if len(groupdict) > 0:
                                renamedChr = delimeter.join(
                                    [groupdict[x] for x in sorted(groupdict.keys()) \
                                     if groupdict[x] is not None])
                            else:
                                groups = match.groups('')
                                if len(groups) == 0:
                                    renamedChr = match.group(0)
                                else:
                                    renamedChr = delimeter.join(groups)

                            chrResultList.append(prefix + renamedChr + suffix)
                    else:
                        chrResultList.append(prefix + ch + suffix)

            for ch, renamedCh in zip(tempChrNamesList, chrResultList):
                renamedChrsDict[ch] = renamedCh

        return renamedChrsDict

    @classmethod
    def _getRenamedChrListFromCache(cls, prevChoices):
        if prevChoices.selectGenome is not None and prevChoices.renamedChrs:
            renamedChrs = prevChoices.renamedChrs
            if isinstance(renamedChrs, unicode):
                renamedChrs = ast.literal_eval(renamedChrs)

            return renamedChrs.values()

    @classmethod
    def _getTempChromosomeNamesList(cls, prevChoices):
        chrNames = prevChoices.tempChrNames
        if isinstance(chrNames, unicode):
            chrNames = ast.literal_eval(chrNames)

        return chrNames
    
    @staticmethod
    def getResetBoxes():
        return ['selectGenome']

    @classmethod
    def _getChosenGenome(cls, prevChoices):
        uploadedGenomeHist = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0].split(":"))
        genomeName = GenomeImporter.getGenomeAbbrv(uploadedGenomeHist)
        gi = GenomeInfo(genomeName)

        return gi
    
    @classmethod
    def validateAndReturnErrors(cls, choices):
        if choices.selectGenome is None:
            return ''

        chosenGenome = cls._getChosenGenome(choices)
        # if chosenGenome.isInstalled():
        #     return 'Genome ' + chosenGenome.genome + ' is already installed. Please remove it before trying to install it again.'

        numOrigChrs = len(cls._getTempChromosomeNamesList(choices))
        
        if choices.editChrNames == cls.YES:
            numRenamedChrs = len(choices.chrNamesFound.split(os.linesep))
            if numRenamedChrs != numOrigChrs:
                return 'The number of renamed chromosomes is not equal to the original count of '\
                        'chromosomes: %i != %i' % (numRenamedChrs, numOrigChrs)
        
        if choices.editChrNamesWithRegExp == cls.YES:
            try:
                import re
                pattern = re.compile(choices.regExp.strip())
            except Exception, e:
                return 'Error in regular expression: ', e
        
        chrList = cls._getRenamedChrListFromCache(choices)

        selectedChrs = cls._getSelectedChrs(choices, 'chrSelectionType', 'selectChrs', 'chrList')
        selectedStandardChrs = cls._getSelectedChrs(choices, 'standardChrSelectionType', 'selectStandardChrs', 'standardChrList')

        for selected in [selectedChrs, selectedStandardChrs]:
            if selected:
                for ch in selected:
                    if ch not in chrList:
                        return 'Chromosome "%s" is not a valid chromosome name. ' \
                        'It is not allowed to edit the names in the chromosome selection list. ' \
                        'This error may also arise from renaming the chromosome name ' \
                        'based on changes in the previous options. If so, please reset the ' \
                        'chromosome selection list by selecting "All" and then "From chromosome list" ' \
                        'in the appropriate selection box.' % ch

        renamedChrList = cls._getRenamedChrListFromCache(choices)
        if renamedChrList:
            if len(renamedChrList) != len(set(renamedChrList)):
                duplicates = [ch for ch, count in Counter(renamedChrList).items() if count > 1]
                return 'Chromosomes with non-unique name were found: ' + str(duplicates) + '. Please rename them.'

        if not selectedStandardChrs or len(selectedStandardChrs) == 0:
            return 'You need to select at least one chromosome as a standard chromosome.'
        
        valid_chars = ''.join([chr(i) for i in range(33, 127) if i not in [46, 47, 92]])

        if chrList:
            for curChr in chrList:
                illegalchars = ''.join(c for c in curChr if c not in valid_chars)
                if len(illegalchars)>0:
                    return 'Chromosome name "%s" contains illegal characters: "%s". Please rename using legal characters "%s".' % (curChr, illegalchars,valid_chars)
    
    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
        print 'Executing...'
        
        tempInfoFile = ExternalTrackManager.extractFnFromGalaxyTN(choices.selectGenome.split(":"))
        abbrv = GenomeImporter.getGenomeAbbrv(tempInfoFile)

        for folder in cls.TRACK_FOLDERS:
            removeGenomeData(abbrv, folder, removeFromShelve=False)

        selectedChrs = cls._getSelectedChrs(choices, 'chrSelectionType', 'selectChrs', 'chrList')
        selectedStandardChrs = cls._getSelectedChrs(choices, 'standardChrSelectionType', 'selectStandardChrs', 'standardChrList')

        renamedChrsDict = {}
        renamedChrs = choices.renamedChrs
        if isinstance(renamedChrs, unicode):
            renamedChrs = ast.literal_eval(renamedChrs)
        for ch, renamedCh in renamedChrs.iteritems():
            if renamedCh in selectedChrs:
                renamedChrsDict[ch] = renamedCh

        print 'All chromosomes chosen: ' + str(renamedChrsDict)
        print 'Standard chromosomes chosen: ' + ", ".join(selectedStandardChrs)

        installGenome(abbrv, renamedChrsDict, selectedStandardChrs, username)
        
    @staticmethod
    def isPublic():
        return False
    
    @staticmethod
    def isDynamic():
        return True
    
    @staticmethod
    def getToolDescription():
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.orderedList(['Choose a file from history were you previously have used the '\
                         '"Download Genome Tool". If you have not first used that tool no '\
                         'appropriate elements will appear in the list.',
                         'Rename the chromosome names found in the fasta files if needed. '\
                         'Do not delete or add lines! The standard way of naming chromosome in '\
                         'the Genomic HyperBrowser is "chr1, chr2, ..." and "chrM" '\
                         'for the mithocondrial DNA. Other chromosomes regain their usual name.',
                         'If you want to filter the chromosome names in a same manner for all chromosomes, '\
                         'type a regular expression for filtering. Use parenthesis to select '\
                         'groups to extract. The string matched by the groups will be returned, '\
                         'separated by the underscore character. '\
                         'If the groups are named, they will be presented in their sorted order. '\
                         'If no groups are defined, the whole match is returned. '\
                         'Note: You need to make sure that the pattern matches all chromosome names. '\
                         'Example: "(?P&lt;b&gt;.*)r(?P&lt;a&gt;.*)" return "34_12" for the string "12r34"',
                         'Choose which chromosomes to install.',
                         'Choose which chromosomes to install as "standard" (typically, chr1, chr2, chrX). '\
                         'The unchecked will be treated as "extended" and not usually included in tests '\
                         'in the HyperBrowser.'])
        return str(core)
