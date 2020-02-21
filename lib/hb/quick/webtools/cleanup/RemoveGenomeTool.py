import os
from collections import OrderedDict

from quick.genome.GenomeCommonFunctions import GENOME_PATHS, removeGenomeData
from quick.webtools.GeneralGuiTool import GeneralGuiTool


class RemoveGenomeTool(GeneralGuiTool):

    @staticmethod
    def getToolName():
        return "Remove genome"

    @staticmethod
    def getInputBoxNames():
        return [('Genome', 'genome'),
                ('From which paths to remove the genome', 'paths')]

    @staticmethod    
    def getOptionsBoxGenome():
        return "__genome__"
    
    @classmethod
    def getOptionsBoxPaths(cls, prevChoices):
        return OrderedDict([(key, True) for key in GENOME_PATHS.keys()])
    
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    return ['']

    #@staticmethod    
    #def getOptionsBox4(prevChoices):
    #    return ['']

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        
            
        print 'Executing... starting to remove ' + choices[0] + os.linesep

        trackFolders = [trackFolder for trackFolder, checked in choices.paths.iteritems() if checked]
        genome = choices.genome

        for folder in trackFolders:
            removeGenomeData(genome, folder, removeFromShelve=True)


    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        if not choices.genome:
            return 'Please select a genome'

        if not any([val for val in choices.paths.values()]):
            return 'Please select at least one path'
    
    #@staticmethod
    #def isPublic():
    #    return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    @staticmethod
    def getToolDescription():
        return 'This tool will remove a genome and associated tracks. '+\
               '(Note: Genome is not deleted, but moved to .trash directories)'
    
    @staticmethod
    def isDynamic():
        return False

    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    #@staticmethod    
    #def getOutputFormat():
    #    return 'html'
    #
    #@staticmethod
    #def validateAndReturnErrors(choices):
    #    '''
    #    Should validate the selected input parameters. If the parameters are not valid,
    #    an error text explaining the problem should be returned. The GUI then shows this
    #    to the user and greys out the execute button. If all parameters are valid, the method
    #    whould return None, which enables the execute button.
    #    '''
    #    return None
