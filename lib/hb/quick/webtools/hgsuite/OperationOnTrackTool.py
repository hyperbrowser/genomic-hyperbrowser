from collections import OrderedDict

import numpy

from proto.CommonFunctions import ensurePathExists
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.application.ExternalTrackManager import ExternalTrackManager
from quick.util.GenomeInfo import GenomeInfo
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.webtools.hgsuite.Legend import Legend


class OperationOnTrackTool(GeneralGuiTool):
    @classmethod
    def getToolName(cls):
        return "Operations on track"

    @classmethod
    def getInputBoxNames(cls):
        return [('Select genome or track', 'trackOrGenome'),
                ('Select first track', 'track1'),
                ('Select genome', 'genome'),
                ('Select second track', 'track2'),
                ('Select operations', 'oper')]

    # @classmethod
    # def getInputBoxOrder(cls):
    #     return None
    #
    # @classmethod
    # def getInputBoxGroups(cls, choices=None):
    #     return None

    @classmethod
    def getOptionsBoxTrackOrGenome(cls):
        return ['track', 'genome']

    @classmethod
    def getOptionsBoxTrack1(cls, prevChoices):
        if prevChoices.trackOrGenome == 'track':
            return GeneralGuiTool.getHistorySelectionElement('bed')

    @classmethod
    def getOptionsBoxGenome(cls, prevChoices):
        if prevChoices.trackOrGenome == 'genome':
            return '__genome__'

    @classmethod
    def getOptionsBoxTrack2(cls, prevChoices):
        return GeneralGuiTool.getHistorySelectionElement('bed')

    @classmethod
    def getOptionsBoxOper(cls, prevChoices):
        return ['intersection', 'subtract']

    @classmethod
    def execute(cls, choices, galaxyFn=None, username=''):
        if choices.trackOrGenome == 'genome':
            genome = choices.genome
            data = GenomeInfo.getStdChrLengthDict(genome)

            genomeFile = GalaxyRunSpecificFile(['genome.bed'], galaxyFn)
            ensurePathExists(genomeFile.getDiskPath())
            outputFile = open(genomeFile.getDiskPath(), 'w')
            for chr1, d1 in data.iteritems():
                outputFile.write('\t'.join([str(chr1), str(0), str(d1)]) + '\n')
            outputFile.close()
            track1 = genomeFile.getDiskPath()

        if choices.trackOrGenome == 'track':
            track1 = choices.track1
            track1 = ExternalTrackManager.extractFnFromGalaxyTN(track1.split(':'))

        track2 = choices.track2
        track2 = ExternalTrackManager.extractFnFromGalaxyTN(track2.split(':'))

        import os, subprocess

        print choices.oper

        if choices.oper == "subtract":
            command = """ bedtools subtract -a """ + str(track1) + """ -b  """ + str(track2)

        if choices.oper == "intersection":
            command = """ bedtools intersect -a """ + str(track1) + """ -b  """ + str(track2)

        process = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        results, errors = process.communicate()

        outputFile = open(galaxyFn,'w')
        outputFile.write(results)
        outputFile.close()


    @classmethod
    def validateAndReturnErrors(cls, choices):

        if choices.trackOrGenome:
            if choices.trackOrGenome == 'track':
                if not choices.track1:
                    return "Please select first track"
            if choices.trackOrGenome == 'genome':
                if not choices.genome:
                    return "Please select genome"
            if not choices.track2:
                return "Please select second track"

    # @classmethod
    # def getSubToolClasses(cls):
    #     return None
    #
    @classmethod
    def isPublic(cls):
        return True
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

    @classmethod
    def getToolDescription(cls):

        l = Legend()

        toolDescription = 'The tool allow to proceed operations: intersection or subtract between tracks or genome and track'

        stepsToRunTool = ['Select genome or track',
                          'Select first track/Genome build',
                          'Select second track',
                          'Select operations (intersection, subtract)'
                          ]

        example = {'Example': ['', ["""
        ...
        chr10	3244791	3244792
        chr10	3244825	3244826
        chr10	3256165	3256166
        chr10	6160821	6160822
        chr10	6214122	6214123
        chr10	6626687	6626688
        chr10	6843330	6843331
        ...
                                    """],
               [
                    ['Select genome or track','genome'],
                    ['Genome build','Mouse Dec 2011. (GRCm38/mm10)'],
                    ['Select second track','bed'],
                    ['Select operations','subtract']
                ],
                               [
        """
        ...
        chr10	0	3244791
        chr10	3244792	3244825
        chr10	3244826	3256165
        chr10	3256166	6160821
        chr10	6160822	6214122
        chr10	6214123	6626687
        chr10	6626688	6843330
        chr10	6843331	7412556
        ...
        """
                               ]
                               ]
                   }

        toolResult = 'The output of this tool is a bed file.'

        return Legend().createDescription(toolDescription=toolDescription,
                                          stepsToRunTool=stepsToRunTool,
                                          toolResult=toolResult,
                                          exampleDescription=example
                                          )

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
        return 'bed'
    #
    # @classmethod
    # def getOutputName(cls, choices=None):
    #     return cls.getToolSelectionName()
