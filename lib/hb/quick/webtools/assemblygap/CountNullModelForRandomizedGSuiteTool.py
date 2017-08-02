from collections import OrderedDict

from gold.application.HBAPI import doAnalysis
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.track.Track import Track
from gold.util import CommonConstants
from gold.util.RandomUtil import random
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.gsuite import GSuiteStatUtils
from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
from quick.statistic.GSuiteVsGSuiteWrapperStat import GSuiteVsGSuiteWrapperStat
from quick.webtools.GeneralGuiTool import GeneralGuiTool, GeneralGuiToolMixin
from quick.webtools.mixin.GenomeMixin import GenomeMixin
from quick.webtools.mixin.UserBinMixin import UserBinMixin
from quick.application.GalaxyInterface import GalaxyInterface
from urllib import quote

from quick.webtools.restricted.visualization.visualizationGraphs import visualizationGraphs


class CountNullModelForRandomizedGSuiteTool(GeneralGuiTool, UserBinMixin, GenomeMixin):
    ALLOW_UNKNOWN_GENOME = False
    OPTION = 'random'

    @classmethod
    def getToolName(cls):
        return "Count null model for randomized gSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select orginal gSuite', 'orgGsuite'),
                ('Select column from orginal gSuite', 'orgCol'),
                ('Select additional orginal gSuite', 'addGsuite'),
                ('Second randomized gSuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
                [('Second column from randomized gSuite', 'randCol'),
                 ('Select method', 'method')] + \
                cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxOrgGsuite(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxOrgCol(cls, prevChoices):
        if prevChoices.orgGsuite:
            first = getGSuiteFromGalaxyTN(prevChoices.orgGsuite)
            attributeList = [cls.OPTION] + ['title'] + first.attributes
            return attributeList
        else:
            return

    @classmethod
    def getOptionsBoxAddGsuite(cls, prevChoices):
        if prevChoices.orgCol == cls.OPTION:
            return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')


    @classmethod
    def getOptionsBoxGsuite(cls, prevChoices):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')


    #options: random mean that two gsuites does not have any common column

    @classmethod
    def getOptionsBoxRandCol(cls, prevChoices):
        if prevChoices.gsuite:
            first = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            attributeList = ['title'] + first.attributes
            return attributeList
        else:
            return

    @classmethod
    def getOptionsBoxMethod(cls, prevChoices):
        return ['1', '2']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        orgGsuite = choices.orgGsuite
        randGsuite = choices.gsuite
        orgCol = choices.orgCol
        randCol = choices.randCol
        method = choices.method

        if orgCol == cls.OPTION:
            addGsuite = choices.addGsuite
            additiionalgSuite = getGSuiteFromGalaxyTN(addGsuite)
            addAttributesList = additiionalgSuite.allTrackTitles()

        orginalgSuite = getGSuiteFromGalaxyTN(orgGsuite)
        randomGsuite = getGSuiteFromGalaxyTN(randGsuite)

        if randCol == 'title':
            randAttributesList = randomGsuite.allTrackTitles()
        else:
            randAttributesList = randomGsuite.getAttributeValueList(randCol)

        randAttributesListNotDuplicates = list(set(randAttributesList))
        numRandAttributesList = len(list(set(randAttributesListNotDuplicates)))

        howManyTimesWasEveryTracksRandomize = len(randAttributesList)/numRandAttributesList

        #
        # print 'randAttributesListNotDuplicates', randAttributesListNotDuplicates, '<br>'
        # print 'numRandAttributesList', numRandAttributesList, '<br>'

        if orgCol == 'title' or orgCol == cls.OPTION:
            orgAttributesList = orginalgSuite.allTrackTitles()
        else:
            orgAttributesList = orginalgSuite.getAttributeValueList(orgCol)

        orgAttributesListNotDuplicates = list(set(orgAttributesList) - set(randAttributesList))
        numOrgAttributesListNotDuplicates = len(orgAttributesListNotDuplicates)

        # print 'orgAttributesListNotDuplicates', orgAttributesListNotDuplicates, '<br>'
        # print 'numOrgAttributesListNotDuplicates', numOrgAttributesListNotDuplicates,'<br>'


        #random tracks just for having analysis real to real
        if orgCol != cls.OPTION:
            randOrginalTracks = random.sample(xrange(numOrgAttributesListNotDuplicates), numRandAttributesList)
        else:
            randTracksForTwoOrginalDatasets = random.sample(xrange(len(addAttributesList)),
                                              numRandAttributesList)
            addOrginalTracks = randTracksForTwoOrginalDatasets[0:numRandAttributesList]

            randOrginalTracks = random.sample(xrange(numOrgAttributesListNotDuplicates),
                                              numRandAttributesList)

            print 'addOrginalTracks', addOrginalTracks, len(addOrginalTracks), '<br>'


        print 'randOrginalTracks', randOrginalTracks, '<br>'

        resultsDict = OrderedDict()

        originalTracksVSRandTracks = OrderedDict()

        oTr = 0
        rTr = 0
        for oTrack1 in orginalgSuite.allTracks():
            if oTr in randOrginalTracks:

                #first analysis
                #one random track from gsuite1 - T1
                #second random track from gsuite - T2

                # T1
                oTrackName1 = oTrack1.trackName
                oTrackTitle1 = oTrackName1[-1]

                #T2 - random tracks to comapare
                if orgCol == cls.OPTION:
                    oTrack2 = additiionalgSuite.getTrackFromIndex(addOrginalTracks[rTr])
                    oTrackName2 = oTrack2.trackName
                    oTrackTitle2 = oTrackName2[-1]
                else:
                    oTrack2 = orginalgSuite.getTrackFromTitle(randAttributesListNotDuplicates[rTr])
                    oTrackTitle2 = randAttributesListNotDuplicates[rTr]

                if method == '1':

                    if not oTrackTitle2 in originalTracksVSRandTracks.keys():
                        originalTracksVSRandTracks[oTrackTitle2] = oTrackTitle1

                    if not oTrackTitle2 in resultsDict.keys():
                        resultsDict[oTrackTitle2] = OrderedDict()
                        resultsDict[oTrackTitle2]['firstRealToSecondRealValue'] = 0
                        resultsDict[oTrackTitle2]['firstRealToRandomLessCountedValues'] = 0
                        resultsDict[oTrackTitle2]['firstRealToRandomMoreOrEqualCountedValues'] = 0

                    print 'oTrackTitle1', oTrackTitle1, '<br>'
                    print 'oTrackTitle2', oTrackTitle2, '<br>'
                    analysis1 = cls.countNullModelMethod(choices, oTrack1, oTrack2, orginalgSuite)

                    print 'analysis1', analysis1, '<br>'
                    print 'resultsDict', resultsDict, '<br>'

                    for key0, val0 in analysis1.iteritems():
                        for key1, val1 in val0.iteritems():
                            resultsDict[oTrackTitle2]['firstRealToSecondRealValue'] = float(val1)

                if method == '2':
                    resultsDict[oTrackTitle2] = OrderedDict()
                    resultsDict[oTrackTitle2]['values'] = []

                rTr += 1
            oTr += 1

        print '<br><br><br><br><br>'

        print 'originalTracksVSRandTracks',originalTracksVSRandTracks, '<br>'
        print 'resultsDict', resultsDict, '<br>'

        print '<br><br><br><br><br>'

        # check random number of tracks
        numForEveryTracksRandomize = 0
        for nrRTrack1, rTrack1 in enumerate(randomGsuite.allTracks()):
            rTrackName1 = rTrack1.trackName
            attrRtrack1 = randAttributesList[nrRTrack1]

            print 'attrRtrack1', attrRtrack1, '<br>'
            if orgCol != cls.OPTION:
                oTrack1 = orginalgSuite.getTrackFromTitle(originalTracksVSRandTracks[attrRtrack1])
                oTrackName1 = oTrack1.trackName
                oTrackTitle1 = oTrackName1[-1]
            else:
                if nrRTrack1!=0 and nrRTrack1%(howManyTimesWasEveryTracksRandomize) == 0:
                    numForEveryTracksRandomize+=1

                oTrack1 = additiionalgSuite.getTrackFromIndex(addOrginalTracks[numForEveryTracksRandomize])
                oTrackName1 = oTrack1.trackName
                oTrackTitle1 = oTrackName1[-1]
                attrRtrack1 = oTrackTitle1
                print 'attrRtrack1', attrRtrack1, '<br>'


            print 'oTrackTitle1', oTrackTitle1, '<br>'
            print 'rTrackName1', rTrackName1, '<br>'

            analysis1 = cls.countNullModelMethod(choices, oTrack1, rTrack1, orginalgSuite)
            print 'analysis1', analysis1, '<br>'

            if method == '1':
                val = resultsDict[attrRtrack1]['firstRealToSecondRealValue']
                for key0, val0 in analysis1.iteritems():
                    for key1, val1 in val0.iteritems():
                        print 'val, val1', val, val1, '<br>'
                        if float(val1) < val:
                            resultsDict[attrRtrack1]['firstRealToRandomLessCountedValues'] += 1
                        else:
                            resultsDict[attrRtrack1]['firstRealToRandomMoreOrEqualCountedValues'] += 1
            if method == '2':
                for key0, val0 in analysis1.iteritems():
                    for key1, val1 in val0.iteritems():
                        resultsDict[oTrackTitle1]['values'].append(val1)

        print '<br><br><br><br><br>'
        print 'resultsDict', resultsDict, '<br>'
        print '<br><br><br><br><br>'

        if method == '1':

            pValueList = []
            for key0, it0 in resultsDict.iteritems():
                print key0, it0, '<br>'
                print 'len(randAttributesList)',len(randAttributesList), 'numRandAttributesList', numRandAttributesList, '<br>'
                print 'float(float(len(randAttributesList))/numRandAttributesList)', float(float(len(randAttributesList))/numRandAttributesList), '<br>'
                pValue = float(it0['firstRealToRandomMoreOrEqualCountedValues'])/float(float(len(randAttributesList))/numRandAttributesList)
                print pValue, '<br>'
                pValueList.append(pValue)


            # print pValueList

            vg = visualizationGraphs()
            res = vg.drawScatterChart(
                pValueList,
                seriesName=['p-values'],
                label='<b>{series.name}</b>: {point.y}',
                height=300,
                yAxisTitle='p-values',
                marginTop=30
            )
        if method == '2':

            pValueList = []
            for key0, it0 in resultsDict.iteritems():
                pValueList.append(it0['values'])

            from proto.RSetup import robjects, r
            rCode = 'ourHist <- function(vec) {hist(vec, plot=FALSE)}'
            dd = robjects.FloatVector(pValueList)
            simpleHist = r(rCode)(dd)

            breaks = list(simpleHist.rx2('breaks'))
            counts = list(simpleHist.rx2('counts'))

            res = vg.drawColumnChart(counts,
                                     xAxisRotation=90,
                                     categories=breaks,
                                     showInLegend=False,
                                     histogram=True,
                                     height=400
                                     )


        htmlCore = HtmlCore()
        htmlCore.begin()
        htmlCore.line(res)
        htmlCore.end()

        print 'Results'
        print htmlCore
        print pValueList


    @classmethod
    def countNullModelMethod(cls, choices, oTrack1, oTrack2, orginalgSuite):
        regSpec, binSpec = UserBinMixin.getRegsAndBinsSpec(choices)
        analysisBins = GalaxyInterface._getUserBinSource(regSpec, binSpec,
                                                         genome=orginalgSuite.genome)
        queryTrackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
            [quote(oTrack1.title, safe='')])
        refTrackTitles = CommonConstants.TRACK_TITLES_SEPARATOR.join(
            [quote(oTrack2.title, safe='')])
        queryTrackList = [Track(oTrack1.trackName, oTrack1.title)]
        refTrackList = [Track(oTrack2.trackName, oTrack2.title)]
        # print queryTrackTitles, '<br>'
        # print refTrackTitles, '<br>'
        analysisSpec = AnalysisSpec(GSuiteVsGSuiteWrapperStat)
        analysisSpec.addParameter('queryTracksNum', str(len(queryTrackList)))
        analysisSpec.addParameter('refTracksNum', str(len(refTrackList)))
        analysisSpec.addParameter('queryTrackTitleList', queryTrackTitles)
        analysisSpec.addParameter('refTrackTitleList', refTrackTitles)
        stat = GSuiteStatUtils.T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP
        analysisSpec.addParameter('similarityStatClassName',
                                  str(GSuiteStatUtils.PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING[stat]))
        resultsObj = doAnalysis(analysisSpec, analysisBins, queryTrackList + refTrackList)
        results = resultsObj.getGlobalResult()
        analysis1 = results['Similarity_score_table']
        return analysis1

    @classmethod
    def validateAndReturnErrors(cls, choices):
        return None

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    # @classmethod
    # def isPublic(cls):
    #     return False
    #
    # @classmethod
    # def isRedirectTool(cls):
    #     return False
    #
    # @classmethod
    # def getRedirectURL(cls, choices):
    #     return ''
    #
    # @classmethod
    # def isHistoryTool(cls):
    #     return True
    #
    # @classmethod
    # def isBatchTool(cls):
    #     return cls.isHistoryTool()
    #
    # @classmethod
    # def isDynamic(cls):
    #     return True
    #
    # @classmethod
    # def getResetBoxes(cls):
    #     return []
    #
    # @classmethod
    # def getToolDescription(cls):
    #     return ''
    #
    # @classmethod
    # def getToolIllustration(cls):
    #     return None
    #
    # @classmethod
    # def getFullExampleURL(cls):
    #     return None
    #
    # @classmethod
    # def isDebugMode(cls):
    #     return False
    #
    @classmethod
    def getOutputFormat(cls, choices):
        return 'customhtml'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
