from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.util.GenomeInfo import GenomeInfo
from config.Config import NONSTANDARD_DATA_PATH, ORIG_DATA_PATH, PARSING_ERROR_DATA_PATH, NMER_CHAIN_DATA_PATH
from quick.util.CommonFunctions import ensurePathExists
from gold.util.CommonFunctions import createDirPath
import shutil, os

class RemoveGenomeTool(GeneralGuiTool):
    @staticmethod
    def getToolName():
        return "Remove genome"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Genome']

    @staticmethod    
    def getOptionsBox1():
        "Returns a list of options to be displayed in the first options box"
        return "__genome__"
    
    #@staticmethod    
    #def getOptionsBox2(prevChoices): 
    #    '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
    #    prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
    #    '''
    #    return ['']
    
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

        paths = [NONSTANDARD_DATA_PATH, ORIG_DATA_PATH, PARSING_ERROR_DATA_PATH, NMER_CHAIN_DATA_PATH] +\
                 [createDirPath('', '', allowOverlaps=x) for x in [False, True]]
        
        for p in paths:
            genome = choices[0]
            origPath = os.sep.join([ p, genome ])
            trashPath = os.sep.join([ p, ".trash", genome ])

            if os.path.exists(origPath):
                print 'Moving ' + genome + ' to .trash in folder: ' + p + os.linesep
                ensurePathExists(trashPath)
                shutil.move(origPath, trashPath)


    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
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