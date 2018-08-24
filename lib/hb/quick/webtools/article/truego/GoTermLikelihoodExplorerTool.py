from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager
from proto.HtmlCore import HtmlCore
from proto.TextCore import TextCore
from quick.extra.trueGOProject.trueGO.readGoFile import (ReadGoFile,GoTerms,Genes,GoGeneMapping,GoGeneMatrix)
from quick.extra.trueGOProject.trueGO.userdata import *
from quick.extra.trueGOProject.trueGO.computeLikelihoods import *
from itertools import combinations
import os
from config.Config import DATA_FILES_PATH

class GoTermLikelihoodExplorerTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        """
        Specifies a header of the tool, which is displayed at the top of the
        page.

        Mandatory method for all ProTo tools.
        """
        return "GoTermLikelihoodExplorer"

    @classmethod
    def getInputBoxNames(cls):

        return [("Select species", 'selectSpecies'),
                ("Choose a file with GO terms",'chooseGoTermsFile'),
                ("Choose a list of genes that was used for GO analysis",'chooseGoTermsGeneListFile')]

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
    # @classmethod
    # def getOptionsBoxToolDescTop(cls):
    #     core = HtmlCore()
    #     core.bigHeader('GO terms likelihood explorer')
    #     core.smallHeader('Given two GO terms, this tool provides functionality to explore their likelihoods')
    #     core.divider()
    #     return '__rawStr__', str(core)
    #
    # @classmethod
    # def getOptionsBoxDivider(cls, prevChoices):
    #     core = HtmlCore()
    #     core.divider()
    #     return '__rawStr__', str(core)

    @classmethod
    def getOptionsBoxSelectSpecies(cls):  # Alt: getOptionsBox1()

        return ['Human', 'unsupported species']

    @classmethod
    def getOptionsBoxChooseGoTermsFile(cls, prevChoices):  # Alt: getOptionsBox2()
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
        return GeneralGuiTool.getHistorySelectionElement('tabular')

    @classmethod
    def getOptionsBoxChooseGoTermsGeneListFile(cls, prevChoices):  # Alt: getOptionsBox2()
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
        return GeneralGuiTool.getHistorySelectionElement('tabular')

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
        filename = cls.determineGoAnnotationFile(choices)
        userterms = ExternalTrackManager.extractFnFromGalaxyTN(choices.chooseGoTermsFile)
        usergenes = ExternalTrackManager.extractFnFromGalaxyTN(choices.chooseGoTermsGeneListFile)
        gofile = ReadGoFile(goFn=filename)
        goterms = GoTerms()
        genes = Genes()
        gogenemap = GoGeneMapping()
        gogenemat = GoGeneMatrix()
        gocontent = gofile._readGoFile(goFn=filename)
        gotermlist = goterms.getGoTerms(gocontent)
        genelist = genes.getGenes(gocontent)
        geneuniverselist = genes.getGeneUniverse()
        gogenemapping= gogenemap.getGoGeneMapping(gotermlist,genelist)
        userdata = readUserGoList(userterms)
        usergene_list = readUserGeneList(usergenes)
        present_terms = [term for term in userdata if term in gogenemapping.keys()]
        both_likelihoods = computeLikelihoodsForUserGoTerms(usergoterms=present_terms,usergeneslist=usergene_list,gotermgenes=gogenemapping,geneuniversesize=len(geneuniverselist))
        # #kappa = gogenemat.computeKappaforGoTerms(userdata,gogenemapping,len(geneuniverselist))
        core = HtmlCore()
        core.begin()
        core.tableFromDictionary(dataDict=both_likelihoods,columnNames= ['Pair of GO terms','Both Vs Term1','Both Vs Term2'], sortable=True)
        core.end()
        print core


    @classmethod
    def determineGoAnnotationFile(cls, choices):
        selectSpecies = choices.selectSpecies
        if selectSpecies == "Human":
            filename = os.path.join(DATA_FILES_PATH, 'trueGO_data', 'goa_human.gaf')
        else:
            raise Exception()
        return filename

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
        return None

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
    @classmethod
    def getToolDescription(cls):
        core = HtmlCore()
        core.begin()
        core.paragraph('Tool to explore the ideas of TrueGO project. For more information and notes:')
        core.link('Read here on google docs', 'https://docs.google.com/document/d/1yvI-wZeGB9hzMUoRqawxIdvaRH4xiKgFPfNoaYoGqCk/edit')
        core.end()
        return core
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
