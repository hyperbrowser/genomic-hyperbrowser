import os
import shutil
from collections import OrderedDict
from copy import copy
from datetime import datetime

from config.Config import NONSTANDARD_DATA_PATH, ORIG_DATA_PATH, PARSING_ERROR_DATA_PATH, \
    NMER_CHAIN_DATA_PATH
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.extra.GenomeImporter import GenomeImporter
from quick.genome.GenomeCommonFunctions import STANDARDIZED_TRACKS, PARSING_ERROR_TRACKS, \
    NMER_CHAINS, TRACKS_NO_OVERLAPS, TRACKS_WITH_OVERLAPS, removeGenomeData
from quick.util.CommonFunctions import createDirPath, ensurePathExists
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class InstallGenomeTool(GeneralGuiTool):
    
    NON_UNIQUE_CHROMOSOME_NAME_TEXT="NON_UNIQUE_NAME_NUMBER"

    TRACK_FOLDERS = [STANDARDIZED_TRACKS, PARSING_ERROR_TRACKS, NMER_CHAINS, TRACKS_NO_OVERLAPS, TRACKS_WITH_OVERLAPS]
    
    @staticmethod
    def getToolName():
        return "Install uploaded genome"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return [('Select genome from history', 'selectGenome'), #1
                ('Display editable chromosome names?', 'displayChrNames'), #2
                ('Chromosome names found in fasta file(s)', 'chrNamesFound'), #3
                ('Edit all chromosome names using regular expression?', 'editChrNamesWithRegExp'), #4
                ('Regular expression used to filter chromosome names', 'regExp'), #5
                ('Chromosome name prefix', 'chrNamePrefix'), #6
                ('Chromosome name delimeter', 'chrNameDelimiter'), #7
                ('Chromosome name suffix', 'chrNameSuffix'),#8
                ('Use which chromosomes?', 'chrSelectionType'),#9
                ('Select chromosomes', 'allChrs'), #10
                ('Select chromosomes (delete the ones to not use)', 'chrList'),#11
                ('Use which chromosomes as standard chromosomes (i.e. should always be displayed)?', 'standardChrs'),#12
                ('Select standard chromosomes', 'standardChrsSelection'), #13
                ('Select standard chromosomes (delete the ones to not use)', 'standardChrsList')#14
                 ]

    @staticmethod    
    def getOptionsBoxSelectGenome():
        "Returns a list of options to be displayed in the first options box"
        return '__history__', 'hbgenome'

    
    @staticmethod    
    def getOptionsBoxDisplayChrNames(prevChoices):
        return ['Hide', 'Show']
    
    @staticmethod    
    def getOptionsBoxChrNamesFound(prevChoices):
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)
        '''
        if prevChoices.selectGenome is not None and prevChoices.displayChrNames == 'Show':
            tempChrs = InstallGenomeTool._getTempChromosomeNames(prevChoices.selectGenome)
            return tempChrs, len(tempChrs.split(os.linesep))
        return None
    
    @staticmethod    
    def getOptionsBoxEditChrNamesWithRegExp(prevChoices):
        return ['Keep as they are', 'Edit using regular expression']
        
    @staticmethod    
    def getOptionsBoxRegExp(prevChoices):
        return '.*' if prevChoices.editChrNamesWithRegExp == 'Edit using regular expression' else None
    
    @staticmethod    
    def getOptionsBoxChrNamePrefix(prevChoices):
        return '' if prevChoices.editChrNamesWithRegExp == 'Edit using regular expression' else None
    
    @staticmethod    
    def getOptionsBoxChrNameDelimiter(prevChoices):
        return '_' if prevChoices.editChrNamesWithRegExp == 'Edit using regular expression' else None
    
    @staticmethod    
    def getOptionsBoxChrNameSuffix(prevChoices):
        return '' if prevChoices.editChrNamesWithRegExp == 'Edit using regular expression' else None
    
    @staticmethod    
    def getOptionsBoxChrSelectionType(prevChoices):
        return ['All', 'From selection', 'From chromosome list']

    @staticmethod    
    def getOptionsBoxAllChrs(prevChoices):
        if prevChoices.chrSelectionType == 'From selection':
            return InstallGenomeTool._getRenamedChrDict(prevChoices)
            
    @staticmethod    
    def getOptionsBoxChrList(prevChoices):
        if prevChoices.chrSelectionType == 'From chromosome list':
            chrDict = InstallGenomeTool._getRenamedChrDict(prevChoices)
            return os.linesep.join(chrDict.keys()), len(chrDict), False
    
    @staticmethod
    def getOptionsBoxStandardChrs(prevChoices):
        return ['All previously selected', 'From selection', 'From chromosome list']
    
    @staticmethod    
    def getOptionsBoxStandardChrsSelection(prevChoices):
        if prevChoices.standardChrs == 'From selection':
            return InstallGenomeTool._getRenamedChrDictWithSelection(prevChoices, resetSelected=True, deleteUnselected=True)
            
    @staticmethod    
    def getOptionsBoxStandardChrsList(prevChoices):
        if prevChoices.standardChrs == 'From chromosome list':
            chrDict = InstallGenomeTool._getRenamedChrDictWithSelection(prevChoices, resetSelected=True, deleteUnselected=True)
            return os.linesep.join(chrDict.keys()), len(chrDict), False

    @staticmethod
    def _getRenamedChrDictWithSelection(choices, resetSelected=False, deleteUnselected=False,
            stdChrs=False):
        if stdChrs:
            chrDict = copy(
                InstallGenomeTool._getRenamedChrDictWithSelection(choices, stdChrs=False))

            typeOfSelectionIndex = 11
            chrFromSelectionIndex = 12
            chrFromListIndex = 13
        else:
            chrDict = copy(InstallGenomeTool._getRenamedChrDict(choices))
            for key in chrDict:
                chrDict[key] = True

            typeOfSelectionIndex = 8
            chrFromSelectionIndex = 9
            chrFromListIndex = 10

        if choices[typeOfSelectionIndex] == 'From selection':
            retDict = copy(choices[chrFromSelectionIndex])

        elif choices[typeOfSelectionIndex] == 'From chromosome list':
            selectedChrs = set(
                [x.strip() for x in choices[chrFromListIndex].strip().split(os.linesep)])
            for key in chrDict:
                chrDict[key] = key in selectedChrs
            retDict = chrDict
        else:
            retDict = chrDict

        if deleteUnselected:
            for key in retDict.keys():
                if not retDict[key]:
                    del retDict[key]

        if resetSelected:
            for key in retDict.keys():
                if retDict[key]:
                    retDict[key] = False

        return retDict

    @staticmethod
    def _getRenamedChrDict(prevChoices):
        chrDict = OrderedDict()
        chrList = []

        if prevChoices.selectGenome and prevChoices.displayChrNames == 'Hide':
            chrText = InstallGenomeTool._getTempChromosomeNames(prevChoices.selectGenome)
        else:
            chrText = prevChoices.chrNamesFound

        if chrText:
            if prevChoices.editChrNamesWithRegExp == 'Keep as they are':
                chrList = [x.strip() for x in chrText.split(os.linesep)]
            else:
                prefix = prevChoices.chrNamePrefix
                delimeter = prevChoices.chrNameDelimiter
                suffix = prevChoices.chrNameSuffix
                import re
                try:
                    pattern = re.compile(prevChoices.regExp.strip())
                except:
                    return OrderedDict()

                for line in chrText.split(os.linesep):
                    line = line.strip()

                    if prevChoices.regExp.strip() != '.*':
                        match = pattern.search(line)
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

                            chrList.append(prefix + renamedChr + suffix)
                            continue

                    chrList.append(prefix + line + suffix)

            countDict = {}
            for chrName in chrList:
                if chrName in chrDict:
                    countDict[chrName] = countDict[chrName] + 1 if chrName in countDict else 1
                    chrDict["%s_%s_%d" % (
                    chrName, InstallGenomeTool.NON_UNIQUE_CHROMOSOME_NAME_TEXT,
                    countDict[chrName])] = False
                else:
                    chrDict[chrName] = False
        return chrDict

    @staticmethod
    def _getTempChromosomeNames(galaxyTn):
        if isinstance(galaxyTn, basestring):
            galaxyTn = galaxyTn.split(":")
        tempinfofile=ExternalTrackManager.extractFnFromGalaxyTN(galaxyTn)
        #abbrv=GenomeImporter.getGenomeAbbrv(tempinfofile)
        #return os.linesep.join(GenomeInfo(abbrv).sourceChrNames)
        return os.linesep.join(GenomeImporter.getChromosomeNames(tempinfofile))
    
    
    @staticmethod
    def getResetBoxes():
        return [1, 9]
    
    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']

    @classmethod
    def getChosenGenome(self, prevChoices):
        uploadedGenomeHist = ExternalTrackManager.extractFnFromGalaxyTN(prevChoices[0].split(":"))
        genomeName = GenomeImporter.getGenomeAbbrv(uploadedGenomeHist)
        gi = GenomeInfo(genomeName)

        return gi
    
    @staticmethod
    def validateAndReturnErrors(choices):
        if choices.selectGenome is None:
            return ''

        chosenGenome = InstallGenomeTool.getChosenGenome(choices)
        if chosenGenome.isInstalled():
            return 'Genome ' + chosenGenome.genome + ' is already installed. Please remove it before trying to install it again.'

        numOrigChrs = len(InstallGenomeTool._getTempChromosomeNames(choices.selectGenome).split(os.linesep))
        
        if choices.displayChrNames == 'Show':
            numRenamedChrs = len(choices.chrNamesFound.split(os.linesep))
            if numRenamedChrs != numOrigChrs:
                return  'The number of renamed chromosomes is not equal to the original count of '\
                        'chromosomes: %i != %i' % (numRenamedChrs, numOrigChrs)
        
        if choices.editChrNamesWithRegExp == 'Edit using regular expression':
            try:
                import re
                pattern = re.compile(choices.regExp.strip())
            except Exception, e:
                return 'Error in regular expression: ', e
        
        chrDict = InstallGenomeTool._getRenamedChrDict(choices)

        for typeOfSelectionIndex in [8, 11]:
            if choices[typeOfSelectionIndex] == 'From chromosome list':
                for selectedChr in choices[typeOfSelectionIndex+2].strip().split(os.linesep):
                    selectedChr = selectedChr.strip()
                    if selectedChr not in chrDict:
                        return 'Chromosome "%s" is not a valid chromosome name. '\
                               'It is not allowed to edit the names in the chromosome selection list. '\
                               'This error may also arise from renaming the chromosome name '\
                               'based on changes in the previous options. If so, please reset the '\
                               'chromosome selection list by selecting "All" and then "From chromosome list" '\
                               'in the appropriate selection box.' % selectedChr
                        
        selChrDict = InstallGenomeTool._getRenamedChrDictWithSelection(choices)
        
        selectedChromNames =  [chrom.split('_' + InstallGenomeTool.NON_UNIQUE_CHROMOSOME_NAME_TEXT)[0] for chrom, selected in selChrDict.iteritems() if selected]
        if len(set(selectedChromNames)) != len(selectedChromNames):
            return '%d of the selected chromosome names are not unique. Please rename them.' \
                % (len(selectedChromNames) - len(set(selectedChromNames)))
        
        stdChrDict = InstallGenomeTool._getRenamedChrDictWithSelection(choices, stdChrs=True)
        
        numStdChr = len([x for x in stdChrDict if stdChrDict[x]])
        if numStdChr == 0:
            return 'You need to select at least one chromosome as a standard chromosome.'
        
        valid_chars =''.join([chr(i) for i in range(33, 127) if i not in [46, 47, 92]])
        
        allUsedChrs = [chrom[0] for chrom in chrDict.iteritems() if chrom[-1]]
        for curChr in allUsedChrs:
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
        
        tempinfofile = ExternalTrackManager.extractFnFromGalaxyTN(choices.selectGenome.split(":"))
        abbrv = GenomeImporter.getGenomeAbbrv(tempinfofile)

        for folder in cls.TRACK_FOLDERS:
            removeGenomeData(abbrv, folder, removeFromShelve=False)

        #chrNamesInFasta=gi.sourceChrNames
        chrNamesInFasta = cls._getTempChromosomeNames(choices[0]).split(os.linesep)
        
        chromNamesDict={}
        chrDict = cls._getRenamedChrDictWithSelection(choices)
            
        for i, key in enumerate(chrDict.keys()):
            if chrDict[key]:
                chromNamesDict[chrNamesInFasta[i]]=key
        print 'All chromosomes chosen: ' + str(chromNamesDict)
            
        stdChrDict = cls._getRenamedChrDictWithSelection(choices, stdChrs=True)
        stdChrs = [x for x in stdChrDict if stdChrDict[x]]
        print 'Standard chromosomes chosen: ' + ", ".join(stdChrs)

        gi = GenomeInfo(abbrv)
        GenomeImporter.createGenome(abbrv, gi.fullName, chromNamesDict, stdChrs, username=username)
        
        gi.installedBy = username
        gi.timeOfInstallation = datetime.now()
        gi.store()
        
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
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
