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

    @classmethod
    def getToolName(cls):
        return "Count null model for randomized gSuite"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select orginal gSuite', 'orgGsuite'),
                ('Select column from orginal gSuite', 'orgCol'),
                ('Second randomized gSuite', 'gsuite')] + \
                cls.getInputBoxNamesForGenomeSelection() + \
                [('Second column from randomized gSuite', 'randCol'),
                 ('Select method', 'method')
                 ] + \
                cls.getInputBoxNamesForUserBinSelection()

    @classmethod
    def getOptionsBoxOrgGsuite(cls):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxOrgCol(cls, prevChoices):
        if prevChoices.orgGsuite:
            first = getGSuiteFromGalaxyTN(prevChoices.orgGsuite)
            attributeList = ['title'] + first.attributes
            return attributeList
        else:
            return

    @classmethod
    def getOptionsBoxGsuite(cls, prevChoices):
        return GeneralGuiToolMixin.getHistorySelectionElement('gsuite')

    @classmethod
    def getOptionsBoxRandCol(cls, prevChoices):
        if prevChoices.gsuite:
            first = getGSuiteFromGalaxyTN(prevChoices.gsuite)
            attributeList = ['title'] + first.attributes
            return attributeList
        else:
            return

    @classmethod
    def getOptionsBoxMethod(cls):
        return ['1', '2']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        orgGsuite = choices.orgGsuite
        randGsuite = choices.gsuite
        orgCol = choices.orgCol
        randCol = choices.randCol
        method = choices.method

        orginalgSuite = getGSuiteFromGalaxyTN(orgGsuite)
        randomGsuite = getGSuiteFromGalaxyTN(randGsuite)

        if randCol == 'title':
            randAttributesList = randomGsuite.allTrackTitles()
        else:
            randAttributesList = randomGsuite.getAttributeValueList(randCol)

        randAttributesListNotDuplicates = list(set(randAttributesList))
        numRandAttributesList = len(list(set(randAttributesListNotDuplicates)))

        # print 'randAttributesListNotDuplicates', randAttributesListNotDuplicates, '<br>'
        # print 'numRandAttributesList', numRandAttributesList, '<br>'

        if orgCol == 'title':
            orgAttributesList = orginalgSuite.allTrackTitles()
        else:
            orgAttributesList = orginalgSuite.getAttributeValueList(orgCol)

        orgAttributesListNotDuplicates = list(set(orgAttributesList) - set(randAttributesList))
        numOrgAttributesListNotDuplicates = len(orgAttributesListNotDuplicates)

        # print 'orgAttributesListNotDuplicates', orgAttributesListNotDuplicates, '<br>'
        # print 'numOrgAttributesListNotDuplicates', numOrgAttributesListNotDuplicates,'<br>'


        #random tracks just for having analysis real to real
        randOrginalTracks = random.sample(xrange(numOrgAttributesListNotDuplicates), numRandAttributesList)

        # print 'randOrginalTracks', randOrginalTracks, '<br>'

        resultsDict = OrderedDict()

        oTr = 0
        rTr = 0
        for oTrack1 in orginalgSuite.allTracks():
            if oTr in randOrginalTracks:

                #first analysis
                #one random track from gsuite1 - T1
                #second random track from gsuite - T2

                oTrackName1 = oTrack1.trackName
                oTrackTitle1 = oTrackName1[-1]

                oTrack2 = orginalgSuite.getTrackFromTitle(randAttributesListNotDuplicates[rTr])
                oTrackTitle2 = randAttributesListNotDuplicates[rTr]

                if method == '1':
                    if not oTrackTitle2 in resultsDict.keys():
                        # print 'oTrackTitle1', oTrackTitle1, '<br>'
                        # print 'oTrackTitle2', oTrackTitle2, '<br>'
                        resultsDict[oTrackTitle2] = OrderedDict()
                        resultsDict[oTrackTitle2]['firstRealToSecondRealValue'] = 0
                        resultsDict[oTrackTitle2]['firstRealToRandomLessCountedValues'] = 0
                        resultsDict[oTrackTitle2]['firstRealToRandomMoreOrEqualCountedValues'] = 0


                    analysis1 = cls.countNullModelMethod(choices, oTrack1, oTrack2, orginalgSuite)

                    # print 'analysis1', analysis1, '<br>'
                    # print 'resultsDict', resultsDict, '<br>'

                    for key0, val0 in analysis1.iteritems():
                        # print 'key0, val0', key0, val0, '<br>'
                        for key1, val1 in val0.iteritems():
                            # print 'key1, val1', key1, val1, '<br>'
                            resultsDict[oTrackTitle2]['firstRealToSecondRealValue'] = float(val1)

                if method == '2':
                    resultsDict[oTrackTitle2] = OrderedDict()
                    resultsDict[oTrackTitle2]['values'] = []

                rTr += 1
            oTr += 1

        # print resultsDict

        # check random number of tracks
        for nrRTrack1, rTrack1 in enumerate(randomGsuite.allTracks()):
            rTrackName1 = rTrack1.trackName
            attrRtrack1 = randAttributesList[nrRTrack1]

            oTrack1 = orginalgSuite.getTrackFromTitle(attrRtrack1)
            oTrackName1 = oTrack1.trackName
            oTrackTitle1 = oTrackName1[-1]

            analysis1 = cls.countNullModelMethod(choices, oTrack1, rTrack1, orginalgSuite)

            if method == '1':
                val = resultsDict[oTrackTitle1]['firstRealToSecondRealValue']
                for key0, val0 in analysis1.iteritems():
                    # print 'key0, val0', key0, val0, '<br>'
                    for key1, val1 in val0.iteritems():
                        # print 'key1, val1', key1, val1, '<br>'
                        if float(val1) < val:
                            resultsDict[oTrackTitle1]['firstRealToRandomLessCountedValues'] += 1
                        else:
                            resultsDict[oTrackTitle1]['firstRealToRandomMoreOrEqualCountedValues'] += 1
            if method == '2':
                for key0, val0 in analysis1.iteritems():
                    for key1, val1 in val0.iteritems():
                        resultsDict[oTrackTitle1]['firstRealToSecondRealValue'].append(val1)

        # print resultsDict

        if method == '1':
            pValueList = []
            for key0, it0 in resultsDict.iteritems():
                pValue = it0['firstRealToRandomMoreOrEqualCountedValues']/float(float(len(randAttributesList))/numRandAttributesList)
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
            ss

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
