import re
from copy import copy

from gold.description.AnalysisOption import AnalysisOption
from gold.util.CommonClasses import OrderedDefaultDict
from gold.util.CustomExceptions import ShouldNotOccurError
from gold.application.LogSetup import logging, logException, logMessage

# An analysisDef is a text string from analysisList.py and consists of text and
# configs A config has a name (referred to as label) and a set of choices. Both
# the option and each choice is a tuple of (key,text). Thus, both options and
# choices can be referred to by the keyname and the text. The syntax of a config
# in analysisDef is:
#
# [labelKey:labelText=choiceKey1:choiceText1/choiceKey2:choiceText2]

# A '_' prefix can be used to mark hidden behavior. Text-parts are set equal to
# key if omitted.
#
# The class AnalysisDefHandler is used to handle a whole analysisDef, with each
# option again handled by a AnalysisOption-object

class AnalysisSpec(object):
    #Only supports a single stat, at least for now
    #Takes a MagicStatFactory, as this will resolve into either an unsplittable or a splittable statistic according to what's suited
    #Note: maybe MagicStatFactory should have a synonomous class name that would appear less intrusive in a setting like this?
    #@takes(AnalysisSpec, MagicStatFactory)
    def __init__(self, statistic=None):
        self._statClassList = [statistic] if statistic else []
        self._analysisParts = []
        self._analysisOptionsDict = OrderedDefaultDict(list)

    def integrateParsedAnalysis(self, other):
        assert isinstance(other, AnalysisSpec)
        self._statClassList = copy(other._statClassList)
        self._analysisParts = copy(other._analysisParts)
        self._analysisOptionsDict = copy(other._analysisOptionsDict)

    #@takes(str, str)
    def addParameter(self, paramName, paramValue):
        self._appendAnalysisOption('[%s=%s]' % (paramName, paramValue))

    def _appendAnalysisOption(self, optionLine):
        analysisOption = AnalysisOption(optionLine)
        self._analysisParts.append(analysisOption)
        self._analysisOptionsDict[analysisOption.getLabelKey()].append(analysisOption)

    def _removeAnalysisOption(self, optionLabelKey):
        for option in self._allAnalysisOptions([optionLabelKey], raiseIfEmpty=True):
            self._analysisParts.remove(option)
        self._analysisOptionsDict.remove(optionLabelKey)

    def _allAnalysisOptions(self, labelKeys=None, onlyWithLabelText=False, onlyActivated=False, raiseIfEmpty=False):
        empty = True

        if labelKeys is None:
            labelKeys = self._analysisOptionsDict.keys()

        for key in labelKeys:
            options = self._analysisOptionsDict.get(key)
            if options is not None:
                if onlyWithLabelText:
                    options = [opt for opt in options if opt.getLabelText() != '']
                if onlyActivated:
                    options = [opt for opt in options if opt.isActivated(self)]
                if options:
                    empty = False
                    for opt in options:
                        yield opt

        if empty and raiseIfEmpty:
            raise ShouldNotOccurError

    def getDefAfterChoices(self, filterByActivation=False):
        defAfterChoices = ''
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):
                if filterByActivation and not part.isActivated(self):
                    continue
                defAfterChoices += part.getDefAfterChoice()
            else:
                defAfterChoices += str(part)
        defAfterChoices += ' -> ' + ','.join([x.__name__ for x in self._statClassList])
        return defAfterChoices

        
class AnalysisDefHandler(AnalysisSpec):
    H0_KEY = 'H0'
    H1_KEY = 'H1'
    TAIL_KEY = 'tails'
    TAIL_CHOICE_LEFT  = 'less'
    TAIL_CHOICE_RIGHT = 'more'
    TAIL_CHOICE_BOTH = 'different'
    ASSUMP_LABEL_KEY = 'assumptions'
    RANDOM_SEED_KEY = 'randomSeed'
    RANDOM_SEED_CHOICE_RANDOM = 'Random'
    ILLUSTRATION_FN_KEY = 'illustrationFn'
    TF1_KEY = 'tf1'
    TF2_KEY = 'tf2'
    
    def __init__(self, analysisLine=None, reversed=False):
        super(AnalysisDefHandler, self).__init__()
        self.reversed = reversed
        if analysisLine:
            self._parseDef(analysisLine)

    def _parseDef(self, analysisLine):
        # Older version of first pattern, given no checks
        #                    ([^-[]* #pure text - not '['
        parts = re.findall('''
                            # Match pure text (part[0]):
                           ( (?: [^-[]* (?:-(?!>))? )* #1. pure text - not '[' or '-',
                                                       #2. separated by a possible '-' that is not before a '>'
                                                       #1 and 2 is repeated as long as necessary
                           [^-[\s]+) #should not end with whitespace,
                                     #as this may belong to the '->'-expression
                           # Match option clause (part[1])            
                           |( \[ [^[\]]* \] ) #Matches an expression inside brackets '[]'
                           # Match specification of statistic classes (part[2])
                           |( \s? \-> \s? .* )
                           # Match any additional whitespace (part[3])
                           |(\s*)
                           ''', analysisLine, flags=re.VERBOSE)
        
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        for part in parts:
            if part[0] != '':
                self._analysisParts.append(part[0])
            if part[1] != '':
                self._appendAnalysisOption(part[1])
            if part[2] != '':
                statNames = part[2].replace('->','').replace(' ','').split(',')
                self._statClassList = [STAT_CLASS_DICT[statName] for statName in statNames \
                                       if STAT_CLASS_DICT.get(statName) is not None]
                if len(self._statClassList)==0:
                    if len(statNames)==0:
                        logMessage('No statistic found when parsing analysisDef: ' + analysisLine)
                    else:
                        logMessage('Specified statistics not found in STAT_CLASS_DICT. '
                                   'Statistics: %s, and keys in STAT_CLASS_DICT: %s' %
                                   (str(statNames), str(STAT_CLASS_DICT)))
            if part[3] != '':
                self._analysisParts.append(part[3])

    def setChoice(self, optionLabelKeyOrText, choiceKeyOrText):
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):
                if optionLabelKeyOrText in [part.getLabelKey(), part.getLabelText()]:
                    part.setChoice(choiceKeyOrText)
                    #self.resetValidStat()
                    return
        raise ShouldNotOccurError
    
    def setDefaultChoice(self, optionLabelKeyOrText):
        for part in self._analysisParts:
            if isinstance(part, AnalysisOption):
                if optionLabelKeyOrText in [part.getLabelKey(), part.getLabelText()]:
                    part.setDefaultChoice()
                    return
        raise ShouldNotOccurError

    def reduceChoices(self, optionLabelKey, choiceKeyList):
        for option in self._allAnalysisOptions([optionLabelKey]):
            if len(choiceKeyList) == 0:
                self._removeAnalysisOption(optionLabelKey)
            else:
                option.reduceChoices(choiceKeyList)
            #self.resetValidStat()
            return

    def changeChoices(self, optionLabelKey, choiceList):
        for option in self._allAnalysisOptions([optionLabelKey], raiseIfEmpty=True):
            if len(choiceList) == 0:
                self._removeAnalysisOption(optionLabelKey)
            else:
                option.changeChoices(choiceList)
            return

    def getChoice(self, optionLabelKey):
        for option in self._allAnalysisOptions([optionLabelKey]):
            return option.getChoice()
        return None

    def getChoiceText(self, optionLabelKey):
        for option in self._allAnalysisOptions([optionLabelKey]):
            return option.getChoiceText()
        return None
    
    def getOptionLabelsAsText(self):
        return [opt.getLabelText() for opt in self._allAnalysisOptions(onlyWithLabelText=True)]
    
    def getOptionsAsText(self):
        return dict((opt.getLabelText(), opt.getAllChoiceTexts())
                    for opt in self._allAnalysisOptions(onlyWithLabelText=True))

    def getFilteredOptionLabelsAsText(self, labelKeys):
        return [opt.getLabelText() for opt in self._allAnalysisOptions(labelKeys, onlyWithLabelText=True)]

    def getFilteredOptionsAsText(self, labelKeys):
        return dict((opt.getLabelText(), opt.getAllChoiceTexts())
                    for opt in self._allAnalysisOptions(labelKeys, onlyWithLabelText=True))

    def getOptionsAsKeys(self):
        return dict((opt.getLabelKey(), opt.getAllChoiceKeys())
                    for opt in self._allAnalysisOptions(onlyWithLabelText=True))
        
    def getFirstOptionKeyAndValues(self):
        '''
            Return the first parameter. Temporary usage for API calls of doAnalysis.
        '''
        for opt in self._allAnalysisOptions(onlyWithLabelText=True):
            return opt.getLabelKey(), opt.getAllChoiceKeys()
        return None, None
    
    def getAllOptionsAsKeys(self):
        return dict((opt.getLabelKey(), opt.getAllChoiceKeys()) for opt in self._allAnalysisOptions())
    
    def getAllChoices(self, filterByActivation=False):
        return dict((opt.getLabelKey(), opt.getChoice())
                    for opt in self._allAnalysisOptions(onlyActivated=filterByActivation))

    def getChoicesAsText(self):
        return dict((opt.getLabelText(), opt.getChoiceText())
                    for opt in self._allAnalysisOptions(onlyWithLabelText=True))

    def getFilteredChoicesAsText(self, labelKeys):
        return dict((opt.getLabelText(), opt.getChoiceText())
                    for opt in self._allAnalysisOptions(labelKeys, onlyWithLabelText=True))

    def getDef(self):
        return ''.join((part.getDef() if isinstance(part, AnalysisOption) else str(part))
                       for part in self._analysisParts) \
               + ' -> ' + ','.join([x.__name__ for x in self._statClassList])

    @staticmethod
    def splitAnalysisText(text):
        assert text.count(':') >= 1, text
        splitPos = text.find(':')
        return text[:splitPos], text[splitPos+1:]
 
    # The following methods help interprete data in configs, and thus contains some definitions of semantics
    # def getH0(self):
    #    #print 'My keys: ', self.getOptionsAsKeys()
    #    #if 'H0' in self.getOptionsAsKeys():
    #    #    return self.getChoice('H0')
    #    choices = self.getChoices()
    #    if 'H0' in choices:
    #        return choices['H0']
    #    else:
    #        #print 'My keys: ', self.getOptionsAsKeys()
    #        return None
    #
    #
    # def getH1(self):
    #    #optionKeys = self.getOptionsAsKeys()
    #    #if 'H1' in optionKeys and 'tails' in optionKeys:
    #    choices = self.getChoices()
    #    if 'H1' in choices and 'tails' in choices:
    #        try:
    #            #tailChoice = self.getChoice('tails')
    #            tailChoice = choices['tails']
    #            self.setChoice('H1', tailChoice)
    #            return self.getChoiceText('H1')
    #
    #        except (ShouldNotOccurError), e:
    #            logException(e, logging.WARNING,'Could not find H1, probably mismatch between tails and H1 in analysisDef (tails choice: %s)' % self.getChoice('tails') )
    #        except Exception, e:
    #            logException(e, logging.WARNING,'Could not find H1')
    #    return 'No H1 found..'
    #
    #
    # def getNullModel(self):
    #    if 'assumptions' in self.getOptionsAsKeys():
    #        return self.getChoiceText('assumptions')
    #    else:
    #        return None
    
    def _getFormatConverterKeys(self):
        return [self.TF1_KEY, self.TF2_KEY]
    
    def getFormatConverterOptionLabelsAsText(self):
        return self.getFilteredOptionLabelsAsText(self._getFormatConverterKeys())
    
    def getFormatConverterOptionsAsText(self):
        return self.getFilteredOptionsAsText(self._getFormatConverterKeys())
    
    def getFormatConverterChoicesAsText(self):
        return self.getFilteredChoicesAsText(self._getFormatConverterKeys())
    
    def _getInterfaceChoiceKeys(self):
        return [x for x in self.getAllChoices().keys() if not x in self._getFormatConverterKeys()]
    
    def getInterfaceOptionLabelsAsText(self):
        return self.getFilteredOptionLabelsAsText(self._getInterfaceChoiceKeys())
    
    def getInterfaceOptionsAsText(self):
        return self.getFilteredOptionsAsText(self._getInterfaceChoiceKeys())
    
    def getInterfaceChoicesAsText(self):
        return self.getFilteredChoicesAsText(self._getInterfaceChoiceKeys())
    
    def getH0(self):
        H0 = self.getChoice(self.H0_KEY)
        # if H0 is None:
        #     logMessage('Could not find H0 in analysisDef: ' + self._analysisLine)
        return H0
         
    def getH1(self):
        # H1 = self.getChoiceText(self.H1_KEY)
        # return H1
        tailChoice = self.getChoice(self.TAIL_KEY)
        if tailChoice is None:
            return None
        
        selectedH1Key = self.H1_KEY + '_' + tailChoice
        H1 = self.getChoice(selectedH1Key)
        if H1 is None:
            logMessage(
                'Could not find H1, probably mismatch between tails-choice and corresponding H1-option in analysisDef '
                '(tails choice: %s, options: %s)' % (self.getChoice('tails'), self.getAllOptionsAsKeys())
            )
    
        return H1

    #todo:To be phased out..
    def syncH1WithTail(self):
        optionKeys = self.getAllOptionsAsKeys()
        if self.H1_KEY in optionKeys and self.TAIL_KEY in optionKeys:
            try:
                tailChoice = self.getChoice(self.TAIL_KEY)                
                self.setChoice(self.H1_KEY, tailChoice)
            
            except (ShouldNotOccurError) as e:
                logException(e, logging.WARNING,
                             'Could not find H1, probably mismatch between tails and H1 in analysisDef (tails choice: %s)'
                             % self.getChoice(self.TAIL_KEY))
            except Exception as e:
                logException(e, logging.WARNING,'Could not find H1')
    
    def getNullModel(self):
        nullModel = self.getChoiceText(self.ASSUMP_LABEL_KEY)
        if self.reversed:
            if re.search('[^ ,.]T[12][^ ,.]',nullModel):
                logMessage('Found instance of T1/T2 in null-model that may not refer to '
                           'tracks as assumed in getNullModel')
            assert not 'tempT2' in nullModel
            
            nullModel = nullModel.replace('T1','tempT2')
            nullModel = nullModel.replace('T2','T1')
            nullModel = nullModel.replace('tempT2','T2')
        
        return nullModel
    
    def isTwoSidedTest(self):
        tailChoice = self.getChoice(self.TAIL_KEY)
        if tailChoice is not None and tailChoice == self.TAIL_CHOICE_BOTH:
            return True
        else:
            return False
        
    def getIllustrationFn(self):
        return self.getChoice(self.ILLUSTRATION_FN_KEY)
