
from collections import OrderedDict

from rpy2 import robjects

from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack, GalaxyGSuiteTrack
from proto.CommonFunctions import ensurePathExists
from proto.tools.GeneralGuiTool import HistElement
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin


class CreateGSuiteFromTwoBinomialDistrTool(GeneralGuiTool, UserBinMixin, GenomeMixin):
    @classmethod
    def getToolName(cls):
        return "Create gSuite from two binomal distributions"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select gsuite contain track Y', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
                [('Select probability that R=1 given that Y=1', 'firstProb'),
                ('Select probability that R=0 given that Y=0', 'secondProb'),
                ('Select number of output tracks (subsampling replicates Rs)', 'number'),
                ] + cls.getInputBoxNamesForUserBinSelection()


    @classmethod
    def getOptionsBoxGsuite(cls):  # Alt: getOptionsBox1()
        return GeneralGuiTool.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxFirstProb(cls, prevChoices):  # Alt: getOptionsBox2()
        return '0.9'

    @classmethod
    def getOptionsBoxSecondProb(cls, prevChoices):  # Alt: getOptionsBox2()
        return '0.0000001'

    @classmethod
    def getOptionsBoxNumber(cls, prevChoices):  # Alt: getOptionsBox2()
        return '1'

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        gSuite = getGSuiteFromGalaxyTN(choices.gsuite)
        firstProb = choices.firstProb.encode('utf-8')
        firstProb = firstProb.split(',')
        secondProb = choices.secondProb.encode('utf-8')
        secondProb = secondProb.split(',')

        firstProb = [float(f) for f in firstProb]
        secondProb = [float(f) for f in secondProb]

        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)

        number = int(choices.number)
        gtrackData = cls._readRegSpec(regSpec)

        outGSuite = cls._countResults(gSuite, gtrackData, firstProb, secondProb, number,
                                      galaxyFn)

        GSuiteComposer.composeToFile(outGSuite, cls.extraGalaxyFn['output gSuite'])
        print 'Counted gSuite is in the history'

    @classmethod
    def getExtraHistElements(cls, choices):
        return [HistElement('output gSuite', 'gsuite')]

    @classmethod
    def _countResults(cls, gSuite, gtrackData, firstProb, secondProb, number, galaxyFn):

        outGSuite = GSuite()

        for i, iTrack in enumerate(gSuite.allTracks()):
            trackTitle = iTrack.title
            trackPath = iTrack.path

            datasetPerChromosome = {}
            with open(trackPath, 'r') as f:
                for l in f.readlines():
                    line = l.strip('n').split('\t')
                    if line[0] in gtrackData.keys():
                        if not line[0] in datasetPerChromosome.keys():
                            datasetPerChromosome[line[0]] = []
                        if int(line[1]) >=  gtrackData[line[0]][0] and int(line[1]) <= gtrackData[line[0]][1]:
                            datasetPerChromosome[line[0]].append(int(line[1]))


            for nr in range(0, number):
                for f in firstProb:
                    for s in secondProb:
                        dataset = cls._countAllForRequal01(datasetPerChromosome, gtrackData, f,
                                                           s, number)
                        if len(dataset) > 0:
                            cls._buildTrack(outGSuite, trackTitle, gSuite.genome, dataset, galaxyFn,
                                            nr, f, s)

        return outGSuite

    @classmethod
    def _buildTrack(cls, outGSuite, trackTitle, genome, dataset, galaxyFn, nr, f, s):

        attr = OrderedDict()
        attr['originalTrackName'] = str(trackTitle)
        attr['trackVersion'] = str(nr)
        attr['R=1 and Y=1'] = str(f)
        attr['R=0 and Y=0'] = str(s)

        uri = GalaxyGSuiteTrack.generateURI(galaxyFn=galaxyFn,
                                            extraFileName=trackTitle + '--' + str(nr) + '-' + str(f) + '-' + str(s),
                                            suffix='bed')
        gSuiteTrack = GSuiteTrack(uri)
        outFn = gSuiteTrack.path
        ensurePathExists(outFn)

        with open(outFn, 'w') as contentFile:
            contentFile.write(str(''.join(['\t'.join(hr) + '\n' for hr in dataset])))
        contentFile.close()

        gs = GSuiteTrack(uri, title=''.join(trackTitle + '--' + str(nr) + '-' + str(f) + '-' + str(s)), genome=genome,
                         attributes=attr)

        outGSuite.addTrack(gs)

    @classmethod
    def _countAllForRequal01(cls, datasetPerChromosome, gtrackData, firstProb, secondProb,
                             number):

        allPossibilitiesWithOptionFinalChoice = []
        for chr in datasetPerChromosome.keys():
            allPossibilitiesWith1 = datasetPerChromosome[chr] #[1, 2, 5, 6]
            allPossibilitiesWith0 = [i for i in
                                     range(gtrackData[chr][0], gtrackData[chr][1] + 1)]


            allPossibilitiesWith0 = [x for x in allPossibilitiesWith0 if
                                     x not in datasetPerChromosome[chr]]


            allPossibilitiesWith1BinomalDistribution = cls._countBinomalDistribution(
                n=len(allPossibilitiesWith1), size=1, prob=firstProb)
            allPossibilitiesWith0BinomalDistribution = cls._countBinomalDistribution(
                n=len(allPossibilitiesWith0), size=1, prob=secondProb, reverse = True)


            cls._selectChoiceWith1(chr, allPossibilitiesWith1BinomalDistribution,
                                   allPossibilitiesWith1,
                                   allPossibilitiesWithOptionFinalChoice)


            cls._selectChoiceWith1(chr, allPossibilitiesWith0BinomalDistribution,
                                   allPossibilitiesWith0,
                                   allPossibilitiesWithOptionFinalChoice)

        return allPossibilitiesWithOptionFinalChoice

    @classmethod
    def _selectChoiceWith1(cls, chr, allPossibilitiesWithOptionBinomalDistribution,
                           allPossibilitiesWithOption, finalList):


        for i, elI in enumerate(allPossibilitiesWithOptionBinomalDistribution):

            if elI == 1:

                finalList.append([chr, str(allPossibilitiesWithOption[i]),
                                  str(allPossibilitiesWithOption[i] + 1)])

    @classmethod
    def _readRegSpec(cls, parameters):
        # change for gtrack

        parameters = parameters.encode('utf-8')

        dataOut = {}
        parameters = parameters.replace(' ','').split(',')
        for p in parameters:
            chromosme = p.split(':')[0]
            chromosmeSt = int(p.split(':')[1].split('-')[0])
            chromosmeEnd = int(p.split(':')[1].split('-')[1])

            if not chromosme in dataOut.keys():
                dataOut[chromosme] = [chromosmeSt, chromosmeEnd]



        return dataOut

    @classmethod
    def _countBinomalDistribution(cls, n, size, prob, reverse = False):
        from proto.RSetup import r

        rCode = 'countBinomalDist <- function(vec) {' \
                'rbinom(n=vec[1], size=vec[2], prob=vec[3])' \
                '}'
        dd = robjects.FloatVector(
            [n, size, prob])
        output = r(rCode)(dd)


        if reverse == True:
            output = [1 if x == 0 else 0 for x in list(output)]
        else:
            output = list(output)

        return output

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
