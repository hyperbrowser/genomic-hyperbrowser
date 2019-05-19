from collections import OrderedDict

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GalaxyGSuiteTrack, GSuiteTrack
from proto.CommonFunctions import ensurePathExists
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.origdata.UcscHandler import UcscHandler
from quick.webtools.GeneralGuiTool import GeneralGuiTool

#if line.startswith(
class DivideGSuiteAccordingToColumnInTheTrackTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Create hGSuite based on phrases in title column in tracks"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select gSuite', 'gSuite'),
                ('Select operation', 'operation'),
                ('Select phrases (use colon to provide more than one phrase)', 'param'),
                ('Add phrases separately', 'add')
                ]

    @classmethod
    def getOptionsBoxGSuite(cls):
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxOperation(cls, prevChoices):
        if prevChoices.gSuite:
            return ['division by phrase', 'division by symbol', 'division by individual titles']

    @classmethod
    def getOptionsBoxParam(cls, prevChoices):
        if prevChoices.gSuite:
            if prevChoices.operation != 'division by individual titles':
                return ''

    @classmethod
    def getOptionsBoxAdd(cls, prevChoices):
        if prevChoices.gSuite and prevChoices.param:
            if prevChoices.operation == 'division by phrase':
                par = prevChoices.param.replace(' ', '').split(',')
                lenPar = 0
                tf = False
                for pNum, p in enumerate(par):
                    if pNum == 0:
                        lenPar = len(p)
                    if lenPar == len(p):
                        tf = True
                    else:
                        tf = False

                if tf == True:
                    return ['yes', 'no']


    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):

        if choices.operation == 'division by phrase':
            par = choices.param.replace(' ','').split(',')
        elif choices.operation == 'division by individual titles':
            par = ''
        else:
            par = choices.param.encode('utf-8')
        gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
        attrMut = OrderedDict()

        if choices.operation == 'division by phrase':
            if choices.add in ['yes', 'no']:
                add = choices.add
            else:
                add = 'no'

        for a in gSuite.attributes:
            attrMut[a] = gSuite.getAttributeValueList(a)

        outputGSuite = GSuite()

        for i, iTrack in enumerate(gSuite.allTracks()):

            trackTitle = iTrack.title
            trackPath = iTrack.path

            if choices.operation == 'division by phrase':
                cls.divisionByPhrase(add, attrMut, gSuite, galaxyFn, i, outputGSuite, par, trackPath,
                                 trackTitle)
            elif choices.operation == 'division by individual titles':
                cls.divisionByIndividualTitles('', attrMut, gSuite, galaxyFn, i, outputGSuite, par,
                                     trackPath,
                                     trackTitle)
            else:
                cls.divisionBySymbol('', attrMut, gSuite, galaxyFn, i, outputGSuite, par,
                                     trackPath,
                                     trackTitle)

        GSuiteComposer.composeToFile(outputGSuite, galaxyFn)

    @classmethod
    def divisionByIndividualTitles(cls, add, attrMut, gSuite, galaxyFn, i, outputGSuite, par, trackPath,
                         trackTitle):

        lineDict = {}
        with open(trackPath, 'r') as f:
            for l in f.readlines():
                line = l.strip('\n').split('\t')
                try:
                    if not line[3] in lineDict.keys():
                        lineDict[line[3]] = []
                    lineDict[line[3]].append(l)
                except:
                    pass

        #print lineDict
        for p, it in lineDict.iteritems():

            attr = OrderedDict()
            for k in attrMut.keys():
                attr[k] = attrMut[k][i]
            attr['orginalTitle'] = str(trackTitle)
            attr['orginalTitleFromTrack'] = str(p)

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=str(trackTitle) + '--' + str(p),
                                                suffix='bed')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            with open(outFn, 'w') as contentFile:
                contentFile.write(''.join(it))
            contentFile.close()

            gs = GSuiteTrack(uri, title=''.join(
                str(trackTitle) + '--' + str(p)), genome=gSuite.genome,
                             attributes=attr)

            outputGSuite.addTrack(gs)

    @classmethod
    def divisionByPhrase(cls, add, attrMut, gSuite, galaxyFn, i, outputGSuite, par, trackPath,
                         trackTitle):
        for p in par:

            attr = OrderedDict()
            for k in attrMut.keys():
                attr[k] = attrMut[k][i]
            attr['orginalTitle'] = str(trackTitle)
            if add == 'yes':
                for numPEl, pEl in enumerate(p):
                    attr['attribute' + str(numPEl)] = str(pEl)
            attr['attribute'] = str(p)

            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                                extraFileName=str(trackTitle) + '--' + str(p),
                                                suffix='bed')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)

            lineAll = []
            with open(trackPath, 'r') as f:
                for l in f.readlines():
                    line = l.split('\t')
                    try:
                        if p in line[3]:
                            lineAll.append(l)
                    except:
                        pass

            with open(outFn, 'w') as contentFile:
                contentFile.write(''.join(lineAll))
            contentFile.close()

            gs = GSuiteTrack(uri, title=''.join(
                str(trackTitle) + '--' + str(p)), genome=gSuite.genome,
                             attributes=attr)

            outputGSuite.addTrack(gs)

    @classmethod
    def divisionBySymbol(cls, add, attrMut, gSuite, galaxyFn, i, outputGSuite, par, trackPath,
                         trackTitle):

        #par = symbol

        attr = OrderedDict()
        for k in attrMut.keys():
            attr[k] = attrMut[k][i]
        attr['orginalTitle'] = str(trackTitle)

        attrTemp = OrderedDict()
        lineAll = {}
        with open(trackPath, 'r') as f:
            for l in f.readlines():
                if l.startswith('track name='):
                    for a in l.replace('track name=', '').strip('\n').split(par):
                        attrTemp[a] = ''
                    continue
                line = l.strip('\n').split('\t')
                if len(line) == 4:
                    try:
                        k = tuple(line[3].split(par))
                        if not k in lineAll:
                            lineAll[k] = ''
                        lineAll[k] += l
                    except:
                        pass

        for k, v in lineAll.iteritems():
            kTit = '--'.join(k)
            uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn, extraFileName=str(trackTitle) + '--' + str(kTit), suffix='bed')
            gSuiteTrack = GSuiteTrack(uri)
            outFn = gSuiteTrack.path
            ensurePathExists(outFn)
            with open(outFn, 'w') as contentFile:
                contentFile.write(lineAll[k])
            contentFile.close()


            ik = 0
            for kt in attrTemp.keys():
                attrTemp[kt] = k[ik]
                ik += 1

            gs = GSuiteTrack(uri, title=''.join(str(trackTitle) + '--' + str(kTit)), genome=gSuite.genome, attributes=cls.merge_two_dicts(attr, attrTemp))

            outputGSuite.addTrack(gs)

    @classmethod
    def merge_two_dicts(cls, x, y):
        z = x.copy()
        z.update(y)
        return z

    @classmethod
    def selectColumns(cls):
        return ''

    @classmethod
    def validateAndReturnErrors(cls, choices):

        if not choices.gSuite:
            return 'Select gSuite'

            if choices.operation != 'division by individual titles':
                if not choices.param:
                    return 'Select phrases'

        if choices.gSuite:
            gSuite = getGSuiteFromGalaxyTN(choices.gSuite)
            for i, iTrack in enumerate(gSuite.allTracks()):
                if iTrack.suffix != 'bed':
                    return 'Your tracks need to be in .bed format'

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
        return 'gsuite'
        #return 'customhtml'
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
